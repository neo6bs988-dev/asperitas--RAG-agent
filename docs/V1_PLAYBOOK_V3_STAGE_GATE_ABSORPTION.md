# V1 Playbook v3 and Benchmark Stage-Gate Absorption

Status: completed process subtask for the next V1 step

Scope: Playbook v3 Absorption plus Benchmark Absorption & Stage-Gate Calibration only

Base: post-PR77 metadata integrity hardening at `e470cce698b6460d93736083bcd8e69fc884cdff`

## Boundary

This document absorbs Playbook v3 into the V1 operating/process layer and calibrates benchmark stage-gate doctrine before release-candidate work. It is not a runtime retrieval, ingestion, source expansion, benchmark implementation, performance pack, closure matrix, regression, tag, dry-run, or internal release change.

This subtask does not:

- ingest new sources;
- crawl external sources;
- mutate source registries;
- mutate chunk artifacts;
- tune embeddings, vector indexes, reranking, retrieval, ranking, or answer generation;
- implement a full Failure Collector;
- add MCP connectors;
- claim deployment completion or mature RAG, KG, eval, or compliance infrastructure beyond what is implemented and verified.

## Doctrine Absorbed

Playbook v3 is absorbed as operating doctrine, not as source content or runtime behavior. For V1 work, it means:

- keep roadmap state explicit and auditable;
- separate process doctrine absorbed from performance feature implemented;
- preserve source, chunk, metadata, eval, and runtime artifacts unless the active task explicitly allows them;
- require deterministic stage gates before status language escalates;
- label benchmark evidence as measured, report-only, pending, or blocked;
- keep human review in front of public, investor, partner, legal, regulatory, wet-lab-sensitive, and deployment-related claims.

## Benchmark Absorption

Benchmark references are absorbed as calibration inputs for gate design and reporting discipline. They do not become claims that the system matches any external benchmark product, platform, or operational maturity level.

V1 benchmark doctrine:

- fresh command output is required for any pass or improvement claim;
- historical benchmark notes can guide thresholds but cannot satisfy a fresh gate;
- strict source, priority, evidence label, section, and path-context metrics remain separate from relaxed oracle diagnostics;
- threshold passes do not make `hybrid`, vector, reranker, or answer-generation behavior the default;
- stage-gate language must say whether a result is a process check, retrieval eval, artifact verification, security smoke, chat smoke, or release-only check.

## V1 Stage-Gate Calibration

This subtask calibrates stage gates for the remaining V1 path without completing later roadmap items.

Required gates for this subtask:

- `python -m pytest`
- `python scripts/verify_artifacts.py`
- `python scripts/check_v1_stage_gate_scope.py`
- retrieval eval comparison sufficient to show no runtime retrieval regression
- git diff review confirming protected artifacts and runtime retrieval behavior were not modified

Allowed status after those gates pass: ready for next V1 step.

Status claims still blocked after this subtask alone:

- final pre-RC regression may proceed;
- `v1.0.0-rc1` may be tagged;
- internal dry-run is complete;
- internal release is complete;
- mature RAG, KG, eval, compliance, or deployment completion has been verified.

## Preserved V1 Roadmap

The remaining V1 roadmap stays active:

| Step | Status after this subtask |
|---|---|
| 1. Playbook v3 Absorption | Completed by this process subtask |
| 2. Benchmark Absorption & Stage-Gate Calibration | Completed by this process subtask |
| 3. MVP Performance Pack Backfill | Pending |
| 4. V1 Performance Closure Matrix | Pending |
| 5. P0/P1 Gap Fix Only | Pending |
| 6. Final Pre-RC Regression | Pending |
| 7. v1.0.0-rc1 | Pending |
| 8. Internal Dry-run | Pending |
| 9. v1.0.0-internal | Pending |

## Acceptance Evidence Format

Each PR using this doctrine should report:

1. Files changed.
2. Tests run.
3. Artifact mutation check.
4. Retrieval behavior check.
5. Roadmap status update.
6. Risk summary.
7. GO/NO-GO recommendation.

GO is allowed only when the deterministic checks pass and the diff stays inside docs/process/check-only boundaries. NO-GO is required if the work needs source registry mutation, chunk mutation, retrieval/ranking/embedding/reranker/generation mutation, weakened tests, unverifiable benchmark claims, deployment-complete claims, self-directed ingestion claims, source expansion completion claims, or complete-V1-closeout claims.
