from .helpers import generate_background_noise

NAME = "discontinuity_boundary"


def generate(rng, pool_size):
    """Samples are binary & no confidence margin."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    c1 = {"id": 1, "confidence_e": 0.80, "samples": 10, "confidence_v": 0.80}
    c2 = {"id": 2, "confidence_e": 0.75, "samples": 10000, "confidence_v": 0.7499}
    candidates.extend([c1, c2])
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {2}, True
