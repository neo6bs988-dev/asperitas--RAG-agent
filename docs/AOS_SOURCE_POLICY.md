# AOS Source Policy

## Source Priority

- `P0`: latest user instruction and active prompt/constitution sources.
- `P1`: internal Asperitas source-of-truth documents.
- `P2`: official Asperitas public or investor material.
- `P3`: peer-reviewed science, technical papers, and scientific databases.
- `P4`: government, regulatory, institutional, RFP, grant, and compliance sources.
- `P5`: industry, market, investor, and conference intelligence.
- `P6`: external benchmark and operating doctrine sources.

## Disclosure Levels

- `confidential`: internal source material not suitable for public use.
- `internal`: internal use with lower sensitivity than confidential.
- `external_safe`: potentially usable externally after review.
- `public`: public source material.
- `unknown`: disclosure has not been classified.

## Evidence Labels

- Document-Supported Fact
- Official Source
- Peer-Reviewed Evidence
- Regulatory Source
- Industry Signal
- Inference
- Speculation
- Needs External Verification

## Verification Statuses

- `verified_internal`
- `verified_official`
- `externally_verified`
- `unverified`
- `needs_review`

## Legal and License Caution

Registry creation does not equal legal review. License status can be `owned`, `internal_use`, `public`, `restricted`, `unknown`, or `needs_review`. External use of confidential or restricted sources requires human approval.

## Ingestion Status Caution

Ingestion status describes parser outcome only:

- `parsed`: extractable text was chunked.
- `partial`: some content was parsed, but some inner files or sections were unsupported, rejected, or failed.
- `unsupported`: the source or inner file type is registered/logged but not chunked.
- `failed`: parsing failed or the file was rejected for safety reasons.

Unsupported or failed ingestion does not mean the source is unimportant or false. It means the current local parser could not safely extract usable text.

## Do-Not-Confuse Distinctions

- Source files attached does not mean database fully ingested.
- Source registry created does not mean legal/license review completed.
- Chunks created does not mean production RAG deployed.
- Local retrieval working does not mean production vector DB deployed.
- PPTX/ZIP/HWPX parsing working does not mean full visual, binary, legal, or regulatory interpretation.
- Compliance detection implemented does not mean regulatory approval.
- Prediction or answer generated does not mean wet-lab validation.
- Investor material found does not mean committed capital.
