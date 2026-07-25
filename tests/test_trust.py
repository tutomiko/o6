import argparse
import os
import random

from o6 import O6Matcher

from vector import VECTORS

# Dynamic Seeding for genuine exploration, overrideable via environment variable
GLOBAL_SEED = int(os.environ.get("HARNESS_SEED", random.randint(1, 9999999)))

VALID_PROFILES = ["precise", "balanced", "permissive"]


def parse_args():
    parser = argparse.ArgumentParser(description="o6.matcher statistical trust harness")
    parser.add_argument(
        "--profile",
        choices=VALID_PROFILES,
        default=None,
        help="Matcher profile to test. If omitted, all profiles are run separately.",
    )
    return parser.parse_args()


def build_scenario(rng):
    vector = rng.choice(VECTORS)
    pool_size = rng.randint(8, 20)
    candidates, expected_behavior, valid_winner_ids, is_positive_case = vector.generate(rng, pool_size)
    return candidates, expected_behavior, valid_winner_ids, vector.NAME, is_positive_case


def run_harness(profile):
    num_iterations = 10000
    print(f"==================================================")
    print(f"   STATISTICAL ZERO-TRUST & VULNERABILITY EXPOSURE HARNESS")
    print(f"   Profile:    {profile}")
    print(f"   Seed:       {GLOBAL_SEED} (Export HARNESS_SEED to replicate)")
    print(f"   Iterations: {num_iterations}")
    print(f"==================================================\n")

    rng = random.Random(GLOBAL_SEED)
    matcher = O6Matcher(profile=profile)

    print(f"--- Running Test Module: o6.matcher (profile={profile}) ---")

    passed_count = 0
    failed_count = 0
    exception_count = 0
    schema_violations = 0
    fallthrough_count = 0

    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    scenario_breakdown = {}

    for iteration in range(num_iterations):
        candidates, expected_behavior, valid_winner_ids, scenario_type, is_positive_case = build_scenario(rng)

        if scenario_type not in scenario_breakdown:
            scenario_breakdown[scenario_type] = {"total": 0, "passed": 0, "fp": 0, "fn": 0, "exc": 0}
        scenario_breakdown[scenario_type]["total"] += 1

        try:
            try:
                winner_index = matcher.match(candidates)
                raised = False
            except ValueError:
                # An invalid/unusable pool is treated as "Reject/Elsewhere",
                # same as an explicit UNCERTAIN result.
                winner_index = -1
                raised = True

            if not raised:
                if not isinstance(winner_index, int):
                    schema_violations += 1
                    failed_count += 1
                    continue

                if winner_index != -1:
                    # Winner index must point at a real candidate with a valid id
                    valid_index = (
                        isinstance(candidates, list)
                        and 0 <= winner_index < len(candidates)
                        and isinstance(candidates[winner_index], dict)
                        and isinstance(candidates[winner_index].get("id"), (int, str))
                    )
                    if not valid_index:
                        schema_violations += 1
                        failed_count += 1
                        continue

            is_match = (not raised) and winner_index != -1
            actual_status = "Match Confirmed" if is_match else "Reject/Elsewhere"

            if not is_match:
                fallthrough_count += 1

            actual_winner_id = candidates[winner_index]["id"] if is_match else None

            if is_positive_case:
                if actual_status == "Match Confirmed":
                    if actual_winner_id in (valid_winner_ids or set()):
                        true_positives += 1
                        passed_count += 1
                        scenario_breakdown[scenario_type]["passed"] += 1
                    else:
                        false_positives += 1
                        failed_count += 1
                        scenario_breakdown[scenario_type]["fp"] += 1
                else:
                    false_negatives += 1
                    failed_count += 1
                    scenario_breakdown[scenario_type]["fn"] += 1
            else:
                if actual_status == "Match Confirmed":
                    false_positives += 1
                    failed_count += 1
                    scenario_breakdown[scenario_type]["fp"] += 1
                else:
                    true_negatives += 1
                    passed_count += 1
                    scenario_breakdown[scenario_type]["passed"] += 1

        except Exception as e:
            exception_count += 1
            failed_count += 1
            scenario_breakdown[scenario_type]["exc"] += 1

    accuracy = (passed_count / num_iterations) * 100
    precision = (true_positives / (true_positives + false_positives)) * 100 if (true_positives + false_positives) > 0 else 0.0
    recall = (true_positives / (true_positives + false_negatives)) * 100 if (true_positives + false_negatives) > 0 else 0.0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    print(f"Results for o6.matcher:")
    print(f"  Total Iterations:   {num_iterations}")
    print(f"  Passed Assertions:  {passed_count}")
    print(f"  Failed Assertions:  {failed_count}")
    print(f"  Exceptions Thrown:  {exception_count}")
    print(f"  Schema Violations:  {schema_violations}")
    fallthrough_pct = (fallthrough_count / num_iterations) * 100
    print(f"  Total Fallthroughs: {fallthrough_count} ({fallthrough_pct:.2f}%)")
    print(f"----------------------------------------")
    print(f"  Overall Accuracy:   {accuracy:.2f}%")
    print(f"  Precision:          {precision:.2f}%")
    print(f"  Recall:             {recall:.2f}%")
    print(f"  F1-Score:           {f1_score:.2f}%")
    tp_pct = (true_positives / num_iterations) * 100
    fp_pct = (false_positives / num_iterations) * 100
    tn_pct = (true_negatives / num_iterations) * 100
    fn_pct = (false_negatives / num_iterations) * 100

    print(f"  True Positives:     {true_positives} ({tp_pct:.2f}%)")
    print(f"  False Positives:    {false_positives} ({fp_pct:.2f}%) (Type I Errors)")
    print(f"  True Negatives:     {true_negatives} ({tn_pct:.2f}%)")
    print(f"  False Negatives:    {false_negatives} ({fn_pct:.2f}%) (Type II Errors)")
    print(f"----------------------------------------")

    print("  Scenario Breakdown:")
    for sc, stats in scenario_breakdown.items():
        sc_pass_pct = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0.0
        print(f"    ├─ {sc:<35}: {stats['passed']}/{stats['total']} ({sc_pass_pct:.1f}%) [FP: {stats['fp']}, FN: {stats['fn']}, EXC: {stats['exc']}]")
    print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    args = parse_args()
    if args.profile:
        run_harness(args.profile)
    else:
        for p in VALID_PROFILES:
            run_harness(p)
