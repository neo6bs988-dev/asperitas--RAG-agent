# Protected Reference Mode

## Executive Rule

`mvp003` is the protected deterministic reference retriever. It exists to keep a stable comparison baseline while newer retrieval modes evolve.

Do not silently modify, replace, or reinterpret `mvp003` behavior in workflow, audit, or documentation tasks.

## Mode Boundaries

| Mode | Role | Default? | Notes |
|---|---|---:|---|
| `baseline` | historical TF-IDF baseline | no | comparison and regression context |
| `mvp003` | protected deterministic metadata-aware reference | yes/reference | stable deterministic behavior must be preserved |
| `vector` | embedding/vector foundation mode | no | comparison mode |
| `hybrid` | accepted metadata-vector comparison mode | no | can be used for closeout comparison; not default |
| `deterministic-test` reranker | reranker plumbing test | no | not a quality-improving reranker |

## What Counts as Protected-Reference Risk

Any change that modifies or reinterprets:

- candidate selection in `mvp003`
- scoring weights or ordering in `mvp003`
- source priority handling
- evidence label handling
- section/path-context evaluation assumptions
- default CLI retriever mode
- eval fixture expectations used to judge `mvp003`

## Allowed Without Behavior Change

- Documentation that explains current mode boundaries.
- Eval reports that compare modes without changing defaults.
- Issue closeout reports that state `hybrid` fixes a question while `mvp003` remains limited.
- CI/template changes that run existing commands without changing their semantics.

## Requires Dedicated Behavior PR

- Making `hybrid` the default.
- Modifying `mvp003` scoring or filtering.
- Changing chunk section detection.
- Changing eval pass/fail semantics.
- Treating folder/path context as fake section headings.
- Treating `deterministic-test` as production-quality reranking.

## Acceptance Rule for Future Retrieval Work

A future retrieval/reranker PR must report whether it improves ordering without regression in:

- Source @3
- Source @5
- Source priority
- Evidence label
- Section match
- Path context
- Overall pass rate
- Source-grounding metadata preservation

If it improves one metric while weakening source grounding, it is not accepted without explicit human approval.
