from asperitas_agent.source_registry_transitions import (
    TransitionEvidence,
    validate_registry_status_transition,
)


def test_candidate_can_move_to_review() -> None:
    decision = validate_registry_status_transition("candidate", "needs_review")
    assert decision.allowed
    assert decision.errors == ()


def test_candidate_cannot_jump_to_ingested() -> None:
    decision = validate_registry_status_transition(
        "candidate",
        "ingested",
        TransitionEvidence(ingestion_run_id="run-1", decision_log_ref="log-1"),
    )
    assert not decision.allowed
    assert "transition not allowed: candidate -> ingested" in decision.errors


def test_ingested_requires_run_and_decision_evidence() -> None:
    decision = validate_registry_status_transition("approved", "ingested")
    assert not decision.allowed
    assert "ingested transition requires ingestion_run_id" in decision.errors
    assert "ingested transition requires decision_log_ref" in decision.errors


def test_approved_can_move_to_ingested_with_evidence() -> None:
    decision = validate_registry_status_transition(
        "approved",
        "ingested",
        TransitionEvidence(ingestion_run_id="run-1", decision_log_ref="log-1"),
    )
    assert decision.allowed
    assert decision.errors == ()


def test_blocked_transition_requires_owner_and_reason() -> None:
    decision = validate_registry_status_transition("needs_review", "blocked")
    assert not decision.allowed
    assert "blocked transition requires owner" in decision.errors
    assert "blocked transition requires reason" in decision.errors
