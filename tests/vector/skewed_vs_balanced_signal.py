from .helpers import generate_background_noise

NAME = "skewed_vs_balanced_signal"


def generate(rng, pool_size):
    """Linear signal assumption & equal weighting."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    c1 = {"id": 1, "confidence_e": 0.99, "samples": 1000, "confidence_v": 0.01}
    c2 = {"id": 2, "confidence_e": 0.50, "samples": 1000, "confidence_v": 0.50}
    candidates.extend([c1, c2])
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {2}, True
