from __future__ import annotations

import pytest

from asperitas_agent.benchmark_workflow import (
    DEFAULT_RETRIEVER,
    HYBRID_POLICY,
    RERANKER_POLICY,
    BenchmarkDesignObject,
    BenchmarkRiskFlag,
    HumanApprovalGate,
    MetricObject,
    WorkflowTranslationBoundary,
)
from asperitas_agent.benchmark_workflow_preflight import evaluate_benchmark_workflow_preflight
from test_benchmark_workflow import valid_spec


def low_risk_spec(**overrides):
    return valid_spec(
        risk_flags=(BenchmarkRiskFlag("CITES", "low", "Low-risk source-governance note.", False),),
        human_approval_gates=(HumanApprovalGate("source-review", ("CITES",), "source_governance_reviewer"),),
        **overrides,
    )


def test_valid_low_risk_non_executing_spec_returns_allowed():
    decision = evaluate_benchmark_workflow_preflight(low_risk_spec()).to_dict()

    assert decision["decision"] == "allowed"
    assert decision["validation_errors"] == []
    assert decision["human_approval_requirements"] == []
    assert decision["executed"] is False
    assert decision["ingested"] is False


def test_valid_high_risk_benchmark_spec_requires_human_approval():
    decision = evaluate_benchmark_workflow_preflight(valid_spec()).to_dict()

    assert decision["decision"] == "requires_human_approval"
    domains = {requirement["risk_domain"] for requirement in decision["human_approval_requirements"]}
    assert {"wet_lab", "biosafety", "legal_ip", "financial_investor", "confidential_source"} <= domains
    assert decision["validation_errors"] == []


def test_wet_lab_execution_intent_returns_blocked():
    spec = valid_spec(
        design_object=BenchmarkDesignObject(
            design_id="unsafe-design",
            objective="Execute benchmark as wet-lab work.",
            execution_intent="wet_lab_execution",
            wet_lab_execution_requested=True,
        )
    )

    decision = evaluate_benchmark_workflow_preflight(spec).to_dict()

    assert decision["decision"] == "blocked"
    assert any("wet-lab execution intent is prohibited" in error for error in decision["validation_errors"])


def test_external_execution_target_returns_blocked():
    spec = valid_spec(
        translation_boundary=WorkflowTranslationBoundary(
            boundary_id="unsafe-external-target",
            description="Map to an external execution target.",
            source_format="benchmark_design_object",
            target_format="robot_protocol",
            external_targets=("cloud_lab",),
        )
    )

    decision = evaluate_benchmark_workflow_preflight(spec).to_dict()

    assert decision["decision"] == "blocked"
    assert any("external execution targets are prohibited" in error for error in decision["validation_errors"])


def test_benchmark_metric_as_asperitas_performance_returns_blocked():
    spec = valid_spec(
        metrics=(
            MetricObject(
                metric_id="unsafe-performance-metric",
                name="benchmark cost reduction",
                benchmark_value="40%",
                unit="percent",
                source_context="Ginkgo/OpenAI source metric",
                represents_asperitas_performance=True,
            ),
        )
    )

    decision = evaluate_benchmark_workflow_preflight(spec).to_dict()

    assert decision["decision"] == "blocked"
    assert any("benchmark metrics must not represent Asperitas performance" in error for error in decision["validation_errors"])


def test_changed_retriever_hybrid_or_reranker_policy_returns_blocked():
    spec = valid_spec(
        default_retriever="hybrid",
        hybrid_policy="production_default",
        reranker_policy="default_enabled",
    )

    decision = evaluate_benchmark_workflow_preflight(spec).to_dict()

    assert decision["decision"] == "blocked"
    assert "default retriever must remain mvp003" in decision["validation_errors"]
    assert "hybrid policy must remain explicit/manual/experimental only" in decision["validation_errors"]
    assert "deterministic-test reranker must remain explicit opt-in/non-default" in decision["validation_errors"]


@pytest.mark.parametrize("risk_domain", ["CITES", "Nagoya", "LMO"])
def test_cites_nagoya_lmo_active_flags_require_human_approval(risk_domain):
    spec = valid_spec(
        risk_flags=(BenchmarkRiskFlag(risk_domain, "medium", f"{risk_domain} source-governance risk."),),
        human_approval_gates=(HumanApprovalGate(f"{risk_domain.lower()}-review", (risk_domain,), "compliance_reviewer"),),
    )

    decision = evaluate_benchmark_workflow_preflight(spec).to_dict()

    assert decision["decision"] == "requires_human_approval"
    assert decision["human_approval_requirements"][0]["risk_domain"] == risk_domain
    assert decision["human_approval_requirements"][0]["approval_record_present"] is True


def test_decision_output_preserves_source_risk_metric_and_policy_metadata():
    decision = evaluate_benchmark_workflow_preflight(valid_spec()).to_dict()

    assert decision["source_metadata"] == {
        "source_path": valid_spec().source_path,
        "source_priority": "P5",
        "evidence_label": "Industry Signal",
    }
    assert decision["policy_metadata"] == {
        "default_retriever": DEFAULT_RETRIEVER,
        "hybrid_policy": HYBRID_POLICY,
        "reranker_policy": RERANKER_POLICY,
    }
    assert decision["risk_flags"][0]["risk_domain"] == "wet_lab"
    assert decision["metrics_metadata"][0]["metric_id"] == "benchmark-specific-cost"
    assert decision["metrics_metadata"][0]["source_context"] == "Ginkgo/OpenAI paper benchmark metric"


def test_decision_output_always_reports_no_execution_or_ingestion_when_blocked():
    spec = valid_spec(
        design_object=BenchmarkDesignObject(
            design_id="unsafe-design",
            objective="Execute benchmark.",
            execution_intent="wet_lab_execution",
            wet_lab_execution_requested=True,
        )
    )

    decision = evaluate_benchmark_workflow_preflight(spec).to_dict()

    assert decision["decision"] == "blocked"
    assert decision["executed"] is False
    assert decision["ingested"] is False
