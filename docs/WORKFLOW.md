# Human + Codex Workflow

Use this workflow for all asperitas-agent changes.

## 1. Clarify Objective

- State the requested outcome in one sentence.
- Identify whether the task is source code, docs, eval, release, compliance, or review.
- Confirm any constraint that affects safety, confidentiality, or GitHub writes.

## 2. Inspect Repo

- Read the relevant files before editing.
- Check existing tests, eval scripts, docs, and recent project context.
- Identify whether retrieval, chunking, citations, compliance, or release state is affected.

## 3. Make Plan

- List files to change.
- List verification commands.
- List quality gates that apply.
- Keep the plan small enough to review.

## 4. Implement Smallest Safe Change

- Change only files required by the objective.
- Preserve existing behavior unless the objective requires behavior change.
- Do not delete files unless explicitly instructed.

## 5. Update Tests

- Add or update tests for every code change.
- Update eval fixtures when retrieval behavior intentionally changes.
- Keep tests focused on the changed behavior.

## 6. Run Verification

- Run `pytest` after source code changes.
- Run targeted checks first, then broader checks when risk is higher.
- Report commands and results exactly.

## 7. Run Retrieval Eval If Relevant

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

## 8. Summarize Metrics

Report:

- eval dataset
- command
- top-k settings
- pass/fail count
- metric deltas
- regressions
- known blind spots

## 9. Commit and Push

- Review `git diff` before commit.
- Commit only intended files.
- Use a message that names the milestone or quality gate.
- Push to the intended branch.
- Open or update the PR when review is needed.

## 10. Decide Next MVP Task

- Map the result to the roadmap.
- State whether the current MVP remains open or can close.
- Recommend the next concrete task.

