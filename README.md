# o6

`o6` implements **Dilutive Open-World Cluster Matching (DOwCM)** — a candidate-matching
algorithm that decides whether a query confidently matches one candidate in a pool,
should be rejected outright, or is too ambiguous to call ("query elsewhere").

It combines a confidence signal (harmonic mean of two independent confidence scores)
with a maturity signal (how many samples back that confidence up), then applies
dynamic tiering and relative-margin statistics to separate a clear winner from noise.

## Install

```bash
pip install -e .
```

## Usage

```python
from o6 import O6Matcher, O6MatchStatus, O6Candidate

matcher = O6Matcher(profile="balanced")  # "precise" | "balanced" | "permissive"

candidates = [
    O6Candidate(id="alice", confidence_e=0.92, confidence_v=0.90, samples=500),
    O6Candidate(id="bob",   confidence_e=0.40, confidence_v=0.35, samples=200),
]

status, index = matcher.match(candidates)

if status == O6MatchStatus.MATCH:
    print("Matched:", candidates[index].id)
elif status == O6MatchStatus.UNCERTAIN:
    print("Ambiguous — query elsewhere")
else:
    print("Invalid / rejected pool")
```

Plain dicts are also accepted in place of `O6Candidate`:

```python
matcher.match([
    {"id": 1, "confidence_e": 0.9, "confidence_v": 0.88, "samples": 300},
    {"id": 2, "confidence_e": 0.5, "confidence_v": 0.5,  "samples": 50},
])
```

### `O6Candidate` fields

| Field          | Type         | Description                                   |
|----------------|--------------|------------------------------------------------|
| `id`           | `int \| str` | Unique identifier for the candidate            |
| `confidence_e` | `float`      | Embedding confidence                           |
| `confidence_v` | `float`      | Visual confidence                              |
| `samples`      | `int`        | Number of observations backing the confidence  |

### `matcher.match(candidates)`

Returns a tuple `(O6MatchStatus, index)`:

- `O6MatchStatus.MATCH` (`1`) — a confident match was found; `index` is its
  position in the input list.
- `O6MatchStatus.UNCERTAIN` (`0`) — no candidate was confident enough to
  choose safely; caller should query elsewhere. `index` is `-1`.
- `O6MatchStatus.INVALID` (`-1`) — the pool was empty, malformed, or every
  candidate failed sanitization. `index` is `-1`.

Malformed entries (non-dict/non-`O6Candidate` items, missing IDs, `NaN`/`inf`
values, wrong types, etc.) are silently skipped rather than raising, as long
as at least one candidate in the pool is usable.

## Profiles

Profiles trade off precision for recall by adjusting how harshly weak signal
and low sample counts are penalized, the absolute score floor required to
consider a match at all, and how large a margin the top candidate needs over
the rest of the pool.

| Profile      | Behavior                                                |
|--------------|-----------------------------------------------------------|
| `precise`    | Strictest. Fewer matches, higher confidence when it does. |
| `balanced`   | Default trade-off between precision and recall.           |
| `permissive` | Loosest. More matches, tolerates more ambiguity.           |

## Testing

A statistical fuzz/trust harness lives in `tests/`, covering adversarial
inputs, tie-breaking, scaling behavior, and known failure modes across all
three profiles:

```bash
cd tests
python3 test_trust.py                  # runs all profiles
python3 test_trust.py --profile precise
HARNESS_SEED=42 python3 test_trust.py  # reproducible run
```
