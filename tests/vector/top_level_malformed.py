NAME = "top_level_malformed"


def generate(rng, pool_size):
    """Invalid top-level input."""
    invalid_input = rng.choice([None, "InvalidString", 12345, {"dict": "instead_of_list"}])
    return invalid_input, "Reject/Elsewhere", None, False
