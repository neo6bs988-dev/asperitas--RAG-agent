# Asperitas AI RAG Agent v1.0.0-rc1 Release Notes

Status: internal release candidate

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

V1.0.0-rc1 verifies that the local control-plane stack can run deterministic readiness checks, security checks, chat dry-run workflow checks, audit serialization, artifact verification, and regression tests.

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
