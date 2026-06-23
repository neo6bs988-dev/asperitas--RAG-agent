# OPENAI Benchmark Notes

Priority: P6 External Benchmark
Use: Agent skills, eval loops, GitHub/Codex workflow, reusable workflow packaging.

## Sources
1. Codex Agent Skills
   - URL: https://developers.openai.com/codex/skills
   - Key idea: a skill is a directory with `SKILL.md` plus optional `scripts/`, `references/`, `assets/`, and agent metadata. Codex can discover repository-scoped skills under `.agents/skills`.
2. OpenAI Skills repository
   - URL: https://github.com/openai/skills
   - Use: examples only; review license before copying.
3. OpenAI Evals
   - URL: https://github.com/openai/evals
   - Use: evaluation harness reference.

## Patterns to Absorb
- Repository-scoped skills should live under `.agents/skills`.
- Keep each skill focused on one job.
- Put trigger scope in each skill description.
- Use progressive disclosure: metadata first, detailed instructions only when activated.
- Prefer instruction-only skills unless deterministic scripts are necessary.
- Test prompt triggers against each skill.

## Asperitas V1 Application
- Create skills for retrieval, evaluation, citation, source audit, workflow planning, compliance audit, and security tests.
- Do not make Codex rely on one huge instruction block.
- Convert repeated successful MVP workflows into reusable `SKILL.md` files.
