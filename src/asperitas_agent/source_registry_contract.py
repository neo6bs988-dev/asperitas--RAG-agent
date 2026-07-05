from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT_REQUIRED_FIELDS = {"schema_version", "registry_name", "generated_at", "entries"}
ENTRY_REQUIRED_FIELDS = {
    "source_id",
    "title",
    "path_or_url",
    "priority",
    "source_type",
    "confidentiality",
    "license_status",
    "collection_status",
    "verification_status",
    "registry_status",
    "owner",
    "updated_at",
    "allowed_use",
    "compliance_tags",
    "evidence_span_policy",
    "decision_implication",
    "ingestion_allowed",
    "embedding_allowed",
    "kg_allowed",
    "external_output_allowed",
}

DOWNSTREAM_FLAGS = {
    "ingestion_allowed",
    "embedding_allowed",
    "kg_allowed",
    "external_output_allowed",
}

UNREVIEWED_LICENSE_STATUSES = {"unknown", "pending_review", "blocked"}


class SourceRegistryContractError(ValueError):
    """Raised when a source registry document violates the V11.1 contract."""


def load_source_registry_document(path: Path) -> dict[str, Any]:
    """Load a V11.1 source-registry JSON document."""

    return json.loads(path.read_text(encoding="utf-8"))


def validate_source_registry_document(document: dict[str, Any]) -> list[str]:
    """Return V11.1 contract errors for a source-registry document.

    This validation is intentionally deterministic and standard-library only.
    It does not replace legal, compliance, ingestion, or eval review.
    """

    errors: list[str] = []
    missing_root = ROOT_REQUIRED_FIELDS - set(document)
    for field in sorted(missing_root):
        errors.append(f"missing root field: {field}")

    if document.get("schema_version") != "v11.1":
        errors.append("schema_version must be v11.1")

    entries = document.get("entries")
    if not isinstance(entries, list):
        errors.append("entries must be a list")
        return errors

    seen_source_ids: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entry {index} must be an object")
            continue

        source_id = entry.get("source_id", f"entry_{index}")
        missing_entry = ENTRY_REQUIRED_FIELDS - set(entry)
        for field in sorted(missing_entry):
            errors.append(f"{source_id} missing field: {field}")

        if source_id in seen_source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        seen_source_ids.add(str(source_id))

        if entry.get("registry_status") == "candidate":
            for flag in DOWNSTREAM_FLAGS - {"external_output_allowed"}:
                if entry.get(flag) is not False:
                    errors.append(f"{source_id} candidate must set {flag}=false")

        if entry.get("license_status") in UNREVIEWED_LICENSE_STATUSES:
            if entry.get("embedding_allowed") is not False:
                errors.append(f"{source_id} unreviewed license must set embedding_allowed=false")
            if entry.get("external_output_allowed") is not False:
                errors.append(f"{source_id} unreviewed license must set external_output_allowed=false")

        if entry.get("registry_status") == "ingested":
            evidence = entry.get("evidence")
            if not isinstance(evidence, dict):
                errors.append(f"{source_id} ingested entry requires evidence object")
            else:
                if not evidence.get("ingestion_run_id"):
                    errors.append(f"{source_id} ingested entry requires ingestion_run_id")
                if not evidence.get("decision_log_ref"):
                    errors.append(f"{source_id} ingested entry requires decision_log_ref")

    return errors


def assert_valid_source_registry_document(document: dict[str, Any]) -> None:
    """Raise if the source registry document violates the V11.1 contract."""

    errors = validate_source_registry_document(document)
    if errors:
        raise SourceRegistryContractError("; ".join(errors))
