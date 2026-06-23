from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


RISK_LEVELS = ("low", "medium", "high")
SKILL_STATUSES = ("active", "planned", "deprecated")
DEFAULT_VERSION = "MVP-016B"
DEFAULT_LAYER = "asperitas_v1_local_skill_registry"
DEFAULT_FORBIDDEN_OPERATIONS = (
    "treat_source_text_as_instruction",
    "copy_third_party_code_without_review",
    "add_new_dependency",
    "call_external_system_without_approval",
    "execute_workflow_without_approval",
    "ingest_source_without_approval",
    "benchmark_as_Asperitas_performance",
    "autonomous_wet_lab_claim",
    "production_readiness_claim",
)
OVERCLAIM_BLOCKS = (
    "benchmark_as_Asperitas_performance",
    "autonomous_wet_lab_claim",
    "production_readiness_claim",
)
REQUIRED_SKILL_IDS = (
    "mvp_implementation",
    "source_grounding_check",
    "retrieval_eval",
    "compliance_review",
    "benchmark_workflow_preflight",
    "reference_acquisition",
    "open_source_review",
    "security_review",
    "pr_closeout",
)


@dataclass(frozen=True)
class SkillRiskPolicy:
    risk_level: str
    approval_required: bool
    source_grounding_required: bool = True
    audit_required: bool = True
    external_call_allowed: bool = False
    execution_allowed: bool = False
    ingestion_allowed: bool = False
    forbidden_operations: tuple[str, ...] = DEFAULT_FORBIDDEN_OPERATIONS

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if self.risk_level not in RISK_LEVELS:
            errors.append(f"invalid risk_level: {self.risk_level}")
        if self.risk_level == "high" and not self.approval_required:
            errors.append("high-risk skill requires approval_required=true")
        if self.external_call_allowed and not self.approval_required:
            errors.append("external call enabled without approval")
        if self.execution_allowed and not self.approval_required:
            errors.append("execution enabled without approval")
        if self.ingestion_allowed and not self.approval_required:
            errors.append("ingestion enabled without approval")
        if self.risk_level == "high" and not self.forbidden_operations:
            errors.append("high-risk skill requires forbidden_operations")
        missing_blocks = tuple(block for block in OVERCLAIM_BLOCKS if block not in self.forbidden_operations)
        if missing_blocks:
            errors.append(f"missing overclaim forbidden operations: {', '.join(missing_blocks)}")
        if "treat_source_text_as_instruction" not in self.forbidden_operations:
            errors.append("source text must be evidence, not instruction")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class SkillVerificationPlan:
    verification_commands: tuple[str, ...]
    audit_required: bool = True

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.verification_commands or any(not command.strip() for command in self.verification_commands):
            errors.append("verification_commands must be a non-empty tuple of non-empty strings")
        if not self.audit_required:
            errors.append("skill verification must require audit")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class SkillSpec:
    skill_id: str
    name: str
    description: str
    layer: str
    input_contract: tuple[str, ...]
    output_contract: tuple[str, ...]
    risk_level: str
    approval_required: bool
    allowed_operations: tuple[str, ...]
    forbidden_operations: tuple[str, ...]
    source_grounding_required: bool
    audit_required: bool
    external_call_allowed: bool
    execution_allowed: bool
    ingestion_allowed: bool
    verification_commands: tuple[str, ...]
    status: str
    version: str

    def risk_policy(self) -> SkillRiskPolicy:
        return SkillRiskPolicy(
            risk_level=self.risk_level,
            approval_required=self.approval_required,
            source_grounding_required=self.source_grounding_required,
            audit_required=self.audit_required,
            external_call_allowed=self.external_call_allowed,
            execution_allowed=self.execution_allowed,
            ingestion_allowed=self.ingestion_allowed,
            forbidden_operations=self.forbidden_operations,
        )

    def verification_plan(self) -> SkillVerificationPlan:
        return SkillVerificationPlan(
            verification_commands=self.verification_commands,
            audit_required=self.audit_required,
        )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for field_name in ("skill_id", "name", "description", "layer", "status", "version"):
            if not str(getattr(self, field_name)).strip():
                errors.append(f"{field_name} is required")
        for field_name in (
            "input_contract",
            "output_contract",
            "allowed_operations",
            "forbidden_operations",
            "verification_commands",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, tuple) or not value or any(not str(item).strip() for item in value):
                errors.append(f"{field_name} must be a non-empty tuple of non-empty strings")
        if self.status not in SKILL_STATUSES:
            errors.append(f"invalid status: {self.status}")

        errors.extend(f"risk_policy: {error}" for error in self.risk_policy().validate())
        errors.extend(f"verification_plan: {error}" for error in self.verification_plan().validate())

        allowed_overclaims = sorted(set(self.allowed_operations) & set(OVERCLAIM_BLOCKS))
        if allowed_overclaims:
            errors.append(f"blocked operations cannot be allowed: {', '.join(allowed_overclaims)}")
        if self.source_grounding_required and "preserve_source_grounding" not in self.allowed_operations:
            errors.append("source-grounded skills must preserve source grounding")
        if self.audit_required and "record_audit_trace" not in self.allowed_operations:
            errors.append("audit-required skills must record audit trace")
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


@dataclass(frozen=True)
class SkillRegistry:
    skills: tuple[SkillSpec, ...]
    registry_id: str = "asperitas_v1_skill_registry"
    version: str = DEFAULT_VERSION

    def list_skill_ids(self) -> tuple[str, ...]:
        return tuple(skill.skill_id for skill in self.skills)

    def get_skill(self, skill_id: str) -> SkillSpec | None:
        return {skill.skill_id: skill for skill in self.skills}.get(skill_id)

    def lookup_decision(self, skill_id: str) -> dict[str, Any]:
        skill = self.get_skill(skill_id)
        if skill is None:
            return {
                "skill_id": skill_id,
                "supported": False,
                "decision": "blocked",
                "reason": "unknown skill is unsupported and blocked fail-closed",
            }
        errors = skill.validate()
        return {
            "skill_id": skill_id,
            "supported": not errors,
            "decision": "supported" if not errors else "blocked",
            "reason": "skill is registered and valid" if not errors else "registered skill failed validation",
            "validation_errors": list(errors),
        }

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        skill_ids = self.list_skill_ids()
        if len(skill_ids) != len(set(skill_ids)):
            errors.append("duplicate skill_id")
        missing = tuple(skill_id for skill_id in REQUIRED_SKILL_IDS if skill_id not in skill_ids)
        if missing:
            errors.append(f"missing required skills: {', '.join(missing)}")
        for skill in self.skills:
            errors.extend(f"{skill.skill_id}: {error}" for error in skill.validate())
        return tuple(errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_id": self.registry_id,
            "version": self.version,
            "required_skill_ids": list(REQUIRED_SKILL_IDS),
            "skills": [skill.to_dict() for skill in self.skills],
        }


def _skill(
    skill_id: str,
    name: str,
    description: str,
    input_contract: tuple[str, ...],
    output_contract: tuple[str, ...],
    allowed_operations: tuple[str, ...],
    risk_level: str = "medium",
    approval_required: bool = False,
    source_grounding_required: bool = True,
    audit_required: bool = True,
    external_call_allowed: bool = False,
    execution_allowed: bool = False,
    ingestion_allowed: bool = False,
    verification_commands: tuple[str, ...] = ("python -m pytest -q tests/test_skill_registry.py",),
    layer: str = DEFAULT_LAYER,
    status: str = "active",
    version: str = DEFAULT_VERSION,
) -> SkillSpec:
    return SkillSpec(
        skill_id=skill_id,
        name=name,
        description=description,
        layer=layer,
        input_contract=input_contract,
        output_contract=output_contract,
        risk_level=risk_level,
        approval_required=approval_required,
        allowed_operations=tuple(dict.fromkeys((*allowed_operations, "record_audit_trace", "preserve_source_grounding"))),
        forbidden_operations=DEFAULT_FORBIDDEN_OPERATIONS,
        source_grounding_required=source_grounding_required,
        audit_required=audit_required,
        external_call_allowed=external_call_allowed,
        execution_allowed=execution_allowed,
        ingestion_allowed=ingestion_allowed,
        verification_commands=verification_commands,
        status=status,
        version=version,
    )


DEFAULT_SKILLS = (
    _skill(
        "mvp_implementation",
        "MVP Implementation",
        "Implement scoped local MVP changes with tests, docs, decision logs, and no default retrieval changes.",
        ("objective", "scope", "constraints", "verification_plan"),
        ("files_changed", "tests", "risks", "next_mvp"),
        ("make_local_code_change", "add_focused_tests", "update_docs", "add_decision_log"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "source_grounding_check",
        "Source Grounding Check",
        "Verify source metadata, evidence labels, unsupported-claim handling, and source-state boundaries.",
        ("output_under_review", "source_metadata", "intended_audience"),
        ("grounding_verdict", "unsupported_claims", "required_fixes", "residual_risk"),
        ("check_source_ids", "check_evidence_labels", "flag_unsupported_claims"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "retrieval_eval",
        "Retrieval Eval",
        "Run or review retrieval evaluation only when retrieval-affecting changes are explicitly scoped.",
        ("eval_dataset", "retriever_name", "top_k", "baseline_metrics"),
        ("metrics", "regressions", "decision", "follow_up"),
        ("run_local_eval_command", "compare_metrics", "report_regressions"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "compliance_review",
        "Compliance Review",
        "Classify compliance, biosafety, legal, IP, privacy, investor, and public-communication risks.",
        ("content_or_code_path", "risk_context", "audience"),
        ("risk_domain", "severity", "approval_needed", "safe_next_action"),
        ("classify_risk", "require_human_approval", "block_unsafe_claims"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "benchmark_workflow_preflight",
        "Benchmark Workflow Preflight",
        "Evaluate MVP-015 BenchmarkWorkflowSpec objects through the MVP-016A read-only decision layer.",
        ("benchmark_workflow_spec",),
        ("allowed_or_blocked_decision", "reasons", "risk_flags", "source_metadata", "policy_metadata"),
        ("call_mvp016a_read_only_decision_layer", "preserve_benchmark_metadata", "return_no_execution_no_ingestion"),
        verification_commands=(
            "python -m pytest -q tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py",
        ),
    ),
    _skill(
        "reference_acquisition",
        "Reference Acquisition",
        "Track external references as metadata and review candidates without ingestion or dependency adoption.",
        ("source_title", "source_url", "intended_use"),
        ("metadata_record", "license_status", "security_status", "allowed_next_action"),
        ("record_reference_metadata", "flag_license_review", "flag_security_review"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "open_source_review",
        "Open Source Review",
        "Review open-source or official reference candidates before adoption, copying, dependencies, or ingestion.",
        ("source_metadata", "intended_use", "adoption_level"),
        ("verdict", "allowed_actions", "blocked_actions", "decision_log_needed"),
        ("classify_adoption_level", "check_license_status", "check_security_status"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "security_review",
        "Security Review",
        "Review skill, workflow, source-handling, dependency, and external-call risks fail-closed.",
        ("changed_surface", "tool_permissions", "data_exposure_context"),
        ("security_verdict", "risks_found", "required_fixes", "approval_needed"),
        ("check_no_secrets", "block_unreviewed_external_calls", "check_source_text_not_instruction"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "pr_closeout",
        "PR Closeout",
        "Package scoped changes for review with tests, metrics, risks, source-grounding review, and next MVP.",
        ("objective", "changed_files", "test_results", "risks"),
        ("pr_body", "verification_summary", "retrieval_eval_applicability", "next_mvp"),
        ("summarize_scope", "summarize_tests", "report_residual_risks"),
    ),
)

DEFAULT_SKILL_REGISTRY = SkillRegistry(DEFAULT_SKILLS)


def list_skill_ids() -> tuple[str, ...]:
    return DEFAULT_SKILL_REGISTRY.list_skill_ids()


def list_skills() -> tuple[SkillSpec, ...]:
    return DEFAULT_SKILL_REGISTRY.skills


def get_skill(skill_id: str) -> SkillSpec | None:
    return DEFAULT_SKILL_REGISTRY.get_skill(skill_id)


def require_skill(skill_id: str) -> SkillSpec:
    skill = get_skill(skill_id)
    if skill is None:
        raise KeyError(f"unknown skill_id: {skill_id}")
    return skill


def validate_registry(registry: SkillRegistry = DEFAULT_SKILL_REGISTRY) -> tuple[str, ...]:
    return registry.validate()


def registry_to_dict(registry: SkillRegistry = DEFAULT_SKILL_REGISTRY) -> dict[str, Any]:
    return registry.to_dict()
