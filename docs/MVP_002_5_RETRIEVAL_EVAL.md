# MVP-002.5 Retrieval Evaluation Set

Date: 2026-06-12 KST

## Purpose

MVP-002.5 adds a deterministic retrieval evaluation dataset and scoring harness for the current local TF-IDF retrieval baseline. It measures whether retrieval returns the expected source document and metadata before any future retrieval upgrade.

This milestone does not add embeddings, a vector database, reranking, LLM answer generation, UI, legal approval, regulatory approval, or wet-lab validation.

## Files

- `eval/retrieval_questions.jsonl`: evaluation questions with expected source metadata and rationale.
- `eval/expected_sources.jsonl`: normalized expected source mapping by `question_id`.
- `scripts/run_retrieval_eval.py`: schema validation, baseline retrieval execution, optional external-results scoring, and metrics reporting.
- `tests/test_retrieval_eval.py`: tests for eval loading, schema validation, and scoring behavior.

## Dataset Schema

Each question row includes:

- `question_id`
- `user_question`
- `expected_source_file`
- `expected_source_priority`
- `expected_chunk_or_section`
- `expected_evidence_label`
- `rationale`
- `difficulty`: `easy`, `medium`, or `hard`
- `category`: `company_strategy`, `compliance`, `synthetic_biology`, `ai_agent`, `operations`, `market`, or `source_governance`

## Metrics

The scorer reports:

- `source_file_match_at_3`: expected source appears in the top 3 results.
- `source_file_match_at_5`: expected source appears in the top 5 results.
- `source_priority_match`: matched source has the expected priority.
- `evidence_label_match`: matched source has the expected evidence label.
- `section_match`: expected section text appears in the matched title/text when a section hint exists.
- `overall_pass_rate`: expected source appears in top 5, priority matches, evidence label matches, and section match is not false.

## Commands

Run the unit tests with a fresh temp directory on Windows:

```powershell
$py = "C:\Users\jbc89\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$base = Join-Path $env:TEMP ("asperitas-pytest-" + [guid]::NewGuid().ToString("N"))
& $py -m pytest -q --basetemp=$base
```

Run the current TF-IDF baseline retrieval evaluation:

```powershell
$py = "C:\Users\jbc89\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py .\scripts\run_retrieval_eval.py
```

Score external retrieval results instead of the current baseline:

```powershell
& $py .\scripts\run_retrieval_eval.py --results-jsonl .\path\to\results.jsonl
```

External result rows must use this shape:

```json
{"question_id":"MVP0025-Q001","results":[{"source_file":"AGENTS.md","source_priority":"P0","evidence_label":"Document-Supported Fact","title":"AGENTS","text":"Source Priority Policy"}]}
```

## Limitations

- Metrics are source-level and light section-level checks, not answer-quality grading.
- Section matching is simple case-insensitive substring matching.
- Baseline retrieval is the existing deterministic lexical TF-IDF implementation.
- Korean, English, and mixed-language queries may expose tokenization limitations.
- Duplicate or near-duplicate sources can reduce apparent source-level recall even when retrieved evidence is conceptually related.
