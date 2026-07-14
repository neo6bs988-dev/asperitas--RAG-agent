# Retired Current-State Roadmap

## Status

This file is intentionally retained as a stable compatibility pointer because multiple durable repository documents link to this path. It is no longer a mutable status dashboard and must not be updated after every pull request, phase transition, or merge.

## Mutable Execution Authority

Current repository state is determined from live GitHub evidence:

- the latest merged commit on `main`;
- open, Draft, Ready, Closed, and Merged pull requests;
- exact-head CI and Quality Gates results;
- relevant tests, evaluations, artifacts, issues, and decision records;
- explicit human authorization.

GitHub evidence controls current completion state, current branch or PR identity, exact SHAs, and the immediate next action.

## Durable Direction

Use [`ROADMAP.md`](ROADMAP.md) for durable development order and capability gates. Use scoped preflight documents and decision logs for technical contracts, acceptance criteria, rejected alternatives, residual risks, and rollback boundaries.

`ROADMAP.md` is not a live status dashboard. Historical documents remain valid only for their scoped contracts and recorded evidence; stale phase labels, dates, SHAs, or “next step” text do not override live GitHub evidence.

## Operating Rule

Do not create a replacement `CURRENT_STATE.md`, `STATUS.md`, `LATEST_STATE.md`, dated roadmap, or other manually synchronized status file. Resolve mutable state during task preflight from GitHub and preserve only durable rules in repository documentation.

## Truth Boundary

Repository documents, plans, fixtures, evaluators, and scaffolds do not by themselves prove retrieval improvement, protected-holdout generalization, production RAG, production vector DB or KG, production latency, legal or regulatory approval, biosafety or biosecurity approval, wet-lab validation, autonomous execution, production readiness, or biological foundation-model capability.
