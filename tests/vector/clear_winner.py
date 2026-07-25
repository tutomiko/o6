from .helpers import generate_background_noise

NAME = "clear_winner"


def generate(rng, pool_size):
    """Parameterized clear winner (continuous Gaussian domain)."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    winner_id = 1
    winner = {
        "id": winner_id,
        "confidence_e": max(0.0, min(1.0, rng.gauss(0.9, 0.05))),
        "samples": rng.randint(500, 5000),
        "confidence_v": max(0.0, min(1.0, rng.gauss(0.9, 0.05)))
    }
    candidates.append(winner)
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {winner_id}, True
