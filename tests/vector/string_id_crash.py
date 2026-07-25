from .helpers import generate_background_noise

NAME = "string_id_crash"


def generate(rng, pool_size):
    """Winner validity (non-int IDs)."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    c1 = {"id": "dog", "confidence_e": 0.95, "samples": 1000, "confidence_v": 0.95}
    candidates.append(c1)
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {"dog"}, True
