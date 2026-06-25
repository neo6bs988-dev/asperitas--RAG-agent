# Asperitas AI RAG Agent v1.0.0-rc1 Release Notes

Status: draft only; final RC, internal dry-run, and internal release remain pending

Fresh-evidence guard: do not publish these notes, claim GO, create a tag, start an internal dry-run, or claim internal release until the manual release context reruns the required commands and records fresh command output.

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

- full pytest passes
- artifact verifier passes
- release readiness returns `ready_for_internal_rc`
- V1 RC smoke returns `passed`
- chat CLI dry-run returns `dry_run_ready`
- known limitations and V1.1 handoff remain visible

## Human Approval

Tag creation and GitHub release creation are manual, human-approved actions only. This repository change does not create a tag or GitHub release.
