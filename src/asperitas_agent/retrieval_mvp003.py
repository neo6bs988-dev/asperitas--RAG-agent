from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from .chunking import evidence_label_for_priority
from .registry import read_registry
from .retrieval_normalization import (
    expand_query_aliases,
    normalize_text_for_retrieval,
    normalized_token_set,
    source_aliases,
    tokenize_retrieval,
    token_ngrams,
)
from .retrieval_tfidf import search_chunks as search_chunks_baseline
from .schemas import Chunk, SourceRecord


@dataclass
class Mvp003Result:
    query: str
    chunk: Chunk
    score: float
    source_file: str
    score_components: dict[str, float]
    matched_terms: list[str]
    matched_aliases: list[str]

    def to_json(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "chunk_id": self.chunk.chunk_id,
            "source_id": self.chunk.source_id,
            "source_file": self.source_file,
            "title": self.chunk.title,
            "source_priority": self.chunk.source_priority,
            "disclosure_level": self.chunk.disclosure_level,
            "evidence_label": self.chunk.evidence_label,
            "verification_status": self.chunk.verification_status,
            "score": round(self.score, 6),
            "score_components": {key: round(value, 6) for key, value in sorted(self.score_components.items())},
            "matched_terms": self.matched_terms,
            "matched_aliases": self.matched_aliases,
            "risk_tags": self.chunk.risk_tags,
            "text": self.chunk.text,
        }


def build_source_lookup(records: list[SourceRecord]) -> dict[str, SourceRecord]:
    return {record.source_id: record for record in records}


def _query_context(tokens: set[str], normalized_query: str) -> set[str]:
    context: set[str] = set()
    governance = {"source", "priority", "hierarchy", "truth", "evidence", "agent", "codex", "aos", "prompt"}
    if tokens & governance:
        context.add("governance")
    if tokens & {"market", "industry", "conference", "seed", "investor", "ir"}:
        context.add("market")
    if tokens & {"regulation", "regulatory", "lmo", "gmo", "cites", "nagoya", "biosafety", "law", "approval"}:
        context.add("regulatory")
    if tokens & {"company", "business", "strategy", "introduction", "asperitas"}:
        context.add("company")
    if tokens & {"r", "d", "rnd", "research", "project", "ptmc"} or "r d" in normalized_query:
        context.add("rnd")
    if tokens & {"synthetic", "biology", "biofoundry", "crispr", "protein", "antibiotic", "drug", "cell", "genetic"}:
        context.add("science")
    return context


def _priority_bonus(record: SourceRecord, context: set[str]) -> float:
    priority = record.source_priority
    if priority == "P0" and "governance" in context:
        return 5.0
    if priority == "P1" and (context & {"company", "science", "rnd"}):
        return 4.0
    if priority == "P4" and "regulatory" in context:
        return 4.0
    if priority == "P5" and "market" in context:
        return 5.0
    return 0.0


def _evidence_bonus(record: SourceRecord, context: set[str]) -> float:
    label = evidence_label_for_priority(record.source_priority)
    if label == "Industry Signal" and "market" in context:
        return 3.0
    if label == "Regulatory Source" and "regulatory" in context:
        return 3.0
    if label == "Document-Supported Fact" and (context & {"governance", "company", "science", "rnd"}):
        return 1.0
    return 0.0


def _overlap_score(query_tokens: set[str], field_tokens: set[str], weight: float) -> tuple[float, list[str]]:
    matches = sorted(query_tokens & field_tokens)
    if not matches:
        return 0.0, []
    short_penalty = sum(0.35 for token in matches if len(token) <= 2)
    score = max((len(matches) * weight) - short_penalty, 0.0)
    return score, matches


def _phrase_score(needles: list[str], haystack: str, weight: float) -> tuple[float, list[str]]:
    matches = [needle for needle in needles if needle and needle in haystack]
    if not matches:
        return 0.0, []
    return len(matches) * weight, matches


def _duplicate_adjustment(record: SourceRecord, normalized_query: str) -> float:
    path = normalize_text_for_retrieval(record.path)
    bonus = 0.0
    if "industry intelligence" in normalized_query and "p5 industry intelligence" in path:
        bonus += 7.0
    if ("r d" in normalized_query or "rnd" in normalized_query or "projects" in normalized_query) and "p1 rnd projects" in path:
        bonus += 7.0
    if "internal" in normalized_query and "p1 asperitas internal" in path:
        bonus += 3.0
    return bonus


def _body_tfidf_scores(query: str, chunks: list[Chunk]) -> dict[str, float]:
    baseline = search_chunks_baseline(query, chunks, limit=len(chunks))
    if not baseline:
        return {}
    max_score = max(result.score for result in baseline) or 1.0
    return {result.chunk.chunk_id: (result.score / max_score) * 10.0 for result in baseline}


def score_candidate(query: str, chunk: Chunk, record: SourceRecord, base_score: float = 0.0) -> Mvp003Result:
    normalized_query = normalize_text_for_retrieval(query)
    query_aliases = expand_query_aliases(query)
    query_tokens = normalized_token_set(query, *query_aliases)
    query_phrases = [normalized_query, *[normalize_text_for_retrieval(alias) for alias in query_aliases]]
    query_phrases.extend(token_ngrams(tokenize_retrieval(query), max_n=3))
    query_phrases = [phrase for phrase in dict.fromkeys(query_phrases) if len(phrase) > 2]

    source_alias_list = source_aliases(record)
    title_tokens = normalized_token_set(record.title, chunk.title)
    filename_tokens = normalized_token_set(record.original_filename, PurePosixPath(record.path).name, PurePosixPath(record.path).stem)
    path_tokens = normalized_token_set(record.path, " ".join(PurePosixPath(record.path).parts))
    alias_tokens = normalized_token_set(*source_alias_list)
    body_tokens = normalized_token_set(chunk.title, chunk.text[:1400])

    metadata_text = normalize_text_for_retrieval(
        " ".join([record.title, record.original_filename, record.path, record.source_type, record.notes, *source_alias_list])
    )
    title_text = normalize_text_for_retrieval(" ".join([record.title, chunk.title]))
    filename_text = normalize_text_for_retrieval(" ".join([record.original_filename, PurePosixPath(record.path).name]))
    body_text = normalize_text_for_retrieval(chunk.text[:1800])

    components: dict[str, float] = {"body_tfidf": base_score}
    matched_terms: set[str] = set()
    matched_aliases: set[str] = set()

    for key, tokens, weight in (
        ("title_match", title_tokens, 4.0),
        ("filename_match", filename_tokens, 5.0),
        ("path_match", path_tokens, 3.0),
        ("alias_match", alias_tokens, 4.5),
        ("body_token_overlap", body_tokens, 0.55),
    ):
        score, matches = _overlap_score(query_tokens, tokens, weight)
        components[key] = score
        matched_terms.update(matches)

    for key, text, weight in (
        ("exact_title_phrase", title_text, 14.0),
        ("exact_filename_phrase", filename_text, 16.0),
        ("metadata_phrase", metadata_text, 7.0),
        ("body_phrase", body_text, 2.0),
    ):
        score, matches = _phrase_score(query_phrases, text, weight)
        components[key] = score
        matched_terms.update(matches)

    normalized_aliases = [normalize_text_for_retrieval(alias) for alias in source_alias_list]
    alias_phrase_score, alias_matches = _phrase_score(query_phrases, " ".join(normalized_aliases), 10.0)
    components["alias_phrase"] = alias_phrase_score
    matched_aliases.update(alias_matches)

    context = _query_context(query_tokens, normalized_query)
    components["priority_bonus"] = _priority_bonus(record, context)
    components["evidence_label_bonus"] = _evidence_bonus(record, context)
    components["duplicate_context_bonus"] = _duplicate_adjustment(record, normalized_query)

    if record.parse_status not in {"parsed", "partial"}:
        components["parse_status_penalty"] = -5.0
    else:
        components["parse_status_penalty"] = 0.0

    score = sum(components.values())
    return Mvp003Result(
        query=query,
        chunk=chunk,
        score=score,
        source_file=record.path,
        score_components=components,
        matched_terms=sorted(matched_terms)[:30],
        matched_aliases=sorted(matched_aliases)[:20],
    )


def search_chunks_mvp003(
    query: str,
    chunks: list[Chunk],
    records: list[SourceRecord],
    limit: int = 5,
    include_explanations: bool = False,
) -> list[Mvp003Result]:
    if limit <= 0 or not query.strip() or not chunks:
        return []
    lookup = build_source_lookup(records)
    base_scores = _body_tfidf_scores(query, chunks)
    best_by_source: dict[str, Mvp003Result] = {}

    for chunk in chunks:
        record = lookup.get(chunk.source_id)
        if record is None:
            continue
        result = score_candidate(query, chunk, record, base_scores.get(chunk.chunk_id, 0.0))
        if result.score <= 0:
            continue
        current = best_by_source.get(chunk.source_id)
        if current is None or (result.score, -chunk.char_start, chunk.chunk_id) > (current.score, -current.chunk.char_start, current.chunk.chunk_id):
            best_by_source[chunk.source_id] = result

    ranked = sorted(
        best_by_source.values(),
        key=lambda item: (
            item.score,
            item.score_components.get("exact_filename_phrase", 0.0),
            item.score_components.get("alias_phrase", 0.0),
            item.score_components.get("filename_match", 0.0),
            item.chunk.source_priority,
            item.source_file,
        ),
        reverse=True,
    )
    return ranked[:limit]
