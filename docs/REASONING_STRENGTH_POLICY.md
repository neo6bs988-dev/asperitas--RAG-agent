# Reasoning Strength Policy

Every Codex task prompt should start with:

```text
Reasoning Strength: Low / Medium / High / Very High
```

Korean labels:

```text
추론강도: 낮음 / 중간 / 높음 / 매우높음
```

## Level Guide

- Low: tiny docs edits, typo fixes, status summaries.
- Medium: docs/governance updates, small tests, simple issue comments.
- High: source code changes, schemas, MVP implementation, embedding provider work.
- Very High: architecture, retrieval scoring, vector DB, reranking, answer generation, compliance, security, external dependency, release decisions.

## Defaults

- Normal MVP implementation: High.
- Retrieval/vector/reranker/answer/compliance/release tasks: Very High.
- Docs-only operational updates: Medium.
- Cosmetic no-risk edits: Low.

## Required Report Fields

```text
Reasoning Strength Used:
Why this level:
```

## MVP-005 Defaults

- Issue #3 offline embedding provider boundary: High.
- Issue #4 local vector store adapter: Very High.
- Issue #5 vector retrieval eval mode: Very High.
- Issue #6 vector backend selection: Very High.
