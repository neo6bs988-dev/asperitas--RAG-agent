# ASPERITAS AI AGENT DEVELOPMENT PLAYBOOK v1.0

**Classification:** Internal Draft  
**Date:** 2026-06-14  
**Owner:** COO & AI Manager Office  
**Scope:** Asperitas Inc. internal agent-development operating manual  
**Original PDF:** `Asperitas_Agent_Development_Playbook_v1_20260614.pdf`  
**PDF SHA-256:** `9f3d9b3eaa125ef6d8942dc7010a4ec0157b2c655004d3e75eb46509ad876169`

## Core Command

This playbook standardizes the loop:

```text
초안 -> 프롬프트 -> 구현 -> 검증 -> 확인 -> GitHub 커밋/PR -> 학습/개선
```

The purpose is to convert AI-assisted coding from ad-hoc prompting into a repeatable engineering process for all future Asperitas independent agents.

## 0. Executive Summary

Asperitas should not treat agent development as casual “AI에게 맡기기.” Every agent must be built as a reproducible engineering workflow:

1. Define the rough idea and business objective.
2. Convert the idea into a scoped Codex prompt.
3. Implement the smallest safe change.
4. Verify with tests, artifact checks, evals, and git diff.
5. Review logs/screenshots with ChatGPT or a human reviewer.
6. Commit/push through GitHub.
7. Use the result as the base for the next MVP.

## 1. Current Development Loop

| Step | Role | Output | Pass Criteria |
|---|---|---|---|
| 1. Draft | User explains purpose, MVP stage, and desired change. ChatGPT translates it into buildable scope. | MVP brief, scope, non-goals | Clear distinction between what will and will not be built. |
| 2. Prompt | ChatGPT creates a copy-paste Codex task prompt. | Codex task prompt | Includes AGENTS.md, skill instructions, constraints, verification, and report format. |
| 3. Implementation | Codex inspects repo and makes minimal changes. | Code/test/docs changes | Backward compatibility preserved. |
| 4. Verification | Codex or local environment runs pytest, artifact verification, retrieval eval if relevant. | Test logs, eval metrics | No unexplained failures; metrics are stable or explained. |
| 5. Review | User sends screenshots/logs to ChatGPT for interpretation. | Go/fix/hold decision | Commitable state confirmed or risks identified. |
| 6. GitHub Commit | GitHub Desktop or CLI commits and pushes. | Commit hash, clean tree | origin/main synchronized, working tree clean. |
| 7. Next MVP | A new independent prompt continues from the committed state. | Next MVP prompt | Scope is again small and safe. |

## 2. Role Separation

| Actor | Main Function | Should Do | Should Not Do |
|---|---|---|---|
| COO / Product Owner | Direction and success criteria | Define business goal, moat, scalability, compliance requirements. | Approve AI output without verification. |
| ChatGPT | Strategy, design, prompt, review | Decompose requirements, create Codex prompts, interpret logs, decide next step. | Claim repo changes are complete without evidence. |
| Codex | Code implementation and tests | Inspect repo, change files, run tests, report diff and risks. | Delete files, add broad dependencies, perform uncontrolled refactors. |
| GitHub | Memory and collaboration gate | Branch, PR, review, commit history, issue tracking. | Accumulate unverified changes on main. |
| New Developer | Execution and accountability | Run prompts, inspect logs, fix failures, document decisions. | Treat AI-generated output as automatically correct. |

## 3. Standard Step-by-Step Process

### Step 0 — Agent Brief

Every new agent starts with:

```text
Agent name:
Primary user:
Business objective:
Inputs:
Outputs:
Non-goals:
Risks:
MVP success criteria:
Evaluation method:
Target files:
```

### Step 1 — Scope Lock

Before implementation, freeze:

- what will change;
- what must not change;
- tests that must pass;
- whether retrieval eval, artifact verification, or compliance review is required.

### Step 2 — Codex Prompt

Use this pattern:

```text
Use AGENTS.md and relevant .agents/skills instructions.

Task:
[precise task]

Context:
- Repo: asperitas-agent
- MVP stage: [stage]
- Target files: [files or inspect first]

Constraints:
- Do not delete files.
- Make the smallest safe change.
- Preserve backward compatibility.
- Add or update tests.
- Run pytest.
- Run artifact verification.
- Run retrieval eval if retrieval/chunking/scoring is affected.
- Update docs if behavior changes.

Report:
1. objective
2. files changed
3. tests run
4. eval metrics before/after
5. risks
6. unresolved issues
7. next recommended task
```

### Step 3 — Verification Gate

Required checks:

```bash
git status
git branch --show-current
git log -1 --oneline
python -m pytest
python scripts/verify_artifacts.py
# If retrieval/chunking/scoring changed:
python scripts/run_retrieval_eval.py
```

### Step 4 — Commit Standard

Commit message pattern:

```text
Add MVP-XXX <short objective>
Fix MVP-XXX <bug or regression>
Docs MVP-XXX <documentation update>
Eval MVP-XXX <evaluation or metrics update>
```

## 4. Open-Source Intake Protocol

Open-source code is not copied blindly. Use:

```text
Scout -> License -> Security -> Benchmark -> Adapt -> Ledger
```

Checklist:

- repository health;
- license compatibility;
- dependency risk;
- security alerts;
- maintenance status;
- test coverage;
- whether architecture is learned rather than copied;
- NOTICE/LICENSE record if imported.

## 5. GitHub as Organization Memory

GitHub must store:

- source code;
- tests;
- docs;
- PR summaries;
- decision logs;
- failure taxonomy;
- verification results;
- release notes;
- reusable AGENTS.md / skills / workflow templates.

## 6. Skill and Workflow Expansion

After every MVP, ask:

1. Did we repeat the same instruction more than once?
2. Did Codex make a predictable mistake?
3. Did verification require a stable checklist?
4. Did a new workflow become repeatable?

If yes, promote the lesson into:

- `AGENTS.md`;
- `.agents/skills/<skill-name>/SKILL.md`;
- workflow documentation;
- evaluation fixtures;
- decision-log templates.

## 7. Failure Modes

| Failure Mode | Prevention |
|---|---|
| Broad AI refactor | Lock scope and target files. |
| Passing code but broken retrieval | Run retrieval eval when retrieval logic changes. |
| Untracked compliance risk | Add compliance gate and human approval. |
| GitHub clutter | Use branch, PR summary, issue linkage. |
| Lost context in new chat | Use continuation prompt with repo, branch, MVP, tests, unresolved risks. |
| Open-source legal contamination | License/security review before import. |

## 8. Bottom Line

v1.0 establishes the core Asperitas Agent Factory loop. It is the first standardized bridge between vibe coding, ChatGPT prompt design, Codex implementation, GitHub governance, and reusable AI-agent development practice.
