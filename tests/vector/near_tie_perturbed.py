from .helpers import generate_background_noise

NAME = "near_tie_perturbed"


def generate(rng, pool_size):
    """Microscopic float perturbation."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    winner_id = 1
    base_val = rng.uniform(0.8, 0.9)
    eps = 1e-9
    winner = {"id": winner_id, "confidence_e": base_val + eps, "samples": 1000, "confidence_v": base_val}
    loser = {"id": 2, "confidence_e": base_val, "samples": 1000, "confidence_v": base_val}
    candidates.extend([winner, loser])
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {winner_id}, True
