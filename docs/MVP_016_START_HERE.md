# MVP-016 START HERE

Purpose: one-page start guide for Codex/Cursor/Claude Code before implementing MVP-016.

## Read Order
1. `AGENTS.md`
2. `.agents/skills/asperitas-v1-architect/SKILL.md`
3. `01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/V1_FINAL_BENCHMARK_PACK.md`
4. `01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/BENCHMARK_COVERAGE_MATRIX.md`
5. `.agents/skills/asperitas-source-audit/SKILL.md`
6. `.agents/skills/asperitas-evaluation/SKILL.md`
7. `.agents/skills/asperitas-workflow/SKILL.md`
8. `.agents/skills/asperitas-security/SKILL.md`

## MVP-016 Objective
Implement and verify the Skills Framework without breaking MVP-001 to MVP-015 behavior.

## Required Constraints
- Preserve existing tests and existing behavior.
- Do not remove provenance, citation, priority, disclosure, or verification fields.
- Do not ingest external full text unless license/terms review is complete.
- Do not introduce large dependencies unless justified.
- Add tests for skills discovery and required skill files.
- Run the full test suite or clearly report any command that could not run.

## Suggested Task Prompt
```text
Use AGENTS.md and .agents/skills.
Read docs/MVP_016_START_HERE.md.
Read 01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/V1_FINAL_BENCHMARK_PACK.md.
Read 01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/BENCHMARK_COVERAGE_MATRIX.md.

Task: Start MVP-016 Skills Framework.
Goal: make repository-scoped skills discoverable, testable, and documented without changing retrieval behavior yet.

Constraints:
- Preserve MVP-001 to MVP-015 behavior.
- Do not remove existing tests.
- Do not ingest external full text.
- Keep changes small and backward compatible.
- Add tests verifying required `.agents/skills/*/SKILL.md` files exist and have name/description frontmatter.
- Update docs only as needed.

Report:
1. Objective
2. V1 layer improved
3. Benchmark source applied
4. Files changed
5. Tests run
6. Metrics before and after, if applicable
7. Risks
8. Remaining gaps
9. Next MVP action
```

## Acceptance Criteria
- Required skills are present.
- A skill discovery or validation test exists.
- Required frontmatter is validated.
- Benchmark coverage matrix remains metadata-only.
- No external source full text is ingested.
- Test results are reported.

## Next MVPs
- MVP-017: RAGAS-style eval metrics and artifacts.
- MVP-018: workflow/planner layer.
- MVP-019: audit trace layer.
- MVP-020: security/guardrail fixtures.
- MVP-021: MCP expansion plan.
