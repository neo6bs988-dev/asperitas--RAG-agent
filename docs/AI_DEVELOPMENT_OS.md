# AI Development OS

The Asperitas AI Development OS is the operating model for building source-grounded RAG agents with Codex, GitHub, tests, evals, reusable skills, and executable quality gates.

## Workflow, Pipeline, Skill

- Workflow: the human + Codex operating loop from objective to verification, commit, review, and next task.
- Pipeline: executable system behavior such as ingestion, chunking, retrieval, embeddings, vector indexing, reranking, answer generation, or eval.
- Skill: reusable instruction for Codex that tells it when to act, what inputs to gather, which gates apply, how to fail safely, and how to report.

Use workflows to coordinate people, pipelines to run systems, and skills to make Codex repeat the right judgment.

## How The Pieces Work Together

- `AGENTS.md` defines repo-wide behavior, safety rules, testing expectations, and reporting format.
- `.agents/skills/*/SKILL.md` files define reusable task playbooks for RAG development, eval gates, source grounding, compliance, PR review, MVP release management, and MVP-005 embeddings/vector DB work.
- `docs/WORKFLOW.md` defines the standard human + Codex loop.
- `docs/QUALITY_GATES.md` defines checks that must pass before work is done.
- `docs/MVP004_BASELINE_METRICS.md` defines the current retrieval baseline, commands, regression rules, and report format.
- `docs/PIPELINE_AUTOMATION.md` explains the local, CI, PR, and MVP release automation layers.
- `docs/CODEX_TASK_PROMPTS.md` provides reusable prompts for Codex tasks and recovery.
- `docs/PROJECT_CONTEXT.md` and `docs/ROADMAP.md` keep the project stage and MVP path visible.
- `.github/workflows/quality-gates.yml` runs executable checks on push, pull request, and manual dispatch.
- `.github/pull_request_template.md` makes review scope, tests, metrics, source-grounding, and compliance explicit.
- Tests verify source code behavior.
- Retrieval evals verify retrieval quality and regression risk.
- Scripts automate repeated checks when a manual gate becomes frequent.
- GitHub stores review history, commits, pull requests, and release decisions.

## Operating Loop

1. User defines objective.
2. Codex reads `AGENTS.md` and relevant skills.
3. Codex inspects repo files before editing.
4. Codex makes the smallest safe change.
5. Tests/evals/scripts run according to `docs/QUALITY_GATES.md`.
6. Results are reported with metrics, risks, skipped checks, and next task.
7. GitHub commit/PR captures review history.
8. MVP release manager decides whether to close or continue a milestone.

## Reuse For Future Asperitas Agents

To reuse this system:

1. Copy `AGENTS.md`, `docs/WORKFLOW.md`, `docs/QUALITY_GATES.md`, `docs/PIPELINE_AUTOMATION.md`, `docs/CODEX_TASK_PROMPTS.md`, and the relevant `.agents/skills` directory.
2. Replace project mission, source hierarchy, compliance domains, and MVP roadmap.
3. Keep the same gate pattern: inspect, plan, implement, test, eval, review, report.
4. Add agent-specific skills only when repeated work needs a dedicated checklist.
5. Keep every skill tied to concrete inputs, commands, quality gates, and failure conditions.
6. Add CI only after commands are stable enough to run repeatedly.

Do not treat the OS as a static document. Update it when repeated mistakes, new risks, new pipelines, or new MVP stages appear.

## Current Strategic Upgrade

The repo now has three layers:

1. Governance layer: `AGENTS.md`, workflow docs, quality gates, skills.
2. Execution layer: scripts, tests, eval commands, GitHub Actions.
3. Review layer: PR template, MVP baseline metrics, release manager skill.

The next technical frontier is MVP-005: embeddings + vector DB, implemented without breaking MVP-004 deterministic retrieval and source-grounding guarantees.