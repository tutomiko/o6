from .helpers import generate_background_noise

NAME = "extreme_scale"


def generate(rng, pool_size):
    """Extreme range boundaries."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    winner_id = 1
    winner = {"id": winner_id, "confidence_e": 0.999999, "samples": 10**8, "confidence_v": 0.999999}
    candidates.append(winner)
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {winner_id}, True
