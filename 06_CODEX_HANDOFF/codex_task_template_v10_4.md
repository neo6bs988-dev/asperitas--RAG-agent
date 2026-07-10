# Codex Task Template v10.4

```text
Use AGENTS.md and Asperitas Ultimate Prompt Command v10.4.

TASK
{one sentence desired result}

CURRENT CONTEXT
- Repo:
- Branch/PR/SHA:
- Relevant files:
- Prior result/blocker:

MVP / RISK
mvp_type: {MVP-DOC / MVP-REGISTRY / MVP-INGESTION / MVP-RETRIEVAL / MVP-RAG / MVP-COMPLIANCE / MVP-EVAL / MVP-UI / MVP-PERFORMANCE / MVP-RELEASE}
risk_class: {Low / Medium / High / Extra High}

SCOPE
In scope:
- {allowed files/modules/actions}

Out of scope:
- no unrelated rewrites
- no external data ingestion unless explicitly approved
- no production DB/KG/vector/eval/deployment claims unless verified
- no autonomous wet-lab execution
- no secrets, credentials, raw confidential data, or PII in commits/prompts/logs

REQUIREMENTS
- Make the smallest safe diff.
- Preserve backward compatibility unless explicitly approved.
- Add/update tests for every critical behavior.
- If retrieval/chunking/scoring/RAG changes, run golden retrieval/citation/regression evals.
- If compliance/privacy/security is touched, add gate tests and report risks.

VERIFY
Run:
{commands}

REPORT FORMAT
Executive Bottom Line:
Files Changed:
Implementation Summary:
Commands Run:
Tests/Evals:
Security/Privacy/Compliance:
Production-State Claims Check:
Regression Risk:
Open Blockers:
Ready for PR/Merge: yes/no
Next Action:

STOP RULES
Stop before changing files if scope is unclear, required source files are missing, compliance/legal/privacy risk is unresolved, tests cannot be defined, or the change would imply unsupported production-state claims.
```
