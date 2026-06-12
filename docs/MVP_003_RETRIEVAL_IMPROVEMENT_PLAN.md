# MVP-003 Retrieval Improvement Plan

Date: 2026-06-12 KST

Project: Asperitas RAG Agent

Status: Design only. Do not implement from this document until explicitly approved.

## 0. Executive Summary

MVP-002.5 established a frozen deterministic retrieval baseline:

- Tests: 41 passed
- Artifact verification: ok=true
- Registry records: 48
- Chunks: 2821
- Eval questions: 32
- Source file match @3: 34.4%
- Source file match @5: 43.8%
- Source priority match: 43.8%
- Evidence label match: 43.8%
- Section match: 31.2%
- Overall pass rate: 31.2%

MVP-003 should improve retrieval while preserving the existing TF-IDF baseline as a callable baseline. It should not add embeddings, vector DB, external APIs, LLM answer generation, UI, or production RAG claims.

Target MVP-003 metrics:

- Source file match @3: 50%+
- Source file match @5: 60%+
- Section match: 45%+
- Overall pass rate: 45%+

Recommended MVP-003 strategy: build a deterministic metadata-aware lexical retriever that combines body-text TF-IDF with source registry metadata, title/path/filename weighting, Korean-English normalization, synonym normalization, duplicate-source handling, configurable `top_k`, and explainable ranking output.

## 1. Current Retrieval Architecture

Current retrieval path:

1. `data/source_registry.csv` stores source metadata.
2. `data/chunks.jsonl` stores chunk text and provenance metadata.
3. `src/asperitas_agent/chunking.py` creates fixed-size chunks from parsed document text.
4. `src/asperitas_agent/retrieval_tfidf.py` tokenizes query/chunk text and computes deterministic local lexical scores.
5. `scripts/run_retrieval_eval.py` loads eval questions, runs retrieval, maps chunk `source_id` to registry path, and scores source/priority/evidence/section matches.
6. `src/asperitas_agent/rag.py` uses retrieval output and compliance scanning for source-grounded answer summaries.

Current baseline retrieval function:

```python
search_chunks(query: str, chunks: list[Chunk], limit: int = 5) -> list[RetrievalResult]
```

Important preservation requirement:

- `retrieval_tfidf.search_chunks` must remain callable and behaviorally stable as the MVP-002.5 baseline.
- MVP-003 should introduce a new retrieval path rather than rewriting the baseline.

## 2. Why the TF-IDF Baseline Is Weak

The baseline is useful precisely because it exposes the next layer of problems.

Primary weaknesses:

1. It searches only `chunk.title + " " + chunk.text`.
   It does not search `original_filename`, registry `path`, folder, source type, notes, source priority, aliases, or canonical document family.

2. It underweights document identity.
   Many eval questions ask "which source", "which document", or "where should retrieval find". These should be answered heavily from metadata, not only body text.

3. Korean-English normalization is inadequate.
   The corpus contains Korean filenames, Korean source text, English questions, mixed Korean/English technical terms, acronyms, and transliterated concepts. The current tokenizer is too small for that.

4. P0 governance sources overlap heavily.
   README, AGENTS, AOS prompts, constitution PDFs, and Codex guidebooks repeat source hierarchy, development priorities, governance, compliance, and retrieval rules. Without metadata and source-family disambiguation, the wrong P0 source often ranks higher.

5. Section matching is fragile.
   The eval checks literal section text against returned title/text. Fixed-size chunks may exclude section headings or equivalent section labels.

6. Priority and evidence label failures are mostly downstream.
   Source priority and evidence label scores match Source@5 because labels are correct when the expected source is retrieved. The problem is retrieval, not the priority schema.

## 3. MVP-002.5 Failure Categories

From `docs/MVP_002_5_RETRIEVAL_FAILURE_ANALYSIS.md`:

| Failure Category | Estimated Count | Share of 22 Failures | MVP-003 Relevance |
|---|---:|---:|---|
| Metadata mismatch / filename not indexed | 14-18 | 64-82% | Highest priority |
| Weak title/section weighting | 12-16 | 55-73% | Highest priority |
| Korean/English mismatch and mixed-language tokenization | 10-14 | 45-64% | High priority |
| Overlap between similar P0/internal sources | 8-10 | 36-45% | High priority |
| Section-level retrieval failure | 4 | 18% | Partial MVP-003, fuller MVP-004 |
| Duplicate source confusion | 3-4 | 14-18% | Medium priority |
| Missing synonym/alias normalization | 8-12 | 36-55% | High priority |
| Chunk boundary issue | 4-6 | 18-27% | Defer most to MVP-004 |
| Source priority/evidence label downstream failure | 18 | 82% | Improve through source matching |
| Retrieval ranking weakness | 18-22 | 82-100% | Overall MVP-003 target |

## 4. Proposed MVP-003 Retrieval Improvements

### 4.1 Metadata-Aware Scoring

Add a new retriever that scores both chunk text and registry metadata.

Metadata fields to search:

- `SourceRecord.title`
- `SourceRecord.original_filename`
- `SourceRecord.path`
- source folder segments such as `P0_ACTIVE_PROMPT`, `P1_ASPERITAS_INTERNAL`, `P5_INDUSTRY_INTELLIGENCE`
- `SourceRecord.source_priority`
- `SourceRecord.source_type`
- `SourceRecord.parse_status`
- selected registry `notes`
- chunk `title`
- chunk `evidence_label`
- chunk `verification_status`

Design intent:

- Keep chunks as evidence units.
- Enrich each candidate score with source-level metadata.
- Do not mutate `chunks.jsonl` or `source_registry.csv` for MVP-003 unless a later implementation explicitly chooses a backward-compatible artifact.

### 4.2 Source Priority Weighting

Priority should not blindly override lexical relevance, but it should help tie-breaking and exact-source disambiguation.

Recommended default weighting:

| Priority | Suggested Multiplier / Bonus |
|---|---:|
| P0 | modest governance bonus for agent/system questions |
| P1 | modest internal source bonus for company/science/strategy questions |
| P4 | compliance/regulatory bonus for regulatory queries |
| P5 | industry/market bonus for market/conference queries |

Avoid a universal P0 boost. That would worsen false positives where AOS documents already dominate unrelated questions.

Implementation concept:

- Detect query category signals deterministically.
- Apply context-aware priority bonus only when query terms imply the priority class.
- Preserve raw lexical score and explain the bonus separately.

### 4.3 Evidence Label Weighting

Evidence labels should be a secondary signal.

Recommended approach:

- `Document-Supported Fact` should not automatically dominate, because both P0 and P1 use it.
- `Industry Signal` should receive a small bonus for SEED/conference/market/intelligence queries.
- `Regulatory Source` should receive a small bonus for regulation/compliance/LMO/CITES/Nagoya/biosafety queries.

Do not change evidence label assignment in MVP-003 unless a clear bug is found. Use labels as ranking features only.

### 4.4 Section and Title Weighting

Title/path/filename matches should score more than body text for source-identification questions.

Recommended fields and weights:

| Field | Suggested Role |
|---|---|
| exact filename/path substring | strongest deterministic boost |
| normalized title match | strong boost |
| title token overlap | strong boost |
| path folder token overlap | medium boost |
| chunk title | medium boost |
| chunk body TF-IDF | base evidence score |
| section hint match if available | strong boost in eval/debug mode only |

Important distinction:

- Production retrieval should not know expected eval section hints.
- Eval scoring can continue to check expected sections.
- Retriever should improve section recall by indexing chunk title, source title, heading-like text, and path/title metadata, not by reading eval answers.

### 4.5 Korean-English Query Normalization

Add deterministic normalization before scoring:

- Unicode normalization with `unicodedata.normalize("NFKC", text)`.
- Casefold Latin tokens.
- Preserve Hangul syllables.
- Split Latin, numbers, Hangul, and acronym tokens predictably.
- Normalize punctuation variants, underscores, hyphens, parentheses, ampersands, and slashes.
- Keep short but important acronyms such as AI, IR, DB, R&D, LMO, GMO.

Do not introduce external morphological analyzers in MVP-003. Keep it dependency-light and reproducible.

### 4.6 Synonym Normalization

Add a small deterministic synonym/alias map. This can live in code or a small local config file.

Initial alias candidates:

- `source hierarchy`, `source of truth`, `source priority policy`, `evidence hierarchy`
- `IR`, `investor deck`, `IR deck`
- `PTMC`, `2026 PTMC project`
- `SEED`, `conference`, `industry intelligence`
- `LMO`, `GMO`, `regulation`, `regulatory trends`
- `CRISPR`, `gene editing`
- `AI roadmap`, `AI study roadmap`
- `company introduction`, `Asperitas introduction`
- `biofoundry`, `바이오파운드리`
- `synthetic biology`, `합성생물학`

Rules:

- Synonyms must be deterministic and local.
- They must not call external APIs.
- They must be explainable in ranking output.
- They should be tested so additions do not unexpectedly lower benchmark performance.

### 4.7 Duplicate Source Penalty / Source-Family Handling

Some sources exist in multiple folders or versions:

- PTMC in internal and R&D project folders.
- SEED in internal and industry intelligence folders.
- Multiple AOS/constitution versions.

MVP-003 should not merge or delete duplicate sources. Provenance must remain exact.

Recommended design:

- Add source-family inference at retrieval time from filename/title/path.
- Penalize near-duplicate sources only when the query contains folder/category cues that favor one copy.
- Keep both sources eligible.
- Explain duplicate handling in ranking output.

Example:

- Query contains `industry intelligence` and `SEED`: boost `P5_INDUSTRY_INTELLIGENCE/SEED`.
- Query contains `R&D projects` and `PTMC`: boost `P1_RND_PROJECTS/2026 PTMC project`.

### 4.8 Configurable Top-K

MVP-003 retriever should support configurable `top_k` while preserving CLI/eval defaults.

Recommended parameters:

- `limit` or `top_k`: default 5
- optional `candidate_pool`: default 50
- optional `include_explanations`: default false for CLI, true for eval/debug output

The eval harness should be able to request top-5 and still compute the frozen metrics.

### 4.9 Deterministic Scoring

All scoring must remain local and deterministic.

Do:

- Use stable sorting.
- Use explicit tie-breakers.
- Round output scores for reporting.
- Keep scores decomposed into components.

Do not:

- Use randomness.
- Use network calls.
- Use model calls.
- Use embeddings.
- Use vector databases.

### 4.10 Explainable Ranking Output

MVP-003 should make each ranking auditable.

Recommended output fields:

- `query`
- `rank`
- `chunk_id`
- `source_id`
- `source_file`
- `title`
- `source_priority`
- `evidence_label`
- `score`
- `score_components`
  - `body_tfidf`
  - `title_match`
  - `filename_match`
  - `path_match`
  - `priority_bonus`
  - `evidence_label_bonus`
  - `synonym_bonus`
  - `duplicate_penalty`
- `matched_terms`
- `matched_aliases`
- `risk_tags`

This is critical for diagnosing future regressions.

## 5. Proposed File Changes

Documentation-only in this planning step:

- `docs/MVP_003_RETRIEVAL_IMPROVEMENT_PLAN.md`

Proposed implementation files for a later approved MVP-003 implementation:

| File | Proposed Action | Purpose |
|---|---|---|
| `src/asperitas_agent/retrieval_tfidf.py` | Preserve unchanged or only add comments if needed | Keep MVP-002.5 baseline callable. |
| `src/asperitas_agent/retrieval_mvp003.py` | Add | New metadata-aware deterministic retriever. |
| `src/asperitas_agent/retrieval_normalization.py` | Add | Unicode/token/synonym normalization helpers. |
| `src/asperitas_agent/retrieval_explain.py` | Optional add | Shared score component/explanation structures if retriever grows. |
| `scripts/run_retrieval_eval.py` | Extend conservatively | Add `--retriever baseline|mvp003` and optional output artifact path. |
| `tests/test_retrieval_mvp003.py` | Add | Unit tests for metadata scoring, field weighting, duplicate handling, top_k, and explanations. |
| `tests/test_retrieval_normalization.py` | Add | Unit tests for Korean/English normalization and aliases. |
| `docs/MVP_003_RETRIEVAL_RESULTS.md` | Add after implementation | Record metric deltas and known failures. |

Do not modify:

- `eval/retrieval_questions.jsonl`
- `eval/expected_sources.jsonl`
- `tests/test_retrieval_eval.py`, except to document assumptions if absolutely necessary

## 6. Proposed Function and Module Structure

### `retrieval_normalization.py`

Suggested functions:

```python
def normalize_text_for_retrieval(text: str) -> str: ...
def tokenize_retrieval(text: str) -> list[str]: ...
def expand_query_aliases(tokens: list[str], text: str) -> list[str]: ...
def source_aliases(record: SourceRecord) -> list[str]: ...
```

Design goals:

- Pure functions.
- No external dependencies.
- Deterministic outputs.
- Unit tested with Korean, English, mixed acronym, path, and filename cases.

### `retrieval_mvp003.py`

Suggested dataclasses:

```python
@dataclass
class ScoredCandidate:
    result: RetrievalResult
    score_components: dict[str, float]
    matched_terms: list[str]
    matched_aliases: list[str]
```

Suggested functions:

```python
def build_source_lookup(records: list[SourceRecord]) -> dict[str, SourceRecord]: ...
def score_metadata(query: str, chunk: Chunk, record: SourceRecord) -> tuple[float, dict[str, float]]: ...
def search_chunks_mvp003(
    query: str,
    chunks: list[Chunk],
    records: list[SourceRecord],
    limit: int = 5,
    include_explanations: bool = False,
) -> list[dict] | list[RetrievalResult]: ...
```

Design goals:

- Reuse baseline TF-IDF scoring where practical.
- Keep baseline callable separately.
- Return normal retrieval output by default.
- Return expanded explainable output when requested.

### `scripts/run_retrieval_eval.py`

Proposed extension:

```powershell
python .\scripts\run_retrieval_eval.py --retriever baseline
python .\scripts\run_retrieval_eval.py --retriever mvp003
python .\scripts\run_retrieval_eval.py --retriever mvp003 --output .\09_LOGS\run_logs\retrieval_eval_mvp003.jsonl
```

Rules:

- Default should remain compatible.
- Baseline mode must reproduce MVP-002.5 metrics.
- MVP-003 mode must report comparable metrics.
- Missing files/schema failures should still exit nonzero.

## 7. Expected Metric Improvements

Target metrics:

| Metric | MVP-002.5 Baseline | MVP-003 Target |
|---|---:|---:|
| Source file match @3 | 34.4% | 50%+ |
| Source file match @5 | 43.8% | 60%+ |
| Source priority match | 43.8% | 60%+ |
| Evidence label match | 43.8% | 60%+ |
| Section match | 31.2% | 45%+ |
| Overall pass rate | 31.2% | 45%+ |

Expected contribution by improvement:

| Improvement | Expected Main Gain |
|---|---|
| Metadata-aware indexing | +15 to +25 points Source@5 |
| Title/path/filename weighting | +10 to +20 points Source@3 |
| Korean-English normalization | +8 to +15 points Source@5 on mixed-language cases |
| Synonym/alias normalization | +8 to +15 points Source@5 on named-source cases |
| Duplicate source handling | +3 to +8 points Source@5 |
| Section/title weighting | +10 to +15 points section match if section text is visible |

These gains are not additive. A realistic MVP-003 goal is Source@5 in the 60-70% range and overall pass rate above 45%.

## 8. Implementation Order

1. Create retrieval normalization tests.
   Cover Hangul, Latin, acronym, filename, path, and mixed-language queries.

2. Add `retrieval_normalization.py`.
   Implement deterministic normalization, tokenization, and alias expansion.

3. Add `retrieval_mvp003.py` with metadata-aware scoring.
   Use registry records and chunks together. Preserve baseline retrieval module.

4. Add explainable scoring components.
   Ensure score components are visible in debug/eval output.

5. Extend eval script with retriever selection.
   Add `--retriever baseline|mvp003`. Default behavior should remain stable or explicitly documented.

6. Add tests for metadata ranking.
   Include cases where filename/path should beat generic body text.

7. Add tests for duplicate handling.
   Include PTMC-like and SEED-like duplicate paths.

8. Run full tests.
   Use fresh `--basetemp` on Windows/OneDrive.

9. Run baseline eval and MVP-003 eval.
   Confirm baseline is unchanged and MVP-003 improves target metrics.

10. Document results.
   Add an MVP-003 results doc only after implementation is complete.

## 9. Test Plan

### Unit Tests

Add tests for:

- Korean/English tokenization.
- Unicode normalization.
- Acronym retention: AI, IR, DB, R&D, LMO, GMO, CRISPR.
- Filename/path tokenization.
- Alias expansion.
- Metadata scoring.
- Priority-specific bonuses.
- Evidence-label-specific bonuses.
- Duplicate source penalty/boost.
- Configurable `top_k`.
- Explainable score components.

### Regression Tests

Preserve:

- Existing 41 tests passing.
- Baseline eval metrics reproducible in baseline mode.
- Artifact verification `ok=true`.
- Compliance gate still blocks CITES/high-risk requests.

### Evaluation Tests

Run:

```powershell
$py = "C:\Users\jbc89\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$base = Join-Path $env:TEMP ("asperitas-pytest-" + [guid]::NewGuid().ToString("N"))
& $py -m pytest -q --basetemp=$base
& $py .\scripts\run_retrieval_eval.py --retriever baseline
& $py .\scripts\run_retrieval_eval.py --retriever mvp003
& $py -m asperitas_agent.cli verify-artifacts
```

Expected after implementation:

- Baseline metrics remain unchanged.
- MVP-003 Source@3 >= 50%.
- MVP-003 Source@5 >= 60%.
- MVP-003 Section match >= 45%.
- MVP-003 Overall pass rate >= 45%.

## 10. Risks and Tradeoffs

1. Metadata overfitting risk.
   Heavy filename/path weighting may improve source-identification evals but reduce body-evidence relevance. Mitigation: preserve body TF-IDF and expose score components.

2. P0 dominance risk.
   A universal source-priority boost could make P0 sources dominate all questions. Mitigation: priority weighting must be query-context aware.

3. Alias overreach risk.
   Too many aliases can cause false positives. Mitigation: keep alias table small, explicit, tested, and explainable.

4. Duplicate handling risk.
   Penalizing duplicates can hide valid evidence. Mitigation: never remove duplicates; apply only small, explainable boosts/penalties.

5. Section metric risk.
   Section match may remain low until MVP-004 structure-aware chunking. Mitigation: do not contort MVP-003 retrieval to solve chunking problems.

6. Unicode normalization risk.
   Normalization can accidentally collapse meaningful distinctions. Mitigation: test filenames, Korean strings, acronyms, and original path matching.

7. Benchmark overfitting risk.
   Optimizing only 32 questions can produce brittle retrieval. Mitigation: add explainability and keep changes general; do not edit expected answers.

8. Compatibility risk.
   RAG and CLI currently depend on baseline retrieval. Mitigation: add MVP-003 retrieval behind explicit function/flag before changing default behavior.

## 11. Stop Criteria for MVP-003

MVP-003 is complete when all of the following are true:

1. Existing TF-IDF baseline remains callable.
2. Baseline eval mode reproduces MVP-002.5 metrics.
3. MVP-003 retriever is deterministic and local.
4. No embeddings, vector DB, external APIs, LLM generation, or UI are added.
5. Full tests pass.
6. Artifact verification remains `ok=true`.
7. Compliance gate behavior remains preserved.
8. MVP-003 eval reaches or clearly approaches:
   - Source@3 >= 50%
   - Source@5 >= 60%
   - Section match >= 45%
   - Overall pass rate >= 45%
9. Ranking explanations expose why each top result was selected.
10. Remaining failures are documented without changing the benchmark.

If MVP-003 cannot reach the target without structure-aware chunking, stop after deterministic metadata/tokenization improvements and defer section-heavy improvements to MVP-004.

## 12. Deferred to MVP-004 or Later

### MVP-004

- Heading-aware chunking.
- PDF page-aware chunks.
- PPTX slide-aware chunks.
- HWPX structure-aware parsing.
- Section-title fields in chunk metadata.
- Data quality reports linking parse quality to retrieval failures.
- Better section matching that uses structural metadata instead of literal substring only.

### MVP-005 or Later

- Embeddings.
- Vector DB.
- Semantic reranking.
- LLM answer generation.
- UI.
- External APIs.
- Production deployment claims.
- Legal/regulatory/wet-lab approval workflows.

## 13. Key Architectural Decisions

1. Preserve baseline retrieval.
   `retrieval_tfidf.search_chunks` remains the MVP-002.5 baseline.

2. Add new retrieval module instead of rewriting old one.
   This allows direct baseline-vs-MVP-003 comparison.

3. Use registry metadata as first-class retrieval evidence.
   The source registry is not only governance metadata; it is retrieval context.

4. Keep scoring deterministic and explainable.
   Every ranking improvement should produce inspectable score components.

5. Avoid external dependencies in MVP-003.
   Unicode-aware local normalization is enough for this phase.

6. Treat priority/evidence labels as ranking features, not ground-truth overrides.
   They should help disambiguate, not replace relevance.

7. Do not solve chunking in MVP-003.
   Section-aware chunking belongs primarily to MVP-004.

## 14. Recommended Implementation Prompt

Use this prompt only after approving MVP-003 implementation:

```text
Implement MVP-003 deterministic retrieval improvement.

Constraints:
- Preserve `retrieval_tfidf.search_chunks` as the MVP-002.5 baseline.
- Do not modify `eval/retrieval_questions.jsonl`.
- Do not modify `eval/expected_sources.jsonl`.
- Do not add embeddings, vector DB, external APIs, LLM generation, or UI.
- Add metadata-aware deterministic retrieval in a new module.
- Add Unicode-aware Korean/English normalization and deterministic aliases.
- Add explainable score components.
- Extend the eval script with `--retriever baseline|mvp003`.
- Ensure baseline mode reproduces MVP-002.5 metrics.
- Run tests, baseline eval, MVP-003 eval, and artifact verification.
- Document final MVP-003 metrics and remaining failures.
```
