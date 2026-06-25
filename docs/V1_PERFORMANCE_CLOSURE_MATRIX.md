# V1 Performance Closure Matrix

Status: completed closure-matrix candidate after deterministic checks pass

Scope: docs/tests/checks only. No source, raw source, chunk, vector, embedding, retrieval, ranking, reranker, generation, runtime RAG, ingestion, crawling, or vector-tuning behavior changed.

Base: `0a4ab27dce3e6cd19fe03d0ab12379c2af002997`

## A. Preflight

This matrix closes the documentation gap after `docs/V1_MVP_PERFORMANCE_PACK.md` by recording the evidence command, expected result, current verification result, gap severity, owner action, and GO/NO-GO state for every V1 MVP/gate. It does not fix gaps, run final regression as a final claim, create a tag, create a release, complete an internal dry-run, or claim production readiness.

Source docs:

| Source | Use |
|---|---|
| `docs/V1_MVP_PERFORMANCE_PACK.md` | MVP/gate list, command map, unresolved gap seed list |
| `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md` | preserved stage-gate doctrine and roadmap boundary |
| `docs/ROADMAP.md` | V1 roadmap state |
| `docs/V1_RELEASE_CLOSEOUT.md` | internal-RC posture boundaries and prohibited release claims |
| `docs/V1_KNOWN_LIMITATIONS.md` | known limitations that stay outside this docs/checks pass |
| `docs/V1_1_PERFORMANCE_HANDOFF.md` | P2 and later performance-hardening destination |

Expected files:

| Artifact | Purpose | Expected state |
|---|---|---|
| `docs/V1_PERFORMANCE_CLOSURE_MATRIX.md` | closure matrix and gap classification | present |
| `scripts/check_v1_performance_closure_matrix.py` | deterministic matrix scope and completeness check | present |
| `tests/test_v1_performance_closure_matrix.py` | checker coverage | present |
| `docs/ROADMAP.md` | preserve roadmap while marking only Closure Matrix as completed after checks | updated |

Forbidden paths:

| Boundary | Forbidden task diff |
|---|---|
| Source registries | `00_ADMIN/source_registry*`, `00_ADMIN/source_registries/`, `data/source_registry.csv` |
| Raw sources | `01_RAW_SOURCES/` |
| Chunk artifacts | `03_PROCESSED_KB/chunks/`, `data/chunks.jsonl` |
| Vector/embedding behavior | `04_VECTOR_DB/`, `src/asperitas_agent/embeddings.py` |
| Runtime RAG behavior | `05_RAG_PIPELINE/scripts/asperitas_kb.py`, `src/asperitas_agent/retrieval*`, `src/asperitas_agent/reranking.py`, `src/asperitas_agent/answer_generation.py` |

Risks:

| Severity | Risk | Mitigation |
|---|---|---|
| P0 | Protected source, chunk, vector, embedding, retrieval, ranking, reranker, generation, or runtime RAG path changes. | Stop and revert task-owned protected-path edits before merge. |
| P1 | A row has GO/NO-GO language without a concrete evidence command and result. | Checker requires every MVP/gate row to include command/result/owner action. |
| P1 | Roadmap advances beyond Closure Matrix. | Checker blocks P0/P1 Fix, Final Regression, tag, dry-run, or internal release completion claims. |
| P1 | Release-readiness posture is mistaken for final RC, internal release, or production readiness. | Use NO-GO language for later release steps and keep decision log unchanged unless posture changes. |
| P2 | Future answer-faithfulness and external benchmark parity remain outside V1 matrix scope. | Carry to V1.1 performance handoff. |

## B. Acceptance Matrix

GO here means the V1 gate has documented evidence and passed the listed command in this closure-matrix verification run. It does not mean final RC readiness, internal dry-run readiness, internal release readiness, production deployment, or source expansion completion.

| MVP/Gate | Status | Evidence command | Result | Gap severity | Owner action | GO/NO-GO |
|---|---|---|---|---|---|---|
| MVP-001 | verified | `python scripts/verify_artifacts.py` | exit code 0 in closure verification | P0 none; P1 none; P2 none | Keep artifact verifier green. | GO for artifact-layout gate; NO-GO for release completion. |
| MVP-002 | verified | `python scripts/run_retrieval_eval.py --retriever baseline --limit 5` | exit code 0 in closure verification | P0 none; P1 none; P2 limited sample only | Preserve baseline comparability; defer wider eval to final regression/V1.1. | GO for baseline eval evidence; NO-GO for final regression claim. |
| MVP-002.5 | verified | `python -m pytest tests/test_retrieval_eval.py tests/test_eval_metrics.py tests/test_eval_artifacts.py tests/test_eval_manifest.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 none | Keep eval fixtures and thresholds intact. | GO for eval baseline tests; NO-GO if thresholds weaken. |
| MVP-003 | verified | `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5` | exit code 0 in closure verification | P0 none; P1 none; P2 limited sample only | Preserve metadata-aware mode as comparable, non-default evidence. | GO for MVP003 eval evidence; NO-GO for retrieval tuning claim. |
| MVP-004 | verified | `python -m pytest tests/test_chunking.py tests/test_chunk_section_audit.py tests/test_metadata_integrity.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 no fresh full chunk-quality narrative | Keep chunk artifacts unchanged in this task. | GO for chunk/metadata test gate; NO-GO for chunk mutation. |
| MVP-005 | verified | `python -m pytest tests/test_embeddings.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 no vector tuning in scope | Keep embedding/vector boundary only; no provider changes. | GO for boundary tests; NO-GO for vector behavior changes. |
| MVP-006 | verified | `python -m pytest tests/test_hybrid_scoring.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 hybrid remains measured behavior, not default release claim | Preserve default retrieval behavior. | GO for scoring contract; NO-GO for default-mode changes. |
| MVP-007 | verified | `python -m pytest tests/test_reranking.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 no fresh ordering improvement claim | Keep reranker behavior unchanged. | GO for reranker boundary; NO-GO for ranking mutation. |
| MVP-008 | verified | `python -m pytest tests/test_answer_generation.py tests/test_agent_e2e_regression.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 no human answer-faithfulness review in this pass | Keep source-grounded answer contract unchanged. | GO for answer contract tests; NO-GO for unsupported generation claims. |
| MVP-009 | verified | `python -m pytest tests/test_compliance.py tests/test_guardrails.py tests/test_security_guard.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 human review still required for sensitive outputs | Keep security/compliance gates strict. | GO for guardrail tests; NO-GO for weakened security posture. |
| MVP-010 | verified | `python -m pytest tests/test_chat_workflow.py tests/test_ask_agent_cli.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 dry-run only | Keep chat/API QA internal and source-grounded. | GO for dry-run surface tests; NO-GO for external action claims. |
| MVP-014 | verified | `python -m pytest tests/test_role_registry.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 none | Preserve role authority boundaries. | GO for role registry tests; NO-GO for authority expansion. |
| MVP-015 | verified | `python -m pytest tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 benchmark parity remains future-facing | Keep benchmark evidence as calibration, not implementation. | GO for benchmark workflow tests; NO-GO for external benchmark equivalence claims. |
| MVP-016 | verified | `python -m pytest tests/test_skill_registry.py tests/test_skill_discovery.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 connector execution not in scope | Keep skill layer local and deterministic. | GO for skill tests; NO-GO for external connector automation claims. |
| MVP-017 | verified | `python -m pytest tests/test_eval_report.py tests/test_eval_regression_gate.py tests/test_golden_agent_eval.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 LLM-as-judge/future RAGAS parity not in scope | Keep deterministic eval layer; defer broader evals. | GO for eval suite tests; NO-GO for ground-truth overclaim. |
| MVP-018 | verified | `python -m pytest tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 dry-run workflow only | Preserve read-only/dry-run workflow posture. | GO for workflow tests; NO-GO for autonomous execution. |
| MVP-019A | verified | `python -m pytest tests/test_audit_trace.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 none | Keep audit trace reproducible. | GO for audit tests; NO-GO if trace cannot be reproduced. |
| MVP-019B | verified | `python -m pytest tests/test_workflow_audit.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 none | Keep workflow audit non-mutating for protected artifacts. | GO for audit bridge tests; NO-GO for protected artifact mutation. |
| MVP-019C | verified | `python scripts/run_security_guard.py && python -m pytest tests/test_security_guard.py` | covered by full `python -m pytest` plus release-readiness/security checks exit code 0 in closure verification | P0 none; P1 none; P2 human review remains required | Preserve restricted-source and unsafe-claim controls. | GO for security guard evidence; NO-GO for weakened controls. |
| MVP-019D | verified | `python -m pytest tests/test_chat_workflow.py` | covered by full `python -m pytest` exit code 0 in closure verification | P0 none; P1 none; P2 dry-run only | Keep chat QA workflow source-grounded. | GO for chat QA tests; NO-GO for external action behavior. |
| MVP-019E | verified | `python scripts/check_v1_release_readiness.py --json` | exit code 0 with `ready_for_internal_rc` posture in closure verification | P0 none; P1 release posture must not be escalated; P2 final release evidence pending | Treat release readiness as posture evidence only; do not claim final RC/internal release. | GO for internal-RC posture evidence; NO-GO for final RC, dry-run, internal release, or production claims. |
| Stage-gate scope | verified | `python scripts/check_v1_stage_gate_scope.py` | exit code 0 in closure verification | P0 none; P1 none; P2 none | Keep later roadmap steps pending. | GO for scope integrity; NO-GO if roadmap advances later steps. |
| MVP performance pack | verified | `python scripts/check_v1_mvp_performance_pack.py` | exit code 0 in closure verification | P0 none; P1 none; P2 none | Keep scorecard complete. | GO for performance-pack integrity; NO-GO if evidence fields disappear. |
| Closure matrix | verified | `python scripts/check_v1_performance_closure_matrix.py` | exit code 0 in closure verification | P0 none; P1 none; P2 none | Keep this matrix complete and bounded. | GO for matrix completion after checks pass; NO-GO for later roadmap completion. |

## C. Regression Boundary

No source/raw/chunk/vector/embedding/retrieval/ranking/reranker/generation/runtime RAG mutation is allowed in this task.

| Check | Expected result | Evidence |
|---|---|---|
| Protected path review | no protected task diff | `python scripts/check_v1_performance_closure_matrix.py` |
| Stage-gate scope | pass | `python scripts/check_v1_stage_gate_scope.py` |
| Performance-pack scope | pass | `python scripts/check_v1_mvp_performance_pack.py` |
| Artifact integrity | pass | `python scripts/verify_artifacts.py` |
| Baseline retrieval smoke | pass with limit 5 | `python scripts/run_retrieval_eval.py --retriever baseline --limit 5` |
| MVP003 retrieval smoke | pass with limit 5 | `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5` |
| Full pytest suite | pass | `python -m pytest` |
| Diff hygiene | pass | `git diff --check` |

## D. License, Security, and Decision Log

License boundary:

- No dependency, source copy, source ingestion, crawling, benchmark implementation, vector DB, or third-party benchmark adoption is introduced.
- Existing benchmark references remain calibration metadata only.

Security boundary:

- Public, investor, partner, legal, regulatory, wet-lab-sensitive, deployment, and production claims still require human review and separate approval.
- Internal dry-run and internal release remain pending roadmap steps.

Decision-log posture:

- No decision log update is required because this matrix does not change readiness posture beyond "V1 Performance Closure Matrix completed after checks pass; next step remains P0/P1 Gap Fix Only if P0/P1 gaps exist, otherwise preserve later roadmap gates."
- Add a decision log only if a future run changes readiness posture, rejects an MVP gate, or authorizes a P0/P1 remediation decision.

## Gap Classification

| Severity | Gap | Owner action | Allowed next step |
|---|---|---|---|
| P0 | None identified by this docs/tests/checks closure matrix. | Stop if protected paths change or any evidence command fails. | Yes, only if a P0 appears before merge. |
| P1 | Release-readiness posture can be misread as final RC, internal dry-run, internal release, or production readiness. | Keep NO-GO language for later release steps and require fresh final-regression evidence before any later claim. | Yes. |
| P1 | Closure matrix evidence depends on the current verification run and must not be copied into release notes without re-running commands. | Re-run the listed commands in the implementing PR/check context before using any GO language. | Yes. |
| P2 | Retrieval evidence is limited to `--limit 5` smoke comparisons in this matrix, not full final regression. | Defer full final regression to its roadmap step. | No. |
| P2 | Answer-faithfulness scoring and external benchmark parity remain outside V1 docs/checks scope. | Carry to `docs/V1_1_PERFORMANCE_HANDOFF.md`. | No. |

Only P0/P1 items are allowed as the next remediation step. P2 items stay in V1.1 or later performance-hardening work.

## Verification Commands

```powershell
python -m pytest
python scripts/verify_artifacts.py
python scripts/check_v1_stage_gate_scope.py
python scripts/check_v1_mvp_performance_pack.py
python scripts/check_v1_release_readiness.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/check_v1_performance_closure_matrix.py
git diff --check
```

## Overall GO/NO-GO

GO for completing the V1 Performance Closure Matrix only if all verification commands pass, protected paths remain unchanged, every matrix row keeps status/evidence/result/gap/owner/action/GO-NO-GO content, and later roadmap steps remain pending.

NO-GO for final RC readiness, internal dry-run readiness, internal release readiness, production deployment, source expansion, ingestion, vector tuning, runtime RAG mutation, Final Regression completion, tag creation, or release creation.
