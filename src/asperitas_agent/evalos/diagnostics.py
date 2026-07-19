from __future__ import annotations

from typing import Any

from .contracts import FailureEvidence


LAYER_FIELDS = (
    ("AUTHORITY", "authority_ok"),
    ("CONTEXT", "context_ok"),
    ("RETRIEVAL", "retrieval_ok"),
    ("FRESHNESS", "freshness_ok"),
    ("MODEL", "model_ok"),
    ("TOOL", "tool_ok"),
    ("WORKFLOW_STATE", "workflow_state_ok"),
    ("VERIFICATION", "verification_ok"),
    ("DOMAIN_EVIDENCE", "domain_evidence_ok"),
    ("USER_EXPERIENCE", "user_experience_ok"),
    ("OPERATIONS", "operations_ok"),
)


def diagnose_failure_layer(value: dict[str, Any]) -> dict[str, Any]:
    evidence = FailureEvidence.from_dict(value)
    failed_layers = [
        layer
        for layer, field in LAYER_FIELDS
        if not bool(getattr(evidence, field))
    ]

    if failed_layers:
        controlling_layer = failed_layers[0]
        prompt_change_allowed = False
    elif evidence.expected == evidence.observed:
        controlling_layer = "NO_FAILURE"
        prompt_change_allowed = False
    elif evidence.prompt_reproduced:
        controlling_layer = "PROMPT"
        prompt_change_allowed = True
    else:
        controlling_layer = "SPECIFICATION"
        prompt_change_allowed = False

    return {
        "case_id": evidence.case_id,
        "controlling_layer": controlling_layer,
        "failed_layers": failed_layers,
        "prompt_change_allowed": prompt_change_allowed,
        "rule": (
            "Change prompt text only after non-prompt layers pass and the "
            "failure is reproduced at the prompt layer."
        ),
    }


def diagnose_suite(values: list[dict[str, Any]]) -> dict[str, Any]:
    reports = [diagnose_failure_layer(value) for value in values]
    expected = {
        str(value["case_id"]): str(value["expected_layer"])
        for value in values
    }
    mismatches = [
        report["case_id"]
        for report in reports
        if report["controlling_layer"] != expected[report["case_id"]]
    ]
    return {
        "passed": not mismatches,
        "case_count": len(reports),
        "mismatches": mismatches,
        "reports": reports,
    }
