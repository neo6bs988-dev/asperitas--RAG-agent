# ASPERITAS AI AGENT FACTORY PLAYBOOK v2.0

**Classification:** Internal Developer Operating Manual  
**Date:** 2026-06-15  
**Owner:** COO & AI Manager Office  
**Scope:** Asperitas Inc. internal agent-development operating manual  
**Original PDF:** `Asperitas_Agent_Development_Playbook_v2_20260615.pdf`  
**PDF SHA-256:** `cb04062f291f5ebd004e4cbfba7da86371ce1aa77ed42e27c1843bc0449ae362`

## Core Command

All independent agent development must follow:

```text
초안 -> 프롬프트 -> 구현 -> 검증 -> 확인 -> GitHub 커밋/PR -> 회고 -> 스킬/워크플로우 업데이트
```

AI-generated code is not trusted by default. It is verified, reviewed, committed, and converted into reusable company process through `AGENTS.md`, skills, workflows, tests, and decision logs.

## Revision Log

| Version | Date | Core Change | Meaning |
|---|---:|---|---|
| v1.0 | 2026-06-14 | Basic development loop, GitHub, Codex prompt, onboarding skeleton. | Initial playbook. |
| v2.0 | 2026-06-15 | Rebuilt into Agent Factory operating system: developer loop, open-source intake, skill/workflow loop, verification gates, GitHub governance, prompt library. | Practical development standard. |

## 0. Executive Command

Asperitas will not build only one agent. It may build:

- Asperitas RAG Agent;
- Literature Intelligence Agent;
- Compliance & Biosafety Agent;
- Protocol Design Agent;
- Investor / IR Agent;
- Biofoundry Automation Agent;
- Market Intelligence Agent.

Therefore, development must not depend on individual intuition. It must become a repeatable company factory.

| CEO-grade Instruction | Asperitas Translation | Field Execution |
|---|---|---|
| Use AI as a production line, not a toy. | Every AI development request needs a loop and gate. | Include Task Brief, Constraints, Tests, Report. |
| Combine speed and quality. | Move fast, but never merge unverified work. | branch -> test -> verify -> PR -> review -> merge. |
| Turn failure into assets. | Record errors in Failure Taxonomy and Decision Log. | Update AGENTS.md / Skills for repeated failures. |
| Absorb good external assets, but not legal/security contamination. | Open-source intake must pass formal protocol. | Scout -> License -> Security -> Benchmark -> Adapt. |
| Humans set standards; AI compresses repetition. | Final approval remains human. | Treat AI output as a verification target, not evidence. |

## 1. Asperitas Agent Factory Overview

```text
[Idea / Business Need]
 ↓
[Agent Brief: objective, users, data, risks, non-goals]
 ↓
[Prompt Engineering: ChatGPT converts rough idea into Codex task]
 ↓
[Codex Implementation: smallest safe change + tests]
 ↓
[Verification Gate: pytest + artifact verify + eval + diff]
 ↓
[Human Review: screenshot/log/result check]
 ↓
[GitHub Commit/PR: traceable organization memory]
 ↓
[Retrospective: update AGENTS.md / Skills / workflow templates]
 ↓
[Next Agent / Next MVP]
```

### Five Principles

1. **Scope Lock:** define what will not change before coding.
2. **Small Safe Change:** one task should achieve one objective.
3. **Verification First:** success means tests/evals/diff/logs pass, not that AI says it is done.
4. **GitHub as Memory:** issues, PRs, commits, and decision logs are organizational memory.
5. **Skill Compounding:** repeated instructions and review standards are promoted into AGENTS.md and skills.

## 2. Agent Development Priority

| Priority | Agent | Purpose | Initial MVP Output |
|---|---|---|---|
| P0 | Asperitas RAG Agent | Search and answer from internal docs, regulations, papers, and market intelligence. | ingest -> chunk -> retrieval eval -> source citation. |
| P1 | Literature Intelligence Agent | Search papers, extract methods, summarize evidence. | paper metadata parser, claim/evidence table. |
| P1 | Compliance & Biosafety Agent | Automate regulatory, ethics, and biosafety checklist review. | risk taxonomy, SOP checklist, audit log. |
| P2 | Protocol Design Agent | Support DBTL protocol drafts and experimental-variable design. | protocol template, parameter extraction. |
| P2 | Investor / IR Agent | Support investor Q&A, market benchmarks, IR docs. | Q&A bank, competitor matrix. |
| P3 | Biofoundry Automation Agent | Connect toward LIMS, robotics, and scheduling automation. | API mock, workflow scheduler spec. |

## 3. Current Standard Loop

| Step | What Happens | Owner | Completion Condition |
|---|---|---|---|
| 1. Draft | Rough business/technical objective. | User / PM | Goal, current state, desired change written. |
| 2. Prompting | ChatGPT converts draft into Codex task. | ChatGPT | Task, Context, Constraints, Verification, Report included. |
| 3. Preflight | Codex reads repo state, relevant files, and risks before edits. | Codex | File list, expected changes, test plan reported. |
| 4. Implementation | Smallest safe code/test/docs change. | Codex | Changed files remain within scope. |
| 5. Verification | Run pytest, eval, artifact verification, lint, git diff. | Codex + Developer | All required checks pass or failures are explained. |
| 6. Human Review | User/lead reviews result screenshot/log/summary. | User / Lead | Bugs, uncertainty, remaining risks checked. |
| 7. Commit / Push | Commit, push, or PR through GitHub. | Developer | Commit message, PR summary, tests run recorded. |
| 8. Retrospective | Promote repeated lessons into AGENTS.md / Skills. | AI Manager | Durable rule added for next task. |

## 4. Must-Not-Skip Checks

```bash
git status
git branch --show-current
git log -1 --oneline
python -m pytest
python scripts/verify_artifacts.py
# If retrieval/chunking/scoring changed:
python scripts/run_retrieval_eval.py
```

Also inspect:

- `git diff` for scope creep;
- changed file list;
- docs update requirement;
- source provenance requirement;
- compliance / biosafety / legal gates;
- regression risk;
- open-source license or dependency change.

## 5. Codex Prompt Operating System

Every Codex task should include:

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Task:
[clear implementation objective]

Context:
- Current repo: asperitas-agent
- Current MVP stage: [MVP-XXX]
- Target files: [files, or inspect first]

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

## 6. GitHub Governance

### Branching

Use feature branches for implementation:

```text
mvp-006-vector-retrieval-eval
fix-mvp-004-chunk-section-regression
docs-agent-playbook-v2
```

### Commit Messages

```text
Add MVP-006 vector retrieval eval mode
Fix MVP-004 heading path regression
Docs add agent factory playbook
Eval add failure taxonomy baseline
```

### PR Summary Template

```markdown
## Objective

## Files Changed

## Tests Run

## Eval Metrics

## Risk / Regression Review

## Compliance / Safety Check

## Screenshots / Logs

## Next Task
```

### Protected Main Rule

`main` should remain recoverable. Prefer PRs for meaningful changes. Direct commits are acceptable only for low-risk docs or controlled administrative updates.

## 7. Open-Source Intake Protocol

Good open-source projects may be studied aggressively, but not copied blindly.

```text
Scout -> License -> Security -> Benchmark -> Adapt -> Ledger
```

| Gate | Question | Evidence |
|---|---|---|
| Scout | Is this project technically relevant? | repo link, feature comparison. |
| License | Can we legally use it? | license type, NOTICE requirements. |
| Security | Does it add supply-chain risk? | dependency scan, known CVEs. |
| Benchmark | Is it better than our current approach? | tests, metrics, examples. |
| Adapt | Can we adapt architecture without contamination? | minimal implementation plan. |
| Ledger | Did we document source and usage? | open-source ledger / decision log. |

Never import code without license and security review.

## 8. Verification Gate

| Change Type | Required Verification |
|---|---|
| Chunking / Retrieval | pytest + retrieval eval before/after + sample chunk inspection. |
| Ingestion | fixture ingest + artifact verification + metadata check. |
| Evaluation | eval snapshot + regression threshold + report. |
| CLI / UI | smoke test + docs update + backward compatibility check. |
| Compliance | unit tests + red-team samples + false-positive review. |
| Dependency | license/security review + lockfile diff + minimal import check. |

## 9. AGENTS.md / Skills / Workflow Pipeline

Repeated instructions should move from chat into repo-level operating assets.

### AGENTS.md Should Define

- role and active AOS;
- non-negotiable engineering principles;
- source provenance rules;
- compliance gates;
- required implementation report;
- acceptance criteria;
- no-fabrication rule;
- test and eval requirements.

### Skill Folder Pattern

```text
.agents/skills/<skill-name>/SKILL.md
.agents/skills/<skill-name>/examples/
.agents/skills/<skill-name>/fixtures/
.agents/skills/<skill-name>/tests/
```

### Skill Promotion Criteria

Promote a process into a skill when:

- the same prompt is reused at least three times;
- errors repeat;
- verification has a stable checklist;
- another developer must reproduce the workflow;
- the process affects quality, safety, compliance, or speed.

## 10. New Chat Continuation Protocol

When development continues in a new chat, paste:

```text
We are developing the Asperitas RAG Agent.

Current repo: asperitas-agent
GitHub repo: neo6bs988-dev/asperitas--RAG-agent
Branch: main or [branch]
Current MVP: [MVP-XXX]
Last completed commit: [hash]
Working tree: clean / unknown
Last tests: [pytest result]
Last eval: [metric summary]
Current task: [next task]
Constraints:
- Use AGENTS.md and relevant skills.
- Do not delete files.
- Make the smallest safe change.
- Preserve backward compatibility.
- Add or update tests.
- Run pytest and artifact verification.
- Run retrieval eval if retrieval/chunking/scoring changes.
Report in the standard 7-part format.
```

## 11. Claude Code / Codex Parallel Strategy

Use Codex as the default for GitHub-connected implementation and verification. Use Claude Code or similar tools when:

- long-form refactoring analysis is needed;
- multi-file architecture review is needed;
- prompt/skill/workflow documentation must be expanded;
- a second implementation opinion is useful.

Do not let tools compete without a single source of truth. GitHub main + AGENTS.md + decision logs remain authoritative.

## 12. New Developer 7-Day Onboarding Plan

| Day | Objective | Deliverable |
|---:|---|---|
| 1 | Understand repo, AOS, Agent Factory loop. | Repo map and glossary. |
| 2 | Run local tests and artifact verification. | Test log. |
| 3 | Read AGENTS.md and skills. | Notes on required rules. |
| 4 | Execute a docs-only Codex task. | Small PR. |
| 5 | Execute a test-only improvement. | Test PR. |
| 6 | Execute a small implementation task. | Feature PR. |
| 7 | Write retrospective and propose one skill update. | Decision log + skill proposal. |

## 13. Report Format

Every implementation report must include:

```text
1. objective
2. files changed
3. tests run
4. eval metrics before/after
5. risks
6. unresolved issues
7. next recommended task
```

## 14. Operating Risks and Prohibited Behavior

Prohibited:

- deleting files without explicit approval;
- claiming a database/RAG/KG/eval system is production-deployed when only a scaffold exists;
- adding dependencies without review;
- hiding failed tests;
- ignoring retrieval eval after retrieval changes;
- treating AI output as authoritative evidence;
- bypassing compliance gates for CITES, Nagoya, LMO, biosafety, biosecurity, legal, financial, or external communications.

## 15. KPIs

Track:

- time from brief to passing test;
- number of regressions per MVP;
- retrieval eval stability;
- artifact verification status;
- PR review turnaround;
- repeated failure count;
- number of durable rules promoted into AGENTS.md / skills;
- open-source intake pass/fail rate;
- onboarding time to first safe PR.

## 16. Bottom Line

v2.0 upgrades v1.0 from a general guide into an operating manual. The core development loop remains the same, but now includes GitHub governance, open-source intake, skill compounding, workflow pipeline design, new-chat continuity, and onboarding. This is the standard process for scaling Asperitas from one RAG agent into a repeatable internal Agent Factory.
