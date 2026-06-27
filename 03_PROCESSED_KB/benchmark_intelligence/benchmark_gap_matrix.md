# Benchmark Gap Matrix

Source scope: `ASP-P6-D1F4C9FC8737` extracted from attached PDF and `ASP-P6-188684F599A7` attached source map. External CSV links were not crawled.

| Workflow layer | Implemented repo fact | Benchmark inference | Verification need | Backlog implication |
|---|---|---|---|---|
| Source collection | Repo has raw source folders and registries. | Benchmark pack should enter P6 only. | License review for every external artifact. | Keep P6 separate from P0/P1/P2 truth. |
| Metadata | Repo has metadata schemas and source priority policy. | Benchmark artifacts need evidence_use and forbidden_use fields. | Decide whether schema should formally add these fields later. | Add backward-compatible metadata extension only if runtime needs it. |
| Extraction/chunking | PDF is extracted and page-aware chunks are generated in this pack. | Page refs are sufficient for benchmark traceability. | Human spot-check Korean extraction quality. | Add OCR fallback only if extraction gaps appear. |
| Embedding/vector | Offline deterministic embeddings can be generated. | Persisted offline index is useful for local RAG development. | Confirm whether production vector DB exists before claiming production indexing. | Keep status as offline persisted artifact. |
| RAG/evidence | Repo requires source IDs, evidence labels, confidence boundaries. | Benchmark claims should be surfaced as inference/verification-needs. | Add runtime guard if P6 answer promotion is observed. | Add eval fixtures included in this pack. |
| Workflow/agent | Repo has workflow planner/acceptance layers. | Best workflow is source->metadata->RAG->eval->agent->approval->decision log. | Validate with future end-to-end dogfood. | Create operational backlog from synthesis. |
