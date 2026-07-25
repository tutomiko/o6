# o6

`o6` is a lightweight candidate-matching library built around **Dilutive Open-World Cluster Matching (DOwCM)** — a statistical method for deciding, out of a pool of candidates, whether one of them is a confident match or whether the result is genuinely uncertain and should be resolved elsewhere.

It's designed for open-world settings: you don't get to assume the correct answer is always in the pool. Sometimes none of the candidates are good enough, and DOwCM is built to recognize that and say so, rather than force a pick.

## How it works

Each candidate is scored using a combination of:

- **Signal strength** — a harmonic mean of two independent confidence signals (`confidence_e` and `confidence_v`), which punishes candidates where either signal is weak.
- **Maturity** — a function of how many samples back a candidate's confidence, so thinly-evidenced candidates are naturally discounted.

These combine into a single score per candidate, which is then evaluated against the rest of the pool using:

1. **An absolute anchor** — the top candidate's score must clear a minimum bar on its own merit, regardless of how the rest of the pool looks.
2. **Dynamic tiering** — candidates are clustered into a "top tier" based on the pool's own statistical spread (its standard deviation), rather than a fixed threshold.
3. **Relative dominance** — the top tier must beat the next tier by a margin that scales with how noisy the pool is, so a clean pool needs less separation to trust a winner, and a noisy pool needs more.

This "dilutive" design means that adding more noise or more ambiguous candidates to the pool makes the matcher progressively more conservative, rather than picking a winner by default.

## Installation

```bash
pip install -e .
```

## Usage

```python
from o6 import O6Matcher, O6Candidate

candidates = [
    O6Candidate(id="alice", confidence_e=0.91, confidence_v=0.88, samples=340),
    O6Candidate(id="bob", confidence_e=0.42, confidence_v=0.39, samples=12),
]

matcher = O6Matcher(profile="balanced")

try:
    result = matcher.match(candidates)
    if result == -1:
        print("No confident match — query elsewhere.")
    else:
        print(f"Matched candidate: {candidates[result]}")
except ValueError as e:
    print(f"Matching could not be performed: {e}")
```

Candidates can be passed as `O6Candidate` instances or as plain dicts with `id`, `confidence_e`, `confidence_v`, and `samples` keys.

### Return value

`match()` returns a single `int`:

- The **index** of the matched candidate in the original input list, if a confident match was found.
- **`-1`**, if no candidate was confident enough to be treated as a match (query elsewhere).

If the input itself is unusable — not a list, empty, or containing no candidates that survive sanitization — `match()` raises a `ValueError` describing the problem, instead of returning a sentinel value. Malformed individual candidates (bad types, NaN/Infinity confidences, etc.) are silently filtered out of the pool rather than raising, since a messy pool is still a usable pool as long as something in it is valid.

## Matcher profiles

`O6Matcher` ships with three tuning profiles that trade off precision and recall by adjusting how strict the anchor, tiering, and margin requirements are:

- **`precise`** — For situations where a wrong match is costly and it's safe to fall back to "uncertain" often. Prioritizes confidence over coverage: it would rather say "I don't know" than commit to a shaky match.
- **`balanced`** — A general-purpose default for most workloads, offering a reasonable middle ground between confidently matching and correctly abstaining.
- **`permissive`** — For situations where missing a real match is costly and false positives are more tolerable, or where downstream logic can absorb a wrong guess. Prioritizes coverage over confidence: it will commit to a match more readily, even in noisier or more ambiguous pools.

```python
matcher = O6Matcher(profile="precise")
```

## Testing

A statistical stress-test harness is included under `tests/`, which runs the matcher against a large library of adversarial and edge-case scenarios (noise floors, near-ties, malformed input, extreme scale, fuzzed data, etc.) across thousands of randomized iterations per profile.

```bash
cd tests
python3 test_trust.py                     # runs all profiles
python3 test_trust.py --profile balanced  # runs a single profile
```

Set `HARNESS_SEED` to reproduce a specific run:

```bash
HARNESS_SEED=12345 python3 test_trust.py
```

## License

Add your license of choice here.
