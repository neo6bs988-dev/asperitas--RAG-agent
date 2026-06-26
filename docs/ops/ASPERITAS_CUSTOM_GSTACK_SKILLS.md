# Asperitas Custom gstack Skills

Status: future-skill proposal

Related issue: #96

## Purpose

Propose Asperitas-specific custom skills that could be added after the docs-only gstack operating-stack phase is proven useful. These skills are proposals only. They are not installed, generated, or required by this repository today.

Each future skill must preserve:

- `AGENTS.md`;
- ASPERITAS PRIME v2.0;
- inherited AOS layers;
- source hierarchy;
- evidence labels;
- compliance and biosafety escalation;
- no false production-status claims.

## Adoption Rules

Before any custom skill becomes required:

1. Use it manually as a checklist.
2. Run it optionally in one or more internal PRs.
3. Record benefits, misses, and reviewer burden.
4. Confirm no runtime or artifact mutation is caused by the skill.
5. Approve required mode only after a stable internal release.

## Proposed Skills

### `/asperitas-strategy-review`

Role: Asperitas strategy reviewer.

Goal: Review a proposed product, workflow, or development plan through PRIME, AOS, and the four operating personas.

Inputs:

- issue or plan;
- intended user;
- source status;
- constraints;
- success criteria.

Checks:

- scalability;
- moat;
- biosafety/compliance;
- capital efficiency;
- learning velocity;
- Biological Intelligence Factory alignment.

Output:

- execute / verify / pivot / kill recommendation;
- source status;
- assumptions;
- missing evidence;
- next action.

### `/asperitas-rag-review`

Role: source-grounded RAG reviewer.

Goal: Review retrieval, chunking, metadata, reranking, answer generation, and citation changes before implementation or merge.

Required when:

- retrieval logic changes;
- document chunking changes;
- metadata handling changes;
- embeddings or vector DB behavior changes;
- reranking changes;
- answer-generation behavior changes.

Checks:

- source IDs preserved;
- source priority preserved;
- evidence labels preserved;
- confidence and unsupported-claim handling preserved;
- retrieval eval commands selected;
- before/after metrics reported.

Output:

- changed-surface classification;
- required eval commands;
- expected metrics table;
- regression risks;
- GO/NO-GO recommendation.

### `/asperitas-compliance-review`

Role: compliance and biosafety gatekeeper.

Goal: Identify compliance, confidentiality, IP, legal, public-communication, investor, and biosafety risks before release or external use.

Triggers:

- CITES;
- Nagoya Protocol / ABS;
- LMO / GMO;
- K-BDS;
- biosafety;
- biosecurity;
- wet-lab protocol execution;
- personal data;
- confidential data;
- investor or public claims;
- legal, IP, or financial recommendations.

Output:

- risk domain;
- severity;
- source evidence;
- missing approval;
- blocked content if any;
- safe next action.

### `/asperitas-release-gate`

Role: internal release gate reviewer.

Goal: Confirm whether a release candidate has enough evidence to proceed.

Inputs:

- release branch;
- release notes;
- closeout packet;
- test output;
- artifact verification output;
- readiness script output;
- smoke test output;
- retrieval metrics when applicable.

Required commands:

```bash
python -m pytest
python scripts/verify_artifacts.py
python scripts/check_v1_release_readiness.py --json
python scripts/run_v1_rc_smoke.py --json
python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json
```

Output:

- GO / CONDITIONAL / NO-GO;
- blocking evidence gaps;
- release-risk summary;
- rollback plan;
- human approval needed.

### `/asperitas-dbtl-plan`

Role: DBTL planning reviewer.

Goal: Convert a biological hypothesis or R&D direction into a safe, evidence-labeled DBTL plan without bypassing qualified supervision or compliance review.

Boundaries:

- do not provide unsafe operational wet-lab instructions;
- do not claim validation unless verified;
- escalate biosafety, biosecurity, LMO/GMO, CITES, Nagoya, environmental, animal, human, or regulatory risk;
- distinguish concept, in silico plan, experimental design, and wet-lab execution.

Output:

- hypothesis;
- evidence status;
- minimum viable experiment at a safe conceptual level;
- controls and success metrics;
- failure metrics;
- compliance gates;
- IP capture questions;
- kill / pivot / scale criteria.

## Future Skill Packaging

If these become real gstack or Codex skills later, create them through a separate approved implementation task.

That task must:

- read current gstack host instructions;
- avoid vendoring full gstack source;
- keep generated skill files clearly separated from product runtime code;
- add tests or validation appropriate to the skill packaging;
- document rollback;
- open a separate PR.
