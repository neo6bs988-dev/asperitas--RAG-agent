# MVP-006 Phase 5 Hybrid Graduation Decision

Date: 2026-06-16

Related issue: #28

## Decision

Promote `hybrid` from explicit experimental eval mode to accepted retrieval eval mode, but do not make it the default or recommended production retrieval path before MVP-007.

`mvp003` remains the protected deterministic reference retriever. `hybrid` should be run as a required comparison mode for MVP-007 reranker preparation and future retrieval-quality gates.

## Current Mode Policy

| Mode | Policy | Default status |
|---|---|---|
| `baseline` | Legacy deterministic TF-IDF baseline for historical comparison. | CLI eval default remains unchanged. |
| `mvp003` | Protected deterministic metadata-aware reference retriever. | Reference baseline for non-regression. |
| `vector` | Accepted secondary eval signal using local offline embeddings. | Not default. |
| `hybrid` | Accepted eval comparison mode combining `mvp003`, vector, section, and metadata signals. | Not default. |

## Why Not Default Yet

Hybrid reached 100.0% overall on the current retrieval fixture, but the fixture has 32 questions and is still small. The Phase 3 hybrid improvement also uses eval-time section expectations for same-source section substitution. That is valid for an eval mode, but it is not yet a general production retrieval policy because a production query path would need to infer or receive section intent without answer-key fields.

Default or recommended production use should wait until MVP-007 reranker work proves that ordering can improve without depending on fixture-specific expected-section signals.

## Live Eval Comparison

Dataset: `eval/retrieval_questions.jsonl`

Top-k: `--limit 5`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `mvp003` | 93.8% | 96.9% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `hybrid` | 100.0% | 96.9% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

Observed improvement versus `mvp003`:

- Overall: +6.2 percentage points.
- Section match: +6.5 percentage points.
- Source @5: no regression.
- Source priority: no regression.
- Evidence label: no regression.
- Path context: no regression.

## Graduation Criteria

`hybrid` may remain accepted only when all of the following hold on the full retrieval fixture:

- no regression versus `mvp003` in source file match @5;
- no regression versus `mvp003` in source priority match;
- no regression versus `mvp003` in evidence label match;
- no regression versus `mvp003` in section match;
- no regression versus `mvp003` in path-context match when path-context expectations exist;
- no regression in metadata preservation for source IDs, source files, priorities, evidence labels, section fields, heading context, embedding metadata, and content hash;
- `baseline`, `mvp003`, and `vector` remain separately callable and behaviorally protected;
- `mvp003` remains the deterministic reference baseline;
- improvements are not presented as production-ready unless they work without fixture-specific expected-answer fields.

## Regression Criteria

Revert `hybrid` to experimental if any accepted quality gate shows:

- source file match @5 below `mvp003`;
- source priority or evidence label below `mvp003`;
- section match below `mvp003`;
- path-context match below `mvp003` when applicable;
- missing required source-grounding metadata in returned hybrid rows;
- hidden changes to `baseline`, `mvp003`, or `vector`;
- reliance on new external services, generated indexes, secrets, model binaries, or network access.

## MVP-007 Implication

MVP-007 should use:

- `mvp003` as the protected deterministic baseline;
- `hybrid` as an accepted comparison mode and candidate source for reranker experiments;
- `baseline` and `vector` as required context modes for regression visibility.

Do not start reranker implementation from this decision. The next issue should define the reranker contract, inputs, outputs, metadata preservation rules, and eval comparison plan.

