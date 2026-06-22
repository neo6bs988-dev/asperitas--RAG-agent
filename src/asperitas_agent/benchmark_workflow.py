from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SOURCE_PRIORITIES = ("P0", "P1", "P2", "P3", "P4", "P5", "P6")
EVIDENCE_LABELS = (
    "Document-Supported Fact",
    "Official Source",
    "Peer-Reviewed Evidence",
    "Regulatory Source",
    "Industry Signal",
    "Inference",
    "Speculation",
    "Needs External Verification",
)
ALLOWED_USE_CASES = (
    "strategy",
    "science",
    "compliance",
    "market",
    "fundraising",
    "operations",
    "agent_development",
    "rag",
    "historical_context",
    "benchmarking",
)
PROHIBITED_USE_CASES = (
    "wet_lab_execution",
    "protocol_automation",
    "cloud_lab_connection",
    "lims_eln_robotics_integration",
    "external_execution_system",
    "autonomous_wet_lab_claim",
    "production_hybrid_claim",
)
COMPLIANCE_RISK_FLAGS = (
    "CITES",
    "Nagoya",
    "LMO",
    "biosafety",
    "biosecurity",
    "legal_ip",
    "financial_investor",
    "privacy",
    "confidential_source",
    "wet_lab",
)
APPROVAL_REQUIRED_FLAGS = (
    "wet_lab",
    "biosafety",
    "biosecurity",
    "legal_ip",
    "financial_investor",
    "confidential_source",
)
PROHIBITED_EXTERNAL_TARGETS = (
    "cloud_lab",
    "lims",
    "eln",
    "robotics",
    "external_execution_system",
    "wet_lab_robot",
)
PROHIBITED_CLAIM_TYPES = (
    "asperitas_performance",
    "production_hybrid",
    "autonomous_wet_lab",
    "wet_lab_validation",
)
DEFAULT_RETRIEVER = "mvp003"
HYBRID_POLICY = "explicit_manual_experimental_only"
RERANKER_POLICY = "deterministic_test_explicit_opt_in_non_default"


@dataclass(frozen=True)
class BenchmarkRiskFlag:
    risk_domain: str
    severity: str
    rationale: str
    human_approval_required: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if self.risk_domain not in COMPLIANCE_RISK_FLAGS:
            errors.append(f"unknown risk_domain: {self.risk_domain}")
        if self.severity not in ("low", "medium", "high"):
            errors.append("risk severity must be low, medium, or high")
        if not self.rationale.strip():
            errors.append("risk rationale is required")
        if self.risk_domain in APPROVAL_REQUIRED_FLAGS and not self.human_approval_required:
            errors.append(f"{self.risk_domain} requires human approval")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HumanApprovalGate:
    gate_id: str
    risk_domains: tuple[str, ...]
    required_reviewer: str
    approval_required: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.gate_id.strip():
            errors.append("approval gate_id is required")
        if not self.risk_domains:
            errors.append("approval gate risk_domains are required")
        for domain in self.risk_domains:
            if domain not in COMPLIANCE_RISK_FLAGS:
                errors.append(f"unknown approval risk_domain: {domain}")
        if any(domain in APPROVAL_REQUIRED_FLAGS for domain in self.risk_domains) and not self.approval_required:
            errors.append("high-risk approval gate must require approval")
        if not self.required_reviewer.strip():
            errors.append("approval gate required_reviewer is required")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MetricObject:
    metric_id: str
    name: str
    benchmark_value: float | int | str | None
    unit: str
    source_context: str
    represents_asperitas_performance: bool = False

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.metric_id.strip():
            errors.append("metric_id is required")
        if not self.name.strip():
            errors.append("metric name is required")
        if not self.unit.strip():
            errors.append("metric unit is required")
        if not self.source_context.strip():
            errors.append("metric source_context is required")
        if self.represents_asperitas_performance:
            errors.append("benchmark metrics must not represent Asperitas performance")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationGate:
    gate_id: str
    description: str
    fail_closed: bool = True
    blocks_execution: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.gate_id.strip():
            errors.append("validation gate_id is required")
        if not self.description.strip():
            errors.append("validation gate description is required")
        if not self.fail_closed:
            errors.append("validation gates must fail closed")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorkflowTranslationBoundary:
    boundary_id: str
    description: str
    source_format: str
    target_format: str
    descriptive_only: bool = True
    executable: bool = False
    external_targets: tuple[str, ...] = ()

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.boundary_id.strip():
            errors.append("translation boundary_id is required")
        if not self.description.strip():
            errors.append("translation boundary description is required")
        if not self.source_format.strip() or not self.target_format.strip():
            errors.append("translation boundary formats are required")
        if not self.descriptive_only:
            errors.append("workflow translation boundary must remain descriptive only")
        if self.executable:
            errors.append("workflow translation boundary must not be executable")
        prohibited = sorted(set(self.external_targets) & set(PROHIBITED_EXTERNAL_TARGETS))
        if prohibited:
            errors.append(f"external execution targets are prohibited: {', '.join(prohibited)}")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkDesignObject:
    design_id: str
    objective: str
    parameters: dict[str, str] = field(default_factory=dict)
    execution_intent: str = "benchmark_analysis_only"
    wet_lab_execution_requested: bool = False
    protocol_automation_requested: bool = False

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.design_id.strip():
            errors.append("design_id is required")
        if not self.objective.strip():
            errors.append("design objective is required")
        if self.execution_intent != "benchmark_analysis_only":
            errors.append("design execution_intent must be benchmark_analysis_only")
        if self.wet_lab_execution_requested:
            errors.append("wet-lab execution intent is prohibited")
        if self.protocol_automation_requested:
            errors.append("protocol automation intent is prohibited")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunResultMetadata:
    run_id: str
    result_summary: str
    captured_fields: tuple[str, ...]
    external_execution_performed: bool = False
    wet_lab_validation_claimed: bool = False

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.run_id.strip():
            errors.append("run_id is required")
        if not self.result_summary.strip():
            errors.append("result_summary is required")
        if not self.captured_fields:
            errors.append("captured_fields are required")
        if self.external_execution_performed:
            errors.append("external execution must not be represented in MVP-015")
        if self.wet_lab_validation_claimed:
            errors.append("wet-lab validation must not be claimed")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HypothesisLog:
    hypothesis_id: str
    claim: str
    evidence_label: str
    confidence: str
    verification_needed: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.hypothesis_id.strip():
            errors.append("hypothesis_id is required")
        if not self.claim.strip():
            errors.append("hypothesis claim is required")
        if self.evidence_label not in EVIDENCE_LABELS:
            errors.append(f"unknown hypothesis evidence_label: {self.evidence_label}")
        if self.confidence not in ("low", "medium", "high"):
            errors.append("hypothesis confidence must be low, medium, or high")
        if self.evidence_label in ("Inference", "Speculation", "Needs External Verification") and not self.verification_needed:
            errors.append("unverified hypothesis labels must keep verification_needed true")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkWorkflowSpec:
    workflow_id: str
    title: str
    source_path: str
    source_priority: str
    evidence_label: str
    allowed_use_cases: tuple[str, ...]
    prohibited_use_cases: tuple[str, ...]
    design_object: BenchmarkDesignObject
    validation_gates: tuple[ValidationGate, ...]
    translation_boundary: WorkflowTranslationBoundary
    metrics: tuple[MetricObject, ...]
    run_result_metadata: RunResultMetadata
    hypothesis_logs: tuple[HypothesisLog, ...]
    human_approval_gates: tuple[HumanApprovalGate, ...]
    risk_flags: tuple[BenchmarkRiskFlag, ...]
    default_retriever: str = DEFAULT_RETRIEVER
    hybrid_policy: str = HYBRID_POLICY
    reranker_policy: str = RERANKER_POLICY
    autonomous_wet_lab_claim: bool = False

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.workflow_id.strip():
            errors.append("workflow_id is required")
        if not self.title.strip():
            errors.append("title is required")
        if not self.source_path.strip():
            errors.append("source_path is required")
        if self.source_priority not in SOURCE_PRIORITIES:
            errors.append(f"unknown source_priority: {self.source_priority}")
        if self.evidence_label not in EVIDENCE_LABELS:
            errors.append(f"unknown evidence_label: {self.evidence_label}")
        if not self.allowed_use_cases:
            errors.append("allowed_use_cases are required")
        for use_case in self.allowed_use_cases:
            if use_case not in ALLOWED_USE_CASES:
                errors.append(f"unknown allowed_use_case: {use_case}")
        if not self.prohibited_use_cases:
            errors.append("prohibited_use_cases are required")
        required_prohibited = {
            "wet_lab_execution",
            "protocol_automation",
            "cloud_lab_connection",
            "lims_eln_robotics_integration",
            "external_execution_system",
            "autonomous_wet_lab_claim",
        }
        missing_prohibited = sorted(required_prohibited - set(self.prohibited_use_cases))
        if missing_prohibited:
            errors.append(f"missing prohibited use cases: {', '.join(missing_prohibited)}")
        for use_case in self.prohibited_use_cases:
            if use_case not in PROHIBITED_USE_CASES:
                errors.append(f"unknown prohibited_use_case: {use_case}")
        if self.default_retriever != DEFAULT_RETRIEVER:
            errors.append("default retriever must remain mvp003")
        if self.hybrid_policy != HYBRID_POLICY:
            errors.append("hybrid policy must remain explicit/manual/experimental only")
        if self.reranker_policy != RERANKER_POLICY:
            errors.append("deterministic-test reranker must remain explicit opt-in/non-default")
        if self.autonomous_wet_lab_claim:
            errors.append("autonomous wet-lab claim is prohibited")

        errors.extend(f"design_object: {error}" for error in self.design_object.validate())
        errors.extend(f"translation_boundary: {error}" for error in self.translation_boundary.validate())
        errors.extend(f"run_result_metadata: {error}" for error in self.run_result_metadata.validate())
        errors.extend(_validate_tuple("validation_gates", self.validation_gates))
        errors.extend(_validate_tuple("metrics", self.metrics))
        errors.extend(_validate_tuple("hypothesis_logs", self.hypothesis_logs))
        errors.extend(_validate_tuple("human_approval_gates", self.human_approval_gates))
        errors.extend(_validate_tuple("risk_flags", self.risk_flags))

        risk_domains = {flag.risk_domain for flag in self.risk_flags}
        approval_domains = {domain for gate in self.human_approval_gates for domain in gate.risk_domains}
        missing_approval = sorted((risk_domains & set(APPROVAL_REQUIRED_FLAGS)) - approval_domains)
        if missing_approval:
            errors.append(f"missing human approval gates for: {', '.join(missing_approval)}")
        return tuple(errors)

    def require_valid(self) -> None:
        errors = self.validate()
        if errors:
            raise ValueError("; ".join(errors))

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "title": self.title,
            "source_path": self.source_path,
            "source_priority": self.source_priority,
            "evidence_label": self.evidence_label,
            "allowed_use_cases": list(self.allowed_use_cases),
            "prohibited_use_cases": list(self.prohibited_use_cases),
            "design_object": self.design_object.to_dict(),
            "validation_gates": [gate.to_dict() for gate in self.validation_gates],
            "translation_boundary": self.translation_boundary.to_dict(),
            "metrics": [metric.to_dict() for metric in self.metrics],
            "run_result_metadata": self.run_result_metadata.to_dict(),
            "hypothesis_logs": [log.to_dict() for log in self.hypothesis_logs],
            "human_approval_gates": [gate.to_dict() for gate in self.human_approval_gates],
            "risk_flags": [flag.to_dict() for flag in self.risk_flags],
            "default_retriever": self.default_retriever,
            "hybrid_policy": self.hybrid_policy,
            "reranker_policy": self.reranker_policy,
            "autonomous_wet_lab_claim": self.autonomous_wet_lab_claim,
        }


def _validate_tuple(field_name: str, items: tuple[Any, ...]) -> tuple[str, ...]:
    if not items:
        return (f"{field_name} are required",)
    errors: list[str] = []
    for item in items:
        validate = getattr(item, "validate", None)
        if validate is None:
            errors.append(f"{field_name} item lacks validate method")
            continue
        errors.extend(f"{field_name}: {error}" for error in validate())
    return tuple(errors)

