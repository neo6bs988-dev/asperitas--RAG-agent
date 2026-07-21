from __future__ import annotations

from typing import Any


def decide_shadow_release(
    *,
    analysis: dict[str, Any],
    policy: dict[str, Any],
    actual_repository_agent_executed: bool,
    exact_repository_head_verified: bool,
    approved_shadow_storage_configured: bool,
) -> dict[str, Any]:
    invalid: list[str] = []
    hold: list[str] = []

    if str(policy["effect_ceiling"]).upper() not in {"NONE", "READ"}:
        invalid.append("EFFECT_CEILING_TOO_HIGH")
    if bool(policy["provider_export_enabled"]):
        invalid.append("PROVIDER_EXPORT_ENABLED")
    if bool(policy["network_egress_enabled"]):
        invalid.append("NETWORK_EGRESS_ENABLED")
    if bool(policy["content_capture_enabled"]):
        invalid.append("RAW_CONTENT_CAPTURE_ENABLED")
    if not analysis["passed"]:
        invalid.append("SHADOW_ANALYSIS_FAILED")
    if not actual_repository_agent_executed:
        hold.append("ACTUAL_REPOSITORY_AGENT_NOT_EXECUTED")
    if not exact_repository_head_verified:
        hold.append("EXACT_REPOSITORY_HEAD_NOT_VERIFIED")
    if not approved_shadow_storage_configured:
        hold.append("APPROVED_SHADOW_STORAGE_NOT_CONFIGURED")

    if invalid:
        return {
            "status": "INVALID",
            "promotion_allowed": False,
            "reasons": invalid + hold,
        }
    if hold:
        return {
            "status": "NO_EFFECT_SHADOW_SPEC_CANDIDATE",
            "promotion_allowed": False,
            "reasons": hold,
        }
    return {
        "status": "NO_EFFECT_SHADOW_READY_FOR_CONTROLLED_RUN",
        "promotion_allowed": False,
        "reasons": [
            "actual repository agent and exact head verified",
            "controlled shadow execution requires separate approval",
        ],
    }
