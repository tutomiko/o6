from .helpers import generate_background_noise

NAME = "early_truth_false_negative"


def generate(rng, pool_size):
    """Early truth false negative stress (Type II error exposure)."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    accurate_candidate = {
        "id": 77,
        "confidence_e": 0.6,
        "samples": 5,
        "confidence_v": 0.6
    }
    candidates.append(accurate_candidate)
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {77}, True
