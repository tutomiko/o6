from .helpers import generate_background_noise

NAME = "shifted_calibration_false_negative"


def generate(rng, pool_size):
    """Hard-coded thresholds (False Negative exposure)."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    winner_id = 77
    winner = {"id": winner_id, "confidence_e": 0.52, "samples": 5000, "confidence_v": 0.52}
    candidates.append(winner)
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {winner_id}, True
