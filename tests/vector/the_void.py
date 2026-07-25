from .helpers import generate_background_noise

NAME = "the_void"


def generate(rng, pool_size):
    """Dynamic the void."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    return candidates, "Reject/Elsewhere", None, False
