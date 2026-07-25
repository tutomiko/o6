import math

from .candidate import O6Candidate

VALID_PROFILES = ("precise", "balanced", "permissive")

UNCERTAIN = -1


class O6Matcher:
    """
    Executes the Dynamic Tiering & Inverse-Density Model.
    Utilizes dynamic exponentiation and relative margin scaling to smoothly
    trade precision for recall without disabling core statistical guardrails.
    """

    def __init__(self, profile="balanced"):
        if profile not in VALID_PROFILES:
            raise ValueError(f"Unknown profile '{profile}'. Must be one of {list(VALID_PROFILES)}.")

        self.profile = profile

        # --- Profile Parameterization ---
        # sig_exp: signal penalty exponent | mat_exp: maturity penalty exponent
        if profile == "precise":
            self.sig_exp, self.mat_exp = 2.0, 2.0
            self.anchor = 0.50
            self.margin_multiplier = 1.00
        elif profile == "balanced":
            self.sig_exp, self.mat_exp = 1.5, 1.5
            self.anchor = 0.35
            self.margin_multiplier = 0.75
        elif profile == "permissive":
            self.sig_exp, self.mat_exp = 1.0, 1.0
            self.anchor = 0.20
            self.margin_multiplier = 0.50

    def match(self, candidates):
        """
        Runs the matcher over a pool of candidates.

        Returns:
            An int: the index of the matched candidate in the *original*
            input list, or UNCERTAIN (-1) if no candidate is confidently
            matched (query elsewhere).

        Raises:
            ValueError: if candidates is invalid (not a list, empty, or no
                candidate in it is usable after sanitization).
        """
        if not candidates or not isinstance(candidates, list):
            raise ValueError("candidates must be a non-empty list.")

        original_pool_size = len(candidates)
        valid_candidates = []

        # --- 1. Robust Data Sanitization ---
        for idx, c in enumerate(candidates):
            cid, confidence_e, confidence_v, samples = self._extract_fields(c)
            if cid is None:
                continue

            try:
                # Reject Booleans masquerading as valid numbers
                if isinstance(confidence_e, bool) or isinstance(confidence_v, bool) or isinstance(samples, bool):
                    continue

                confidence_e = float(confidence_e)
                confidence_v = float(confidence_v)

                if not (math.isfinite(confidence_e) and math.isfinite(confidence_v)):
                    continue

                # Domain Bounding: Confidence must be a valid probability
                if not (0.0 <= confidence_e <= 1.0) or not (0.0 <= confidence_v <= 1.0):
                    continue

                samples = 0 if samples is None else max(0, int(samples))

                # --- 2. Base Mathematical Foundations ---
                epsilon = 1e-6
                base_harmonic = (2 * confidence_e * confidence_v) / (confidence_e + confidence_v + epsilon)
                base_maturity = samples / (samples + 1.0)

                signal_power = base_harmonic ** self.sig_exp
                maturity_power = base_maturity ** self.mat_exp

                total_score = signal_power * maturity_power

                valid_candidates.append({
                    "id": cid,
                    "index": idx,
                    "Score": total_score,
                })
            except (ValueError, TypeError, OverflowError):
                continue

        pool_size = len(valid_candidates)
        if pool_size == 0:
            raise ValueError("No usable candidates remained after sanitization.")

        # --- 2.5 Trust Factor (Zero-Trust Integrity Penalty) ---
        trust_factor = pool_size / original_pool_size

        # --- 3. Deterministic Sorting & Statistics ---
        valid_candidates.sort(key=lambda x: (-x["Score"], str(x["id"])))
        top_cand = valid_candidates[0]
        top_score = top_cand["Score"]

        pool_mean = sum(c["Score"] for c in valid_candidates) / pool_size
        variance = sum((c["Score"] - pool_mean) ** 2 for c in valid_candidates) / pool_size
        sigma = math.sqrt(variance)

        # --- 4. The Absolute Asymptotic Anchor (Adjusted for Trust) ---
        # The perceived maturity of the score decays linearly with corrupted data
        if (top_score * trust_factor) <= self.anchor:
            return UNCERTAIN

        if pool_size == 1:
            return top_cand["index"]

        # --- 5. Dynamic Tiering & Relative Dominance ---
        top_tier = [c for c in valid_candidates if (top_score - c["Score"]) <= sigma]
        top_tier_avg = sum(c["Score"] for c in top_tier) / len(top_tier)

        rest_of_pool = [c for c in valid_candidates if (top_score - c["Score"]) > sigma]
        next_tier_score = rest_of_pool[0]["Score"] if rest_of_pool else 0.0

        margin = top_tier_avg - next_tier_score

        # Margin requirement scales with noise, profile, AND the inverse of trust
        margin_req = (pool_mean * self.margin_multiplier) / trust_factor

        if margin < margin_req:
            return UNCERTAIN

        # --- 6. The Clear Winner ---
        return top_cand["index"]
        
    @staticmethod
    def _extract_fields(c):
        """
        Pulls (id, confidence_e, confidence_v, samples) out of a candidate that
        may be an O6Candidate instance, a dict, or malformed/garbage input.
        Returns (None, None, None, None) if the candidate is unusable.
        """
        if isinstance(c, O6Candidate):
            return c.id, c.confidence_e, c.confidence_v, c.samples

        if not isinstance(c, dict) or c.get("id") is None:
            return None, None, None, None

        return (
            c["id"],
            c.get("confidence_e", 0.0),
            c.get("confidence_v", 0.0),
            c.get("samples", 0),
        )
