---
name: security-review
description: Use to review agent, skill, workflow, CI, and source-handling changes for unsafe behavior, hidden tool execution, secret exposure, and untrusted-source instruction risks.
---

# Security Review Skill

## Purpose

Review changes that affect agent behavior, skills, workflows, CI, dependencies, connectors, or source handling.

## Checks

1. No secrets, tokens, credentials, or private keys are committed.
2. No skill enables external calls by default.
3. No skill silently executes state-changing commands.
4. No retrieved source text is treated as a higher-priority instruction.
5. No external repository code is copied without license and security review.
6. No dependency is added without a reason and verification plan.
7. High-risk actions require human approval.
8. Logs avoid sensitive content and preserve traceability.

## Skill-Specific Checks

For every `SKILL.md`:

- description is specific and not overbroad;
- instructions are concise;
- allowed and forbidden actions are clear;
- risky actions fail closed;
- supporting scripts are optional and reviewed before use;
- third-party skills are treated as untrusted until reviewed.

## Report Format

```text
Security Verdict: pass | needs_revision | blocked
Changed Surface:
Risks Found:
Required Fixes:
Approval Needed:
Residual Risk:
```
