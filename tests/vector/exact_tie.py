from .helpers import generate_background_noise

NAME = "exact_tie"


def generate(rng, pool_size):
    """Exact tie resolution."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    base_val = rng.uniform(0.85, 0.95)
    c1 = {"id": 1, "confidence_e": base_val, "samples": 1000, "confidence_v": base_val}
    c2 = {"id": 2, "confidence_e": base_val, "samples": 1000, "confidence_v": base_val}
    candidates.extend([c1, c2])
    if rng.choice([True, False]):
        candidates.reverse()
    return candidates, "Match Confirmed", {1}, True
