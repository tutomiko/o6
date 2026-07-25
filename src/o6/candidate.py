from dataclasses import dataclass


@dataclass
class O6Candidate:
    """
    A single candidate entry in the matching pool.

    Attributes:
        id: Unique identifier for the candidate (int or str).
        confidence_e: Embedding confidence score [0.0, 1.0 nominally].
        confidence_v: Visual confidence score (formerly V_siglip) [0.0, 1.0 nominally].
        samples: Number of observed samples backing this candidate's confidence.
    """
    id: object
    confidence_e: float = 0.0
    confidence_v: float = 0.0
    samples: int = 0
