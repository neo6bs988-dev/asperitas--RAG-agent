# Developer Foundation Open-Source Pattern Additions

Status: developer-foundation hardening
Scope: Codex/Claude-style skills, GitHub CI, Dependabot, source-grounding and security review recipes

## Executive Bottom Line

This update adds developer-facing scaffolding inspired by official OpenAI Codex Skills, Anthropic Claude Code Skills, GitHub Actions, and Dependabot documentation.

It does not copy third-party source code, add runtime dependencies, change retrieval behavior, ingest sources, or alter answer generation.

The purpose is to make future MVP-016+ Codex work more repeatable, testable, and auditable.

## Why These Additions

Official Codex Skills describe skills as reusable workflow packages containing instructions, resources, and optional scripts. Anthropic Claude Code skills use `SKILL.md` files with frontmatter and concise instructions. GitHub Actions provides a standard way to build and test Python projects in CI, and Dependabot can monitor package ecosystems on a schedule.

These patterns are useful for Asperitas because V1 requires repeatable Skills, Evaluation, Workflow, Audit, and Security layers.

## Added Developer Assets

### Agent Skills

```text
.agents/skills/mvp-implementation/SKILL.md
.agents/skills/source-grounding-check/SKILL.md
.agents/skills/pr-closeout/SKILL.md
.agents/skills/reference-acquisition/SKILL.md
.agents/skills/security-review/SKILL.md
```

These skills are instruction-only by default. They are designed to help Codex and other coding agents follow repo-specific workflows without repeatedly pasting long prompts.

### GitHub CI

```text
.github/workflows/ci.yml
```

The workflow runs on pull requests and pushes to `main`. It:

- checks out the repo;
- sets up Python 3.11;
- installs `pytest`;
- installs `requirements.txt` if present;
- runs pytest when the `tests` directory exists;
- runs `scripts/verify_artifacts.py` when present;
- runs `git diff --check`.

### Dependabot

```text
.github/dependabot.yml
```

The configuration tracks:

- GitHub Actions updates;
- Python/pip dependency updates at repo root.

It does not install packages or modify runtime behavior by itself.

## Boundaries

This update does not:

- add RAGAS dependency;
- add LangGraph dependency;
- add MCP connector;
- add OpenAI or Anthropic SDK dependency;
- ingest external documentation;
- copy third-party repository code;
- change retrieval, chunking, scoring, embeddings, vector DB, reranking, answer generation, or eval fixtures;
- claim production readiness.

## Future Use

MVP-016 should use these skill files as operational context while implementing the actual `SkillSpec` / `SkillRegistry` code.

MVP-017 should add evaluation-layer code and metric reports.

MVP-018 should add workflow/planner code.

MVP-019 should add audit/security runtime behavior and security fixtures.

## Manual Addition Guide

To add a new repo-level skill later:

```bash
mkdir -p .agents/skills/<skill-name>
notepad .agents/skills/<skill-name>/SKILL.md
```

Use this template:

```markdown
---
name: <skill-name>
description: Explain exactly when this skill should and should not trigger.
---

# <Skill Name>

## Purpose

## Trigger

## Rules

## Verification

## Report Format
```

Then run:

```bash
git status --short --branch
git add .agents/skills/<skill-name>/SKILL.md
git commit -m "Add <skill-name> skill"
git push origin <branch>
```

Open a PR and include tests or explain why no tests are needed.
