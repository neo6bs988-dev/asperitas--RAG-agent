# Asperitas AI RAG Agent v1.0.0-rc1 Release Notes

Status: draft only; final pre-RC regression evidence recorded for RC preparation; final RC, internal dry-run, and internal release remain pending

Fresh-evidence guard: final pre-RC regression evidence is recorded in `docs/V1_FINAL_PRE_RC_REGRESSION.md` for `main` at `ebe19bd174d75a06a6e46e001776b9f60735f910`. Do not publish these notes, create a tag, start an internal dry-run, or claim internal release from this documentation change; this documentation change does not claim production readiness.

## Scope

- local/internal chat-style QA control wrapper
- dry-run CLI by default
- security guard
- workflow planning/run/inspection/acceptance
- audit trace
- eval/regression artifacts
- artifact verification
- release readiness checker

## Non-Scope

- public SaaS
- production customer deployment
- default real RAG answer provider
- default vector DB/reranker replacement
- autonomous wet-lab execution
- external connector automation
- clinical/regulatory/commercial performance claim

## What This RC Verifies

When the required manual closeout checks are rerun and recorded, V1.0.0-rc1 is intended to verify that the local control-plane stack can run deterministic readiness checks, security checks, chat dry-run workflow checks, audit serialization, artifact verification, and regression tests.

It does not verify public launch readiness, customer deployment readiness, autonomous research operation, regulatory approval, clinical performance, commercial performance, or biological model capability.

## Required Manual Closeout Checks

- full pytest passes: recorded, 543 passed
- artifact verifier passes: recorded, 48 registry records and 2821 chunks
- release readiness returns `ready_for_internal_rc`: recorded, 14/14 checks passed
- security guard passes with explicit input: recorded, low risk and 0 findings
- V1 RC smoke returns `passed`: recorded, 5/5 checks passed
- chat CLI dry-run returns `dry_run_ready`: recorded; no answer provider wired warning remains
- baseline and MVP003 retrieval evals pass command exits: recorded, 34.4% and 93.8% overall pass rates
- known limitations and V1.1 handoff remain visible

## Human Approval

Tag creation and GitHub release creation are manual, human-approved actions only. This repository change does not create a tag or GitHub release.
