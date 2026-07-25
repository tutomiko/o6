import math
from enum import IntEnum

from .candidate import O6Candidate

VALID_PROFILES = ("precise", "balanced", "permissive")


class O6MatchStatus(IntEnum):
    INVALID = -1   # rejected / invalid input
    UNCERTAIN = 0   # query elsewhere
    MATCH = 1       # matched


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
            A tuple (O6MatchStatus, index) where index is the position of the
            matched candidate in the *original* input list, or -1 if rejected
            or uncertain (query elsewhere).
        """
        if not candidates or not isinstance(candidates, list):
            return (O6MatchStatus.INVALID, -1)

        valid_candidates = []

        # --- 1. Robust Data Sanitization ---
        for idx, c in enumerate(candidates):
            cid, confidence_e, confidence_v, samples = self._extract_fields(c)
            if cid is None:
                continue

            try:
                confidence_e = float(confidence_e)
                confidence_v = float(confidence_v)

                if not (math.isfinite(confidence_e) and math.isfinite(confidence_v)):
                    continue

                samples = 0 if samples is None else max(0, int(samples))

                # --- 2. Base Mathematical Foundations (Stable across all profiles) ---
                epsilon = 1e-6
                # Harmonic mean guarantees severe punishment for scores approaching 0
                base_harmonic = (2 * confidence_e * confidence_v) / (confidence_e + confidence_v + epsilon)
                # Asymptotic limit approaching 1.0
                base_maturity = samples / (samples + 1.0)

                # Apply dynamic exponentiation based on profile strictness
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
            return (O6MatchStatus.INVALID, -1)

        # --- 3. Deterministic Sorting & Statistics ---
        valid_candidates.sort(key=lambda x: (-x["Score"], str(x["id"])))
        top_cand = valid_candidates[0]
        top_score = top_cand["Score"]

        pool_mean = sum(c["Score"] for c in valid_candidates) / pool_size
        variance = sum((c["Score"] - pool_mean) ** 2 for c in valid_candidates) / pool_size
        sigma = math.sqrt(variance)

        # --- 4. The Absolute Asymptotic Anchor ---
        if top_score <= self.anchor:
            return (O6MatchStatus.UNCERTAIN, -1)

        if pool_size == 1:
            return (O6MatchStatus.MATCH, top_cand["index"])

        # --- 5. Dynamic Tiering & Relative Dominance ---
        top_tier = [c for c in valid_candidates if (top_score - c["Score"]) <= sigma]
        top_tier_avg = sum(c["Score"] for c in top_tier) / len(top_tier)

        rest_of_pool = [c for c in valid_candidates if (top_score - c["Score"]) > sigma]
        next_tier_score = rest_of_pool[0]["Score"] if rest_of_pool else 0.0

        margin = top_tier_avg - next_tier_score

        # Margin requirement scales with the noise (pool_mean), scaled by the profile
        margin_req = pool_mean * self.margin_multiplier

        if margin < margin_req:
            return (O6MatchStatus.UNCERTAIN, -1)

        # --- 6. The Clear Winner ---
        return (O6MatchStatus.MATCH, top_cand["index"])

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
