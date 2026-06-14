# Human + Codex Workflow

Use this workflow for all asperitas-agent changes. The goal is to keep every change small, verifiable, source-grounded, and compliance-aware.

## 1. Clarify Objective

- State the requested outcome in one sentence.
- Identify whether the task is source code, docs, eval, release, compliance, or review.
- Identify the current MVP stage.
- Confirm any constraint that affects safety, confidentiality, GitHub writes, or public/investor-facing claims.

## 2. Select Relevant Skill

Use `AGENTS.md` plus the narrowest applicable skill:

- `.agents/skills/asperitas-rag-development/SKILL.md`
- `.agents/skills/retrieval-eval-quality-gate/SKILL.md`
- `.agents/skills/source-grounding-citation/SKILL.md`
- `.agents/skills/compliance-biosafety-review/SKILL.md`
- `.agents/skills/github-pr-review/SKILL.md`
- `.agents/skills/mvp-release-manager/SKILL.md`

If multiple skills apply, use the strictest gate. Retrieval + compliance + public claims must not be treated as a simple code task.

## 3. Inspect Repo

- Read the relevant files before editing.
- Check existing tests, eval scripts, docs, and recent project context.
- Identify whether retrieval, chunking, citations, compliance, or release state is affected.
- Check `docs/MVP004_BASELINE_METRICS.md` when working on MVP-004 retrieval/chunking behavior.

## 4. Make Plan

- List files to change.
- List verification commands.
- List quality gates that apply.
- Keep the plan small enough to review.
- Avoid changing source code during docs/governance tasks.

## 5. Implement Smallest Safe Change

- Change only files required by the objective.
- Preserve existing behavior unless the objective requires behavior change.
- Do not delete files unless explicitly instructed.
- Prefer additive changes over destructive rewrites.

## 6. Update Tests

- Add or update tests for every source-code behavior change.
- Update eval fixtures when retrieval behavior intentionally changes.
- Keep tests focused on the changed behavior.
- Do not claim test coverage that was not added or run.

## 7. Run Verification

Use the minimum applicable gate from `docs/QUALITY_GATES.md`.

Canonical commands:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5
```

Docs-only changes may skip pytest and retrieval eval, but the report must say why.

## 8. Run Retrieval Eval If Relevant

Run retrieval eval when the change affects:

- chunking
- indexing
- metadata filtering
- scoring
- embeddings
- vector DB behavior
- hybrid retrieval
- reranking
- answer generation

Report both baseline and MVP-003 metadata-aware retriever results unless the task explicitly narrows the scope.

## 9. Summarize Metrics

Report:

- eval dataset
- command
- retriever mode
- top-k settings
- pass/fail count
- metric deltas
- regressions
- known blind spots
- decision: pass / conditional pass / fail

Use `docs/MVP004_BASELINE_METRICS.md` for the current MVP-004 report format.

## 10. Commit and Push

- Review `git diff` before commit.
- Commit only intended files.
- Use a message that names the milestone or quality gate.
- Push to the intended branch.
- Open or update the PR when review is needed.
- Use `.github/pull_request_template.md` for PRs.

## 11. CI Review

The executable CI workflow is `.github/workflows/quality-gates.yml`.

After push or PR:

- Check whether the quality-gates workflow ran.
- If CI fails, treat the task as incomplete until the failure is explained or fixed.
- If CI passes, still perform human review for strategic fit, source-grounding, and compliance.

## 12. Decide Next MVP Task

- Map the result to the roadmap.
- State whether the current MVP remains open or can close.
- Recommend the next concrete task.
- If closing a milestone, use `.agents/skills/mvp-release-manager/SKILL.md`.

## Default Next Step After This Workflow Upgrade

For MVP-004, the next technical task is to run the full quality pipeline, record the observed output under a decision log, and then decide whether to close MVP-004 or move into MVP-005 embeddings + vector DB.