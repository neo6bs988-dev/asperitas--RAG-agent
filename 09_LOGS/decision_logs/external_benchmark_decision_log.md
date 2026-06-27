# External Benchmark Decision Log

## 2026-06-27 — Registry scaffold created

Decision: create a registered-only governance scaffold for external benchmark sources.

Scope:
- Founder/operator doctrine: 15 sources.
- AI-agent architecture: 16 sources.
- AI-bio platform benchmark: 10 sources.
- Total: 41 registered sources.

Rationale:
- The repository needs a legal, auditable source map before raw acquisition or ingestion.
- External benchmark sources improve strategy, agent architecture, and AI-bio platform design, but they must not override internal Asperitas source-of-truth documents.
- Registered-only metadata allows planning without copyright, terms-of-service, or provenance risk.

Truth boundary:
- This is not production database ingestion.
- This is not raw source acquisition.
- This is not markdown extraction.
- This is not chunking.
- This is not embedding/vector DB deployment.
- This is not retrieval/reranking/answer-generation change.
- This is not legal/license approval.

Compliance notes:
- No raw copyrighted pages were crawled or stored.
- SEC/EDGAR-related entries are treated as P4 regulatory/government source records.
- The OpenAI/Ginkgo CFPS manuscript is registered as P3 preprint evidence, not peer-reviewed proof.
- AutoGen is flagged as secondary/legacy due to official Microsoft maintenance-mode notice at the time of registration.

Next action:
1. Run registry validation tests.
2. Perform source-by-source license/terms review.
3. Acquire only approved raw sources.
4. Update ingestion status from `registered_only` to `raw_acquired` only after approval and provenance logging.
5. Process, chunk, embed, and evaluate in separate PRs.
