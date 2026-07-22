from __future__ import annotations

from collections import Counter
from typing import Any


AUTHORITY_RANK = {
    "SYSTEM": 0,
    "DEVELOPER": 1,
    "PROJECT": 2,
    "USER": 3,
    "RUNTIME_EVIDENCE": 4,
    "APPROVED_RECORD": 5,
    "OFFICIAL_PRIMARY": 6,
    "INTERNAL_DOCTRINE": 7,
    "EXTERNAL_CLAIM": 8,
    "UNTRUSTED_CONTENT": 9,
}


def evaluate_context(
    items: list[dict[str, Any]],
    *,
    token_budget: int,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    seen_hashes: set[str] = set()
    active_ids: set[str] = set()
    token_total = 0
    authority_counts: Counter[str] = Counter()

    for item in items:
        item_id = str(item["item_id"])
        status = str(item["lifecycle"]).upper()
        content_hash = str(item["sha256"])
        authority = str(item["authority_class"]).upper()
        tokens = int(item["estimated_tokens"])
        token_total += tokens
        authority_counts[authority] += 1

        if status == "ACTIVE":
            active_ids.add(item_id)
        if content_hash in seen_hashes:
            errors.append(f"DUPLICATE_CONTENT:{item_id}")
        seen_hashes.add(content_hash)

        if status in {"SUPERSEDED", "ARCHIVED", "BLOCKED"} and bool(
            item.get("included", False)
        ):
            errors.append(f"INACTIVE_INCLUDED:{item_id}")

        if bool(item.get("contains_instructions", False)) and authority in {
            "EXTERNAL_CLAIM",
            "UNTRUSTED_CONTENT",
        }:
            if not bool(item.get("instruction_isolation", False)):
                errors.append(f"UNTRUSTED_INSTRUCTION_NOT_ISOLATED:{item_id}")

        if bool(item.get("volatile", False)) and not item.get("as_of"):
            errors.append(f"MISSING_FRESHNESS:{item_id}")

        if authority not in AUTHORITY_RANK:
            errors.append(f"UNKNOWN_AUTHORITY:{item_id}")

        if bool(item.get("included", False)) and not bool(
            item.get("task_relevant", False)
        ):
            warnings.append(f"IRRELEVANT_INCLUDED:{item_id}")

    if token_total > token_budget:
        errors.append("TOKEN_BUDGET_EXCEEDED")

    required_roles = {
        str(item["required_role"])
        for item in items
        if item.get("required_role")
    }
    present_roles = {
        str(item["required_role"])
        for item in items
        if item.get("required_role") and bool(item.get("included", False))
    }
    missing_roles = sorted(required_roles - present_roles)
    if missing_roles:
        errors.append("MISSING_REQUIRED_ROLE:" + ",".join(missing_roles))

    return {
        "passed": not errors,
        "errors": sorted(errors),
        "warnings": sorted(warnings),
        "token_total": token_total,
        "token_budget": token_budget,
        "active_item_count": len(active_ids),
        "authority_counts": dict(sorted(authority_counts.items())),
    }
