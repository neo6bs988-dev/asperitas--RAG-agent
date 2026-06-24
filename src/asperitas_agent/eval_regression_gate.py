from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from asperitas_agent.eval_artifacts import EvalArtifactError, EvalReportArtifact, load_eval_report_artifact


DEFAULT_MIN_REQUIRED_STRICT_METRICS = (
    "faithfulness",
    "answer_relevance",
    "context_precision",
    "context_recall",
    "unsupported_claim_rate",
)


@dataclass(frozen=True)
class EvalRegressionPolicy:
    min_required_strict_metrics: tuple[str, ...] = DEFAULT_MIN_REQUIRED_STRICT_METRICS
    max_strict_metric_drop: float = 0.02
    max_unsupported_claim_rate_increase: float = 0.0
    allow_unknown_metrics: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.min_required_strict_metrics:
            errors.append("min_required_strict_metrics must not be empty")
        if any(not metric_id.strip() for metric_id in self.min_required_strict_metrics):
            errors.append("min_required_strict_metrics must contain non-empty strings")
        if self.max_strict_metric_drop < 0:
            errors.append("max_strict_metric_drop must be non-negative")
        if self.max_unsupported_claim_rate_increase < 0:
            errors.append("max_unsupported_claim_rate_increase must be non-negative")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["min_required_strict_metrics"] = list(self.min_required_strict_metrics)
        return data


@dataclass(frozen=True)
class EvalRegressionDecision:
    ok: bool
    decision: str
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    policy: EvalRegressionPolicy
    baseline_report_id: str | None = None
    candidate_report_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "decision": self.decision,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "policy": self.policy.to_dict(),
            "baseline_report_id": self.baseline_report_id,
            "candidate_report_id": self.candidate_report_id,
        }


def compare_eval_artifacts(
    baseline: EvalReportArtifact | str | Path,
    candidate: EvalReportArtifact | str | Path,
    policy: EvalRegressionPolicy | None = None,
) -> EvalRegressionDecision:
    active_policy = policy or EvalRegressionPolicy()
    policy_errors = active_policy.validate()
    if policy_errors:
        return _decision(False, tuple(f"invalid policy: {error}" for error in policy_errors), (), active_policy)

    baseline_artifact, baseline_error = _coerce_artifact(baseline, "baseline")
    candidate_artifact, candidate_error = _coerce_artifact(candidate, "candidate")
    reasons: list[str] = []
    warnings: list[str] = []
    if baseline_error:
        reasons.append(baseline_error)
    if candidate_error:
        reasons.append(candidate_error)
    if reasons:
        return _decision(False, tuple(reasons), tuple(warnings), active_policy)

    assert baseline_artifact is not None
    assert candidate_artifact is not None
    if not baseline_artifact.ok:
        reasons.append("baseline ok=false")
    if not candidate_artifact.ok:
        reasons.append("candidate ok=false")
    warnings.extend(str(warning) for warning in baseline_artifact.warnings)
    warnings.extend(str(warning) for warning in candidate_artifact.warnings)

    baseline_strict = _strict_results_by_metric(baseline_artifact)
    candidate_strict = _strict_results_by_metric(candidate_artifact)
    baseline_all = _results_by_metric(baseline_artifact)
    candidate_all = _results_by_metric(candidate_artifact)

    unknown_metrics = sorted(set(candidate_all) - _known_metric_ids(candidate_artifact))
    for metric_id in unknown_metrics:
        message = f"unknown metric ids in candidate: {metric_id}"
        if active_policy.allow_unknown_metrics:
            warnings.append(message)
        else:
            reasons.append(message)

    for metric_id in active_policy.min_required_strict_metrics:
        if metric_id not in candidate_strict:
            reasons.append(f"missing strict metric from candidate: {metric_id}")

    for metric_id, result in candidate_strict.items():
        if result.get("passed") is False:
            if metric_id in baseline_strict and baseline_strict[metric_id].get("passed") is not False:
                reasons.append(f"new strict failure: {metric_id}")
            elif metric_id not in baseline_strict:
                reasons.append(f"new strict failure: {metric_id}")

    for metric_id, baseline_result in baseline_strict.items():
        if metric_id not in candidate_strict or metric_id == "unsupported_claim_rate":
            continue
        baseline_value = _numeric_value(baseline_result.get("value"))
        candidate_value = _numeric_value(candidate_strict[metric_id].get("value"))
        if baseline_value is None or candidate_value is None:
            continue
        if baseline_value - candidate_value > active_policy.max_strict_metric_drop:
            reasons.append(
                f"strict metric drop beyond tolerance: {metric_id} "
                f"baseline={baseline_value} candidate={candidate_value}"
            )

    if "unsupported_claim_rate" in baseline_strict and "unsupported_claim_rate" in candidate_strict:
        baseline_value = _numeric_value(baseline_strict["unsupported_claim_rate"].get("value"))
        candidate_value = _numeric_value(candidate_strict["unsupported_claim_rate"].get("value"))
        if baseline_value is not None and candidate_value is not None:
            increase = candidate_value - baseline_value
            if increase > active_policy.max_unsupported_claim_rate_increase:
                reasons.append(
                    "unsupported_claim_rate increase above tolerance: "
                    f"baseline={baseline_value} candidate={candidate_value}"
                )

    return _decision(
        not reasons,
        tuple(reasons),
        tuple(dict.fromkeys(warnings)),
        active_policy,
        baseline_artifact.report_id,
        candidate_artifact.report_id,
    )


def _decision(
    ok: bool,
    reasons: tuple[str, ...],
    warnings: tuple[str, ...],
    policy: EvalRegressionPolicy,
    baseline_report_id: str | None = None,
    candidate_report_id: str | None = None,
) -> EvalRegressionDecision:
    return EvalRegressionDecision(
        ok=ok,
        decision="pass" if ok else "fail",
        reasons=reasons,
        warnings=warnings,
        policy=policy,
        baseline_report_id=baseline_report_id,
        candidate_report_id=candidate_report_id,
    )


def _coerce_artifact(value: EvalReportArtifact | str | Path, label: str) -> tuple[EvalReportArtifact | None, str | None]:
    if isinstance(value, EvalReportArtifact):
        errors = value.validate()
        if errors:
            return None, f"{label} malformed: {'; '.join(errors)}"
        return value, None
    try:
        return load_eval_report_artifact(value), None
    except EvalArtifactError as exc:
        return None, f"{label} malformed: {exc}"


def _results_by_metric(artifact: EvalReportArtifact) -> dict[str, dict[str, Any]]:
    return {str(result.get("metric_id")): result for result in artifact.summary.get("results", []) if isinstance(result, dict)}


def _strict_results_by_metric(artifact: EvalReportArtifact) -> dict[str, dict[str, Any]]:
    return {
        metric_id: result
        for metric_id, result in _results_by_metric(artifact).items()
        if result.get("mode") == "strict"
    }


def _known_metric_ids(artifact: EvalReportArtifact) -> set[str]:
    specs = artifact.report.get("metric_specs", [])
    return {str(spec.get("metric_id")) for spec in specs if isinstance(spec, dict) and not str(spec.get("name", "")).startswith("Unknown Metric:")}


def _numeric_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
