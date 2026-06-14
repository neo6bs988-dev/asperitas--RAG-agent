# AI Development OS

The Asperitas AI Development OS is the operating model for building source-grounded RAG agents with Codex, GitHub, tests, evals, and reusable skills.

## Workflow, Pipeline, Skill

- Workflow: the human + Codex operating loop from objective to verification, commit, and next task.
- Pipeline: executable system behavior such as ingestion, chunking, retrieval, reranking, answer generation, or eval.
- Skill: reusable instruction for Codex that tells it when to act, what inputs to gather, which gates apply, and how to report.

Use workflows to coordinate people, pipelines to run systems, and skills to make Codex repeat the right judgment.

## How The Pieces Work Together

- `AGENTS.md` defines repo-wide behavior, safety rules, testing expectations, and reporting format.
- `.agents/skills/*/SKILL.md` files define reusable task playbooks for RAG development, eval gates, source grounding, compliance, PR review, and MVP release management.
- `docs/WORKFLOW.md` defines the standard human + Codex loop.
- `docs/QUALITY_GATES.md` defines checks that must pass before work is done.
- `docs/PROJECT_CONTEXT.md` and `docs/ROADMAP.md` keep the project stage and MVP path visible.
- Tests verify source code behavior.
- Retrieval evals verify retrieval quality and regression risk.
- Scripts should automate repeated checks when a manual gate becomes frequent.
- GitHub stores review history, commits, pull requests, and release decisions.

## Reuse For Future Asperitas Agents

To reuse this system:

1. Copy `AGENTS.md`, `docs/WORKFLOW.md`, `docs/QUALITY_GATES.md`, and the relevant `.agents/skills` directory.
2. Replace project mission, source hierarchy, compliance domains, and MVP roadmap.
3. Keep the same gate pattern: inspect, plan, implement, test, eval, review, report.
4. Add agent-specific skills only when repeated work needs a dedicated checklist.
5. Keep every skill tied to concrete inputs, commands, quality gates, and failure conditions.

Do not treat the OS as a static document. Update it when repeated mistakes, new risks, or new pipelines appear.

