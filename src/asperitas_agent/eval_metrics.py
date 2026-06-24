from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


METRIC_CATEGORIES = (
    "retrieval_quality",
    "grounding",
    "citation_quality",
    "answer_quality",
    "abstention",
    "compliance",
    "tool_or_skill_use",
)
METRIC_MODES = ("strict", "report_only")
RISK_LEVELS = ("low", "medium", "high")
DEFAULT_VERSION = "MVP-017A"
DEFAULT_REPORT_ID = "asperitas_eval_metric_report"
DEFAULT_GATE_ID = "asperitas_eval_gate_policy"


@dataclass(frozen=True)
class EvalMetricSpec:
    metric_id: str
    name: str
    category: str
    mode: str
    description: str
    input_requirements: tuple[str, ...]
    output_type: str
    pass_threshold: float | None
    fail_threshold: float | None
    higher_is_better: bool
    requires_llm_judge: bool
    source_grounding_required: bool
    audit_required: bool
    risk_level: str
    version: str = DEFAULT_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for field_name in ("metric_id", "name", "category", "mode", "description", "output_type", "risk_level", "version"):
            if not str(getattr(self, field_name)).strip():
                errors.append(f"{field_name} is required")
        if self.category not in METRIC_CATEGORIES:
            errors.append(f"invalid category: {self.category}")
        if self.mode not in METRIC_MODES:
            errors.append(f"invalid mode: {self.mode}")
        if self.risk_level not in RISK_LEVELS:
            errors.append(f"invalid risk_level: {self.risk_level}")
        if not isinstance(self.input_requirements, tuple) or not self.input_requirements:
            errors.append("input_requirements must be a non-empty tuple")
        elif any(not str(requirement).strip() for requirement in self.input_requirements):
            errors.append("input_requirements must contain non-empty strings")
        if self.output_type not in ("score", "rate", "boolean", "label", "json"):
            errors.append(f"invalid output_type: {self.output_type}")
        if self.mode == "strict" and self.pass_threshold is None and self.fail_threshold is None:
            errors.append("strict metric must define pass_threshold or fail_threshold")
        if self.requires_llm_judge and self.mode != "report_only":
            errors.append("requires_llm_judge metrics must be report_only by default")
        if self.metric_id == "unsupported_claim_rate" and self.higher_is_better:
            errors.append("unsupported_claim_rate must set higher_is_better=false")
        if self.category == "compliance" and not (self.source_grounding_required and self.audit_required):
            errors.append("compliance metrics require source_grounding_required and audit_required")
        return tuple(errors)

    def require_valid(self) -> None:
        errors = self.validate()
        if errors:
            raise ValueError("; ".join(errors))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class EvalMetricResult:
    metric_id: str
    value: float | int | bool | str | dict[str, Any] | None
    passed: bool | None
    mode: str
    notes: str = ""
    version: str = DEFAULT_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.metric_id.strip():
            errors.append("metric_id is required")
        if self.mode not in METRIC_MODES:
            errors.append(f"invalid mode: {self.mode}")
        if self.mode == "strict" and self.passed is None:
            errors.append("strict metric result requires passed")
        if not self.version.strip():
            errors.append("version is required")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvalGatePolicy:
    strict_metric_ids: tuple[str, ...]
    report_only_metric_ids: tuple[str, ...]
    fail_closed: bool = True
    policy_id: str = DEFAULT_GATE_ID
    version: str = DEFAULT_VERSION

    def validate(self, specs: tuple[EvalMetricSpec, ...] = ()) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.policy_id.strip():
            errors.append("policy_id is required")
        if not self.version.strip():
            errors.append("version is required")
        if not self.fail_closed:
            errors.append("eval gate policy must fail closed")
        for field_name in ("strict_metric_ids", "report_only_metric_ids"):
            value = getattr(self, field_name)
            if not isinstance(value, tuple):
                errors.append(f"{field_name} must be a tuple")
            elif any(not str(metric_id).strip() for metric_id in value):
                errors.append(f"{field_name} must contain non-empty strings")
        overlap = sorted(set(self.strict_metric_ids) & set(self.report_only_metric_ids))
        if overlap:
            errors.append(f"metric ids cannot be both strict and report_only: {', '.join(overlap)}")
        if specs:
            spec_modes = {spec.metric_id: spec.mode for spec in specs}
            for metric_id in self.strict_metric_ids:
                if spec_modes.get(metric_id) != "strict":
                    errors.append(f"strict policy metric is not strict: {metric_id}")
            for metric_id in self.report_only_metric_ids:
                if spec_modes.get(metric_id) != "report_only":
                    errors.append(f"report_only policy metric is not report_only: {metric_id}")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class EvalMetricReport:
    report_id: str
    metric_specs: tuple[EvalMetricSpec, ...]
    results: tuple[EvalMetricResult, ...]
    gate_policy: EvalGatePolicy
    summary: str = ""
    version: str = DEFAULT_VERSION

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.report_id.strip():
            errors.append("report_id is required")
        if not self.version.strip():
            errors.append("version is required")
        errors.extend(validate_metric_specs(self.metric_specs))
        spec_modes = {spec.metric_id: spec.mode for spec in self.metric_specs}
        metric_ids = set(spec_modes)
        for result in self.results:
            errors.extend(f"{result.metric_id}: {error}" for error in result.validate())
            if result.metric_id not in metric_ids:
                errors.append(f"unknown result metric_id: {result.metric_id}")
            elif result.mode != spec_modes[result.metric_id]:
                errors.append(f"{result.metric_id}: result mode does not match metric spec mode")
        errors.extend(f"gate_policy: {error}" for error in self.gate_policy.validate(self.metric_specs))
        return tuple(errors)

    def aggregate_results(self) -> dict[str, Any]:
        strict_results = tuple(result for result in self.results if result.mode == "strict")
        report_only_results = tuple(result for result in self.results if result.mode == "report_only")
        failed_strict = tuple(result.metric_id for result in strict_results if result.passed is False)
        return {
            "total_results": len(self.results),
            "strict_results": len(strict_results),
            "report_only_results": len(report_only_results),
            "failed_strict_metric_ids": list(failed_strict),
            "passed": not failed_strict,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "version": self.version,
            "summary": self.summary,
            "gate_policy": self.gate_policy.to_dict(),
            "metric_specs": [spec.to_dict() for spec in self.metric_specs],
            "results": [result.to_dict() for result in self.results],
            "aggregate": self.aggregate_results(),
        }


def _metric(
    metric_id: str,
    name: str,
    category: str,
    description: str,
    input_requirements: tuple[str, ...],
    output_type: str = "score",
    mode: str = "report_only",
    pass_threshold: float | None = None,
    fail_threshold: float | None = None,
    higher_is_better: bool = True,
    requires_llm_judge: bool = False,
    source_grounding_required: bool = True,
    audit_required: bool = True,
    risk_level: str = "medium",
    version: str = DEFAULT_VERSION,
) -> EvalMetricSpec:
    return EvalMetricSpec(
        metric_id=metric_id,
        name=name,
        category=category,
        mode=mode,
        description=description,
        input_requirements=input_requirements,
        output_type=output_type,
        pass_threshold=pass_threshold,
        fail_threshold=fail_threshold,
        higher_is_better=higher_is_better,
        requires_llm_judge=requires_llm_judge,
        source_grounding_required=source_grounding_required,
        audit_required=audit_required,
        risk_level=risk_level,
        version=version,
    )


DEFAULT_METRICS = (
    _metric(
        "context_precision",
        "Context Precision",
        "retrieval_quality",
        "Report how much retrieved context is relevant to the evaluation question.",
        ("question", "retrieved_contexts", "reference_answer_or_labels"),
    ),
    _metric(
        "context_recall",
        "Context Recall",
        "retrieval_quality",
        "Report whether required supporting evidence appears in retrieved context.",
        ("question", "retrieved_contexts", "reference_answer_or_labels"),
    ),
    _metric(
        "faithfulness",
        "Faithfulness",
        "grounding",
        "Report whether answer claims are supported by supplied context.",
        ("answer", "retrieved_contexts", "claim_annotations"),
        requires_llm_judge=True,
        risk_level="high",
    ),
    _metric(
        "groundedness",
        "Groundedness",
        "grounding",
        "Report source-grounding coverage for answer claims and citations.",
        ("answer", "source_ids", "evidence_labels", "unsupported_claims"),
        requires_llm_judge=True,
        risk_level="high",
    ),
    _metric(
        "answer_relevancy",
        "Answer Relevancy",
        "answer_quality",
        "Report whether the answer addresses the user question without unsupported expansion.",
        ("question", "answer", "reference_answer_or_rubric"),
        requires_llm_judge=True,
        risk_level="high",
    ),
    _metric(
        "citation_accuracy",
        "Citation Accuracy",
        "citation_quality",
        "Report whether cited source IDs and citation targets support the attached claims.",
        ("answer", "citations", "source_metadata", "retrieved_contexts"),
        risk_level="high",
    ),
    _metric(
        "abstention_accuracy",
        "Abstention Accuracy",
        "abstention",
        "Report whether the system abstains when evidence is insufficient or restricted.",
        ("question", "answer", "source_state", "expected_abstention"),
        output_type="rate",
        risk_level="high",
    ),
    _metric(
        "unsupported_claim_rate",
        "Unsupported Claim Rate",
        "grounding",
        "Report the share of answer claims lacking source support or required verification labels.",
        ("answer", "claim_annotations", "source_metadata"),
        output_type="rate",
        higher_is_better=False,
        risk_level="high",
    ),
    _metric(
        "compliance_trigger_correctness",
        "Compliance Trigger Correctness",
        "compliance",
        "Report whether compliance, biosafety, legal, privacy, investor, and public-communication triggers are surfaced.",
        ("question", "answer", "risk_flags", "expected_triggers"),
        output_type="rate",
        risk_level="high",
    ),
    _metric(
        "skill_selection_accuracy",
        "Skill Selection Accuracy",
        "tool_or_skill_use",
        "Report whether the selected local skill or blocked decision matches the task risk and scope.",
        ("task", "selected_skill", "registry_decision", "expected_skill_or_block"),
        output_type="rate",
        risk_level="high",
    ),
)

DEFAULT_GATE_POLICY = EvalGatePolicy(
    strict_metric_ids=tuple(metric.metric_id for metric in DEFAULT_METRICS if metric.mode == "strict"),
    report_only_metric_ids=tuple(metric.metric_id for metric in DEFAULT_METRICS if metric.mode == "report_only"),
)


def list_default_metrics() -> tuple[EvalMetricSpec, ...]:
    return DEFAULT_METRICS


def get_metric(metric_id: str) -> EvalMetricSpec | None:
    return {metric.metric_id: metric for metric in DEFAULT_METRICS}.get(metric_id)


def require_metric(metric_id: str) -> EvalMetricSpec:
    metric = get_metric(metric_id)
    if metric is None:
        raise KeyError(f"unknown metric_id: {metric_id}")
    return metric


def validate_metric_specs(specs: tuple[EvalMetricSpec, ...]) -> tuple[str, ...]:
    errors: list[str] = []
    metric_ids = tuple(spec.metric_id for spec in specs)
    if len(metric_ids) != len(set(metric_ids)):
        errors.append("duplicate metric_id")
    for spec in specs:
        errors.extend(f"{spec.metric_id}: {error}" for error in spec.validate())
    return tuple(errors)


def default_metric_report(results: tuple[EvalMetricResult, ...] = (), summary: str = "") -> EvalMetricReport:
    return EvalMetricReport(
        report_id=DEFAULT_REPORT_ID,
        metric_specs=DEFAULT_METRICS,
        results=results,
        gate_policy=DEFAULT_GATE_POLICY,
        summary=summary,
    )


def metrics_to_dict(specs: tuple[EvalMetricSpec, ...] = DEFAULT_METRICS) -> dict[str, Any]:
    return {
        "version": DEFAULT_VERSION,
        "metric_categories": list(METRIC_CATEGORIES),
        "metric_modes": list(METRIC_MODES),
        "metrics": [spec.to_dict() for spec in specs],
    }
