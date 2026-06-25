# V1 Final Pre-RC Regression Evidence

Status: completed for RC preparation only; `v1.0.0-rc1`, internal dry-run, and `v1.0.0-internal` remain pending.

Main SHA: `ebe19bd174d75a06a6e46e001776b9f60735f910`

Date: 2026-06-25

## Boundary

This evidence records final pre-RC regression checks on `main`. It does not create or approve a tag, GitHub release, internal dry-run, internal release, production deployment, public SaaS launch, customer deployment, autonomous wet-lab operation, regulatory readiness, clinical performance, commercial performance, or biological model capability.

No tracked registry, raw source, chunk, vector, embedding, retrieval, ranking, reranker, generation, answer-provider, or runtime RAG path changed during this evidence run. P2 performance gaps remain deferred.

## Command Evidence

| Check | Result |
|---|---|
| `python -m pytest` | Passed: 543 passed |
| `python scripts/verify_artifacts.py` | Passed: `ok: true`, 48 registry records, 2821 chunks |
| `python scripts/check_v1_stage_gate_scope.py` | Passed |
| `python scripts/check_v1_mvp_performance_pack.py` | Passed |
| `python scripts/check_v1_performance_closure_matrix.py` | Passed |
| `python scripts/check_v1_p0_p1_gap_fix.py` | Passed |
| `python scripts/check_v1_release_readiness.py --json` | Passed: `ready_for_internal_rc`, 14/14 checks |
| `python scripts/run_security_guard.py --input .pytest_tmp/final_pre_rc_security_guard_input.json --json` | Passed: `ok: true`, `risk_level: low`, `blocked: false`, findings 0 |
| `python scripts/run_v1_rc_smoke.py --json` | Passed: 5/5 checks |
| `python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json` | Passed: `dry_run_ready`; no answer provider wired warning remains |
| `python scripts/run_retrieval_eval.py --retriever baseline --limit 5` | Passed command exit; overall pass rate 34.4% |
| `python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5` | Passed command exit; overall pass rate 93.8% |
| `git diff --check` | Passed |
| `git status --short --branch` | Clean `main...origin/main` at evidence capture |

## Retrieval Metrics

| Retriever | Overall | Relaxed overall | Source @3 | Source @5 | Path context |
|---|---:|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 34.4% | 43.8% | 0.0% |
| mvp003 | 93.8% | 93.8% | 96.9% | 100.0% | 100.0% |

Baseline failures remain known evaluation debt. MVP003 failures remain limited to `MVP0025-Q001` and `MVP0025-Q004`. These do not change the P2 deferral posture.

## Remaining Pending Steps

- `v1.0.0-rc1` tag creation remains pending human approval.
- GitHub release creation remains pending human approval.
- Internal dry-run remains pending.
- `v1.0.0-internal` remains pending.
- P2 performance and answer-quality gaps remain deferred to later work.
