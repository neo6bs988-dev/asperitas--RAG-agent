# V1.3A Retrieval Diagnostic Report

## Executive Bottom Line

V1.3A adds a read-only retrieval diagnostic layer for the V1.2/V1.2B answer-quality fixture cases. The diagnostic confirms fixture source-path existence, checks whether those paths are represented in current registry/chunk metadata, and captures current read-only `mvp003` retrieval outputs where available.

This report does not claim answer quality, retrieval optimization, biological validation, production deployment, legal approval, or regulatory approval.

## Scope Lock

- Diagnostic-only.
- No retrieval behavior change.
- No ranking, embedding, vector DB, reranker, answer-generation, prompt, source registry, chunk artifact, source artifact, or ingestion mutation.
- No fabricated retrieval metrics.

## Current Retrieval Observability

The repo has a stable local retrieval API via `asperitas_agent.retrieval_mvp003.search_chunks_mvp003` and source/chunk readers via `read_registry` and `read_chunks`. The diagnostic script uses those interfaces in read-only mode and captures:

- top-k source IDs and paths;
- source priorities;
- chunk IDs;
- section metadata fields;
- retrieval miss flags against V1.2 expected source scopes;
- wrong-source-priority proxy flags for retrieved non-expected paths;
- citation candidate availability.

## Source Coverage by V1.2 Case

The V1.2 fixture contains 4 cases and 12 expected source-scope paths. The diagnostic baseline records whether each path exists in the repository and whether it is represented in registry/chunk metadata.

Current source-path existence is strong for the V1.2 fixture because all expected paths are repository files. Registry and chunk representation is limited for these documentation/governance paths because current source artifacts primarily represent ingested raw source materials rather than every repository governance document.

## Missing Diagnostic Hooks

- No dedicated answer-quality retrieval harness exists for V1.2 cases separate from current retrieval eval fixtures.
- No source registry mapping guarantees for every repo documentation path used by the V1.2 answer-quality fixture.
- No citation-readiness contract that explicitly maps V1.2 expected source-scope docs to retrievable chunk IDs.
- No behavior score or model judge is executed in V1.3A.

## Risks Before V1.3B

- V1.2 answer-quality cases may rely on governance docs that are present in the repo but not represented as retrieval artifacts.
- Retrieval outputs can contain citation candidates without proving those candidates satisfy the answer-quality rubric.
- Missing registry/chunk representation for expected docs should be treated as a readiness gap, not as an answer-performance score.

## Recommended V1.3B Optimization Targets

- Decide whether V1.2 governance docs should become explicit source registry and chunk artifacts.
- Add a stable retrieval diagnostic contract for answer-quality fixtures before optimizing ranking.
- Preserve `mvp003` deterministic behavior until V1.3B has before/after retrieval evaluation evidence.
- Separate retrieval-readiness metrics from answer-generation quality claims.

## Verification

Expected commands:

```bash
python scripts/diagnose_v1_3a_retrieval_quality.py --overwrite --json
python -m pytest
python scripts/verify_artifacts.py
python scripts/check_v1_release_readiness.py --json
python scripts/check_v1_2_answer_quality_baseline.py
python scripts/run_v1_2_answer_quality_eval.py --overwrite --json
```

## Truth Boundary

This diagnostic reports retrieval-readiness observations only. It is not an answer-quality baseline, not a retrieval optimization result, and not evidence of deployment, biological validation, legal approval, or regulatory approval.
