# MVP-018 Playbook DB Preflight

Date: 2026-06-25
Branch: `mvp018-playbook-db`

## Objective

Add the new agent development workflow playbook to the repository and prepare DB chunking work as a safe, auditable MVP-018 task.

## Added Files

- `docs/PLAYBOOK_AGENT_DEVELOPMENT_WORKFLOW.md`
- `docs/DB_CHUNKING_RUNBOOK.md`

## Current Boundary

This change adds governance and execution runbooks only. It does not by itself prove that new sources were processed into final DB artifacts.

## Required Next Implementation Step

Run Codex against this branch with the prompt in `docs/DB_CHUNKING_RUNBOOK.md`.

Expected work:

1. inspect existing source registry and artifact layout
2. register the new playbook source
3. extract parser-friendly text if needed
4. chunk using existing policy
5. preserve provenance metadata
6. run artifact verification
7. run retrieval eval if retrieval or chunking behavior changes
8. write updated counts into a follow-up decision log

## Verification Required After Codex Work

Expected commands, subject to repository inspection:

```bash
python -m pytest -q
python scripts/verify_artifacts.py
python scripts/evaluate_agent.py
python scripts/run_golden_agent_eval.py
```

## Risks

- Treating a runbook as completed DB work would create a false status claim.
- Updating chunks without retrieval eval may hide recall regressions.
- Duplicating ingestion logic instead of reusing existing scripts may fragment the pipeline.

## Recommended Next Step

Execute MVP-018 Codex implementation from `docs/DB_CHUNKING_RUNBOOK.md`, then update the PR with registry delta, chunk delta, and verification results.
