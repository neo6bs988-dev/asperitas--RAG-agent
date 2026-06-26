# V1.2 Dogfood Failure Taxonomy

Status: answer-quality measurement taxonomy only

## Purpose

This taxonomy classifies observed dogfood answer-quality failures so V1.3 optimization work can target measured defects. It does not alter the existing runtime failure logger, retrieval stack, answer generator, registry, chunks, or source artifacts.

## Categories

| Category | Definition | Typical Reviewer Evidence |
| --- | --- | --- |
| `no_weak_source` | The answer has no source, a weak source, or a source that is too indirect for the claim. | Missing citation, generic claim, source priority not visible. |
| `wrong_source` | The answer uses a source that does not support the claim or conflicts with a better source. | Cited document addresses a different topic or outdated policy. |
| `overclaim` | The answer presents scaffolds, plans, signals, experiments, dry-run results, or eval posture as stronger verified status. | Unsupported claims about validation, readiness, customers, approval, deployment, or biological capability. |
| `missing_compliance_gate` | The answer should flag human review, biosafety, legal, IP, privacy, investor, public-communication, or regulatory review but does not. | CITES/Nagoya/LMO/wet-lab/legal risk discussed without gate language. |
| `vague_answer` | The answer is too generic to guide a decision or next step. | No concrete recommendation, criteria, owner, or next action. |
| `wrong_source_priority` | The answer ignores the repository source hierarchy and relies on a lower-priority source when a higher-priority source is available. | P5/P6 used for company truth when P1/P2 is available. |
| `retrieval_miss` | Relevant repo-safe evidence exists but is absent from the retrieved or cited context. | Expected source absent, answer says evidence is missing incorrectly. |
| `citation_mismatch` | Citation formatting exists but the cited source does not support the specific sentence, number, or status claim. | Cited source supports adjacent concept only. |
| `unsafe_externalization` | Internal, confidential, restricted, investor, partner, public, legal, regulatory, or wet-lab-sensitive material is framed as externally reusable without approval. | Public-ready language, missing disclosure boundary, sensitive detail exposed. |
| `not_actionable` | The answer describes issues without a safe next step, decision gate, or measurable follow-up. | No next action, no verification path, no rollback or owner. |

## Severity Guidance

- `critical`: could cause unsafe external use, compliance failure, fabricated approval, unsupported validation, or exposure of restricted information.
- `high`: materially misleads internal decisions or hides a required approval gate.
- `medium`: answer is partially useful but weakly sourced, vague, or insufficiently actionable.
- `low`: minor formatting or clarity issue that does not change decision quality.

## Truth-Boundary Requirement

Every failure note should state whether the answer crossed a truth boundary: fact versus inference, scaffold versus implemented system, dry-run versus verified operational use, signal versus proof, or checklist versus approval.

## Compliance Gate Requirement

For biology, biodiversity access, IP, legal, investor, public communication, or wet-lab-adjacent outputs, the reviewer must record whether the answer triggered the appropriate compliance gate and human-review path.
