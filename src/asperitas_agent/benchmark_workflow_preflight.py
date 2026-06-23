from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .benchmark_workflow import (
    APPROVAL_REQUIRED_FLAGS,
    DEFAULT_RETRIEVER,
    HYBRID_POLICY,
    RERANKER_POLICY,
    BenchmarkWorkflowSpec,
)


PREFLIGHT_DECISIONS = ("allowed", "blocked", "requires_human_approval")
ADDITIONAL_APPROVAL_REQUIRED_FLAGS = (
    "CITES",
    "Nagoya",
    "LMO",
    "privacy",
)
PREFLIGHT_APPROVAL_REQUIRED_FLAGS = tuple(
    dict.fromkeys((*APPROVAL_REQUIRED_FLAGS, *ADDITIONAL_APPROVAL_REQUIRED_FLAGS))
)


@dataclass(frozen=True)
class BenchmarkWorkflowPreflightDecision:
    decision: str
    reasons: tuple[str, ...]
    risk_flags: tuple[dict[str, Any], ...]
    validation_errors: tuple[str, ...]
    human_approval_requirements: tuple[dict[str, Any], ...]
    source_metadata: dict[str, str]
    policy_metadata: dict[str, str]
    metrics_metadata: tuple[dict[str, Any], ...]
    executed: bool = False
    ingested: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reasons": list(self.reasons),
            "risk_flags": [dict(flag) for flag in self.risk_flags],
            "validation_errors": list(self.validation_errors),
            "human_approval_requirements": [dict(requirement) for requirement in self.human_approval_requirements],
            "source_metadata": dict(self.source_metadata),
            "policy_metadata": dict(self.policy_metadata),
            "metrics_metadata": [dict(metric) for metric in self.metrics_metadata],
            "executed": self.executed,
            "ingested": self.ingested,
        }


def evaluate_benchmark_workflow_preflight(spec: BenchmarkWorkflowSpec) -> BenchmarkWorkflowPreflightDecision:
    validation_errors = spec.validate()
    risk_flags = tuple(flag.to_dict() for flag in spec.risk_flags)
    human_approval_requirements = _human_approval_requirements(spec)
    source_metadata = {
        "source_path": spec.source_path,
        "source_priority": spec.source_priority,
        "evidence_label": spec.evidence_label,
    }
    policy_metadata = {
        "default_retriever": spec.default_retriever,
        "hybrid_policy": spec.hybrid_policy,
        "reranker_policy": spec.reranker_policy,
    }
    metrics_metadata = tuple(metric.to_dict() for metric in spec.metrics)

    if validation_errors:
        decision = "blocked"
        reasons = ("Benchmark workflow spec failed MVP-015 validation and is blocked fail-closed.",)
    elif human_approval_requirements:
        decision = "requires_human_approval"
        reasons = (
            "Benchmark workflow spec is valid and non-executing, but active risk flags require human approval.",
        )
    else:
        decision = "allowed"
        reasons = (
            "Benchmark workflow spec is valid, non-executing, non-ingesting, and has no active approval-triggering risk flags.",
        )

    return BenchmarkWorkflowPreflightDecision(
        decision=decision,
        reasons=reasons,
        risk_flags=risk_flags,
        validation_errors=validation_errors,
        human_approval_requirements=human_approval_requirements,
        source_metadata=source_metadata,
        policy_metadata=policy_metadata,
        metrics_metadata=metrics_metadata,
        executed=False,
        ingested=False,
    )


def _human_approval_requirements(spec: BenchmarkWorkflowSpec) -> tuple[dict[str, Any], ...]:
    approval_domains = {domain for gate in spec.human_approval_gates for domain in gate.risk_domains}
    requirements: list[dict[str, Any]] = []

    for flag in spec.risk_flags:
        if flag.risk_domain not in PREFLIGHT_APPROVAL_REQUIRED_FLAGS or not _is_active_approval_risk(flag):
            continue
        matching_gates = [
            gate
            for gate in spec.human_approval_gates
            if flag.risk_domain in gate.risk_domains and gate.approval_required
        ]
        requirements.append(
            {
                "risk_domain": flag.risk_domain,
                "severity": flag.severity,
                "rationale": flag.rationale,
                "approval_gate_ids": [gate.gate_id for gate in matching_gates],
                "required_reviewers": [gate.required_reviewer for gate in matching_gates],
                "approval_record_present": flag.risk_domain in approval_domains,
            }
        )

    return tuple(requirements)


def decision_to_dict(decision: BenchmarkWorkflowPreflightDecision) -> dict[str, Any]:
    return decision.to_dict()


def _is_active_approval_risk(flag: Any) -> bool:
    return bool(flag.human_approval_required or flag.severity in ("medium", "high"))
