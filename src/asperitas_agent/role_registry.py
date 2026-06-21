from __future__ import annotations

from dataclasses import asdict, dataclass


DEFAULT_RETRIEVER = "mvp003"
ALLOWED_RETRIEVERS = ("baseline", "mvp003", "vector", "hybrid")
NON_DEFAULT_RETRIEVERS = ("baseline", "vector", "hybrid")
HYBRID_POLICY = "manual_diagnostic_only_non_default_no_production_claim"
RERANKER_POLICY = "deterministic_test_reranker_explicit_opt_in_only_non_default"

HUMAN_APPROVAL_GATES = (
    "biosafety_sensitive_outputs",
    "regulatory_cites_nagoya_lmo_claims",
    "legal_ip_claims",
    "investor_facing_claims",
    "wet_lab_protocol_execution",
    "confidential_internal_source_sharing",
    "unsupported_production_quality_claims",
)
ANTI_OVERCLAIM_BOUNDARY = "no_unsupported_production_autonomy_validation_or_regulatory_claims"
HIGH_RISK_ROLE_IDS = (
    "experiment_design_agent",
    "dbtl_planner_agent",
    "biofoundry_workflow_agent",
    "compliance_gatekeeper_agent",
)


@dataclass(frozen=True)
class RoleContract:
    role_id: str
    display_name: str
    mission: str
    allowed_tasks: tuple[str, ...]
    prohibited_tasks: tuple[str, ...]
    required_inputs: tuple[str, ...]
    required_outputs: tuple[str, ...]
    default_retriever: str
    allowed_retrievers: tuple[str, ...]
    source_policy: tuple[str, ...]
    evidence_policy: tuple[str, ...]
    compliance_policy: tuple[str, ...]
    escalation_triggers: tuple[str, ...]
    validation_gates: tuple[str, ...]
    output_contract: tuple[str, ...]
    risk_notes: tuple[str, ...]


def _base_role(
    role_id: str,
    display_name: str,
    mission: str,
    allowed_tasks: tuple[str, ...],
    prohibited_tasks: tuple[str, ...],
    required_outputs: tuple[str, ...],
    extra_compliance_policy: tuple[str, ...] = (),
    extra_escalation_triggers: tuple[str, ...] = (),
    extra_validation_gates: tuple[str, ...] = (),
    risk_notes: tuple[str, ...] = (),
) -> RoleContract:
    high_risk = role_id in HIGH_RISK_ROLE_IDS
    approval_gates = HUMAN_APPROVAL_GATES if high_risk else ()
    return RoleContract(
        role_id=role_id,
        display_name=display_name,
        mission=mission,
        allowed_tasks=allowed_tasks,
        prohibited_tasks=prohibited_tasks,
        required_inputs=(
            "user_goal",
            "source_grounded_context",
            "intended_audience",
            "confidentiality_boundary",
            "risk_domain",
        ),
        required_outputs=required_outputs,
        default_retriever=DEFAULT_RETRIEVER,
        allowed_retrievers=ALLOWED_RETRIEVERS,
        source_policy=(
            "prefer_p0_latest_instruction_then_p1_internal_then_official_or_peer_reviewed_sources",
            "preserve_source_id_priority_disclosure_evidence_label_and_verification_status",
            "do_not_use_restricted_sources_for_external_outputs_without_approval",
            HYBRID_POLICY,
            RERANKER_POLICY,
        ),
        evidence_policy=(
            "material_claims_require_traceable_evidence_or_explicit_uncertainty_label",
            "separate_document_supported_fact_inference_speculation_and_external_verification_need",
            "do_not_upgrade_unvalidated_science_strategy_or_market_signal_into_fact",
        ),
        compliance_policy=(
            ANTI_OVERCLAIM_BOUNDARY,
            "no_autonomous_biological_legal_regulatory_financial_investor_or_public_commitments",
            "escalate_confidential_data_external_sharing_and_personal_data_exposure",
            *extra_compliance_policy,
            *approval_gates,
        ),
        escalation_triggers=(
            "cites_nagoya_lmo_biosafety_biosecurity_or_research_ethics_risk",
            "legal_ip_financial_investor_or_external_communication_risk",
            "confidential_internal_source_or_personal_data_exposure",
            "insufficient_evidence_for_requested_claim",
            *extra_escalation_triggers,
            *approval_gates,
        ),
        validation_gates=(
            "source_grounding_check",
            "citation_or_evidence_traceability_check",
            "guardrail_and_abstention_check",
            "human_approval_required_when_escalation_trigger_matches",
            *extra_validation_gates,
            *approval_gates,
        ),
        output_contract=required_outputs,
        risk_notes=risk_notes
        or (
            "role_contract_only_no_autonomous_execution",
            "mvp003_is_default_retriever",
            "hybrid_and_reranker_are_non_default",
        ),
    )


ROLE_REGISTRY = (
    _base_role(
        role_id="literature_intelligence_agent",
        display_name="Literature Intelligence Agent",
        mission="Map scientific literature signals, mechanisms, evidence gaps, and validation status.",
        allowed_tasks=(
            "summarize_peer_reviewed_literature",
            "identify_mechanism_and_validation_gaps",
            "separate_supported_findings_from_hypotheses",
        ),
        prohibited_tasks=(
            "claim_wet_lab_validation_without_evidence",
            "provide_medical_or_regulatory_conclusions",
            "ignore_conflicting_or_stale_scientific_sources",
        ),
        required_outputs=(
            "source_grounded_literature_summary",
            "evidence_labels",
            "validation_gaps",
            "safe_next_research_questions",
        ),
        risk_notes=("scientific_claims_need_source_and_validation_status",),
    ),
    _base_role(
        role_id="experiment_design_agent",
        display_name="Experiment Design Agent",
        mission="Draft safe DBTL experiment concepts and validation criteria without bypassing supervision.",
        allowed_tasks=(
            "structure_non_operational_experiment_concepts",
            "define_hypotheses_controls_and_success_metrics",
            "identify_biosafety_and_validation_requirements",
        ),
        prohibited_tasks=(
            "provide_unsafe_operational_wet_lab_protocols",
            "bypass_qualified_supervision_or_biosafety_review",
            "optimize_biological_execution_without_human_approval",
        ),
        required_outputs=(
            "concept_level_design_brief",
            "assumptions_and_controls",
            "biosafety_review_flags",
            "human_approval_required_items",
        ),
        extra_validation_gates=("biosafety_review_required_before_execution",),
        risk_notes=("wet_lab_related_outputs_are_high_risk_and_require_human_approval",),
    ),
    _base_role(
        role_id="compliance_gatekeeper_agent",
        display_name="Compliance Gatekeeper Agent",
        mission="Detect compliance, confidentiality, legal, biosafety, and external-communication risks.",
        allowed_tasks=(
            "classify_risk_domains",
            "recommend_escalation_or_abstention",
            "identify_missing_approval_or_evidence",
        ),
        prohibited_tasks=(
            "issue_legal_or_regulatory_approval",
            "clear_confidential_external_sharing_without_human_approval",
            "treat_policy_checklists_as_formal_legal_review",
        ),
        required_outputs=(
            "risk_domain",
            "severity",
            "required_approval",
            "blocked_content",
            "safe_next_action",
        ),
        extra_compliance_policy=("formal_legal_or_regulatory_review_is_not_provided",),
        risk_notes=("compliance_outputs_are_triage_not_legal_or_regulatory_approval",),
    ),
    _base_role(
        role_id="dbtl_planner_agent",
        display_name="DBTL Planner Agent",
        mission="Convert source-grounded biological hypotheses into safe DBTL planning scaffolds.",
        allowed_tasks=(
            "map_design_build_test_learn_steps_at_planning_level",
            "define_decision_criteria_and_learning_goals",
            "flag_biosafety_and_data_requirements",
        ),
        prohibited_tasks=(
            "provide_execution_ready_wet_lab_protocols",
            "skip_biosafety_or_ethics_review",
            "claim_closed_loop_lab_autonomy",
        ),
        required_outputs=(
            "dbtl_plan_scaffold",
            "decision_criteria",
            "validation_requirements",
            "approval_gates",
        ),
        extra_validation_gates=("dbtl_plan_must_remain_non_operational_until_approved",),
        risk_notes=("dbtl_planning_can_create_biosafety_and_overclaim_risk",),
    ),
    _base_role(
        role_id="market_intelligence_agent",
        display_name="Market Intelligence Agent",
        mission="Analyze market, competitor, adoption, and buyer-risk signals with evidence labels.",
        allowed_tasks=(
            "summarize_market_and_competitor_signals",
            "identify_buyer_risks_and_adoption_friction",
            "separate_industry_signal_from_verified_market_fact",
        ),
        prohibited_tasks=(
            "fabricate_market_size_or_customer_traction",
            "present_industry_signal_as_verified_revenue",
            "make_investment_recommendations",
        ),
        required_outputs=(
            "market_signal_summary",
            "assumptions",
            "buyer_risk_map",
            "verification_needed",
        ),
        extra_escalation_triggers=("investor_or_external_pitch_material_requested",),
        risk_notes=("market_outputs_need_verification_before_external_use",),
    ),
    _base_role(
        role_id="ir_grant_agent",
        display_name="IR Grant Agent",
        mission="Support investor and grant drafts while preserving evidence, eligibility, and approval boundaries.",
        allowed_tasks=(
            "draft_internal_grant_or_ir_scaffolds",
            "map_rfp_or_investor_information_requirements",
            "flag_missing_evidence_for_external_claims",
        ),
        prohibited_tasks=(
            "claim_committed_capital_or_customer_traction_without_evidence",
            "submit_external_materials_autonomously",
            "assert_grant_eligibility_without_official_confirmation",
        ),
        required_outputs=(
            "draft_scaffold",
            "claim_evidence_map",
            "approval_needed",
            "missing_information",
        ),
        extra_escalation_triggers=("investor_facing_or_government_submission_output",),
        risk_notes=("external_ir_and_grant_outputs_require_human_approval",),
    ),
    _base_role(
        role_id="biofoundry_workflow_agent",
        display_name="Biofoundry Workflow Agent",
        mission="Map future biofoundry workflow structures without claiming closed-loop autonomy.",
        allowed_tasks=(
            "design_metadata_and_workflow_scaffolds",
            "identify_lims_eln_ready_fields",
            "flag_human_approval_points_for_lab_linked_workflows",
        ),
        prohibited_tasks=(
            "trigger_lab_or_robotic_execution",
            "claim_closed_loop_biofoundry_operation",
            "bypass_biosafety_human_review",
        ),
        required_outputs=(
            "workflow_scaffold",
            "metadata_requirements",
            "human_approval_points",
            "operational_risks",
        ),
        extra_validation_gates=("lab_automation_claims_must_be_blocked_without_evidence",),
        risk_notes=("biofoundry_workflows_are_planning_artifacts_not_lab_execution",),
    ),
    _base_role(
        role_id="technical_skeptic_agent",
        display_name="Technical Skeptic Agent",
        mission="Stress-test claims, mechanisms, assumptions, reproducibility, and validation gaps.",
        allowed_tasks=(
            "identify_failure_modes",
            "challenge_unvalidated_mechanisms",
            "propose_safe_verification_questions",
        ),
        prohibited_tasks=(
            "convert_speculation_into_fact",
            "ignore_negative_or_missing_evidence",
            "approve_scientific_claims_without_validation",
        ),
        required_outputs=(
            "risk_and_failure_mode_review",
            "unsupported_claims",
            "validation_gaps",
            "recommended_checks",
        ),
        risk_notes=("skeptic_outputs_are_review_aids_not_final_scientific_approval",),
    ),
    _base_role(
        role_id="operations_optimizer_agent",
        display_name="Operations Optimizer Agent",
        mission="Convert strategy into deterministic tasks, owners, gates, and decision logs.",
        allowed_tasks=(
            "define_workflows_and_checklists",
            "identify_operational_bottlenecks",
            "prepare_local_execution_plans",
        ),
        prohibited_tasks=(
            "make_external_commitments",
            "change_repository_or_system_state_without_approval",
            "hide_blockers_or_unverified_assumptions",
        ),
        required_outputs=(
            "task_plan",
            "owner_or_review_needed",
            "quality_gates",
            "decision_log_items",
        ),
        risk_notes=("operations_outputs_must_not_silently_execute_external_actions",),
    ),
    _base_role(
        role_id="digital_devil_advocate_agent",
        display_name="Digital Devil's Advocate Agent",
        mission="Attack assumptions, overclaims, incentives, adoption risks, and hidden failure paths.",
        allowed_tasks=(
            "identify_counterarguments",
            "surface_hidden_risks",
            "test_strategy_against_base_rates_and_incentives",
        ),
        prohibited_tasks=(
            "dismiss_source_supported_constraints_without_reason",
            "invent_negative_evidence",
            "replace_decision_maker_judgment",
        ),
        required_outputs=(
            "counterargument_map",
            "hidden_risks",
            "assumption_tests",
            "decision_options",
        ),
        risk_notes=("devil_advocate_outputs_are_decision_support_not_final_strategy",),
    ),
)

_ROLE_BY_ID = {role.role_id: role for role in ROLE_REGISTRY}
_REQUIRED_STRING_FIELDS = ("role_id", "display_name", "mission", "default_retriever")
_REQUIRED_TUPLE_FIELDS = (
    "allowed_tasks",
    "prohibited_tasks",
    "required_inputs",
    "required_outputs",
    "allowed_retrievers",
    "source_policy",
    "evidence_policy",
    "compliance_policy",
    "escalation_triggers",
    "validation_gates",
    "output_contract",
    "risk_notes",
)


def list_role_ids() -> tuple[str, ...]:
    return tuple(role.role_id for role in ROLE_REGISTRY)


def list_roles() -> tuple[RoleContract, ...]:
    return ROLE_REGISTRY


def get_role(role_id: str) -> RoleContract | None:
    return _ROLE_BY_ID.get(role_id)


def require_role(role_id: str) -> RoleContract:
    role = get_role(role_id)
    if role is None:
        raise KeyError(f"unknown role_id: {role_id}")
    return role


def validate_role(role: RoleContract) -> tuple[str, ...]:
    errors: list[str] = []

    for field_name in _REQUIRED_STRING_FIELDS:
        if not str(getattr(role, field_name)).strip():
            errors.append(f"{role.role_id}: {field_name} is required")

    for field_name in _REQUIRED_TUPLE_FIELDS:
        value = getattr(role, field_name)
        if not isinstance(value, tuple) or not value or any(not str(item).strip() for item in value):
            errors.append(f"{role.role_id}: {field_name} must be a non-empty tuple of non-empty strings")

    if role.default_retriever != DEFAULT_RETRIEVER:
        errors.append(f"{role.role_id}: default_retriever must be {DEFAULT_RETRIEVER}")

    if role.default_retriever == "hybrid":
        errors.append(f"{role.role_id}: hybrid must not be the default retriever")

    unknown_retrievers = tuple(retriever for retriever in role.allowed_retrievers if retriever not in ALLOWED_RETRIEVERS)
    if unknown_retrievers:
        errors.append(f"{role.role_id}: unknown allowed retrievers: {', '.join(unknown_retrievers)}")

    joined_policy = " ".join((*role.source_policy, *role.compliance_policy, *role.validation_gates)).casefold()
    if "reranker" in joined_policy and RERANKER_POLICY not in role.source_policy:
        errors.append(f"{role.role_id}: reranker policy must remain explicit opt-in")
    if ANTI_OVERCLAIM_BOUNDARY not in role.compliance_policy:
        errors.append(f"{role.role_id}: compliance policy must include anti-overclaim boundary")

    if role.role_id in HIGH_RISK_ROLE_IDS:
        missing_gates = tuple(gate for gate in HUMAN_APPROVAL_GATES if gate not in role.validation_gates)
        if missing_gates:
            errors.append(f"{role.role_id}: missing human approval gates: {', '.join(missing_gates)}")

    return tuple(errors)


def validate_registry() -> tuple[str, ...]:
    errors: list[str] = []
    role_ids = list_role_ids()
    if len(role_ids) != len(set(role_ids)):
        errors.append("role_id values must be unique")
    if set(_ROLE_BY_ID) != set(role_ids):
        errors.append("role lookup map must match role registry")
    for role in ROLE_REGISTRY:
        errors.extend(validate_role(role))
    return tuple(errors)


def role_to_dict(role: RoleContract) -> dict[str, object]:
    data = asdict(role)
    return {key: list(value) if isinstance(value, tuple) else value for key, value in data.items()}


def registry_to_dict() -> dict[str, object]:
    return {
        "registry_name": "asperitas_agent_role_registry",
        "registry_version": "MVP-014-phase-1",
        "default_retriever": DEFAULT_RETRIEVER,
        "allowed_retrievers": list(ALLOWED_RETRIEVERS),
        "non_default_retrievers": list(NON_DEFAULT_RETRIEVERS),
        "hybrid_policy": HYBRID_POLICY,
        "reranker_policy": RERANKER_POLICY,
        "high_risk_role_ids": list(HIGH_RISK_ROLE_IDS),
        "roles": [role_to_dict(role) for role in ROLE_REGISTRY],
    }
