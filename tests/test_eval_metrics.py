from __future__ import annotations

import json

from asperitas_agent.eval_metrics import (
    DEFAULT_METRICS,
    EvalGatePolicy,
    EvalMetricReport,
    EvalMetricResult,
    EvalMetricSpec,
    default_metric_report,
    list_default_metrics,
    metrics_to_dict,
    validate_metric_specs,
)


EXPECTED_DEFAULT_METRIC_IDS = (
    "context_precision",
    "context_recall",
    "faithfulness",
    "groundedness",
    "answer_relevancy",
    "citation_accuracy",
    "abstention_accuracy",
    "unsupported_claim_rate",
    "compliance_trigger_correctness",
    "skill_selection_accuracy",
)


def valid_spec(**overrides):
    kwargs = {
        "metric_id": "test_metric",
        "name": "Test Metric",
        "category": "answer_quality",
        "mode": "report_only",
        "description": "Test metric contract.",
        "input_requirements": ("question", "answer"),
        "output_type": "score",
        "pass_threshold": None,
        "fail_threshold": None,
        "higher_is_better": True,
        "requires_llm_judge": False,
        "source_grounding_required": True,
        "audit_required": True,
        "risk_level": "medium",
        "version": "test",
    }
    return EvalMetricSpec(**{**kwargs, **overrides})


def test_default_metrics_load():
    metrics = list_default_metrics()

    assert tuple(metric.metric_id for metric in metrics) == EXPECTED_DEFAULT_METRIC_IDS
    assert metrics == DEFAULT_METRICS


def test_default_metric_ids_are_unique():
    metric_ids = tuple(metric.metric_id for metric in list_default_metrics())

    assert len(metric_ids) == len(set(metric_ids))


def test_all_default_specs_validate():
    assert validate_metric_specs(list_default_metrics()) == ()
    for metric in list_default_metrics():
        assert metric.validate() == ()


def test_strict_threshold_required():
    errors = valid_spec(mode="strict", pass_threshold=None, fail_threshold=None).validate()

    assert "strict metric must define pass_threshold or fail_threshold" in errors


def test_llm_judge_metrics_are_report_only_by_default():
    llm_judge_metrics = tuple(metric for metric in list_default_metrics() if metric.requires_llm_judge)

    assert llm_judge_metrics
    assert all(metric.mode == "report_only" for metric in llm_judge_metrics)
    errors = valid_spec(mode="strict", pass_threshold=0.8, requires_llm_judge=True).validate()
    assert "requires_llm_judge metrics must be report_only by default" in errors


def test_unsupported_claim_rate_lower_is_better():
    metric = next(metric for metric in list_default_metrics() if metric.metric_id == "unsupported_claim_rate")

    assert metric.higher_is_better is False
    errors = valid_spec(metric_id="unsupported_claim_rate", higher_is_better=True).validate()
    assert "unsupported_claim_rate must set higher_is_better=false" in errors


def test_compliance_metric_requires_audit_and_source_grounding():
    metric = next(metric for metric in list_default_metrics() if metric.category == "compliance")

    assert metric.source_grounding_required is True
    assert metric.audit_required is True
    errors = valid_spec(category="compliance", source_grounding_required=False, audit_required=True).validate()
    assert "compliance metrics require source_grounding_required and audit_required" in errors
    errors = valid_spec(category="compliance", source_grounding_required=True, audit_required=False).validate()
    assert "compliance metrics require source_grounding_required and audit_required" in errors


def test_invalid_spec_fails_closed():
    spec = valid_spec(
        metric_id="",
        category="invalid",
        mode="invalid",
        input_requirements=(),
        output_type="invalid",
        risk_level="critical",
    )
    errors = spec.validate()

    assert "metric_id is required" in errors
    assert "invalid category: invalid" in errors
    assert "invalid mode: invalid" in errors
    assert "input_requirements must be a non-empty tuple" in errors
    assert "invalid output_type: invalid" in errors
    assert "invalid risk_level: critical" in errors
    assert "duplicate metric_id" in validate_metric_specs((valid_spec(metric_id="duplicate"), valid_spec(metric_id="duplicate")))


def test_report_aggregates_results():
    report = default_metric_report(
        (
            EvalMetricResult("context_precision", 0.91, True, "strict"),
            EvalMetricResult("unsupported_claim_rate", 0.22, False, "strict"),
            EvalMetricResult("faithfulness", None, None, "report_only", notes="judge deferred"),
        )
    )

    aggregate = report.aggregate_results()

    assert aggregate == {
        "total_results": 3,
        "strict_results": 2,
        "report_only_results": 1,
        "failed_strict_metric_ids": ["unsupported_claim_rate"],
        "passed": False,
    }
    assert report.validate() == (
        "context_precision: result mode does not match metric spec mode",
        "unsupported_claim_rate: result mode does not match metric spec mode",
    )


def test_report_json_safe():
    report = EvalMetricReport(
        report_id="test_report",
        metric_specs=(valid_spec(metric_id="strict_metric", mode="strict", pass_threshold=0.9),),
        results=(EvalMetricResult("strict_metric", 0.95, True, "strict"),),
        gate_policy=EvalGatePolicy(strict_metric_ids=("strict_metric",), report_only_metric_ids=()),
        summary="JSON serialization contract only.",
    )

    assert report.validate() == ()
    first = json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":"))
    second = json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":"))

    assert first == second
    payload = json.loads(first)
    assert payload["aggregate"]["passed"] is True
    assert json.dumps(metrics_to_dict(), sort_keys=True, separators=(",", ":")) == json.dumps(
        metrics_to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    )
