from .helpers import generate_background_noise

NAME = "tight_cluster"


def generate(rng, pool_size):
    """Dynamic tight cluster."""
    candidates = generate_background_noise(rng, 10, pool_size - 2)
    base_signal = rng.uniform(0.45, 0.52)
    for i in range(3):
        candidates.append({
            "id": i + 1,
            "confidence_e": base_signal + rng.gauss(0, 0.01),
            "samples": rng.randint(50, 150),
            "confidence_v": base_signal + rng.gauss(0, 0.01)
        })
    rng.shuffle(candidates)
    return candidates, "Reject/Elsewhere", None, False
