---
name: compliance-biosafety-review
description: Use whenever biological data, biodiversity data, CITES, Nagoya Protocol, LMO, K-BDS, privacy, security, or regulatory risk is affected.
---

# Compliance Biosafety Review

## When To Use

- Biological, biodiversity, species, genomic, protein, pathway, wet-lab, or DBTL content is affected.
- CITES, Nagoya Protocol, LMO, K-BDS, privacy, security, IP, legal, or regulatory risk appears.
- Public, investor, partner, or grant-facing claims are generated.

## When Not To Use

- Pure internal tooling with no biological data, confidential data, or external claim impact.
- Formatting-only docs changes with no risk-bearing content.
- Generic GitHub process review.

## Required Inputs

- Content or code path under review.
- Data type and source classification.
- Intended audience and use case.
- Jurisdiction or regulatory context if known.
- Missing approvals or licenses.

## Workflow Steps

1. Classify risk domain.
2. Identify affected data and audience.
3. Check source permissions, disclosure level, and verification status.
4. Flag unsafe biological, regulatory, legal, privacy, or security output.
5. Require human approval where needed.
6. Recommend safe alternative wording or blocked action.

## Quality Gates

- Risk domain is named.
- Missing evidence or approval is explicit.
- Restricted content is not exposed.
- Unsafe wet-lab or compliance-bypassing detail is blocked.
- Public or investor claims are source-supported.

## Report Format

- Risk domain:
- Severity:
- Evidence reviewed:
- Missing approvals:
- Decision:
- Safe next action:
- Human approval needed:

## Failure Conditions

- Regulated biological risk is ignored.
- Confidential or personal data is exposed.
- Legal, regulatory, or validation status is overstated.
- Unsafe operational biological instructions are produced.

## Next-Step Recommendation Format

- Next compliance task:
- Approval needed:
- Evidence needed:
- Blocking risk:

