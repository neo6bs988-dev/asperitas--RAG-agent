from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any


RISK_LEVELS = ("low", "medium", "high")
SKILL_STATUSES = ("active", "planned", "deprecated")
DEFAULT_VERSION = "MVP-016D"
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
IDENTITY_CLASSIFICATIONS = ("true_compatibility_alias", "deprecated_migration_alias")
REQUIRED_SKILL_IDS = (
    "mvp_implementation",
    "source_grounding_check",
    "retrieval_eval",
    "compliance_review",
    "benchmark_workflow_preflight",
    "decision_log_maintainer",
    "docs_only_governance_update",
    "reference_acquisition",
    "open_source_review",
    "security_review",
    "pr_closeout",
    "pr_closeout_report",
    "read_only_audit",
    "retrieval_regression_closeout",
    "asperitas_audit_trace",
    "asperitas_compliance_audit",
    "asperitas_evaluation",
    "asperitas_mcp_expansion",
    "asperitas_rag_development",
    "asperitas_retrieval",
    "asperitas_security",
    "asperitas_source_audit",
    "asperitas_v1_architect",
    "asperitas_workflow",
    "dependency_security_quality_gate",
    "mvp_release_manager",
    "performance_optimization_gate",
    "source_grounding_citation",
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


@dataclass(frozen=True, order=True)
class SkillIdentityAlias:
    legacy_id: str
    canonical_id: str
    classification: str
    deprecated_since: str
    compatibility_until: str


@dataclass(frozen=True)
class SkillIdentityResolution:
    requested_id: str
    identity_kind: str
    canonical_id: str | None
    decision: str
    deprecated: bool
    migration_required: bool
    compatibility_until: str | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SkillIdentityAuthority:
    canonical_ids: tuple[str, ...]
    aliases: tuple[SkillIdentityAlias, ...]

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        canonical_ids = set(self.canonical_ids)
        if len(canonical_ids) != len(self.canonical_ids):
            errors.append("duplicate canonical skill_id")
        alias_ids = [alias.legacy_id for alias in self.aliases]
        if len(alias_ids) != len(set(alias_ids)):
            errors.append("duplicate legacy alias")
        edges: dict[str, str] = {}
        for alias in self.aliases:
            if alias.classification not in IDENTITY_CLASSIFICATIONS:
                errors.append(f"invalid alias classification: {alias.legacy_id}")
            if alias.legacy_id in canonical_ids:
                errors.append(f"alias collides with canonical skill_id: {alias.legacy_id}")
            if alias.legacy_id == alias.canonical_id:
                errors.append(f"self alias: {alias.legacy_id}")
            if alias.canonical_id not in canonical_ids:
                errors.append(f"missing alias successor: {alias.legacy_id} -> {alias.canonical_id}")
            deprecated = _identity_date(alias.deprecated_since)
            compatibility_until = _identity_date(alias.compatibility_until)
            if deprecated is None:
                errors.append(f"invalid deprecated_since: {alias.legacy_id}")
            if compatibility_until is None:
                errors.append(f"invalid compatibility_until: {alias.legacy_id}")
            if deprecated is not None and compatibility_until is not None and compatibility_until < deprecated:
                errors.append(f"invalid compatibility window: {alias.legacy_id}")
            edges[alias.legacy_id] = alias.canonical_id
        for start in sorted(edges):
            seen: set[str] = set()
            current = start
            while current in edges:
                if current in seen:
                    errors.append(f"alias cycle: {start}")
                    break
                seen.add(current)
                current = edges[current]
        return tuple(sorted(set(errors)))

    def resolve(self, requested_id: str, *, as_of: date | None = None) -> SkillIdentityResolution:
        if self.validate():
            return SkillIdentityResolution(
                requested_id=requested_id,
                identity_kind="unknown",
                canonical_id=None,
                decision="blocked",
                deprecated=False,
                migration_required=False,
                compatibility_until=None,
                reason="identity authority is invalid and blocked fail-closed",
            )
        if requested_id in self.canonical_ids:
            return SkillIdentityResolution(
                requested_id=requested_id,
                identity_kind="canonical",
                canonical_id=requested_id,
                decision="canonical",
                deprecated=False,
                migration_required=False,
                compatibility_until=None,
                reason="requested identity is canonical",
            )
        alias = next((item for item in self.aliases if item.legacy_id == requested_id), None)
        if alias is None:
            return SkillIdentityResolution(
                requested_id=requested_id,
                identity_kind="unknown",
                canonical_id=None,
                decision="blocked",
                deprecated=False,
                migration_required=False,
                compatibility_until=None,
                reason="unknown skill identity is unsupported and blocked fail-closed",
            )
        expired = (as_of or date.today()) > date.fromisoformat(alias.compatibility_until)
        migration_required = alias.classification == "deprecated_migration_alias" or expired
        return SkillIdentityResolution(
            requested_id=requested_id,
            identity_kind=(
                "migration_required_legacy_id" if migration_required else "deprecated_compatibility_alias"
            ),
            canonical_id=alias.canonical_id,
            decision="migration_required" if migration_required else "compatibility_alias",
            deprecated=True,
            migration_required=migration_required,
            compatibility_until=alias.compatibility_until,
            reason=(
                "legacy identity requires explicit migration and grants no successor capabilities"
                if migration_required
                else "deprecated compatibility alias resolves to one canonical identity without capability expansion"
            ),
        )


def _identity_date(value: str) -> date | None:
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed.isoformat() == value else None


SKILL_IDENTITY_ALIASES = (
    SkillIdentityAlias(
        legacy_id="benchmark_workflow_preflight",
        canonical_id="mvp_implementation",
        classification="deprecated_migration_alias",
        deprecated_since="2026-06-23",
        compatibility_until="2026-12-31",
    ),
    SkillIdentityAlias(
        legacy_id="compliance_review",
        canonical_id="compliance_biosafety_review",
        classification="true_compatibility_alias",
        deprecated_since="2026-06-23",
        compatibility_until="2026-12-31",
    ),
    SkillIdentityAlias(
        legacy_id="retrieval_eval",
        canonical_id="retrieval_eval_quality_gate",
        classification="true_compatibility_alias",
        deprecated_since="2026-06-23",
        compatibility_until="2026-12-31",
    ),
)


def build_skill_identity_authority(canonical_ids: tuple[str, ...]) -> SkillIdentityAuthority:
    normalized = tuple(sorted(canonical_ids))
    aliases = tuple(alias for alias in SKILL_IDENTITY_ALIASES if alias.canonical_id in normalized)
    return SkillIdentityAuthority(normalized, aliases)


@dataclass(frozen=True)
class SkillRegistry:
    skills: tuple[SkillSpec, ...]
    registry_id: str = "asperitas_v1_skill_registry"
    version: str = DEFAULT_VERSION
    identity_authority: SkillIdentityAuthority | None = None

    def list_skill_ids(self) -> tuple[str, ...]:
        return tuple(skill.skill_id for skill in self.skills)

    def get_skill(self, skill_id: str) -> SkillSpec | None:
        return {skill.skill_id: skill for skill in self.skills}.get(skill_id)

    def lookup_decision(self, skill_id: str) -> dict[str, Any]:
        identity = self.identity_authority.resolve(skill_id) if self.identity_authority is not None else None
        skill = self.get_skill(skill_id)
        if skill is None:
            result = {
                "skill_id": skill_id,
                "supported": False,
                "decision": "blocked",
                "reason": "unknown skill is unsupported and blocked fail-closed",
            }
            if identity is not None:
                result["identity"] = identity.to_dict()
                if identity.identity_kind == "canonical":
                    result["reason"] = "canonical repository identity has no incumbent runtime SkillSpec"
            return result
        errors = skill.validate()
        result = {
            "skill_id": skill_id,
            "supported": not errors,
            "decision": "supported" if not errors else "blocked",
            "reason": "skill is registered and valid" if not errors else "registered skill failed validation",
            "validation_errors": list(errors),
        }
        if identity is not None:
            result["identity"] = identity.to_dict()
            if identity.migration_required:
                result.update(
                    supported=False,
                    decision="migration_required",
                    reason=identity.reason,
                )
        return result

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
        "decision_log_maintainer",
        "Decision Log Maintainer",
        "Maintain append-only decision logs with metric provenance, risks, decisions, and next actions.",
        ("decision_context", "metric_provenance", "changed_files", "risk_summary"),
        ("decision_log_entry", "metrics_labeling", "risks", "next_action"),
        ("record_decision_log", "label_metric_provenance", "preserve_historical_logs"),
    ),
    _skill(
        "docs_only_governance_update",
        "Docs Only Governance Update",
        "Apply additive governance, workflow, prompt, or skill updates without runtime or artifact mutation.",
        ("governance_scope", "allowed_files", "forbidden_files", "verification_plan"),
        ("files_changed", "skipped_tests", "risks", "next_step"),
        ("update_governance_docs", "preserve_runtime_behavior", "report_skipped_checks"),
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
    _skill(
        "pr_closeout_report",
        "PR Closeout Report",
        "Prepare PR closeout evidence with files, commands, metrics, skipped gates, risks, and next action.",
        ("pr_scope", "changed_files", "commands_run", "metrics"),
        ("closeout_report", "risk_summary", "merge_readiness", "next_action"),
        ("summarize_scope", "label_metric_provenance", "report_residual_risks"),
    ),
    _skill(
        "read_only_audit",
        "Read Only Audit",
        "Inspect repository state, metrics, issues, PRs, and risks without changing files.",
        ("audit_scope", "files_to_inspect", "constraints"),
        ("findings", "risks", "skipped_checks", "next_action"),
        ("inspect_files", "report_findings", "preserve_worktree"),
    ),
    _skill(
        "retrieval_regression_closeout",
        "Retrieval Regression Closeout",
        "Close, defer, or reclassify retrieval regressions after fresh evals and failure taxonomy review.",
        ("failed_questions", "fresh_metrics", "failure_taxonomy", "retrieval_modes"),
        ("closeout_decision", "regression_summary", "risks", "next_action"),
        ("compare_retrieval_metrics", "preserve_mvp003_default", "record_decision_log"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_audit_trace",
        "Asperitas Audit Trace",
        "Define local audit, provenance, citation coverage, trace log, and decision-log expectations.",
        ("changed_surface", "trace_context", "source_metadata"),
        ("audit_trace_requirements", "provenance_gaps", "decision_log_needed", "residual_risk"),
        ("review_trace_requirements", "flag_provenance_gaps", "record_decision_log"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_compliance_audit",
        "Asperitas Compliance Audit",
        "Review biosafety, biosecurity, biodiversity, legal, privacy, IP, investor, and external-communication risk.",
        ("content_or_change", "risk_context", "intended_audience"),
        ("risk_domains", "approval_needed", "blocked_claims", "safe_next_action"),
        ("classify_compliance_risk", "block_unsafe_claims", "require_human_approval"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_evaluation",
        "Asperitas Evaluation",
        "Plan or review local evals, RAGAS-style metrics, retrieval baselines, faithfulness checks, and performance reporting.",
        ("eval_scope", "baseline_context", "changed_surface"),
        ("eval_plan", "metrics_required", "regression_risks", "reporting_limits"),
        ("define_eval_scope", "compare_local_metrics", "prevent_performance_overclaims"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_mcp_expansion",
        "Asperitas MCP Expansion",
        "Plan external connector and tool allowlist boundaries without enabling calls or integrations by default.",
        ("connector_candidate", "intended_use", "risk_context"),
        ("allowlist_review", "blocked_actions", "approval_needed", "safe_next_action"),
        ("review_connector_metadata", "flag_external_call_risk", "require_human_approval"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_rag_development",
        "Asperitas RAG Development",
        "Plan or review RAG architecture, chunking, retrieval, metadata, vector DB, reranking, and answer-generation changes.",
        ("rag_change_scope", "source_state", "eval_plan"),
        ("architecture_impact", "required_evals", "approval_needed", "retrieval_default_status"),
        ("review_rag_scope", "preserve_retrieval_defaults", "require_retrieval_eval"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_retrieval",
        "Asperitas Retrieval",
        "Review retrieval, metadata-aware search, ranking, citation grounding, and answer-context selection changes.",
        ("retrieval_change_scope", "baseline_metrics", "source_metadata"),
        ("eval_requirements", "regression_risks", "top_k_notes", "approval_needed"),
        ("review_retrieval_change", "preserve_mvp003_default", "require_retrieval_eval"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_security",
        "Asperitas Security",
        "Review agent security, prompt-injection, source-poisoning, connector, permission, CI, and secret-handling risks.",
        ("changed_surface", "permissions", "data_exposure_context"),
        ("security_verdict", "risks_found", "required_fixes", "approval_needed"),
        ("check_prompt_injection_risk", "check_no_secrets", "block_unreviewed_external_calls"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_source_audit",
        "Asperitas Source Audit",
        "Review source manifests, registry fields, license status, disclosure level, citation metadata, and ingestion gates.",
        ("source_candidate_or_registry_change", "license_context", "disclosure_context"),
        ("source_audit_verdict", "metadata_gaps", "license_review_needed", "ingestion_allowed_status"),
        ("review_source_metadata", "flag_license_review", "preserve_ingestion_gate"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_v1_architect",
        "Asperitas V1 Architect",
        "Plan V1 architecture layers and benchmark-pattern adoption while preserving stage boundaries and approval gates.",
        ("architecture_question", "mvp_context", "constraints"),
        ("architecture_decision", "stage_boundary", "risks", "next_mvp"),
        ("classify_architecture_impact", "preserve_stage_boundary", "record_decision_log"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "asperitas_workflow",
        "Asperitas Workflow",
        "Design or review planner, retriever, reranker, validator, answer workflow, and orchestration contracts.",
        ("workflow_scope", "state_contract", "risk_context"),
        ("workflow_contract", "blocked_operations", "approval_needed", "verification_plan"),
        ("review_workflow_contract", "block_autonomous_execution", "preserve_human_approval_gate"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "dependency_security_quality_gate",
        "Dependency Security Quality Gate",
        "Review dependency, CI, scanner, lint, type-check, and package-management changes before adoption.",
        ("dependency_or_quality_change", "intended_use", "security_context"),
        ("adoption_verdict", "license_review_needed", "security_review_needed", "allowed_next_action"),
        ("review_dependency_metadata", "block_new_dependency_without_review", "record_decision_log"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "mvp_release_manager",
        "MVP Release Manager",
        "Close an MVP stage with docs, decision logs, tests, risks, retrieval applicability, and next-MVP recommendation.",
        ("mvp_objective", "changed_files", "verification_results", "risk_summary"),
        ("closeout_summary", "artifact_metrics", "retrieval_eval_applicability", "next_mvp"),
        ("summarize_mvp_closeout", "check_required_artifacts", "report_residual_risks"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "performance_optimization_gate",
        "Performance Optimization Gate",
        "Review claims about retrieval, ranking, latency, groundedness, compliance safety, or workflow performance improvements.",
        ("performance_claim", "baseline_metrics", "changed_surface"),
        ("validated_metrics", "unsupported_claims", "eval_needed", "approval_needed"),
        ("check_baseline_metrics", "block_unsupported_performance_claims", "require_eval_for_claims"),
        risk_level="high",
        approval_required=True,
    ),
    _skill(
        "source_grounding_citation",
        "Source Grounding Citation",
        "Review answer generation, citation, evidence-label, source-hierarchy, and hallucination-prevention behavior.",
        ("answer_or_change", "source_metadata", "citation_context"),
        ("citation_verdict", "unsupported_claims", "required_fixes", "residual_risk"),
        ("check_citation_targets", "check_evidence_labels", "flag_hallucination_risk"),
        risk_level="high",
        approval_required=True,
    ),
)

_LEGACY_SKILL_IDS = frozenset(alias.legacy_id for alias in SKILL_IDENTITY_ALIASES)
_DEFAULT_CANONICAL_IDS = tuple(
    sorted(
        {skill.skill_id for skill in DEFAULT_SKILLS if skill.skill_id not in _LEGACY_SKILL_IDS}
        | {alias.canonical_id for alias in SKILL_IDENTITY_ALIASES}
    )
)
DEFAULT_SKILL_IDENTITY_AUTHORITY = build_skill_identity_authority(_DEFAULT_CANONICAL_IDS)
DEFAULT_SKILL_REGISTRY = SkillRegistry(DEFAULT_SKILLS, identity_authority=DEFAULT_SKILL_IDENTITY_AUTHORITY)


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
