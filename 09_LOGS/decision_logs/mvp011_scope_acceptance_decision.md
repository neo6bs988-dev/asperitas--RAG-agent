# MVP-011 Scope Acceptance Decision

## 1. Date

2026-06-15

## 2. Context

MVP-011 Failure Analysis / Error Taxonomy was completed and validated. A post-merge audit found scope contamination and external history changes around the MVP-011 merge history.

The audited MVP-011 implementation commit was `35637bf656822c3d6c9d487e4a11e43314fba119` (`수정 / FIX`). The earlier audited repository state was `6e6bb35d6e49861a0e169c469fef4de559d06b24` (`Add v2 agent factory playbook markdown archive`). At the time this decision note was created, local `main` had advanced to `a80749da7e61fad15938ac5c10c87e29bbd4e33e` (`Add MVP-005 Phase 4 closure summary`) and remained synced with `origin/main`.

## 3. MVP-011 Expected Scope

- `docs/MVP_011_FAILURE_TAXONOMY.md`
- `scripts/evaluate_agent.py`
- `scripts/run_golden_agent_eval.py`
- `src/asperitas_agent/failure_taxonomy.py`
- `tests/test_failure_taxonomy.py`

## 4. Actual Additional Files / Changes Found

- `01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/Asperitas_Agent_Development_Playbook_v1_20260614.pdf`
- `01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/Asperitas_Agent_Development_Playbook_v2_20260615.pdf`
- `docs/playbooks/Asperitas_Agent_Development_Playbook_v1_20260614.md`
- `docs/playbooks/Asperitas_Agent_Development_Playbook_v2_20260615.md`
- `docs/playbooks/README.md`
- `docs/MVP005_PHASE2_CLOSURE_SUMMARY.md`
- `docs/MVP005_PHASE3_CLOSURE_SUMMARY.md`
- `docs/MVP005_PHASE4_CLOSURE_SUMMARY.md`
- `docs/REASONING_STRENGTH_POLICY.md`
- `src/asperitas_agent/embeddings.py`
- `tests/test_embeddings.py`
- `scripts/run_retrieval_eval.py`
- `tests/test_retrieval_eval.py`

## 5. Decision

- The raw playbook PDF is accepted as an internal source/archive asset.
- The v2 playbook markdown archive is accepted as documentation/process archive.
- Embedding/vector-store-related code is accepted as existing upstream/non-MVP-011 work, but is not approved for production retrieval ranking or runtime use until a dedicated MVP explicitly validates it.
- MVP-011 failure taxonomy is accepted as additive evaluation metadata only.

## 6. Non-Approval Boundary

- This decision does not approve external APIs.
- This decision does not approve LLM APIs.
- This decision does not approve production vector DB integration.
- This decision does not approve retrieval ranking changes.
- This decision does not approve ingestion reruns.
- This decision does not approve registry or chunks mutation.
- This decision does not approve UI/web server work.

## 7. Validation Snapshot

- `python -m pytest -q`: 137 passed
- `python scripts/verify_artifacts.py`: ok true, registry_records 48, chunk_count 2821
- `python scripts/evaluate_agent.py`: ok true, 3/3
- `python scripts/run_golden_agent_eval.py`: ok true, 6/6
- Working tree: clean before this decision note
- Origin sync: 0 0 before this decision note

## 8. Risk Classification

- MVP-011 implementation risk: accepted / medium but validated
- Git history risk: accepted with documentation
- Forbidden-scope risk: controlled by explicit non-approval boundary
- Release-readiness: GO after this note

## 9. Next Step

After this decision note is created and validation remains green, proceed to MVP-012 planning/preflight.
