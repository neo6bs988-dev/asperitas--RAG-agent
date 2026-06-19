# MVP-013 Hybrid Boundary and Section Selection Closeout

Date: 2026-06-19

Latest baseline at closeout:

- `f1acc22 Harden hybrid retrieval eval runtime`
- `2bc2170 Document MVP-007 Phase 3 candidate-preserving reranker strategy`

Related documents:

- `docs/MVP006_PHASE5_HYBRID_GRADUATION_DECISION.md`
- `docs/MVP007_RERANKER_CONTRACT.md`
- `docs/MVP007_PHASE2_RERANKER_EVAL_REPORT.md`
- `09_LOGS/decision_logs/mvp007_phase3_candidate_preserving_reranker_strategy.md`

## Decision

Close MVP-013 as a boundary, policy, and handoff milestone.

MVP-013 does not redesign retrieval ranking, does not modify chunks, does not modify source registry records, does not modify eval fixtures, and does not start MVP-014.

`mvp003` remains the protected deterministic reference retriever. `hybrid` remains explicit, non-default, and eval-assisted. `--reranker deterministic-test` remains explicit, opt-in, and non-default.

## Hybrid Eval Boundary / Manual Slow Gate Policy

The normal fast validation boundary is:

```bash
python -m pytest -q
python scripts/verify_artifacts.py
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

The manual hybrid gate is:

```bash
python scripts/run_retrieval_eval.py --retriever hybrid --limit 5
```

The manual reranker comparison gate is:

```bash
python scripts/run_retrieval_eval.py --retriever mvp003 --reranker deterministic-test --limit 5
```

Do not require full `hybrid + reranker` eval as a default gate. It is expensive and should run only when a task explicitly targets hybrid-reranking interactions.

Run the manual hybrid gate when a change touches:

- `scripts/run_retrieval_eval.py` hybrid candidate collection, scoring, sorting, section substitution, or path-context logic;
- `src/asperitas_agent/hybrid_scoring.py`;
- retrieval scoring or metadata fields used by hybrid;
- chunk section metadata or path-context eval semantics;
- vector eval candidate construction used by hybrid;
- eval policy that claims hybrid quality, hybrid graduation, or hybrid non-regression.

Skip full hybrid eval only when the task does not affect hybrid behavior. When skipped, report the reason and residual risk.

## Production-Safe Section Selection Design

Hybrid currently benefits from eval-time same-source section substitution. That is acceptable for an eval comparison mode because the expected section is available from the fixture.

Production-safe section selection must not depend on answer-key fields such as `expected_chunk_or_section`.

Any future production-safe design must:

1. infer section intent from the user query, metadata, or explicit user-provided filters;
2. preserve source ID, source file, source priority, evidence label, disclosure level, section fields, heading context, embedding metadata, and content hash;
3. fail closed to the protected base retriever order if source-grounding metrics would regress;
4. keep `mvp003` callable as the reference retriever;
5. keep `hybrid` and reranking non-default until a separate production-readiness decision approves otherwise;
6. report exact commands, dataset, top-k, metrics, and regressions before any quality claim.

Section improvements are acceptable only when they do not reduce:

- source file match @5;
- source priority match;
- evidence label match;
- section match;
- path-context match, when path-context expectations exist;
- required source-grounding metadata preservation.

## Production-Claim Restrictions

The current `hybrid` score must not be described as production retrieval quality.

Known validated metrics are eval-fixture metrics only:

Dataset: `eval/retrieval_questions.jsonl`

Top-k: `--limit 5`

| Mode | Overall | Source @3 | Source @5 | Priority | Evidence | Section | Path context |
|---|---:|---:|---:|---:|---:|---:|---:|
| `mvp003` | 93.8% | 96.9% | 100.0% | 100.0% | 100.0% | 93.5% | 100.0% |
| `hybrid` | 100.0% | 96.9% | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

These metrics support only this claim:

> On the current local retrieval eval fixture, explicit `hybrid --limit 5` matched or exceeded `mvp003` while preserving source-grounding gates.

These metrics do not support claims of:

- production retrieval readiness;
- regulatory, legal, scientific, wet-lab, or customer validation;
- default retriever approval;
- production reranker approval;
- external API, vector DB, or model-backed deployment.

## Stop Rules

Stop and report before committing if:

- hybrid source @5, priority, evidence, section, path context, or metadata preservation regresses versus `mvp003`;
- full hybrid eval exits silently, times out, or leaves lingering retrieval-eval Python processes;
- a change modifies chunks, registry records, or eval fixtures outside the approved task scope;
- a change makes `hybrid` or reranking default;
- a report implies production hybrid quality without external validation.

## MVP-014 Agent Role Registry Handoff

MVP-014 should start only after this closeout is committed and pushed cleanly.

Recommended MVP-014 scope:

- create an Agent Role Registry that defines local agent roles, responsibilities, allowed actions, prohibited actions, required inputs, required outputs, validation gates, and escalation paths;
- keep the registry deterministic and local-only;
- do not add external APIs, web servers, vector DBs, generated indexes, secrets, endpoints, cloud resources, or model binaries;
- do not change retrieval ranking, chunks, registry records, or eval fixtures unless explicitly approved;
- preserve the existing source-grounding, compliance, guardrail, and retrieval evaluation gates.

MVP-014 should not implement autonomous external actions. It should define role boundaries and validation policy first.

## Closeout Recommendation

Commit this document as the MVP-013 closeout record, then proceed to MVP-014 read-only preflight.
