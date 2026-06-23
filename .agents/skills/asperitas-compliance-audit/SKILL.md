---
name: asperitas-compliance-audit
description: Use when work touches biosafety, biosecurity, CITES, Nagoya, LMO, regulatory, legal, privacy, IP, investor, or external communication risk.
---

# Asperitas Compliance Audit Skill

## Purpose
Ensure high-risk biological, legal, regulatory, financial, or external-facing outputs receive explicit risk classification and human approval gates.

## Trigger Conditions
Use this skill for:
- CITES or biodiversity access
- Nagoya Protocol or benefit sharing
- LMO/GMO or engineered organisms
- Biosafety or biosecurity
- Wet-lab protocol, strain, vector, or experimental execution
- Investor/legal/IP-sensitive communication
- External publication or public claim

## Workflow
1. Classify risk domain.
2. Separate fact, inference, speculation, and verification need.
3. Identify source support and missing evidence.
4. Decide gate status: allow, allow with caveat, human approval required, or block.
5. Record rationale in decision log.
6. For code changes, add tests for gate behavior.

## Output Requirements
Report:
1. Risk domain
2. Trigger reason
3. Evidence status
4. Gate decision
5. Required human review
6. Safe next action

## Stop Rules
- Do not provide operational wet-lab execution guidance for risky biological work without explicit safety context and approval.
- Do not claim regulatory or legal approval.
- Do not allow external-facing claims that exceed verified evidence.
