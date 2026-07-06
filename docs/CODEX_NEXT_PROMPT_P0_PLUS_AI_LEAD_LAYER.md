# Codex Next Prompt - P0+ AI Lead Operating Layer

Use this prompt for the next repo update after the P0+ AI Lead doctrine merge.

```text
Codex Reasoning Level: 매우높음

Goal:
Turn the P0+ AI Lead Operating Layer from doctrine into one small repo-enforced asset that improves workflow, evaluation, governance, or organizational learning without changing runtime RAG behavior.

Scope:
- Read README.md, AGENTS.md, docs/TOP_SOURCE_TRIAD_OPERATING_BASELINE.md, docs/P0_PLUS_AI_LEAD_OPERATING_LAYER.md, and .github/PULL_REQUEST_TEMPLATE.md.
- Choose exactly one narrow implementation target:
  1. add a failure-taxonomy fixture for repeated AI-agent development failures,
  2. add a governance checklist for source/eval/compliance PRs,
  3. add a small parser/test that verifies PR-template required P0+ fields are present,
  4. add a workflow README that converts one recurring task into an SOP.
- Do not touch retrieval, generation, vector DB, KG, ingestion, external services, dependencies, or production config.

Evidence:
- Treat the two reports `글로벌 AI 리더·기업·엔지니어 종합 보고서.pdf` and `프로젝트 내 AI 리드 내재화 실행계획 보고서.pdf` as operating doctrine only.
- Do not claim production AI Lead organization, production eval system, governance OS, RAG/KG, tracing, compliance approval, or foundation-model capability.

Constraints:
- Use the smallest sufficient architecture: deterministic docs/schema/test helper before any agent framework.
- Preserve source status, truth boundary, and non-overclaim rules.
- Add tests only if a machine-checkable artifact is created or changed.
- Keep PR narrow and reviewable.

Output:
- One branch and one PR.
- PR body must include:
  - Top Source Triad + V11.1 + P0+ AI Lead alignment
  - Codex reasoning level
  - changed files
  - reusable asset added or updated
  - verification
  - skipped checks and rationale
  - production-status boundary
  - next action

Verification:
- Run the smallest relevant check.
- For docs-only: markdown/path sanity and truth-boundary review.
- For parser/test: targeted pytest for the new test.
- Do not claim tests passed unless actually run.

Stop Rules:
- Stop if the change would require runtime behavior changes, external service integration, dependencies, autonomous agent execution, or source ingestion.
- Stop if the requested claim cannot be supported by merged code, test logs, eval artifacts, decision logs, or human approval.
```
