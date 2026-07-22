from __future__ import annotations

from collections import defaultdict
import math
from typing import Any


def _wilson_lower(successes: int, trials: int) -> float:
    if trials <= 0:
        return 0.0
    z = 1.959963984540054
    p = successes / trials
    denominator = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denominator
    margin = (
        z
        * math.sqrt(
            p * (1 - p) / trials + z * z / (4 * trials * trials)
        )
        / denominator
    )
    return max(0.0, center - margin)


def compare_candidates(
    trials: list[dict[str, Any]],
    *,
    minimum_trials_per_slice: int,
    critical_pass_required: float,
    candidate_delta_min: float,
) -> dict[str, Any]:
    if not trials:
        raise ValueError("trials must not be empty")

    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for trial in trials:
        grouped[str(trial["slice"])][str(trial["variant"])].append(trial)

    slice_reports: dict[str, Any] = {}
    underpowered: list[str] = []
    candidate_deltas: list[float] = []
    critical_failures: list[str] = []

    for slice_name, variants in sorted(grouped.items()):
        if set(variants) != {"candidate", "incumbent"}:
            raise ValueError(f"{slice_name}: both variants are required")

        result: dict[str, Any] = {}
        for variant, rows in sorted(variants.items()):
            successes = sum(bool(row["passed"]) for row in rows)
            trials_count = len(rows)
            critical_rows = [row for row in rows if bool(row["critical"])]
            critical_rate = (
                sum(bool(row["passed"]) for row in critical_rows)
                / len(critical_rows)
                if critical_rows
                else 1.0
            )
            result[variant] = {
                "trials": trials_count,
                "pass_rate": successes / trials_count,
                "wilson_lower_95": _wilson_lower(successes, trials_count),
                "critical_pass_rate": critical_rate,
                "mean_cost": sum(float(row["cost"]) for row in rows)
                / trials_count,
                "mean_latency_ms": sum(
                    float(row["latency_ms"]) for row in rows
                )
                / trials_count,
            }
            if trials_count < minimum_trials_per_slice:
                underpowered.append(f"{slice_name}:{variant}")
            if (
                variant == "candidate"
                and critical_rate < critical_pass_required
            ):
                critical_failures.append(slice_name)

        delta = (
            result["candidate"]["pass_rate"]
            - result["incumbent"]["pass_rate"]
        )
        candidate_deltas.append(delta)
        result["pass_rate_delta"] = delta
        result["candidate_cost_delta"] = (
            result["candidate"]["mean_cost"]
            - result["incumbent"]["mean_cost"]
        )
        result["candidate_latency_delta_ms"] = (
            result["candidate"]["mean_latency_ms"]
            - result["incumbent"]["mean_latency_ms"]
        )
        slice_reports[slice_name] = result

    aggregate_delta = sum(candidate_deltas) / len(candidate_deltas)
    passed = (
        not underpowered
        and not critical_failures
        and aggregate_delta >= candidate_delta_min
        and all(delta >= 0 for delta in candidate_deltas)
    )
    return {
        "passed": passed,
        "aggregate_pass_rate_delta": aggregate_delta,
        "underpowered": sorted(underpowered),
        "critical_failures": sorted(critical_failures),
        "slice_reports": slice_reports,
        "thresholds": {
            "minimum_trials_per_slice": minimum_trials_per_slice,
            "critical_pass_required": critical_pass_required,
            "candidate_delta_min": candidate_delta_min,
        },
    }
