# MVP-010 Golden Query Suite

## Purpose

MVP-010 adds a deterministic golden query regression pack for answer quality. MVP-009 proves that the local agent pipeline runs end to end; MVP-010 checks that selected answers remain status-correct, citation-backed, guardrail-aware, deterministic, and grounded in retrieved evidence.

This is an evaluation layer only. It does not change retrieval ranking, answer generation, guardrails, chunks, registry files, or source ingestion.

## Files

- `eval/golden_agent_queries.jsonl` stores checked-in golden cases.
- `scripts/run_golden_agent_eval.py` runs the golden suite and prints JSON by default.
- `tests/test_golden_agent_eval.py` validates the golden file and evaluator behavior.

## Golden Query Schema

Each JSONL record includes:

- `id`: stable unique case id.
- `category`: answer-quality category.
- `query`: user query passed to the local deterministic agent.
- `top_k`: retrieval count.
- `mode`: optional execution mode. `empty_corpus` is used only to validate no-evidence abstention.
- `expected_status`: `answered`, `caution`, or `abstained`.
- `expected_guardrail_decision`: optional guardrail decision expectation.
- `min_evidence_count`: minimum evidence items required.
- `min_citation_count`: minimum citations required.
- `required_answer_substrings`: stable concepts that must appear in the answer.
- `forbidden_answer_substrings`: claims that must not appear.
- `required_evidence_labels`: optional evidence labels that must be present.
- `required_source_priority_max`: optional maximum allowed source priority, such as `P0` or `P1`.
- `notes`: human-readable rationale.

## Validation Checks

The evaluator checks:

- AgentResponse schema shape.
- Expected status.
- Expected guardrail decision when specified.
- Minimum evidence count.
- Minimum citation count.
- Citation subset integrity against evidence citation keys.
- `metadata.citation_integrity.citations_subset_of_evidence`.
- Required answer substrings.
- Forbidden answer substrings.
- Required evidence labels.
- Source priority ceiling.
- Determinism across two identical runs.
- Protected file hashes before and after evaluation.

## Commands

Run compact JSON:

```powershell
python scripts/run_golden_agent_eval.py
```

Run pretty JSON:

```powershell
python scripts/run_golden_agent_eval.py --pretty
```

Run with the existing full harness:

```powershell
pytest -q
python scripts/evaluate_agent.py
python scripts/run_golden_agent_eval.py --pretty
```

## Adding A Golden Query Safely

1. Run the candidate query through `scripts/ask_agent.py`.
2. Record the honest current status, guardrail decision, evidence count, citation count, labels, and source priorities.
3. Add stable concept-level substrings, not full answer text.
4. Add forbidden substrings for unsafe overclaims.
5. Avoid exact formatting requirements unless format is the behavior being tested.
6. Re-run `python scripts/run_golden_agent_eval.py`.
7. Confirm protected files are unchanged.

## Anti-Overfitting Rules

- Runtime code under `src/asperitas_agent/` must not read `eval/golden_agent_queries.jsonl`.
- Runtime code must not special-case golden ids, exact query strings, `pytest`, CI, or test filenames.
- Tests and evaluation scripts may read the golden file.
- Golden expectations should verify evidence integrity, status behavior, and meaningful concepts, not exact full answer prose.
- Do not weaken guardrails or retrieval checks to pass a golden case.

## Protected Files

The golden evaluator hashes these files before and after evaluation when present:

- `data/chunks.jsonl`
- `data/source_registry.csv`
- `00_ADMIN/source_registry.csv`
- `00_ADMIN/source_registry.jsonl`
- `eval/retrieval_questions.jsonl`
- `eval/expected_sources.jsonl`
- `eval/golden_agent_queries.jsonl`

## Known Limitations

- The suite measures deterministic local answer quality, not production RAG quality.
- It does not add embeddings, a vector database, external APIs, web UI, or LLM generation.
- The current answer composer is extractive and citation-oriented, so golden expectations focus on grounded structure and safety rather than polished narrative quality.
- The `empty_corpus` case is a controlled no-evidence abstention check, not evidence that every unknown query will abstain under normal retrieval.
