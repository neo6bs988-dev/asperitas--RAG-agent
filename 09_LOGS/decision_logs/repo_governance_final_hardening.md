# Decision Log — Repository Governance Final Hardening

Date: 2026-06-23
Status: governance hardening
Branch: repo-governance-final-hardening

## Decision

Add final repository-governance assets before continuing MVP-016 implementation.

## Rationale

After adding V1 reference hardening and developer-foundation skills/CI, the remaining useful public GitHub/open-source-inspired setup at this stage is repository governance:

- security policy;
- code owner review routing;
- open-source adoption policy;
- open-source review skill.

These assets improve reviewability and safe adoption without changing runtime behavior.

## Accepted Scope

- Add `SECURITY.md`.
- Add `.github/CODEOWNERS`.
- Add `docs/OPEN_SOURCE_ADOPTION_POLICY.md`.
- Add `.agents/skills/open-source-review/SKILL.md`.

## Deferred Scope

- No dependency additions.
- No third-party code copying.
- No MCP connector.
- No LangGraph/RAGAS/OpenAI/Anthropic SDK dependency.
- No retrieval, answer-generation, embedding, vector DB, reranking, or eval fixture changes.
- No production ingestion.

## Verification

Docs/governance-only change. Expected checks:

```bash
git status --short --branch
git diff --check
```

CI should run on the PR after creation.

## Risks

- CODEOWNERS only requests review if GitHub branch protection/review rules are configured to use it.
- Security policy gives process guidance but does not replace secret scanning, branch protection, or code scanning settings.
- Open-source adoption policy is governance; actual adoption still requires future PRs.

## Next Recommended MVP

MVP-016 — implement `SkillSpec` / `SkillRegistry` using the newly added skills and governance policy as operating context.
