from .helpers import generate_background_noise

NAME = "duplicate_ids"


def generate(rng, pool_size):
    """Duplicate IDs."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    c1 = {"id": 7, "confidence_e": 0.90, "samples": 100, "confidence_v": 0.90}
    c2 = {"id": 7, "confidence_e": 0.95, "samples": 150, "confidence_v": 0.95}
    candidates.extend([c1, c2])
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {7}, True
