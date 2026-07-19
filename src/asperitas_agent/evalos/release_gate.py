from __future__ import annotations

import hashlib
import json
from typing import Any

from .contracts import PromptHarnessRelease


def release_hash(value: dict[str, Any]) -> str:
    payload = {
        key: raw
        for key, raw in value.items()
        if key != "release_sha256"
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_release(value: dict[str, Any]) -> dict[str, Any]:
    record = PromptHarnessRelease.from_dict(value)
    errors: list[str] = []

    if record.effect_ceiling not in {"READ", "DRAFT", "NO_EFFECT"}:
        errors.append("EFFECT_CEILING_TOO_HIGH")
    if not record.rollback.strip():
        errors.append("ROLLBACK_MISSING")
    if len(record.context_manifest_sha256) != 64:
        errors.append("CONTEXT_MANIFEST_HASH_INVALID")
    computed = release_hash(value)
    if value.get("release_sha256") != computed:
        errors.append("RELEASE_HASH_MISMATCH")

    return {
        "passed": not errors,
        "errors": errors,
        "computed_sha256": computed,
    }


def decide_release(
    *,
    release_validation: dict[str, Any],
    diagnostics: dict[str, Any],
    context: dict[str, Any],
    candidate_eval: dict[str, Any],
    private_oracle_accessed: bool,
    threshold_changed_after_results: bool,
) -> dict[str, Any]:
    invalid: list[str] = []
    hold: list[str] = []

    if not release_validation["passed"]:
        invalid.append("RELEASE_CONTRACT_INVALID")
    if private_oracle_accessed:
        invalid.append("PRIVATE_ORACLE_ACCESSED")
    if threshold_changed_after_results:
        invalid.append("POST_HOC_THRESHOLD_CHANGE")
    if not diagnostics["passed"]:
        hold.append("FAILURE_LAYER_ROUTING_MISMATCH")
    if not context["passed"]:
        hold.append("CONTEXT_QUALITY_GATE_FAILED")
    if not candidate_eval["passed"]:
        hold.append("CANDIDATE_EVAL_FAILED")

    if invalid:
        return {
            "status": "INVALID",
            "promotion_allowed": False,
            "reasons": invalid + hold,
        }
    if hold:
        return {
            "status": "HOLD",
            "promotion_allowed": False,
            "reasons": hold,
        }
    return {
        "status": "PROMPT_HARNESS_RELEASE_CANDIDATE",
        "promotion_allowed": False,
        "reasons": [
            "public-safe synthetic prompt-harness controls passed",
            "repository regression, exact-head CI, protected holdout, and independent review remain required",
        ],
    }
