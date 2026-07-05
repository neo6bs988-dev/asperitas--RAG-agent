from pathlib import Path

import pytest

from asperitas_agent.source_registry_contract import (
    SourceRegistryContractError,
    assert_valid_source_registry_document,
    load_source_registry_document,
    validate_source_registry_document,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = ROOT / "02_SOURCE_REGISTRY" / "source_registry.example.json"


def test_example_registry_document_passes_contract_validation() -> None:
    document = load_source_registry_document(EXAMPLE_PATH)
    assert validate_source_registry_document(document) == []


def test_duplicate_source_id_is_rejected() -> None:
    document = load_source_registry_document(EXAMPLE_PATH)
    duplicate = dict(document["entries"][0])
    document["entries"].append(duplicate)

    errors = validate_source_registry_document(document)

    assert any(error.startswith("duplicate source_id:") for error in errors)


def test_candidate_downstream_use_violation_is_rejected() -> None:
    document = load_source_registry_document(EXAMPLE_PATH)
    candidate = next(entry for entry in document["entries"] if entry["registry_status"] == "candidate")
    candidate["embedding_allowed"] = True

    errors = validate_source_registry_document(document)

    assert any("candidate must set embedding_allowed=false" in error for error in errors)


def test_unreviewed_license_external_output_violation_is_rejected() -> None:
    document = load_source_registry_document(EXAMPLE_PATH)
    candidate = next(entry for entry in document["entries"] if entry["license_status"] == "pending_review")
    candidate["external_output_allowed"] = True

    errors = validate_source_registry_document(document)

    assert any("unreviewed license must set external_output_allowed=false" in error for error in errors)


def test_assert_valid_raises_on_invalid_document() -> None:
    with pytest.raises(SourceRegistryContractError):
        assert_valid_source_registry_document({"schema_version": "v11.1", "entries": "not-list"})
