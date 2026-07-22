from __future__ import annotations

from dataclasses import dataclass
from typing import Any


FAILURE_LAYERS = {
    "SPECIFICATION",
    "AUTHORITY",
    "CONTEXT",
    "RETRIEVAL",
    "FRESHNESS",
    "MODEL",
    "TOOL",
    "WORKFLOW_STATE",
    "VERIFICATION",
    "DOMAIN_EVIDENCE",
    "USER_EXPERIENCE",
    "OPERATIONS",
    "PROMPT",
}


@dataclass(frozen=True)
class PromptHarnessRelease:
    release_id: str
    model: str
    reasoning_configuration: str
    instruction_version: str
    context_manifest_sha256: str
    tool_schema_version: str
    permission_profile: str
    workflow_version: str
    output_contract_version: str
    verification_version: str
    rollback: str
    effect_ceiling: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PromptHarnessRelease":
        return cls(
            release_id=str(value["release_id"]),
            model=str(value["model"]),
            reasoning_configuration=str(value["reasoning_configuration"]),
            instruction_version=str(value["instruction_version"]),
            context_manifest_sha256=str(value["context_manifest_sha256"]),
            tool_schema_version=str(value["tool_schema_version"]),
            permission_profile=str(value["permission_profile"]),
            workflow_version=str(value["workflow_version"]),
            output_contract_version=str(value["output_contract_version"]),
            verification_version=str(value["verification_version"]),
            rollback=str(value["rollback"]),
            effect_ceiling=str(value["effect_ceiling"]),
        )


@dataclass(frozen=True)
class FailureEvidence:
    case_id: str
    expected: str
    observed: str
    prompt_reproduced: bool
    authority_ok: bool
    context_ok: bool
    retrieval_ok: bool
    freshness_ok: bool
    model_ok: bool
    tool_ok: bool
    workflow_state_ok: bool
    verification_ok: bool
    domain_evidence_ok: bool
    user_experience_ok: bool
    operations_ok: bool

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "FailureEvidence":
        return cls(
            case_id=str(value["case_id"]),
            expected=str(value["expected"]),
            observed=str(value["observed"]),
            prompt_reproduced=bool(value["prompt_reproduced"]),
            authority_ok=bool(value["authority_ok"]),
            context_ok=bool(value["context_ok"]),
            retrieval_ok=bool(value["retrieval_ok"]),
            freshness_ok=bool(value["freshness_ok"]),
            model_ok=bool(value["model_ok"]),
            tool_ok=bool(value["tool_ok"]),
            workflow_state_ok=bool(value["workflow_state_ok"]),
            verification_ok=bool(value["verification_ok"]),
            domain_evidence_ok=bool(value["domain_evidence_ok"]),
            user_experience_ok=bool(value["user_experience_ok"]),
            operations_ok=bool(value["operations_ok"]),
        )
