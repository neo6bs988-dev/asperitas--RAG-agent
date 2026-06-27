# V1.3D Truth/Compliance Router Report

## Executive Bottom Line

V1.3D adds a small deterministic post-draft truth/compliance router. It checks the query, evidence metadata, citations, and drafted answer before final output, then blocks unsafe overclaims or adds a human-review gate where relevant.

This change does not alter retrieval, ranking, scoring, chunking, embeddings, vector DB behavior, reranking, source ingestion, registry artifacts, or chunk artifacts.

## Baseline Commits

- V1.3C answer contract merge: `65a200cc7736bb946bbf1ead7d71a5129bff7c61`
- P6 benchmark DB pack/precedence guard merge: `9c3d8ee7d9cb6885540aa9f67a8ecff297d468ec`

Both commits were verified as ancestors of `origin/main` before implementation.

## Scope Lock

Implemented scope:

- Post-draft router module: `src/asperitas_agent/truth_compliance_router.py`
- Minimal answer-generation integration after the V1.3C contract draft is built
- Deterministic router tests and check script
- V1.3D eval report artifacts

Out of scope and unchanged:

- Retrieval scoring and ranking
- Source ingestion
- Source registry and chunk artifacts
- Embeddings, vector DB, and reranker behavior
- Broad prompt or answer-contract rewrite

## Router Behavior

The router checks for:

- internal factual answer boundaries
- missing-evidence abstention
- unsafe production, deployment, wet-lab, legal, regulatory, vector-DB, external-ingestion, or foundation-model completion overclaims
- P6 benchmark material being promoted to Asperitas fact
- source-map-only URLs being cited as ingested evidence
- unverified P1 material being stated as verified fact
- completion claims without acquisition, license, chunk, embed, index, and eval evidence

When a blocking condition is found, the router appends a `Truth/compliance router:` block and downgrades an `answered` response to `caution`. Source-map-only citations are removed from `citations_used`.

## Compliance Gate Behavior

Compliance, biosafety, legal, regulatory, CITES, Nagoya, LMO, GMO, approval, and wet-lab-sensitive questions trigger an explicit human-review gate when relevant:

- Human review is required before public, investor, legal, regulatory, biosafety, or wet-lab-sensitive use.

## P6 And Source-Map Handling

- P0-P4/internal sources remain the factual authority for Asperitas status.
- P6 benchmark material is analogy/doctrine only.
- P6 cannot override P0-P4/internal evidence.
- Source-map-only URLs cannot be cited as ingested evidence.
- Source-map-only material requires acquisition, license, chunking, embedding, indexing, and eval logs before citation as ingested evidence.

## Verification Results

Baseline preflight passed:

- `python scripts/verify_artifacts.py`
- `python scripts/check_v1_release_readiness.py --json`
- `python scripts/check_v1_3c_answer_contract.py --overwrite --json`
- `python scripts/run_golden_agent_eval.py`

Targeted V1.3D verification passed:

- `python -m pytest tests/test_v1_3d_truth_compliance_router.py tests/test_v1_3c_answer_contract.py -q`
- `python scripts/check_v1_3c_answer_contract.py --overwrite --json`
- `python scripts/check_v1_3d_truth_compliance_router.py --overwrite --json`

The V1.3D check reports:

- `ok: true`
- `retrieval_scoring_changed: false`
- `source_artifacts_mutated: false`
- 6 router cases passed

## Truth Boundary

This router is a deterministic safety and truth-boundary check. It is not legal clearance, regulatory clearance, production deployment evidence, wet-lab validation, full external ingestion proof, foundation-model completion proof, or answer-quality proof beyond the covered deterministic cases.

## Risks And Rollback

Primary risk: phrase-based overclaim detection can be conservative and may add a caution block to borderline wording.

Rollback is straightforward: remove the router call from `answer_generation.py` and delete `truth_compliance_router.py` plus V1.3D tests/artifacts.

## Next Step

V1.4 Cost/Latency/Token Optimization.
