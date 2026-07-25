from .helpers import generate_background_noise, generate_fuzz_garbage

NAME = "fuzz_poisoning"


def generate(rng, pool_size):
    """Adversarial fuzz poisoning."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    winner_id = 1
    winner = {"id": winner_id, "confidence_e": 0.92, "samples": 1000, "confidence_v": 0.92}
    for i in range(5):
        candidates.append(generate_fuzz_garbage(rng, id_val=100 + i))
    candidates.append(winner)
    rng.shuffle(candidates)
    return candidates, "Match Confirmed", {winner_id}, True
