from __future__ import annotations

from dataclasses import dataclass


REGISTRY_STATUSES = {
    "candidate",
    "needs_review",
    "approved",
    "ingested",
    "blocked",
    "archived",
}

ALLOWED_TRANSITIONS = {
    "candidate": {"needs_review", "blocked", "archived"},
    "needs_review": {"approved", "blocked", "archived"},
    "approved": {"ingested", "blocked", "archived"},
    "ingested": {"archived"},
    "blocked": {"archived"},
    "archived": set(),
}


@dataclass(frozen=True)
class TransitionEvidence:
    owner: str = ""
    decision_log_ref: str = ""
    ingestion_run_id: str = ""
    reason: str = ""


@dataclass(frozen=True)
class TransitionDecision:
    allowed: bool
    errors: tuple[str, ...]


def validate_registry_status_transition(
    current_status: str,
    next_status: str,
    evidence: TransitionEvidence | None = None,
) -> TransitionDecision:
    """Validate a V11.1 source-registry status transition.

    This is a deterministic gate. It does not ingest sources, modify files,
    create embeddings, or approve legal/commercial use.
    """

    evidence = evidence or TransitionEvidence()
    errors: list[str] = []

    if current_status not in REGISTRY_STATUSES:
        errors.append(f"unknown current_status: {current_status}")
    if next_status not in REGISTRY_STATUSES:
        errors.append(f"unknown next_status: {next_status}")
    if errors:
        return TransitionDecision(False, tuple(errors))

    if next_status not in ALLOWED_TRANSITIONS[current_status]:
        errors.append(f"transition not allowed: {current_status} -> {next_status}")

    if next_status == "ingested":
        if not evidence.ingestion_run_id:
            errors.append("ingested transition requires ingestion_run_id")
        if not evidence.decision_log_ref:
            errors.append("ingested transition requires decision_log_ref")

    if next_status in {"approved", "blocked", "archived"} and not evidence.owner:
        errors.append(f"{next_status} transition requires owner")

    if next_status == "blocked" and not evidence.reason:
        errors.append("blocked transition requires reason")

    return TransitionDecision(not errors, tuple(errors))
