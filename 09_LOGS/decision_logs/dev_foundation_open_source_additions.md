# Decision Log — Developer Foundation Open-Source Pattern Additions

Date: 2026-06-23
Status: developer-foundation hardening
Branch: dev-foundation-skills-ci-hardening

## Decision

Add repo-level developer workflow scaffolding inspired by official OpenAI Codex Skills, Anthropic Claude Code Skills, GitHub Actions, and Dependabot documentation.

## Rationale

The user asked to add only developer-necessary open-source/public patterns that improve the repo before continuing MVP-016 and V1 performance hardening.

The chosen additions improve repeatability and reviewability without changing runtime behavior:

- instruction-only agent skills;
- source-grounding review recipe;
- PR closeout recipe;
- reference acquisition recipe;
- security review recipe;
- lightweight CI;
- Dependabot configuration.

## Accepted Scope

- Add `.agents/skills/*/SKILL.md` workflow recipes.
- Add GitHub Actions CI smoke workflow.
- Add Dependabot configuration.
- Add documentation explaining what was added and how to add future skills.

## Deferred Scope

- No external source ingestion.
- No dependency adoption from OpenAI, Anthropic, LangGraph, LlamaIndex, RAGAS, MCP, or Google ADK.
- No retrieval or answer-generation changes.
- No vector DB or embedding changes.
- No runtime audit logging implementation.
- No prompt-injection test implementation yet.
- No copied third-party code.

## Verification

This change is mostly workflow/docs scaffolding. Expected checks:

```bash
git status --short --branch
git diff --check
```

CI will run after PR creation and will attempt pytest and artifact verification when matching files exist.

## Risk

- New CI may expose existing environment assumptions that were previously local-only.
- Dependabot may create update PRs later.
- Skill text must remain concise and trustworthy because skill metadata can affect agent behavior.

## Next Recommended MVP

MVP-016 — implement actual `SkillSpec` / `SkillRegistry` code using the added `.agents/skills` as operating context.
