from __future__ import annotations

import re
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable

from .schemas import (
    AbstentionDecision,
    EvidenceItem,
    EvidencePack,
    EvidenceRiskFlags,
    RetrieverMetadata,
    SourceCoverageSummary,
)


DEFAULT_RETRIEVER_NAME = "mvp003-deterministic-metadata"
DEFAULT_RETRIEVER_VERSION = "MVP-003"
DEFAULT_SNIPPET_CHARS = 700
WEAK_SECTION_COVERAGE_THRESHOLD = 0.5


def _compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def make_text_excerpt(text: str, max_chars: int = DEFAULT_SNIPPET_CHARS) -> str:
    compact = _compact_text(text)
    if max_chars <= 0:
        return ""
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3].rstrip() + "..."


def _to_mapping(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return dict(result)
    if hasattr(result, "to_json"):
        payload = result.to_json()
        if isinstance(payload, dict):
            return dict(payload)
    if is_dataclass(result):
        return asdict(result)
    payload: dict[str, Any] = {}
    for key in ("query", "score", "source_file", "source_path"):
        if hasattr(result, key):
            payload[key] = getattr(result, key)
    chunk = getattr(result, "chunk", None)
    if chunk is not None:
        payload.update(
            {
                "chunk_id": getattr(chunk, "chunk_id", ""),
                "source_id": getattr(chunk, "source_id", ""),
                "title": getattr(chunk, "title", ""),
                "source_priority": getattr(chunk, "source_priority", ""),
                "evidence_label": getattr(chunk, "evidence_label", ""),
                "section": getattr(chunk, "section", ""),
                "section_heading": getattr(chunk, "section_heading", ""),
                "section_path": getattr(chunk, "section_path", []),
                "section_level": getattr(chunk, "section_level", None),
                "parent_section": getattr(chunk, "parent_section", ""),
                "subsection": getattr(chunk, "subsection", ""),
                "text": getattr(chunk, "text", ""),
            }
        )
    return payload


def _source_path(payload: dict[str, Any]) -> str:
    return str(payload.get("source_path") or payload.get("source_file") or "")


def _source_title(payload: dict[str, Any]) -> str:
    return str(payload.get("source_title") or payload.get("title") or "")


def _section_path(payload: dict[str, Any]) -> list[str]:
    value = payload.get("section_path", [])
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


def _has_section_metadata(item: EvidenceItem) -> bool:
    return bool(item.section or item.section_heading or item.section_path)


def build_evidence_items(results: Iterable[Any], top_k: int, snippet_chars: int = DEFAULT_SNIPPET_CHARS) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for rank, result in enumerate(list(results)[: max(top_k, 0)], start=1):
        payload = _to_mapping(result)
        items.append(
            EvidenceItem(
                rank=rank,
                chunk_id=str(payload.get("chunk_id") or ""),
                score=round(float(payload.get("score") or 0.0), 6),
                source_id=str(payload.get("source_id") or ""),
                source_title=_source_title(payload),
                source_path=_source_path(payload),
                source_priority=str(payload.get("source_priority") or ""),
                evidence_label=str(payload.get("evidence_label") or ""),
                section=str(payload.get("section") or ""),
                section_heading=str(payload.get("section_heading") or ""),
                section_path=_section_path(payload),
                section_level=payload.get("section_level") if isinstance(payload.get("section_level"), int) else None,
                parent_section=str(payload.get("parent_section") or ""),
                subsection=str(payload.get("subsection") or ""),
                text_excerpt=make_text_excerpt(str(payload.get("text") or ""), snippet_chars),
                citation_key=f"[E{rank}]",
            )
        )
    return items


def build_source_coverage_summary(items: list[EvidenceItem]) -> SourceCoverageSummary:
    unique_source_ids = {item.source_id or item.source_path for item in items if item.source_id or item.source_path}
    priorities = sorted({item.source_priority for item in items if item.source_priority})
    labels = sorted({item.evidence_label for item in items if item.evidence_label})
    section_paths = sorted({" > ".join(item.section_path) for item in items if item.section_path})
    return SourceCoverageSummary(
        unique_source_count=len(unique_source_ids),
        source_priorities_present=priorities,
        evidence_labels_present=labels,
        section_paths_present=section_paths,
        missing_section_metadata_count=sum(1 for item in items if not _has_section_metadata(item)),
        missing_source_priority_count=sum(1 for item in items if not item.source_priority),
        missing_evidence_label_count=sum(1 for item in items if not item.evidence_label),
    )


def build_risk_flags(items: list[EvidenceItem], summary: SourceCoverageSummary) -> EvidenceRiskFlags:
    total = len(items)
    section_coverage = 0.0 if total == 0 else (total - summary.missing_section_metadata_count) / total
    return EvidenceRiskFlags(
        no_evidence_found=total == 0,
        low_source_diversity=total >= 2 and summary.unique_source_count < 2,
        missing_source_priority=summary.missing_source_priority_count > 0,
        missing_evidence_label=summary.missing_evidence_label_count > 0,
        missing_section_metadata=summary.missing_section_metadata_count > 0,
        weak_section_coverage=total > 0 and section_coverage < WEAK_SECTION_COVERAGE_THRESHOLD,
    )


def build_abstention_decision(flags: EvidenceRiskFlags, summary: SourceCoverageSummary, item_count: int) -> AbstentionDecision:
    reasons: list[str] = []
    if flags.no_evidence_found:
        reasons.append("No retrieved evidence was available.")
    if item_count > 0 and summary.missing_source_priority_count == item_count:
        reasons.append("All evidence items are missing source priority metadata.")
    if item_count > 0 and summary.missing_evidence_label_count == item_count:
        reasons.append("All evidence items are missing evidence labels.")
    if flags.weak_section_coverage and flags.low_source_diversity:
        reasons.append("Evidence has weak section coverage and low source diversity.")
    return AbstentionDecision(should_abstain=bool(reasons), reasons=reasons)


def build_context_block(items: list[EvidenceItem]) -> str:
    blocks: list[str] = []
    for item in items:
        section = item.section_heading or item.section or (" > ".join(item.section_path) if item.section_path else "n/a")
        source = item.source_title or item.source_id or item.source_path or "unknown source"
        blocks.append(
            "\n".join(
                [
                    f"{item.citation_key} Source: {source}",
                    f"{item.citation_key} Path: {item.source_path or 'n/a'}",
                    f"{item.citation_key} Priority: {item.source_priority or 'n/a'} | Evidence: {item.evidence_label or 'n/a'}",
                    f"{item.citation_key} Section: {section}",
                    f"{item.citation_key} Excerpt: {item.text_excerpt}",
                ]
            )
        )
    return "\n\n".join(blocks)


def build_evidence_pack(
    query: str,
    retrieval_results: Iterable[Any],
    top_k: int = 5,
    retriever_name: str = DEFAULT_RETRIEVER_NAME,
    retriever_version: str = DEFAULT_RETRIEVER_VERSION,
    snippet_chars: int = DEFAULT_SNIPPET_CHARS,
) -> EvidencePack:
    items = build_evidence_items(retrieval_results, top_k=top_k, snippet_chars=snippet_chars)
    summary = build_source_coverage_summary(items)
    flags = build_risk_flags(items, summary)
    abstention = build_abstention_decision(flags, summary, len(items))
    return EvidencePack(
        query=query,
        retriever=RetrieverMetadata(retriever_name=retriever_name, retriever_version=retriever_version, top_k=top_k),
        evidence_items=items,
        source_coverage_summary=summary,
        risk_flags=flags,
        abstention=abstention,
        context_block=build_context_block(items),
    )
