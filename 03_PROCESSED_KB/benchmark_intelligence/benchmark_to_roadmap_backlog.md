# Benchmark To Roadmap Backlog

| Priority | Item | Source basis | Acceptance check |
|---|---|---|---|
| P0 | Add P6 precedence eval: P6 cannot override P0/P1/P2 facts. | Benchmark boundary claim cards | Test/eval fixture passes. |
| P0 | Add CSV source-map guard: URLs are not treated as ingested. | Attached registry ingestion_status | Eval fixture passes. |
| P1 | Expose evidence_label/confidence/verification_status on benchmark claims. | Claim-card artifact | JSONL schema check passes. |
| P1 | Separate implemented repo fact vs benchmark inference in workflow synthesis. | Synthesis artifact | Markdown contains all three sections. |
| P2 | Decide whether `evidence_use` becomes a formal metadata schema field. | User-required metadata | Backward-compatible schema proposal. |
| P2 | Add OCR fallback only if extraction QA finds missing page text. | PDF extraction status | Spot-check report. |
