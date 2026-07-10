# Prompt Lint Checklist v10.4

Use before Medium/High/Extra High risk Codex or RAG tasks.

## Required Prompt Slots
- [ ] Goal
- [ ] Scope
- [ ] Evidence
- [ ] Constraints
- [ ] Output
- [ ] Verification
- [ ] Stop Rules

## Governance
- [ ] MVP type declared
- [ ] Risk class declared
- [ ] Source hierarchy stated
- [ ] Fact / inference / speculation boundary stated
- [ ] Production-state non-confusion rule included

## Security / Privacy / Compliance
- [ ] Secrets/PII handling specified
- [ ] Confidential source handling specified
- [ ] Biosafety/legal/compliance trigger specified
- [ ] Human approval gate included when needed

## Verification
- [ ] Test/eval commands listed
- [ ] Regression risk considered
- [ ] Report format specified
- [ ] Next action specified

## Fail Conditions
Fail the prompt if it asks Codex to:
- ingest/scrape external data without approval
- expose confidential data or PII
- claim production DB/KG/vector/eval/legal/wet-lab completion without verification
- modify broad unrelated files
- run high-risk biological or compliance-sensitive work without approval
