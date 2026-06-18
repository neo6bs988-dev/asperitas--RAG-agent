# MVP-008 Source-Grounded Answer Contract

Date: 2026-06-19

Related issue: #14

## Objective

Define the contract for source-grounded answer generation before MVP-008 Phase 2 implementation work.

This document is a contract and implementation plan. It does not change retrieval behavior, reranker behavior, eval scoring semantics, model behavior, or default retriever policy.

## Current Foundation

The repository already has the retrieval and evidence foundation needed for MVP-008:

- `baseline`, `mvp003`, `vector`, and `hybrid` retrieval modes remain separately callable.
- `mvp003` remains the protected deterministic reference retriever.
- `hybrid` is an accepted comparison mode, not default.
- Reranking is explicit and disabled unless requested.
- `EvidencePack`, `EvidenceItem`, `GuardrailDecision`, and `GroundedAnswer` schemas exist as deterministic scaffolding.
- The current deterministic answer composer is not a free-form LLM answer generator.

MVP-008 Phase 1 defines the stricter contract that Phase 2 must implement and test.

## Allowed Inputs

An answer generator may use only retrieved evidence rows and derived evidence-pack fields. It must not use eval answer keys, hidden benchmark files, prompt-only assumptions, or unstated external knowledge.

Allowed retrieval row fields:

| Field | Use |
|---|---|
| `rank` | Retrieval order and debug trace. |
| `chunk_id` | Stable chunk reference for citation traceability. |
| `source_id` | Primary source identity. |
| `source_file` or `source_path` | Source path and path-context traceability. |
| `title` or `source_title` | Human-readable source label. |
| `source_priority` | Source hierarchy and trust policy. |
| `evidence_label` | Claim status and evidence type. |
| `section` | Chunk-local section context when present. |
| `section_heading` | Chunk-local heading when present. |
| `section_path` | Heading ancestry when present. |
| `heading_context` | Additional heading ancestry when present. |
| `text` or `text_excerpt` | Only source text allowed for factual answer content. |
| `score` | Optional debug trace, not factual evidence. |
| `score_components` | Optional debug trace, not factual evidence. |
| `mvp003_rank`, `vector_rank`, `section_candidate_rank` | Optional debug trace for hybrid/eval analysis. |
| `embedding_model`, `embedding_dim`, `embedding_version`, `content_hash` | Metadata preservation and debug trace. |
| `reranker_metadata` | Optional debug trace for explicit reranker runs. |

Not allowed as factual answer sources:

- eval fixtures such as `eval/retrieval_questions.jsonl` or `eval/expected_sources.jsonl`;
- test-only expected answers;
- model priors;
- user-provided claims unless they are clearly labeled as user-provided and not verified;
- retrieval scores or ranks as proof of truth.

## Output Contract

Every source-grounded answer must serialize to a structure with these fields:

| Field | Required behavior |
|---|---|
| `query` | Original user query. |
| `answer_status` | One of `answered`, `caution`, or `abstained`. |
| `answer_text` | Human-readable answer with citation markers on every material claim. |
| `claim_blocks` | Phase 2 target: structured claim records with citation keys and claim type. |
| `citations_used` | List of citation keys used in `answer_text`. |
| `citation_coverage` | Evidence count, cited evidence count, uncited evidence count, and all-claims-cited flag. |
| `evidence_used` | Citation records preserving source and chunk metadata. |
| `guardrail_decision_summary` | Evidence sufficiency and warning/abstention decision. |
| `limitations` | Evidence gaps, caveats, warnings, and missing approvals. |
| `unsupported_claims` | Phase 2 target: claims removed, abstained, or marked unsupported. |
| `metadata` | Generator name, version, deterministic flag, retrieval mode, and optional debug mode. |

Phase 2 may keep backward-compatible fields from the existing `GroundedAnswer` schema, but it must not remove source-grounding fields without a migration plan and tests.

## Claim Types

Material answer claims must be classified as one of:

- `sourced_fact`: directly supported by retrieved evidence.
- `inference`: limited reasoning over cited facts, labeled as inference.
- `uncertainty`: explicit gap, limitation, or missing evidence.
- `unsupported`: not allowed in final factual answer text.

Legal, regulatory, biosafety, IP, investor, market, scientific-validation, wet-lab, customer, traction, deployment, or product-performance claims require direct evidence and must be blocked, abstained, or labeled as uncertainty when evidence is insufficient.

## Citation Format

Use deterministic citation keys in answer text:

```text
[E1]
[E2]
```

Each citation key must resolve to exactly one evidence record. A citation record must preserve:

| Field | Required |
|---|---|
| `citation_key` | Yes. Example: `[E1]`. |
| `source_id` | Yes when present on retrieval row. |
| `source_file` or `source_path` | Yes. |
| `source_priority` | Yes. |
| `evidence_label` | Yes. |
| `chunk_id` | Yes when present on retrieval row. |
| `section` | Preserve when available. |
| `section_heading` | Preserve when available. |
| `section_path` | Preserve when available. |
| `heading_context` | Preserve when available. |
| `retrieval_mode` | Preserve at answer/evidence-pack metadata level. |
| `rank` | Preserve for debug trace. |
| `score` | Preserve for debug trace. |
| `score_components` | Preserve for debug trace when present. |
| `content_hash` | Preserve when present. |
| `reranker_metadata` | Preserve when present for explicit reranker runs. |

Citation text must never point to a source ID or chunk ID that was not present in retrieved evidence.

## Answer Text Rules

Every material sentence or bullet must end with one or more citation markers unless it is explicitly an uncertainty, limitation, or next-action statement.

Allowed wording:

```text
The retrieved evidence states that ... [E1]
Based on [E1] and [E2], a cautious inference is ...
The retrieved evidence is insufficient to determine ...
```

Disallowed wording:

```text
Asperitas has regulatory approval.
This biology is validated.
The product is deployed.
Investors have committed capital.
```

Those claims are disallowed unless direct retrieved evidence supports them and the output clearly preserves source priority, evidence label, and validation status.

## Insufficient-Evidence Behavior

The generator must abstain or answer with caution when evidence is insufficient.

Abstain when:

- no retrieved evidence is available;
- all evidence lacks source priority;
- all evidence lacks evidence labels;
- evidence is too sparse and section coverage is weak;
- the query asks for legal, regulatory, biosafety, wet-lab, investor, market, IP, scientific-validation, product-performance, deployment, customer, or public-facing claims not directly supported by retrieved evidence.

Required abstention wording:

```text
The system cannot answer this from the retrieved evidence.
```

The answer must then include:

- why evidence is insufficient;
- what evidence is missing;
- recommended next action, such as retrieving more sources, escalating for human review, or narrowing the question.

## Unsupported-Claim Behavior

Unsupported claims must not be presented as facts.

Phase 2 implementation must either:

1. remove the unsupported claim from `answer_text`;
2. move it to `unsupported_claims` with reason and missing evidence; or
3. convert it to explicit uncertainty.

Unsupported-claim records should include:

| Field | Purpose |
|---|---|
| `claim_text` | The blocked or rewritten claim. |
| `reason` | Why the claim is unsupported. |
| `missing_evidence` | What source or validation is needed. |
| `risk_domain` | Optional: legal, regulatory, biosafety, IP, investor, market, science, privacy, security, public communication. |
| `recommended_next_action` | Retrieve more evidence, ask user for source, or escalate. |

## Uncertainty Wording

Use precise uncertainty wording:

- `The retrieved evidence does not establish ...`
- `The evidence supports ... but does not establish ...`
- `This is an inference from cited evidence, not a validated fact ...`
- `Human review is required before treating this as legal, regulatory, biosafety, investor, or public-facing guidance.`

Do not use vague confidence language such as "probably true" unless the uncertainty is tied to retrieved evidence and limitations.

## Metadata Preservation Requirements

The answer path must preserve source-grounding metadata from retrieval row to evidence pack to final answer.

Required preserved fields:

- `source_id`
- `source_file` or `source_path`
- `source_priority`
- `evidence_label`
- `chunk_id`
- `section`
- `section_heading`
- `section_path`
- `heading_context`
- `rank`
- `score`
- `score_components`
- `embedding_model`
- `embedding_dim`
- `embedding_version`
- `content_hash`
- `retrieval_mode`
- `reranker_metadata`

Missing optional fields may be empty, but they must not be fabricated.

## Compliance And Disclosure Rules

The answer generator must escalate or abstain when the query or evidence involves:

- CITES, Nagoya Protocol, LMO, K-BDS, biosafety, biosecurity, privacy, security, IP, legal, financial, investor, public-communication, or regulatory risk;
- wet-lab execution or operational biological instructions;
- claims of validation, deployment, product performance, customer traction, or committed capital.

Default posture for internal Asperitas material is internal/confidential. The generator must not expose confidential or restricted source text in public-mode outputs unless a future disclosure policy explicitly allows it.

## Phase 2 Implementation Plan

MVP-008 Phase 2 / Issue #15 should implement the smallest testable answer-generation contract layer:

1. Add explicit `ClaimBlock`, `CitationRecord`, and `UnsupportedClaim` schema fields or backward-compatible equivalents.
2. Extend evidence-pack construction to preserve `heading_context`, embedding metadata, `content_hash`, retrieval mode, and optional reranker metadata when present.
3. Add citation formatting helpers that produce deterministic `[E#]` keys and citation records.
4. Add insufficient-evidence and unsupported-claim tests.
5. Add source-grounding tests proving every material claim maps to retrieved citation keys.
6. Add compliance-sensitive abstention tests for legal, regulatory, biosafety, investor, public-communication, validation, and deployment claims.
7. Keep any LLM integration out of scope until deterministic contract tests pass.

## Phase 2 Acceptance Criteria

Phase 2 is acceptable only when:

- all answer claims are cited or explicitly marked uncertainty;
- citation records resolve to retrieved evidence;
- source priority and evidence label survive output formatting;
- unsupported claims are removed, blocked, or recorded as unsupported;
- no answer generator reads eval answer keys or benchmark fixtures;
- no external API, LLM call, model binary, endpoint, secret, generated index, or cloud service is required;
- retrieval modes remain unchanged.

## Quality Gates

For Phase 1:

```bash
python -m pytest
python scripts/verify_artifacts.py
```

Retrieval eval is not required for this Phase 1 contract document because retrieval, reranking, scoring, and eval semantics are unchanged.

For Phase 2, add targeted tests and run retrieval eval only if answer-generation evidence selection changes retrieval inputs, retrieval mode choice, ranking, reranking, or eval semantics.

