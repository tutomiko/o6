import random


def generate_fuzz_garbage(rng, id_val):
    """Generates malicious candidate dictionaries to test data sanitization and semantic bounds."""
    fuzz_types = [
        {"id": id_val, "confidence_e": float("nan"), "samples": 100, "confidence_v": 0.8},
        {"id": id_val, "confidence_e": float("inf"), "samples": 100, "confidence_v": 0.8},
        {"id": id_val, "confidence_e": -float("inf"), "samples": -50, "confidence_v": -1.0},
        {"id": id_val, "confidence_e": "Extreme", "samples": None, "confidence_v": [1, 2, 3]},
        {"id": id_val, "samples": 500},
        {"confidence_e": 0.9, "confidence_v": 0.9},
        "NOT_A_DICT",
        None,
        12345,
        {"id": id_val, "confidence_e": 0.8, "samples": 0, "confidence_v": 0.8},
        {"id": id_val, "confidence_e": 5000.0, "samples": 100, "confidence_v": 0.8},
        {"id": id_val, "confidence_e": 0.5, "samples": 100, "confidence_v": -999.0},
    ]
    return rng.choice(fuzz_types)


def generate_background_noise(rng, start_id, count, mean=0.2, stddev=0.1):
    """Generates background noise using continuous Gaussian distributions across the domain."""
    noise = []
    for i in range(count):
        confidence_e = max(0.0, min(1.0, rng.gauss(mean, stddev)))
        confidence_v = max(0.0, min(1.0, rng.gauss(mean, stddev)))
        samples = max(1, int(rng.expovariate(1.0 / 100.0)))
        noise.append({
            "id": start_id + i,
            "confidence_e": confidence_e,
            "samples": samples,
            "confidence_v": confidence_v
        })
    return noise
