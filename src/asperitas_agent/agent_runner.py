from __future__ import annotations

from pathlib import Path
from typing import Any

from .answer_generation import generate_grounded_answer
from .answer_verification_integration import ANSWER_VERIFICATION_METADATA_KEY, expose_answer_verification_metadata
from .chunking import read_chunks
from .claim_verifier_schema import AnswerVerificationSummary
from .evidence_pack import build_evidence_pack
from .guardrails import evaluate_evidence_guardrail
from .registry import read_registry
from .retrieval_mvp003 import search_chunks_mvp003
from .runtime_verifier import build_runtime_answer_verification_summary
from .schemas import AgentResponse, Chunk, GroundedAnswer, SourceRecord


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "source_registry.csv"
DEFAULT_CHUNKS_PATH = REPO_ROOT / "data" / "chunks.jsonl"
RUNNER_NAME = "local-deterministic-agent-runner"
RUNNER_VERSION = "MVP-008"


def _validate_inputs(query: str, top_k: int) -> str:
    clean_query = (query or "").strip()
    if not clean_query:
        raise ValueError("query must not be empty")
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer")
    return clean_query


def _load_records_and_chunks(
    registry_path: Path | None,
    chunks_path: Path | None,
    records: list[SourceRecord] | None,
    chunks: list[Chunk] | None,
) -> tuple[list[SourceRecord], list[Chunk]]:
    loaded_records = records if records is not None else read_registry(registry_path or DEFAULT_REGISTRY_PATH)
    loaded_chunks = chunks if chunks is not None else read_chunks(chunks_path or DEFAULT_CHUNKS_PATH)
    return loaded_records, loaded_chunks


def _response_metadata(
    *,
    answer: GroundedAnswer,
    citation_subset_ok: bool,
    evidence_keys: set[str],
    retriever_metadata: dict[str, Any],
    answer_verification_summary: AnswerVerificationSummary | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "runner_name": RUNNER_NAME,
        "runner_version": RUNNER_VERSION,
        "deterministic": True,
        "citation_integrity": {
            "citations_subset_of_evidence": citation_subset_ok,
            "evidence_citation_keys": sorted(evidence_keys),
        },
        "retriever": dict(retriever_metadata),
        "answer_generation": answer.metadata.to_json(),
        "limitations": list(answer.limitations),
    }
    if answer_verification_summary is None:
        return metadata

    enriched_answer = expose_answer_verification_metadata(answer, answer_verification_summary)
    verification_metadata = enriched_answer["metadata"].get(ANSWER_VERIFICATION_METADATA_KEY)
    if verification_metadata is not None:
        metadata[ANSWER_VERIFICATION_METADATA_KEY] = verification_metadata
    return metadata


def ask_agent(
    query: str,
    top_k: int = 5,
    registry_path: Path | None = None,
    chunks_path: Path | None = None,
    records: list[SourceRecord] | None = None,
    chunks: list[Chunk] | None = None,
    answer_verification_summary: AnswerVerificationSummary | None = None,
    runtime_verifier_enabled: bool = False,
) -> AgentResponse:
    clean_query = _validate_inputs(query, top_k)
    loaded_records, loaded_chunks = _load_records_and_chunks(registry_path, chunks_path, records, chunks)
    retrieved = search_chunks_mvp003(clean_query, loaded_chunks, loaded_records, limit=top_k, include_explanations=True)
    pack = build_evidence_pack(clean_query, retrieved, top_k=top_k)
    decision = evaluate_evidence_guardrail(pack)
    answer = generate_grounded_answer(pack, decision)

    evidence = [item.to_json() for item in pack.evidence_items]
    evidence_keys = {item["citation_key"] for item in evidence if item.get("citation_key")}
    citation_subset_ok = set(answer.citations_used) <= evidence_keys
    if not citation_subset_ok:
        raise RuntimeError("generated answer used citations not present in the evidence pack")

    verification_summary = answer_verification_summary
    if runtime_verifier_enabled:
        verification_summary = build_runtime_answer_verification_summary(
            question=clean_query,
            answer=answer,
            evidence_items=pack.evidence_items,
            enabled=True,
            caller_supplied_summary=answer_verification_summary,
        )

    return AgentResponse(
        query=clean_query,
        top_k=top_k,
        status=answer.answer_status,
        answer=answer.answer_text,
        citations_used=list(answer.citations_used),
        evidence_count=len(pack.evidence_items),
        evidence=evidence,
        guardrail=decision.to_json(),
        metadata=_response_metadata(
            answer=answer,
            citation_subset_ok=citation_subset_ok,
            evidence_keys=evidence_keys,
            retriever_metadata=pack.retriever.to_json(),
            answer_verification_summary=verification_summary,
        ),
    )
