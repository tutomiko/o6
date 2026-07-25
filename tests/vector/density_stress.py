from .helpers import generate_background_noise

NAME = "density_stress"


def generate(rng, pool_size):
    """Large-scale density stress."""
    winner_id = 1
    candidates = generate_background_noise(rng, 10, rng.randint(500, 1500))
    winner = {"id": winner_id, "confidence_e": 0.95, "samples": 5000, "confidence_v": 0.95}
    candidates.append(winner)
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {winner_id}, True
