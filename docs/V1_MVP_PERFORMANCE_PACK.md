# V1 MVP Performance Pack Backfill

Status: completed performance scorecard backfill for internal RC preparation

Scope: docs/tests/checks only. No runtime retrieval, generation, ingestion, vector, embedding, chunking, registry, ranking, reranker, or source artifact behavior changed.

Base: `36ab8814b5bdf7f6cd440acb9b1da428c492b190`

## A. Preflight

This pack backfills verification scorecards for the implemented V1 MVP surface before internal RC evaluation. It does not start the V1 Performance Closure Matrix, P0/P1 Gap Fix Only, Final Pre-RC Regression, tag creation, internal dry-run, or internal release.

Expected scorecard files and checks:

| Artifact | Purpose | Expected state |
|---|---|---|
| `docs/V1_MVP_PERFORMANCE_PACK.md` | MVP metrics, thresholds, commands, gaps, and GO/NO-GO states | present |
| `scripts/check_v1_mvp_performance_pack.py` | deterministic docs-only scorecard boundary check | present |
| `tests/test_v1_mvp_performance_pack.py` | checker coverage | present |
| `docs/ROADMAP.md` | preserve V1 roadmap while marking only this step as completed | updated |
| `docs/V1_PLAYBOOK_V3_STAGE_GATE_ABSORPTION.md` | Playbook v3 and Stage-Gate status | unchanged completed posture |

Forbidden changes:

- source registry or source registry workbook mutation;
- raw source ingestion, crawling, or source expansion;
- processed chunk, raw chunk, vector, embedding, retrieval, ranking, reranker, or answer-generation logic mutation;
- eval fixture weakening or test threshold weakening;
- roadmap advancement beyond MVP Performance Pack Backfill;
- claims of production readiness, final RC readiness, public release readiness, internal dry-run completion, or internal release completion.

Primary risks:

| Risk | Severity | Mitigation |
|---|---|---|
| Performance metrics are documented without fresh command output | P1 | Every pass claim requires a command and this pack reports GO/NO-GO by gate, not final release status. |
| Existing release-readiness language is mistaken for final release readiness | P1 | This pack labels release readiness as internal-RC posture only and keeps later V1 steps pending. |
| Regression check misses protected runtime edits | P0 | Use `git diff --name-only` review plus `scripts/check_v1_stage_gate_scope.py` and this pack checker. |
| Some future MVP metrics remain unimplemented | P2 | Mark future or non-default performance metrics as unresolved gaps instead of claiming closure. |

## B. MVP Acceptance Scorecard

Each MVP row has one primary metric, threshold, command, and GO/NO-GO rule. GO here means the scorecard has a verifiable gate for the MVP surface; it does not mean production readiness or final RC readiness.

| MVP | Surface | Metric | Threshold | Command | GO/NO-GO |
|---|---|---|---|---|---|
| MVP-001 | Foundation and artifact layout | Core artifact verifier exit status | exit code 0 | `python scripts/verify_artifacts.py` | GO if artifact verifier passes and required files remain present; NO-GO if required artifacts are missing. |
| MVP-002 | Retrieval structure | Baseline retrieval eval exit status and reported query count | exit code 0 with `--limit 5` completing | `python scripts/run_retrieval_eval.py --retriever baseline --limit 5` | GO if baseline eval completes without runtime mutation; NO-GO if metric cannot be reproduced. |
| MVP-002.5 | Evaluation baseline | Pytest eval coverage exit status | exit code 0 | `python -m pytest tests/test_retrieval_eval.py tests/test_eval_metrics.py tests/test_eval_artifacts.py tests/test_eval_manifest.py` | GO if eval tests pass; NO-GO if eval fixtures or thresholds are weakened. |
| MVP-003 | Metadata-aware retrieval | MVP003 retrieval eval exit status and reported query count | exit code 0 with `--limit 5` completing | `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5` | GO if metadata-aware eval completes without protected artifact mutation; NO-GO if metadata-aware mode cannot be measured. |
| MVP-004 | Structure-aware chunking | Chunk and metadata integrity test exit status | exit code 0 | `python -m pytest tests/test_chunking.py tests/test_chunk_section_audit.py tests/test_metadata_integrity.py` | GO if chunk/metadata tests pass and chunk artifacts are unchanged; NO-GO if chunk data or logic mutates in this pack. |
| MVP-005 | Embedding and vector boundary | Embedding schema and vector boundary tests | exit code 0 | `python -m pytest tests/test_embeddings.py` | GO if boundary tests pass without provider, vector DB, or tuning changes; NO-GO if vector behavior is introduced or changed. |
| MVP-006 | Hybrid retrieval | Hybrid scoring tests | exit code 0 | `python -m pytest tests/test_hybrid_scoring.py` | GO if scoring contract tests pass without changing retrieval defaults; NO-GO if hybrid becomes default or traceability regresses. |
| MVP-007 | Reranker boundary | Reranking tests | exit code 0 | `python -m pytest tests/test_reranking.py` | GO if reranker contract tests pass without reranker logic edits; NO-GO if ordering behavior changes in this pack. |
| MVP-008 | Source-grounded answer generation | Answer generation and end-to-end agent regression tests | exit code 0 | `python -m pytest tests/test_answer_generation.py tests/test_agent_e2e_regression.py` | GO if citation and insufficient-evidence behavior tests pass; NO-GO if generation logic or claims expand. |
| MVP-009 | Compliance and guardrails | Compliance, guardrail, and security guard tests | exit code 0 | `python -m pytest tests/test_compliance.py tests/test_guardrails.py tests/test_security_guard.py` | GO if high-risk handling tests pass; NO-GO if security or compliance gates are weakened. |
| MVP-010 | Internal chat/API QA surface | Chat workflow and CLI smoke tests | exit code 0 | `python -m pytest tests/test_chat_workflow.py tests/test_ask_agent_cli.py` | GO if dry-run chat/CLI tests pass; NO-GO if external execution or release claims are introduced. |
| MVP-014 | Agent role registry | Role registry tests | exit code 0 | `python -m pytest tests/test_role_registry.py` | GO if role boundaries remain deterministic; NO-GO if role authority expands. |
| MVP-015 | Benchmark workflow schema | Benchmark workflow tests | exit code 0 | `python -m pytest tests/test_benchmark_workflow.py tests/test_benchmark_workflow_preflight.py` | GO if benchmark schema/preflight tests pass; NO-GO if benchmark evidence is treated as implementation. |
| MVP-016 | Skills layer | Skill registry and discovery tests | exit code 0 | `python -m pytest tests/test_skill_registry.py tests/test_skill_discovery.py` | GO if local skill registry/discovery tests pass; NO-GO if external connector or runtime automation is implied. |
| MVP-017 | Eval suite | Eval report, regression gate, and golden eval tests | exit code 0 | `python -m pytest tests/test_eval_report.py tests/test_eval_regression_gate.py tests/test_golden_agent_eval.py` | GO if deterministic eval layer tests pass; NO-GO if LLM-as-judge output is claimed as ground truth. |
| MVP-018 | Workflow layer | Workflow planner/run/inspector/acceptance tests | exit code 0 | `python -m pytest tests/test_workflow_planner.py tests/test_workflow_run.py tests/test_workflow_inspector.py tests/test_workflow_acceptance.py` | GO if workflow dry-run tests pass; NO-GO if autonomous execution is introduced. |
| MVP-019A | Audit trace | Audit trace tests | exit code 0 | `python -m pytest tests/test_audit_trace.py` | GO if audit serialization tests pass; NO-GO if audit trace cannot be reproduced. |
| MVP-019B | Workflow audit bridge | Workflow audit tests | exit code 0 | `python -m pytest tests/test_workflow_audit.py` | GO if workflow audit tests pass; NO-GO if audit state mutates protected artifacts. |
| MVP-019C | Security guard | Security guard script and tests | exit code 0 | `python scripts/run_security_guard.py && python -m pytest tests/test_security_guard.py` | GO if security guard smoke and tests pass; NO-GO if restricted-source or unsafe-claim controls weaken. |
| MVP-019D | Chat QA workflow | Chat workflow tests | exit code 0 | `python -m pytest tests/test_chat_workflow.py` | GO if chat QA remains dry-run and source-grounded; NO-GO if external action or unsupported answer behavior appears. |
| MVP-019E | Release readiness posture | Release readiness checker exit status | exit code 0 and internal-RC posture only | `python scripts/check_v1_release_readiness.py --json` | GO if checker reports internal-RC posture without production/final-release claims; NO-GO if later roadmap steps are implied complete. |

## C. Regression Boundary

Protected artifact and runtime mutation check:

| Boundary | Expected result | Verification |
|---|---|---|
| Source registry files | unchanged | `git diff --name-only -- 00_ADMIN/source_registry* 00_ADMIN/source_registries data/source_registry.csv` returns no task diff |
| Raw sources | unchanged | `git diff --name-only -- 01_RAW_SOURCES` returns no task diff |
| Chunk artifacts | unchanged | `git diff --name-only -- 03_PROCESSED_KB/chunks data/chunks.jsonl` returns no task diff |
| Vector and embedding behavior | unchanged | no `04_VECTOR_DB`, `src/asperitas_agent/embeddings.py`, or provider changes |
| Retrieval/ranking/reranker/generation behavior | unchanged | no `src/asperitas_agent/retrieval*`, `src/asperitas_agent/reranking.py`, or `src/asperitas_agent/answer_generation.py` changes |
| Stage-gate scope | pass | `python scripts/check_v1_stage_gate_scope.py` |
| Performance-pack scope | pass | `python scripts/check_v1_mvp_performance_pack.py` |
| Whitespace and patch hygiene | pass | `git diff --check` |

## D. License, Security, and Decision Log

License boundary:

- This pack adds no dependency, source copy, source ingestion, benchmark implementation, or third-party content adoption.
- Existing external benchmark references remain calibration metadata only.
- No production knowledge-base ingestion or long-form source summarization is authorized by this pack.

Security boundary:

- Security guard posture must remain at least as strict as the existing `tests/test_security_guard.py` and `scripts/run_security_guard.py` checks.
- Public, investor, partner, legal, regulatory, wet-lab-sensitive, deployment, and production claims still require human review and source evidence.
- Dry-run workflow checks do not authorize autonomous execution or external actions.

Decision-log posture:

- No decision log update is required for this pack because V1 readiness posture does not advance beyond "MVP Performance Pack Backfill completed; next step remains V1 Performance Closure Matrix."
- Add a decision log only if a later run changes V1 readiness posture, rejects an MVP gate, or records a P0/P1 remediation decision.

## Unresolved Gaps

| Severity | Gap | Owner action |
|---|---|---|
| P0 | None introduced by this docs/tests/checks backfill. | Stop if any protected artifact/runtime diff appears before merge. |
| P1 | Fresh full command output must be captured by the implementing PR run before using any GO language in release notes. | Run the verification commands listed below and paste results into PR evidence. |
| P1 | Release-readiness checker language must remain internal-RC posture only. | Re-run `python scripts/check_v1_release_readiness.py --json` during closure matrix, not in this backfill as release completion. |
| P2 | Some future-facing performance dimensions, such as full answer-faithfulness scoring and external benchmark parity, remain out of scope. | Keep them in V1.1/performance handoff, not this pack. |

## Verification Commands

Required for this pack:

```powershell
python -m pytest
python scripts/verify_artifacts.py
python scripts/check_v1_stage_gate_scope.py
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
python scripts/check_v1_mvp_performance_pack.py
git diff --check
```

Optional release-posture smoke for later closure matrix evidence:

```powershell
python scripts/check_v1_release_readiness.py --json
```

## Overall GO/NO-GO

GO for merging the MVP Performance Pack Backfill only if:

- all required verification commands pass;
- no protected artifact or runtime retrieval/generation diff exists;
- every MVP row keeps metric, threshold, command, and GO/NO-GO text;
- P0 gaps remain empty;
- later V1 roadmap steps remain pending.

NO-GO for final RC readiness, internal dry-run readiness, internal release readiness, production deployment, source expansion, Closure Matrix, P0/P1 Fix, or Final Regression. Those steps remain separate V1 roadmap items.
