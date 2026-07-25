from .helpers import generate_background_noise

NAME = "wrong_tie_breaker"


def generate(rng, pool_size):
    """Arbitrary tie breaker."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    c1 = {"id": 1, "confidence_e": 0.9, "samples": 0, "confidence_v": 0.9}
    c2 = {"id": 99, "confidence_e": 0.9, "samples": 5000, "confidence_v": 0.9}
    candidates.extend([c1, c2])
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {99}, True
