---
name: source-grounding-citation
description: Use whenever answer generation, citations, evidence labels, source hierarchy, or hallucination prevention is affected.
---

# Source Grounding Citation

## When To Use

- Answer generation changes.
- Citation format, evidence labels, confidence labels, source hierarchy, or hallucination prevention changes.
- Retrieved evidence is transformed, summarized, or exposed to users.

## When Not To Use

- Retrieval-only scoring changes with no answer or citation behavior impact.
- Docs-only edits that do not affect grounding rules.
- Pure GitHub process review.

## Required Inputs

- Source hierarchy and evidence label rules.
- Example retrieved chunks.
- Expected answer format.
- Citation requirements.
- Known unsupported-claim failure cases.

## Workflow Steps

1. Inspect answer and citation path.
2. Map every material claim to source IDs.
3. Confirm source priority, evidence label, and confidence survive output formatting.
4. Remove or label unsupported claims.
5. Check insufficient-evidence behavior.
6. Run citation or answer-groundedness tests if available.
7. Report residual hallucination risk.

## Quality Gates

- Claims trace to source IDs.
- Citations point to retrievable sources.
- Unsupported claims are removed or labeled.
- Restricted sources are not exposed for disallowed use.
- Insufficient evidence produces a clear answer, not fabrication.

## Report Format

- Affected answer path:
- Citation behavior:
- Evidence labels:
- Unsupported claims:
- Tests or checks:
- Residual risk:
- Next step:

## Failure Conditions

- Generated answers contain claims not supported by retrieved evidence.
- Citation IDs cannot be resolved.
- Evidence labels are dropped.
- Restricted or confidential source text is exposed.

## Next-Step Recommendation Format

- Next grounding task:
- Failure case addressed:
- Required fixture:
- Quality gate:

