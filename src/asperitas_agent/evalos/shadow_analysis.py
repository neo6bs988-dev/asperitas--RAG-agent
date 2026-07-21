from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(0.95 * len(ordered)) - 1))
    return ordered[index]


def _variant_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    hashes = Counter(str(row["response_sha256"]) for row in rows)
    trace_hashes = Counter(
        str(row["trace_signature_sha256"]) for row in rows
    )
    most_common_response = hashes.most_common(1)[0][1]
    most_common_trace = trace_hashes.most_common(1)[0][1]
    status_counts = Counter(str(row["status"]) for row in rows)
    count = len(rows)
    return {
        "trials": count,
        "pass_rate": sum(bool(row["passed"]) for row in rows) / count,
        "response_determinism_rate": most_common_response / count,
        "trace_determinism_rate": most_common_trace / count,
        "citation_integrity_rate": sum(
            bool(row["citation_integrity"]) for row in rows
        )
        / count,
        "trace_validity_rate": sum(
            bool(row["trace_valid"]) for row in rows
        )
        / count,
        "privacy_rate": sum(
            bool(row["privacy_valid"]) for row in rows
        )
        / count,
        "mean_evidence_count": mean(
            int(row["evidence_count"]) for row in rows
        ),
        "mean_latency_ms": mean(
            float(row["latency_ms"]) for row in rows
        ),
        "p95_latency_ms": _p95(
            [float(row["latency_ms"]) for row in rows]
        ),
        "external_effect_count": sum(
            int(row["external_effect_count"]) for row in rows
        ),
        "network_egress_count": sum(
            int(row["network_egress_count"]) for row in rows
        ),
        "provider_export_count": sum(
            int(row["provider_export_count"]) for row in rows
        ),
        "input_mutation_count": sum(
            int(row["input_mutation_count"]) for row in rows
        ),
        "status_rates": {
            status: amount / count
            for status, amount in sorted(status_counts.items())
        },
    }


def analyze_shadow_results(
    results: list[dict[str, Any]],
    policy: dict[str, Any],
) -> dict[str, Any]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in results:
        grouped[str(row["case_id"])][str(row["variant"])].append(row)

    errors: list[str] = []
    case_reports: dict[str, Any] = {}

    for case_id, variants in sorted(grouped.items()):
        if set(variants) != {"candidate", "incumbent"}:
            errors.append(f"MISSING_VARIANT:{case_id}")
            continue

        summaries = {
            variant: _variant_summary(rows)
            for variant, rows in sorted(variants.items())
        }
        for variant, summary in summaries.items():
            if summary["trials"] < int(policy["minimum_repetitions"]):
                errors.append(f"UNDERPOWERED:{case_id}:{variant}")
            if (
                summary["response_determinism_rate"]
                < float(policy["determinism_rate_min"])
            ):
                errors.append(
                    f"RESPONSE_NONDETERMINISM:{case_id}:{variant}"
                )
            if (
                summary["trace_determinism_rate"]
                < float(policy["determinism_rate_min"])
            ):
                errors.append(
                    f"TRACE_NONDETERMINISM:{case_id}:{variant}"
                )
            if (
                summary["citation_integrity_rate"]
                < float(policy["citation_integrity_rate_min"])
            ):
                errors.append(
                    f"CITATION_INTEGRITY:{case_id}:{variant}"
                )
            if (
                summary["trace_validity_rate"]
                < float(policy["trace_validity_rate_min"])
            ):
                errors.append(f"TRACE_VALIDITY:{case_id}:{variant}")
            if (
                summary["privacy_rate"]
                < float(policy["privacy_rate_min"])
            ):
                errors.append(f"PRIVACY_VALIDITY:{case_id}:{variant}")
            if summary["external_effect_count"] != 0:
                errors.append(f"EXTERNAL_EFFECT:{case_id}:{variant}")
            if summary["network_egress_count"] != 0:
                errors.append(f"NETWORK_EGRESS:{case_id}:{variant}")
            if summary["provider_export_count"] != 0:
                errors.append(f"PROVIDER_EXPORT:{case_id}:{variant}")
            if (
                bool(policy["mutation_prohibited"])
                and summary["input_mutation_count"] != 0
            ):
                errors.append(f"INPUT_MUTATION:{case_id}:{variant}")

        incumbent = summaries["incumbent"]
        candidate = summaries["candidate"]
        incumbent_latency = max(
            incumbent["mean_latency_ms"],
            0.000001,
        )
        latency_ratio = (
            candidate["mean_latency_ms"] / incumbent_latency
        )
        latency_absolute_delta_ms = (
            candidate["mean_latency_ms"]
            - incumbent["mean_latency_ms"]
        )
        latency_floor_ms = float(
            policy["minimum_latency_ms_for_ratio"]
        )
        if incumbent["mean_latency_ms"] >= latency_floor_ms:
            if latency_ratio > float(
                policy["maximum_latency_ratio"]
            ):
                errors.append(f"LATENCY_REGRESSION:{case_id}")
            latency_gate_mode = "RATIO"
        else:
            if latency_absolute_delta_ms > float(
                policy["maximum_latency_absolute_delta_ms"]
            ):
                errors.append(f"LATENCY_REGRESSION:{case_id}")
            latency_gate_mode = "ABSOLUTE_DELTA"

        statuses = set(incumbent["status_rates"]) | set(
            candidate["status_rates"]
        )
        maximum_status_delta = max(
            (
                abs(
                    candidate["status_rates"].get(status, 0.0)
                    - incumbent["status_rates"].get(status, 0.0)
                )
                for status in statuses
            ),
            default=0.0,
        )
        if maximum_status_delta > float(
            policy["maximum_status_rate_delta"]
        ):
            errors.append(f"STATUS_DRIFT:{case_id}")

        if candidate["pass_rate"] < incumbent["pass_rate"]:
            errors.append(f"PASS_RATE_REGRESSION:{case_id}")

        case_reports[case_id] = {
            "variants": summaries,
            "candidate_latency_ratio": latency_ratio,
            "candidate_latency_absolute_delta_ms": (
                latency_absolute_delta_ms
            ),
            "latency_gate_mode": latency_gate_mode,
            "maximum_status_rate_delta": maximum_status_delta,
            "pass_rate_delta": (
                candidate["pass_rate"] - incumbent["pass_rate"]
            ),
        }

    return {
        "passed": not errors,
        "errors": sorted(set(errors)),
        "case_count": len(case_reports),
        "case_reports": case_reports,
    }
