from __future__ import annotations

import pytest

from asperitas_agent.benchmark_workflow import (
    DEFAULT_RETRIEVER,
    HYBRID_POLICY,
    RERANKER_POLICY,
    BenchmarkDesignObject,
    BenchmarkRiskFlag,
    BenchmarkWorkflowSpec,
    HumanApprovalGate,
    HypothesisLog,
    MetricObject,
    RunResultMetadata,
    ValidationGate,
    WorkflowTranslationBoundary,
)


SOURCE_PATH = (
    "01_RAW_SOURCES/P5_INDUSTRY_INTELLIGENCE/"
    "Gingko bio \uc624\ud508ai \ud65c\uc6a9\ud55c software \uac1c\ubc1cprocess.pdf"
)


def valid_spec(**overrides):
    risk_flags = (
        BenchmarkRiskFlag("wet_lab", "high", "Source benchmark discusses wet-lab-linked autonomous lab work."),
        BenchmarkRiskFlag("biosafety", "high", "Biological workflow claims require biosafety review."),
        BenchmarkRiskFlag("legal_ip", "medium", "Benchmark source licensing and IP use need review."),
        BenchmarkRiskFlag("financial_investor", "medium", "Benchmark performance must not be investor-facing traction."),
        BenchmarkRiskFlag("confidential_source", "medium", "Internal use requires source disclosure boundaries."),
    )
    approval_gates = (
        HumanApprovalGate("wet-lab-review", ("wet_lab", "biosafety"), "qualified_biosafety_reviewer"),
        HumanApprovalGate("legal-ip-review", ("legal_ip",), "legal_or_ip_reviewer"),
        HumanApprovalGate("investor-review", ("financial_investor",), "human_business_reviewer"),
        HumanApprovalGate("confidential-source-review", ("confidential_source",), "source_governance_reviewer"),
    )
    kwargs = {
        "workflow_id": "mvp015-ginkgo-benchmark-workflow",
        "title": "Ginkgo/OpenAI software-process benchmark workflow",
        "source_path": SOURCE_PATH,
        "source_priority": "P5",
        "evidence_label": "Industry Signal",
        "allowed_use_cases": ("benchmarking", "agent_development", "operations", "compliance"),
        "prohibited_use_cases": (
            "wet_lab_execution",
            "protocol_automation",
            "cloud_lab_connection",
            "lims_eln_robotics_integration",
            "external_execution_system",
            "autonomous_wet_lab_claim",
            "production_hybrid_claim",
        ),
        "design_object": BenchmarkDesignObject(
            design_id="schema-first-design-object",
            objective="Represent the benchmark as a non-executable software workflow contract.",
            parameters={"pattern": "schema-first-validation"},
        ),
        "validation_gates": (
            ValidationGate("source-metadata-required", "Require source path, priority, and evidence label."),
            ValidationGate("no-execution", "Block wet-lab or external execution intent."),
        ),
        "translation_boundary": WorkflowTranslationBoundary(
            boundary_id="descriptive-translation-boundary",
            description="Describe AI-design-to-workflow-spec translation without executable adapters.",
            source_format="benchmark_design_object",
            target_format="workflow_specification_description",
        ),
        "metrics": (
            MetricObject(
                metric_id="benchmark-specific-cost",
                name="specific cost",
                benchmark_value="reported by source, not Asperitas",
                unit="source_context_only",
                source_context="Ginkgo/OpenAI paper benchmark metric",
            ),
        ),
        "run_result_metadata": RunResultMetadata(
            run_id="mvp015-read-only-contract",
            result_summary="No run performed; metadata shape only.",
            captured_fields=("source_path", "source_priority", "evidence_label", "risk_flags"),
        ),
        "hypothesis_logs": (
            HypothesisLog(
                hypothesis_id="workflow-pattern-hypothesis",
                claim="Schema-first validation may improve Asperitas agent workflow governance.",
                evidence_label="Inference",
                confidence="medium",
            ),
        ),
        "human_approval_gates": approval_gates,
        "risk_flags": risk_flags,
    }
    return BenchmarkWorkflowSpec(**{**kwargs, **overrides})


def test_valid_benchmark_workflow_spec_passes_validation():
    spec = valid_spec()

    assert spec.validate() == ()
    spec.require_valid()


def test_missing_source_or_evidence_metadata_fails_closed():
    missing_source = valid_spec(source_path="")
    missing_evidence = valid_spec(evidence_label="")

    assert "source_path is required" in missing_source.validate()
    assert any("evidence_label" in error for error in missing_evidence.validate())
    with pytest.raises(ValueError, match="source_path is required"):
        missing_source.require_valid()


def test_wet_lab_execution_intent_is_rejected():
    spec = valid_spec(
        design_object=BenchmarkDesignObject(
            design_id="unsafe-design",
            objective="Try to execute a wet-lab benchmark.",
            execution_intent="wet_lab_execution",
            wet_lab_execution_requested=True,
        )
    )

    errors = spec.validate()

    assert any("benchmark_analysis_only" in error for error in errors)
    assert any("wet-lab execution intent is prohibited" in error for error in errors)


def test_cloud_lab_lims_robotics_and_external_execution_targets_are_prohibited():
    spec = valid_spec(
        translation_boundary=WorkflowTranslationBoundary(
            boundary_id="unsafe-boundary",
            description="Attempt to map to external execution targets.",
            source_format="benchmark_design_object",
            target_format="robot_protocol",
            external_targets=("cloud_lab", "lims", "robotics", "external_execution_system"),
        )
    )

    errors = spec.validate()

    assert any("external execution targets are prohibited" in error for error in errors)


def test_benchmark_metrics_cannot_be_represented_as_asperitas_performance():
    spec = valid_spec(
        metrics=(
            MetricObject(
                metric_id="unsafe-metric",
                name="cost reduction",
                benchmark_value="40%",
                unit="percent",
                source_context="Ginkgo/OpenAI source metric",
                represents_asperitas_performance=True,
            ),
        )
    )

    assert any("must not represent Asperitas performance" in error for error in spec.validate())


def test_workflow_translation_boundary_is_descriptive_only_not_executable():
    spec = valid_spec(
        translation_boundary=WorkflowTranslationBoundary(
            boundary_id="executable-boundary",
            description="Unsafe executable boundary.",
            source_format="design",
            target_format="protocol",
            descriptive_only=False,
            executable=True,
        )
    )

    errors = spec.validate()

    assert any("descriptive only" in error for error in errors)
    assert any("must not be executable" in error for error in errors)


@pytest.mark.parametrize("risk_domain", ["wet_lab", "legal_ip", "financial_investor", "biosafety", "confidential_source"])
def test_human_approval_gate_required_for_high_risk_domains(risk_domain):
    spec = valid_spec(
        risk_flags=(BenchmarkRiskFlag(risk_domain, "high", "High-risk benchmark use case."),),
        human_approval_gates=(),
    )

    errors = spec.validate()

    assert any(f"missing human approval gates for: {risk_domain}" in error for error in errors)


def test_retriever_hybrid_and_reranker_defaults_are_not_changed_or_implied():
    spec = valid_spec()

    assert spec.default_retriever == DEFAULT_RETRIEVER == "mvp003"
    assert spec.hybrid_policy == HYBRID_POLICY == "explicit_manual_experimental_only"
    assert spec.reranker_policy == RERANKER_POLICY == "deterministic_test_explicit_opt_in_non_default"

    unsafe = valid_spec(
        default_retriever="hybrid",
        hybrid_policy="production_default",
        reranker_policy="default_enabled",
    )
    errors = unsafe.validate()

    assert "default retriever must remain mvp003" in errors
    assert "hybrid policy must remain explicit/manual/experimental only" in errors
    assert "deterministic-test reranker must remain explicit opt-in/non-default" in errors


def test_autonomous_wet_lab_claim_is_prohibited():
    spec = valid_spec(autonomous_wet_lab_claim=True)

    assert "autonomous wet-lab claim is prohibited" in spec.validate()
