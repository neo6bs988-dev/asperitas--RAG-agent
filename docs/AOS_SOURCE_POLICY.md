# AOS Source Policy

This policy defines how sources are prioritized, labeled, verified, and used in Asperitas AI RAG Agent outputs. It protects truth, confidentiality, compliance, and benchmark hygiene.

## Source Priority

| Priority | Source Type | Use |
|---|---|---|
| P0 | Latest user instruction and active prompt/constitution sources | Current execution rule unless unsafe, illegal, or scientifically false |
| P1 | Internal Asperitas source-of-truth documents | Internal company facts, internal strategy, AOS/PRIME doctrine |
| P2 | Official Asperitas public or investor material | Approved external positioning |
| P3 | Peer-reviewed science, technical papers, and scientific databases | Biological mechanism and technical claims |
| P4 | Government, regulatory, institutional, RFP, grant, and compliance sources | Law, compliance, grants, policy, eligibility |
| P5 | Industry, market, investor, and conference intelligence | Signals, competitors, adoption, market narrative |
| P6 | External benchmark and operating doctrine sources | Analogy and process doctrine only, not Asperitas fact |

## Source Conflict Rule

Use the source class that matches the claim type:

- internal company facts -> P1;
- public positioning -> P2;
- biology and technical mechanism -> P3;
- laws, grants, regulatory claims -> P4;
- market and investor signals -> P5;
- operating patterns and benchmark lessons -> P6.

If sources conflict, label the conflict and do not synthesize a stronger claim than the evidence supports.

## Benchmark Use Rule

P6 benchmark sources must be converted before use:

```text
Benchmark observation
-> operating principle or failure mode
-> Asperitas-specific control
-> measurable eval gate
-> GitHub evidence
```

Do not write as if a benchmarked company practice is already implemented inside Asperitas. Do not use benchmark doctrine as proof of internal capability, market traction, regulatory readiness, or scientific validation.

## Disclosure Levels

| Level | Meaning |
|---|---|
| confidential | Internal source material not suitable for public use |
| internal | Internal use with lower sensitivity than confidential |
| external_safe | Potentially usable externally after review |
| public | Public source material |
| restricted | Use is limited by confidentiality, license, privacy, or risk |
| unknown | Disclosure has not been classified |

External-facing outputs require disclosure review. Restricted or unknown sources must not be used for public claims without approval.

## Evidence Labels

Use these labels for material claims:

- Document-Supported Fact
- Official Source
- Peer-Reviewed Evidence
- Regulatory Source
- Industry Signal
- Inference
- Speculation
- Needs External Verification

If a claim cannot be tied to evidence, label it as inference, speculation, or needs verification. Never upgrade speculation into fact.

## Verification Statuses

Recommended statuses:

- `verified_internal`
- `verified_official`
- `externally_verified`
- `partially_verified`
- `unverified`
- `needs_review`
- `stale`
- `conflicting`

Verification status is not permanent. Time-sensitive or regulatory claims must be refreshed before use.

## Legal And License Caution

Registry creation does not equal legal review. License status can be:

- `owned`
- `internal_use`
- `public`
- `restricted`
- `unknown`
- `needs_review`
- `rejected`

Do not ingest license-ambiguous, paywalled, restricted, or personal data into production indexes without review. Use review queues for ambiguous sources.

## Ingestion Status Caution

Ingestion status describes processing state, not truth or legal clearance.

| Status | Meaning |
|---|---|
| registered | Source exists in registry |
| parsed | Extractable text was processed |
| chunked | Chunks exist |
| embedded | Embeddings exist |
| indexed | Search index exists |
| kg_linked | KG links exist |
| eval_ready | Evals can reference it |
| partial | Some content was processed but gaps remain |
| unsupported | Registered/logged but not chunked |
| failed | Parsing failed or was rejected |

Unsupported or failed ingestion does not mean the source is false. It means the current pipeline did not safely extract usable text.

## Do-Not-Confuse Distinctions

| Do Not Confuse | With |
|---|---|
| Source files attached | Database fully ingested |
| Source registry created | Legal/license review completed |
| Chunks created | Production RAG deployed |
| Local retrieval working | Production vector DB deployed |
| KG schema drafted | Production KG completed |
| Eval script exists | Eval suite passed |
| Compliance detection implemented | Regulatory approval obtained |
| Prediction or answer generated | Wet-lab validation completed |
| Investor material found | Committed capital |
| P6 benchmark doctrine | Asperitas internal fact |
| RAG core | Biological foundation model |

## Claim Output Rule

For important answers, preserve or internally track:

- source ID;
- source priority;
- source type;
- title or path;
- evidence label;
- verification status;
- confidence;
- claim support status;
- compliance flags;
- missing evidence.

If evidence is insufficient, say what is missing instead of guessing.
