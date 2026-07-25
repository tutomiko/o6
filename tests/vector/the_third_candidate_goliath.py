from .helpers import generate_background_noise

NAME = "the_third_candidate_goliath"


def generate(rng, pool_size):
    """Samples only compare the top two (the unseen Goliath)."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    c1 = {"id": 1, "confidence_e": 0.80, "samples": 50, "confidence_v": 0.80}
    c2 = {"id": 2, "confidence_e": 0.80, "samples": 40, "confidence_v": 0.79}
    c3 = {"id": 3, "confidence_e": 0.79, "samples": 9000, "confidence_v": 0.79}
    candidates.extend([c1, c2, c3])
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {3}, True
