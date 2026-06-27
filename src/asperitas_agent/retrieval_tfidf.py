from __future__ import annotations

import math
import re
from collections import Counter

from .schemas import Chunk, RetrievalResult


BENCHMARK_QUERY_TERMS = {
    "benchmark",
    "benchmarks",
    "benchmarking",
    "comparison",
    "compare",
    "workflow",
    "workflows",
    "operating",
    "process",
    "patterns",
}
INTERNAL_FACT_QUERY_TERMS = {
    "asperitas",
    "internal",
    "company",
    "document",
    "source",
    "covers",
    "synthetic",
    "biology",
    "drug",
    "development",
    "status",
    "outlook",
    "strategy",
}


TOKEN_RE = re.compile(r"[A-Za-z0-9_가-힣]{2,}")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def _is_internal_fact_query(query_tokens: list[str]) -> bool:
    tokens = set(query_tokens)
    if tokens & BENCHMARK_QUERY_TERMS:
        return False
    return bool(tokens & INTERNAL_FACT_QUERY_TERMS)


def search_chunks(query: str, chunks: list[Chunk], limit: int = 5) -> list[RetrievalResult]:
    if limit <= 0:
        return []
    query_tokens = tokenize(query)
    if not query_tokens or not chunks:
        return []
    internal_fact_query = _is_internal_fact_query(query_tokens)
    q_counts = Counter(query_tokens)
    doc_tokens = [tokenize(chunk.title + " " + chunk.text) for chunk in chunks]
    doc_freq: Counter[str] = Counter()
    for tokens in doc_tokens:
        for token in set(tokens):
            if token in q_counts:
                doc_freq[token] += 1

    total_docs = len(chunks)
    scored: list[RetrievalResult] = []
    phrase = query.lower().strip()
    for chunk, tokens in zip(chunks, doc_tokens):
        counts = Counter(tokens)
        score = 0.0
        for token, q_count in q_counts.items():
            count = counts[token]
            if not count:
                continue
            tf = 1 + math.log(count)
            idf = math.log((total_docs + 1) / (doc_freq[token] + 1)) + 1
            score += q_count * tf * idf
        if phrase and phrase in chunk.text.lower():
            score += 2.0
        if internal_fact_query and chunk.source_priority == "P6":
            score *= 0.05
        if score > 0:
            scored.append(RetrievalResult(query=query, chunk=chunk, score=score))
    scored.sort(key=lambda result: result.score, reverse=True)
    return scored[:limit]
