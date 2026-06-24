from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from asperitas_agent.eval_metrics import (
    DEFAULT_GATE_POLICY,
    DEFAULT_METRICS,
    EvalGatePolicy,
    EvalMetricReport,
    EvalMetricResult,
    EvalMetricSpec,
)


DEFAULT_REPORT_ID = "local_eval_report"


class EvalReportError(ValueError):
    """Raised when an explicit eval report input cannot be loaded safely."""


def load_metric_results(path: str | Path) -> list[EvalMetricResult]:
    payload = _load_json_payload(path)
    results_payload = payload.get("results")
    if not isinstance(results_payload, list):
        raise EvalReportError("results must be a list")
    if not results_payload:
        raise EvalReportError("results must not be empty")
    return [_result_from_dict(item, index) for index, item in enumerate(results_payload)]


def build_eval_report(
    results: list[EvalMetricResult],
    metric_specs: tuple[EvalMetricSpec, ...] | None = None,
    metadata: dict[str, Any] | None = None,
) -> EvalMetricReport:
    if not results:
        raise EvalReportError("results must not be empty")
    base_specs = metric_specs or DEFAULT_METRICS
    specs_by_id = {spec.metric_id: spec for spec in base_specs}
    unknown_ids = tuple(dict.fromkeys(result.metric_id for result in results if result.metric_id not in specs_by_id))
    result_modes = {result.metric_id: result.mode for result in results}
    known_specs = tuple(_spec_for_result_mode(spec, result_modes.get(spec.metric_id)) for spec in base_specs)
    all_specs = known_specs + tuple(_unknown_metric_spec(metric_id, result_modes[metric_id]) for metric_id in unknown_ids)
    gate_policy = _gate_policy_for_specs(all_specs)
    report_id = str((metadata or {}).get("report_id") or DEFAULT_REPORT_ID)
    return EvalMetricReport(
        report_id=report_id,
        metric_specs=all_specs,
        results=tuple(results),
        gate_policy=gate_policy,
        summary="Local explicit metric-result report. No automatic scoring, retrieval, or LLM judging performed.",
    )


def summarize_eval_report(report: EvalMetricReport) -> dict[str, Any]:
    results = tuple(report.results)
    known_metric_ids = {spec.metric_id for spec in DEFAULT_METRICS}
    warnings = [f"unknown metric_id: {result.metric_id}" for result in results if result.metric_id not in known_metric_ids]
    errors = list(report.validate())
    if not results:
        errors.append("results must not be empty")

    strict_results = tuple(result for result in results if result.mode == "strict")
    report_only_results = tuple(result for result in results if result.mode == "report_only")
    failed_strict = tuple(result for result in strict_results if result.passed is False)
    passed_strict = tuple(result for result in strict_results if result.passed is True)

    return {
        "ok": not errors and not failed_strict,
        "report_id": report.report_id,
        "summary": report.summary,
        "results": [result.to_dict() for result in results],
        "passed_count": len(passed_strict),
        "failed_count": len(failed_strict),
        "report_only_count": len(report_only_results),
        "strict_count": len(strict_results),
        "warnings": warnings,
        "errors": errors,
        "metadata": _metadata_for_report(report),
    }


def load_report_payload(path: str | Path) -> dict[str, Any]:
    payload = _load_json_payload(path)
    if not isinstance(payload.get("metadata", {}), dict):
        raise EvalReportError("metadata must be an object")
    return payload


def _load_json_payload(path: str | Path) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8")
        payload = json.loads(raw)
    except OSError as exc:
        raise EvalReportError(f"could not read input: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise EvalReportError(f"malformed JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise EvalReportError("input JSON must be an object")
    return payload


def _result_from_dict(item: Any, index: int) -> EvalMetricResult:
    if not isinstance(item, dict):
        raise EvalReportError(f"results[{index}] must be an object")
    required_fields = ("metric_id", "value", "passed", "mode")
    missing = [field for field in required_fields if field not in item]
    if missing:
        raise EvalReportError(f"results[{index}] missing fields: {', '.join(missing)}")
    notes = item.get("notes", "")
    if isinstance(notes, list):
        notes = "; ".join(str(note) for note in notes)
    elif notes is None:
        notes = ""
    elif not isinstance(notes, str):
        notes = str(notes)
    result = EvalMetricResult(
        metric_id=str(item["metric_id"]),
        value=item["value"],
        passed=item["passed"],
        mode=str(item["mode"]),
        notes=notes,
        version=str(item.get("version", "MVP-017A")),
    )
    errors = result.validate()
    if not isinstance(item["passed"], bool) and item["passed"] is not None:
        errors = (*errors, "passed must be true, false, or null")
    if errors:
        raise EvalReportError(f"results[{index}] invalid: {'; '.join(errors)}")
    return result


def _spec_for_result_mode(spec: EvalMetricSpec, result_mode: str | None) -> EvalMetricSpec:
    if result_mode != "strict":
        return spec
    return replace(spec, mode="strict", pass_threshold=0.0 if spec.pass_threshold is None else spec.pass_threshold)


def _unknown_metric_spec(metric_id: str, mode: str = "report_only") -> EvalMetricSpec:
    pass_threshold = 0.0 if mode == "strict" else None
    return EvalMetricSpec(
        metric_id=metric_id,
        name=f"Unknown Metric: {metric_id}",
        category="answer_quality",
        mode=mode,
        description="Unknown metric carried through for local reporting compatibility.",
        input_requirements=("explicit_metric_result",),
        output_type="json",
        pass_threshold=pass_threshold,
        fail_threshold=None,
        higher_is_better=True,
        requires_llm_judge=False,
        source_grounding_required=True,
        audit_required=True,
        risk_level="medium",
    )


def _gate_policy_for_specs(specs: tuple[EvalMetricSpec, ...]) -> EvalGatePolicy:
    return EvalGatePolicy(
        strict_metric_ids=tuple(spec.metric_id for spec in specs if spec.mode == "strict"),
        report_only_metric_ids=tuple(spec.metric_id for spec in specs if spec.mode == "report_only"),
        fail_closed=DEFAULT_GATE_POLICY.fail_closed,
    )


def _metadata_for_report(report: EvalMetricReport) -> dict[str, Any]:
    unsupported_claim_rate = next(
        (spec for spec in report.metric_specs if spec.metric_id == "unsupported_claim_rate"),
        None,
    )
    return {
        "version": report.version,
        "metric_spec_count": len(report.metric_specs),
        "result_count": len(report.results),
        "unsupported_claim_rate_higher_is_better": None
        if unsupported_claim_rate is None
        else unsupported_claim_rate.higher_is_better,
        "automatic_scoring_performed": False,
        "retrieval_executed": False,
        "llm_judge_executed": False,
    }
