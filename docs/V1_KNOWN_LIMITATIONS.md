# V1 Known Limitations

Status: internal release-candidate limitation register

## Core Limitations

- The chat CLI is dry-run by default.
- No real RAG answer provider is enabled by default.
- No external LLM or API call is made by the release readiness flow.
- No MCP or external connector automation is enabled.
- No public-facing product workflow is included.
- No wet-lab, biological protocol, or autonomous research operation is executed.
- No regulatory, clinical, commercial, or biological model performance claim is established.

## Retrieval And Answering

V1 preserves existing retrieval and answer-generation behavior. MVP-019E does not change retrieval, chunking, source registry data, eval fixtures, embeddings, vector DB behavior, reranking, answer generation, or default runtime behavior.

Any future answer-provider wiring must be explicit, opt-in, test-covered, source-grounded, and gated by security, workflow acceptance, audit, and regression checks.

## Security And Compliance

The security guard is deterministic pattern-based logic. It is useful for gating obvious prompt-injection, policy-bypass, secret-exposure, connector/tool, and unsafe operational requests, but it is not a complete security program.

Human review remains required for:

- confidential data handling
- legal, investor, or public communication
- CITES, Nagoya, LMO, biosafety, biosecurity, IP, privacy, or regulatory risk
- wet-lab-sensitive or operational biological requests

## Eval Limitations

The eval layer supports deterministic artifacts and regression gates. It does not turn LLM-as-judge scoring into ground truth, and MVP-019E does not add new retrieval or answer-quality metrics.

## Operational Limitations

Internal users should log failures rather than treating workarounds as release success. Repeated issues should become V1.1 tickets with reproducible inputs, command logs, and expected-versus-observed behavior.
