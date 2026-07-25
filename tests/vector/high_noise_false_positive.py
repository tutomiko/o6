from .helpers import generate_background_noise

NAME = "high_noise_false_positive"


def generate(rng, pool_size):
    """Hard-coded thresholds (False Positive exposure)."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    for i in range(5):
        candidates.append({"id": 200 + i, "confidence_e": 0.6, "samples": 10, "confidence_v": 0.55})
    rng.shuffle(candidates)
    return candidates, "Reject/Elsewhere", None, False
