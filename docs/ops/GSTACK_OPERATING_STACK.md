# gstack Operating Stack

Status: docs-only operating guidance

Related issue: #96

Reference: `neo6bs988-dev/gstack` is used as an external AI development operating-stack reference. This repository does not vendor, copy, or execute the gstack source. gstack is treated as P6 external benchmark and operating doctrine, not as Asperitas company truth.

## Purpose

Use gstack as a future AI development operating stack for improving ChatGPT, Codex, Claude Code, and GitHub development loops without changing Asperitas product runtime behavior.

This document defines how gstack concepts fit the Asperitas AI development workflow:

- scope the work before implementation;
- review plans before code changes;
- preserve AOS, PRIME, AGENTS, source hierarchy, and truth rules;
- run repo-specific gates before PRs and releases;
- leave GitHub evidence for every meaningful change.

## Hard Boundaries

This integration is docs-only until a separate approved implementation task changes that status.

Do not modify:

- retrieval behavior;
- ranking or scoring behavior;
- embeddings;
- vector database behavior;
- reranking;
- answer generation;
- source registry data;
- chunk artifacts;
- release artifacts;
- tests, except documentation-link checks if a future docs tool requires them.

Do not claim that production RAG, KG, eval, compliance, wet-lab validation, foundation-model capability, deployment, customer traction, investor commitment, or regulatory approval exists unless verified by repo evidence and approved release material.

## Relationship To AOS And PRIME

gstack is subordinate to:

1. latest user instruction;
2. repository `AGENTS.md`;
3. ASPERITAS PRIME v2.0;
4. inherited AOS layers;
5. source hierarchy and truth rules;
6. compliance and biosafety escalation rules.

If a gstack-style command, role, or recommendation conflicts with Asperitas governance, Asperitas governance wins.

## Current Path: Codex Docs-Only Integration

Current status:

- no gstack install is required;
- no `.claude/`, `.codex/`, generated skills, browser daemon, or gstack runtime files are added to this repository;
- Codex may use this documentation to structure planning, implementation, review, validation, and PR evidence;
- all product behavior remains unchanged.

Use this path for issue #96 and future docs-only workflow hardening.

## Later Path: Claude Code Plus gstack

After a stable internal release and explicit human approval, Asperitas may install Claude Code and gstack outside the product runtime path.

Planned approach:

1. Install Claude Code on a development machine.
2. Install gstack from the upstream repository into the user's Claude Code skill location.
3. Run gstack in optional team mode first.
4. Observe quality, latency, review burden, and failure modes across several internal PRs.
5. Move to required team mode only after a stable internal release, documented rollback path, and owner approval.

This later path must remain a development-operations layer. It must not become a hidden dependency for runtime code, retrieval quality, source truth, or release artifacts.

## Optional Team Mode Before Required Mode

Recommended adoption order:

1. Personal install for one development operator.
2. Optional team mode for internal contributors.
3. Documented runbook with observed benefits and failure modes.
4. Required mode only after stable internal release and explicit approval.

Required mode is blocked until:

- there is a stable internal release baseline;
- the team has a rollback process;
- PR evidence shows the workflow improves review quality without increasing overclaim risk;
- no runtime or artifact mutation is introduced by the operating-stack setup.

## Codex Host Setup Later

The gstack reference repo documents host support for multiple coding agents, including Codex-oriented generated skills. Asperitas may evaluate a Codex host setup later as a separate task.

Future Codex host setup must:

- be explicit and reversible;
- avoid vendoring full gstack source into this repo;
- keep generated agent skills outside product runtime paths unless separately approved;
- preserve `AGENTS.md` and PRIME/AOS truth rules;
- include a rollback note and validation evidence.

## Standard Development Loop

The standard performance-improvement loop is:

1. ChatGPT scope.
2. `/office-hours`.
3. `/autoplan`.
4. `/plan-eng-review`.
5. Codex implementation.
6. `/review`.
7. `/cso`.
8. `/qa`.
9. `/ship`.
10. `/document-release`.
11. `/retro`.
12. GitHub evidence.

For this repository, those names are operating roles until gstack is installed. They do not imply the gstack runtime actually ran.

## Asperitas Gate Mapping

Map the loop to repo gates as follows:

| Loop step | Asperitas evidence |
|---|---|
| ChatGPT scope | Issue body, acceptance criteria, hard boundaries |
| `/office-hours` | Problem framing, scope risks, missing evidence |
| `/autoplan` | Implementation plan, changed files, test/eval plan |
| `/plan-eng-review` | Architecture, failure modes, source/truth boundary check |
| Codex implementation | Small scoped changes, no unrelated runtime mutation |
| `/review` | Diff review, no source code for docs-only work |
| `/cso` | Security, confidentiality, IP, public-claim risk review |
| `/qa` | Local checks and smoke tests appropriate to changed surface |
| `/ship` | Commit, branch, PR, linked issue |
| `/document-release` | Release evidence docs updated when behavior changes |
| `/retro` | Lessons, skipped checks, next action |
| GitHub evidence | PR body, commands run, validation output, risk notes |

## Canonical Gate Commands

Run from the repository root when relevant:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/check_v1_release_readiness.py --json
python scripts/run_v1_rc_smoke.py --json
python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json
```

For docs-only changes, `python -m pytest` may be skipped when no source code or tests changed, but the skip must be reported. `git diff --check` and no-runtime-file confirmation are still required.

## Source And Truth Boundary Check

Every gstack-assisted workflow must confirm:

- P6 gstack material is used as external operating doctrine only;
- P1 internal Asperitas documents remain the authority for company facts;
- unsupported implementation claims are labeled or removed;
- speculative future workflows are clearly marked future or optional;
- no confidential or personal data is added to public-facing docs.

## Rollback

Rollback is simple for this docs-only phase:

1. Revert the docs under `docs/ops/`.
2. Close or update the PR.
3. No runtime, retrieval, artifact, or test rollback should be needed because this phase does not touch those surfaces.
