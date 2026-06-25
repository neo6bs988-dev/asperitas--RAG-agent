# V1.0.0-rc1 Internal Closeout Packet

Status: draft packet only; final RC, internal dry-run, and internal release remain pending

Fresh-evidence guard: this packet is not release evidence until the listed commands are rerun in the later manual release context and their fresh output is recorded.

## Packet Contents

- release notes draft: `docs/releases/V1_0_0_RC1_RELEASE_NOTES.md`
- manual release steps: `docs/releases/V1_0_0_RC1_MANUAL_RELEASE_STEPS.md`
- internal deploy guide: `docs/V1_INTERNAL_DEPLOY_GUIDE.md`
- V1 closeout: `docs/V1_RELEASE_CLOSEOUT.md`
- known limitations: `docs/V1_KNOWN_LIMITATIONS.md`
- V1.1 handoff: `docs/V1_1_PERFORMANCE_HANDOFF.md`
- smoke runner: `scripts/run_v1_rc_smoke.py`

## RC Checklist

- run full pytest
- run `python scripts/verify_artifacts.py`
- run `python scripts/check_v1_release_readiness.py --json`
- run `python scripts/run_v1_rc_smoke.py --json`
- run `python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json`
- confirm output remains internal/dry-run and does not claim production deployment readiness
- confirm no retrieval, chunk, vector, reranker, embedding, answer, or default runtime changes are included

## V1 Status Snapshot

V1 includes skills, eval, workflow, audit trace, workflow audit, security guard, chat workflow dry-run, release readiness, and this RC packet.

V1 remains in pre-RC internal engineering posture until a later human-approved release step records fresh command output. It is not public SaaS, production customer deployment, autonomous wet-lab execution, external connector automation, clinical/regulatory/commercial proof, or a proven biological model.

## V1.1 Transition Checklist

- collect internal failure logs
- classify failures using the V1.1 taxonomy
- create baseline and candidate artifacts for changes
- run regression gates before merging retrieval or answer-quality work
- keep real answer-provider wiring explicit and opt-in until eval-backed
- keep human review gates for confidential, legal, public, investor, regulatory, and wet-lab-sensitive outputs
