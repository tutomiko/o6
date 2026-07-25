from .helpers import generate_background_noise

NAME = "asymptotic_false_positive"


def generate(rng, pool_size):
    """Asymptotic false positive stress (Type I error exposure)."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    mediocre_candidate = {
        "id": 99,
        "confidence_e": 0.45,
        "samples": 10000000,
        "confidence_v": 0.45
    }
    candidates.append(mediocre_candidate)
    rng.shuffle(candidates)
    return candidates, "Reject/Elsewhere", None, False
