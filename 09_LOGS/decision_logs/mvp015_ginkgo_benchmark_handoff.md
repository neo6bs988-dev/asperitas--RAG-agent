# Decision Log: MVP-015 Ginkgo Benchmark Handoff

## Date

2026-06-22

## Decision

Prepare MVP-015 as a read-only Ginkgo/OpenAI benchmark preflight before implementation.

## Rationale

The Ginkgo/OpenAI autonomous-lab paper is strategically useful as a software-process benchmark, but Asperitas must not overclaim autonomous wet-lab capability. MVP-015 should therefore translate the benchmark into schema-first, eval-driven, compliance-aware workflow architecture rather than lab execution.

## Accepted Scope

- Documentation handoff for Codex.
- Benchmark pattern extraction plan.
- Preflight prompt and inspection order.
- Explicit non-goals and policy boundaries.

## Rejected Scope

- Wet-lab execution.
- Protocol automation.
- External cloud-lab connection.
- New source ingestion.
- Retrieval behavior changes.
- Chunk/registry/eval-fixture mutation.
- Production autonomous-lab claim.

## Policy Boundaries

- `mvp003` remains the protected deterministic reference retriever.
- Hybrid retrieval remains explicit/manual/experimental only.
- Deterministic-test reranker remains explicit opt-in/non-default only.
- No production hybrid claim.
- No autonomous wet-lab claim.
- Human approval is required for biosafety, regulatory, legal/IP, investor-facing, confidential-sharing, and wet-lab-sensitive outputs.

## Verification

Documentation-only handoff. No source code, tests, retrieval behavior, registry files, chunks, or eval fixtures were intentionally changed.

## Next Step

Open a new Codex session for MVP-015 and run the preflight prompt in `docs/MVP015_GINKGO_BENCHMARK_HANDOFF.md` before approving any implementation.
