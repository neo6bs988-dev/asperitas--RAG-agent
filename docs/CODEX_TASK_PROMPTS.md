# Codex Task Prompts

Use these prompts to keep Codex work small, verifiable, and aligned with the repository operating system.

## Universal Task Prompt

```text
Use AGENTS.md and the relevant .agents/skills instructions.

Task:
[write the exact objective]

Context:
- Current repo: asperitas--RAG-agent
- Current MVP stage: [MVP-004 / MVP-005 / etc.]
- Target files: [list if known; otherwise inspect first]

Constraints:
- Do not delete files.
- Make the smallest safe change.
- Preserve backward compatibility.
- Add or update tests for source code changes.
- Run pytest for source code changes.
- Run artifact verification for generated artifacts.
- Run retrieval eval if retrieval/chunking/scoring/answer generation is affected.
- Update docs if behavior, commands, or workflow changes.

Report:
1. Objective
2. Files changed
3. Tests run
4. Artifact verification
5. Retrieval metrics before/after
6. Compliance/source-grounding impact
7. Risks or skipped checks
8. Next recommended task
```

## Docs-Only Governance Prompt

```text
Use AGENTS.md and .agents/skills/github-pr-review/SKILL.md.

Task:
Update governance or workflow documentation only.

Constraints:
- Do not modify source code.
- Do not modify tests.
- Do not claim that a pipeline is implemented unless an executable file exists.
- Re-read every edited document before reporting done.

Report:
- Files changed
- What changed
- Verification performed
- Skipped checks and why
- Next operational improvement
```

## MVP-004 Retrieval/Chunking Prompt

```text
Use AGENTS.md, .agents/skills/asperitas-rag-development/SKILL.md, and .agents/skills/retrieval-eval-quality-gate/SKILL.md.

Task:
[describe MVP-004 chunking/retrieval objective]

Required commands:
python -m pytest
python scripts/verify_artifacts.py
python scripts/audit_chunk_sections.py --json
python scripts/run_retrieval_eval.py --retriever baseline --limit 5
python scripts/run_retrieval_eval.py --retriever mvp003 --limit 5

Acceptance:
- No test failure.
- Artifact verification is ok.
- No unexplained source/evidence regression.
- Section metadata behavior is explicitly reported.

Report using docs/MVP004_BASELINE_METRICS.md format.
```

## Source-Grounded Answer Prompt

```text
Use AGENTS.md and .agents/skills/source-grounding-citation/SKILL.md.

Task:
Implement or review source-grounded answer behavior.

Constraints:
- Every material claim must trace to a source ID.
- Unsupported claims must be removed or labeled.
- Evidence labels and source priority must survive formatting.
- Insufficient evidence must produce an explicit uncertainty response.

Report:
- Affected answer path
- Citation behavior
- Unsupported-claim handling
- Tests/checks
- Residual hallucination risk
```

## Compliance/Biosafety Prompt

```text
Use AGENTS.md and .agents/skills/compliance-biosafety-review/SKILL.md.

Task:
Review the change for biological, biodiversity, regulatory, privacy, IP, legal, investor, or public-communication risk.

Report:
- Risk domain
- Severity
- Evidence reviewed
- Missing approvals
- Decision: clear / mitigate / block / escalate
- Safe next action
- Human approval needed
```

## MVP Release Prompt

```text
Use AGENTS.md and .agents/skills/mvp-release-manager/SKILL.md.

Task:
Decide whether [MVP-X] can close.

Inputs:
- Roadmap entry
- Changed files
- Commands run
- Test/eval results
- Acceptance criteria
- Known risks

Report:
- Release decision: ready / conditional / blocked
- Completed work
- Verification evidence
- Metrics
- Deferred tasks
- Release note
- Next MVP task
```

## Recovery Prompt After Codex Stops

```text
Resume the previous Codex task in this repository.

First:
1. Inspect git status and changed files.
2. Read AGENTS.md and relevant skills.
3. Identify whether the previous task was docs, source code, eval, compliance, or release.
4. Do not continue blindly.

Then report:
- What appears complete
- What appears incomplete
- Whether source code changed
- Which checks must run next
- The safest next command or patch
```