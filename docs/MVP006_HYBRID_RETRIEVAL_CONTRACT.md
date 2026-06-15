# MVP-006 Hybrid Retrieval Contract

Date: 2026-06-15

Related issue: #10

## Objective

Define a safe, explicit hybrid retrieval scoring contract that can combine `mvp003` metadata-aware retrieval with the improved local vector signal without changing existing modes.

Existing modes must remain separately callable:

```bash
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
```

Future hybrid mode must be explicit:

```bash
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

Do not silently change `baseline`, `mvp003`, or `vector`.

## Current Reference Metrics

Dataset: `eval/retrieval_questions.jsonl`

Top-k: `--limit 5`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 43.8% | 43.8% | 43.8% | 34.4% |
| mvp003 | 90.6% | 96.9% | 100.0% | 100.0% | 100.0% | 90.6% |
| vector | 53.1% | 56.2% | 59.4% | 59.4% | 59.4% | 53.1% |

`mvp003` is the reference retriever. Vector is a useful secondary signal, not a replacement.

## Inputs

Hybrid retrieval should build a candidate set from:

1. `mvp003` top-N results.
2. `vector` top-N results.
3. Optional baseline TF-IDF scores already included inside `mvp003` as `body_tfidf`.

Initial recommendation: collect at least `max(limit * 4, 20)` candidates from both `mvp003` and `vector`, merge by `chunk_id`, then rank the merged set by hybrid score.

## Score Components

The scoring contract uses normalized component values in `[0.0, 1.0]`.

| Component | Source | Meaning | Initial role |
|---|---|---|---|
| `mvp003_score` | `search_chunks_mvp003` | Metadata-aware score including title, filename, path, alias, priority, evidence, duplicate context, parse status, and body TF-IDF | Primary relevance and source-governance signal |
| `vector_score` | `InMemoryVectorStore.search` over `LexicalSemanticOfflineEmbeddingProvider` records | Local lexical-semantic similarity over source registry metadata and chunk text | Secondary recall and semantic-neighbor signal |
| `section_score` | result section fields and eval target matching when available | Whether section metadata gives useful local context | Tie-break and grounding-support signal |
| `metadata_score` | required field completeness | Whether the result preserves source-grounding and embedding provenance fields | Guardrail against metadata-dropping candidates |

## Initial Combination Contract

Use `src/asperitas_agent/hybrid_scoring.py` for the first scoring contract:

```text
hybrid_score =
  0.70 * normalized_mvp003_score
+ 0.20 * normalized_vector_score
+ 0.05 * section_score
+ 0.05 * metadata_score
```

Rationale:

- `mvp003` remains the reference signal because it has 90.6% overall pass rate.
- Vector now beats baseline but still trails `mvp003`; it should improve recall without dominating governance-aware ranking.
- Section and metadata scores are small guardrail/tie-break components.
- Weights are explicit and test-covered, and can be tuned only through eval.

## Normalization Rules

`mvp003_score`:

- Normalize inside the candidate set.
- Suggested first formula: `score / max_mvp003_score` when `max_mvp003_score > 0`, else `0.0`.
- Keep the original raw `mvp003` score in debug output.

`vector_score`:

- Vector store score is cosine-like.
- Normalize with `(score + 1.0) / 2.0`, clamped to `[0.0, 1.0]`.
- Keep the original raw vector score in debug output.

`section_score`:

- `1.0` when section, section heading, section path, or heading context directly supports the query or expected section.
- `0.5` when section metadata exists but does not clearly match.
- `0.0` when section metadata is missing.

`metadata_score`:

- Use the fraction of required source-grounding fields present.
- Missing `embedding_*` fields should lower score, not crash hybrid ranking.

## Required Metadata Preservation

Every hybrid result must preserve or derive the following fields:

- `source_id`
- `source_file`
- `source_priority`
- `evidence_label`
- `section`
- `section_heading`
- `section_path`
- `heading_context`
- `embedding_model`
- `embedding_dim`
- `embedding_version`
- `content_hash`

Hybrid result rows should also keep:

- `rank`
- `chunk_id`
- `title`
- `text`
- `score`
- `score_components`
- raw source scores, such as `mvp003_score_raw` and `vector_score_raw`

Metadata rule: if a candidate is found only through `mvp003`, attach vector embedding metadata by building the corresponding `EmbeddingRecord` for its chunk before returning the final result row.

## Tie-Breaking

When `hybrid_score` ties, sort by:

1. Higher normalized `mvp003_score`.
2. Higher normalized `vector_score`.
3. Higher `metadata_score`.
4. Earlier `mvp003` rank if present.
5. Earlier `vector` rank if present.
6. Stable `source_file`, then `chunk_id`.

## Failure Modes

- Vector score dominates and lowers source-priority/evidence accuracy.
- `mvp003` candidates lose because vector finds semantically nearby but wrong sources.
- Hybrid returns chunks without embedding metadata.
- Candidate merging drops the best chunk per source.
- Duplicate source folders regress because source path context is underweighted.
- Section metadata is treated as relevance even when it is merely present.
- Scores become incomparable because raw `mvp003` and vector scales are mixed without normalization.
- Eval improves source match but worsens section match or evidence-label match.

## Rollback Path

If hybrid eval regresses:

1. Keep `baseline`, `mvp003`, and `vector` unchanged.
2. Do not expose `hybrid` as default.
3. Reduce vector weight to `0.10` or disable vector contribution while keeping candidate logging.
4. Re-run all eval modes.
5. If still regressed, remove the `hybrid` eval mode and keep `hybrid_scoring.py` as an inactive contract helper.

No source files, baseline modes, vector provider, or generated artifacts should be deleted as part of rollback unless explicitly requested.

## Eval Plan

Required comparison commands:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/run_retrieval_eval.py --retriever vector --limit 5
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

Hybrid acceptance threshold for the first implementation:

- `baseline`, `mvp003`, and `vector` metrics remain unchanged.
- `hybrid` overall pass rate is not below `mvp003` by more than 2 percentage points.
- `hybrid` source @5, priority, and evidence are not below `mvp003`.
- `hybrid` section match is not below `mvp003` by more than 2 percentage points.
- Every returned result has complete source-grounding metadata or an explicit missing-field debug warning.

If hybrid does not beat `mvp003`, it can still pass as an experimental mode only if it explains recall gains on specific failed questions without degrading reference-mode behavior.

## Implementation Boundary For Issue #11

Issue #10 defines the scoring contract and tests the scoring helper only.

Issue #11 should implement:

- `--retriever hybrid` as a new explicit eval mode;
- candidate collection from `mvp003` and `vector`;
- candidate merge by `chunk_id`;
- normalization of raw source scores;
- `combine_hybrid_score(...)` integration;
- full retrieval eval comparison.

No external vector DB dependency is needed for Issue #11.

