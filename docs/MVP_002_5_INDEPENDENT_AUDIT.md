# MVP-002.5 Independent Audit

Date: 2026-06-12 KST

Project: Asperitas Agent MVP-002.5 Retrieval Evaluation Baseline

Verdict: CONDITIONAL PASS

## Scope

This audit reviews the current local deterministic retrieval evaluation baseline before MVP-003. It does not modify the benchmark, retrieval questions, expected source mappings, tests, production code, retrieval logic, source registry, or generated artifacts.

Current verified baseline:

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

## A. What Is Implemented Correctly

1. Repository structure is coherent for a staged MVP.
   The repository separates raw sources, processed artifacts, agent system docs, tests, scripts, logs, and documentation. The MVP-002.5 eval files live under `eval/`, while the scorer lives under `scripts/`, which keeps benchmark data distinct from executable code.

2. Retrieval baseline is deterministic and locally reproducible.
   `retrieval_tfidf.py` uses local lexical scoring only. This is appropriate for a baseline because future retrieval upgrades can be compared against fixed metrics without network, embedding, or model variance.

3. Evaluation harness validates schema before scoring.
   `run_retrieval_eval.py` rejects missing files, empty JSONL files, invalid JSON rows, duplicate question IDs, invalid difficulty/category values, and mismatches between question rows and expected-source rows.

4. Evaluation reports source-level and metadata-level metrics.
   The scorer measures source file match, source priority match, evidence label match, section match, and overall pass rate. These are the right first metrics for a provenance-first RAG system.

5. Source registry has stable minimum governance fields.
   `source_registry.csv` tracks source ID, title, filename, path, priority, source type, disclosure level, license status, verification status, checksum, parse status, and notes.

6. Chunk artifacts preserve core provenance.
   `chunks.jsonl` carries source ID, priority, source type, disclosure, evidence label, verification status, risk tags, checksum, title, and text.

7. MVP-002 ingestion safety is meaningfully tested.
   Tests cover PPTX text extraction, safe ZIP inspection, path traversal rejection, suspicious executable rejection, unsupported ZIP inner-file logging, HWPX fallback behavior, mixed ingestion, registry validation, and artifact verification.

8. Compliance boundaries are present at the RAG layer.
   High-risk CITES, Nagoya, LMO/GMO, biosafety, wet-lab, legal, investor, and external communication patterns trigger risk flags and human approval requirements.

9. Windows reproducibility workaround is documented.
   The recommended pytest command uses a fresh temp directory to avoid OneDrive locking of `.pytest_tmp`.

10. GitHub readiness is basically sound.
    The repository has a clean `main...origin/main` state after verification, with reproducible test/eval/artifact commands.

## B. Critical Weaknesses

1. Korean tokenization appears broken or severely underpowered.
   `retrieval_tfidf.py` uses `TOKEN_RE = re.compile(r"[A-Za-z0-9_媛-??{2,}")`, which appears mojibake/corrupted rather than an intentional Unicode Korean token range. This likely contributes directly to weak Korean-source recall.

2. Retrieval does not use registry metadata as searchable evidence.
   The TF-IDF index scores only `chunk.title + chunk.text`. It does not index original filename, registry path, source priority, source folder, extension, source type, or alternate names. Many eval questions are file/topic identification questions, so filename/path metadata should be searchable in a future retrieval layer.

3. Section matching is too literal.
   `section_match` checks whether the expected section string appears as a case-insensitive substring in matched title/text. It does not support aliases, Korean morphology, normalized spacing, OCR noise, page headers, or semantically equivalent section labels.

4. Chunking is fixed-size and not structure-aware.
   `chunk_document()` slices normalized text into 1000-character windows with 125-character overlap. It does not use headings, slide boundaries, PDF page boundaries, table units, title/subtitle context, or document sections. This can split relevant evidence away from its section label.

5. Eval set is useful but not yet calibrated.
   The 32-question benchmark contains a mix of source-identification questions, section lookup questions, science topic questions, policy questions, and duplicated-source questions. That is healthy, but failures are not yet tagged by root cause, so MVP-003 cannot yet optimize against specific failure classes.

## C. Hidden Risks

1. Benchmark may over-penalize conceptually valid near-duplicate sources.
   Some expected sources have near duplicates or overlapping AOS/README/P0 content. Retrieval may return a valid related source but fail source-file match because the benchmark demands one exact file.

2. Benchmark may under-test compliance retrieval.
   Compliance gate behavior is tested elsewhere, but MVP-002.5 retrieval eval focuses mostly on expected source identity. It does not yet measure whether high-risk evidence is retrieved early enough for risk-aware answering.

3. Evidence label match is currently derivative of priority.
   Evidence labels are assigned from source priority in chunking. Therefore evidence label metrics mostly mirror source priority/source-file match and do not independently validate nuanced evidence quality.

4. Registry is CSV-based and weakly typed.
   CSV is fine for MVP, but future schema evolution, aliases, parent-child ZIP inner files, source supersession, language, jurisdiction, and canonical document family fields will become hard to manage safely.

5. HWPX/PDF extraction quality can silently affect retrieval quality.
   Ingestion logs expose parse status, but the eval harness does not correlate failures with extraction quality, empty sections, bad OCR/text order, or mojibake.

6. Path and filename normalization are minimal.
   The scorer normalizes slashes and case, but not Unicode normalization, compatibility forms, decomposed Korean jamo, whitespace variants, or legacy macOS filename normalization.

7. No machine-readable failure taxonomy exists yet.
   The eval output lists failed question IDs and top result paths, but not why each failed. This makes regression triage manual and slows MVP-003 iteration.

8. Plain pytest remains environment-sensitive.
   `pyproject.toml` uses repo-local `.pytest_tmp`; on Windows/OneDrive this can be locked. The fresh `--basetemp` workaround is reliable but must be kept in docs and CI instructions.

9. No CI workflow is confirmed.
   GitHub publication is good, but audit readiness should include a GitHub Actions or equivalent reproducibility check if the repository is intended for collaborative development.

10. Compliance pattern strings contain mojibake.
    Several Korean risk patterns in `compliance.py` appear encoding-corrupted. English triggers still work, but Korean compliance detection may be incomplete.

## D. Missing Components

1. Failure taxonomy and per-question failure labels.
   Needed to distinguish Korean tokenization failures, metadata lookup failures, duplicate-source confusion, section-boundary failures, and ranking failures.

2. Metadata-enriched retrieval baseline.
   Needed before embeddings so lexical retrieval can search filenames, paths, folder priority, source type, aliases, and registry notes.

3. Language-aware tokenizer.
   Needed for Korean/English mixed corpora. This does not require embeddings; a deterministic Unicode-aware tokenizer can come first.

4. Alias and canonical source-family fields.
   Needed for AOS versions, duplicated PTMC decks, duplicated SEED files, Korean/English title variants, and sources with decomposed Unicode filenames.

5. Structure-aware chunker.
   Needed for headings, PDF pages, slide boundaries, notes, document titles, and source-specific section metadata.

6. Eval result artifact output.
   The scorer prints summaries but does not persist a JSON/CSV result artifact for longitudinal comparison.

7. Retrieval regression threshold policy.
   There is no documented rule such as "MVP-003 must improve Source@5 by N points without lowering compliance tests."

8. CI verification workflow.
   No confirmed automated GitHub check for tests, artifact verification, and eval baseline reproduction.

9. Data quality report.
   No report correlates parse status, chunk counts, mojibake risk, unsupported entries, and retrieval failures by source.

10. Compliance retrieval eval.
    Current compliance tests validate blocking behavior, but not recall of compliance-relevant evidence by category.

## E. Technical Debt Ranking

| Rank | Debt | Severity | Why It Matters |
|---:|---|---|---|
| 1 | Corrupted or inadequate Korean tokenizer regex | Critical | Directly limits retrieval over Korean source corpus and may distort every metric. |
| 2 | Retrieval ignores filename/path/registry metadata | Critical | Many expected answers are document-level; text-only chunk scoring misses obvious source identity signals. |
| 3 | Fixed-size character chunking | High | Splits headings from body text and harms section-level retrieval. |
| 4 | No failure taxonomy artifact | High | MVP-003 cannot be optimized scientifically without knowing why failures occur. |
| 5 | Literal section substring matching | High | Underestimates retrieval quality and blocks robust section metrics. |
| 6 | CSV registry schema lacks aliases/canonical families | Medium | Duplicate and versioned sources will increasingly confuse retrieval and evaluation. |
| 7 | Mojibake in compliance Korean patterns | Medium | Korean high-risk requests may not trigger reliably. |
| 8 | No persisted eval run artifact | Medium | Harder to compare runs, track regressions, and audit improvements. |
| 9 | OneDrive `.pytest_tmp` sensitivity | Medium | Local verification can fail for environmental reasons despite healthy code. |
| 10 | No confirmed GitHub CI | Medium | Published repo may not be reproducibly verified outside the local machine. |

## F. What Should Be Fixed Before MVP-003

1. Freeze the MVP-002.5 benchmark exactly as-is.
   Do not modify `eval/retrieval_questions.jsonl` or `eval/expected_sources.jsonl` before MVP-003. Treat the current metrics as the baseline.

2. Create a failure analysis report from the existing failed question IDs.
   Each failed question should be tagged with primary and secondary causes: Korean/English mismatch, metadata mismatch, duplicate source confusion, chunk boundary issue, section-level issue, source priority issue, naming inconsistency, or ranking issue.

3. Define an MVP-003 retrieval improvement target.
   Example: improve Source@5 from 43.8% to at least 65% while preserving all artifact/compliance tests and not reducing CITES/high-risk blocking behavior.

4. Fix tokenizer design before changing ranking.
   The current regex should be replaced or supplemented in MVP-003 with deterministic Unicode-aware tokenization, especially for Hangul syllables, Latin terms, numbers, and mixed punctuation.

5. Design metadata-enriched lexical indexing.
   Add registry path, original filename, title aliases, source priority, source type, and source folder as searchable fields in MVP-003. This should be measured against the frozen MVP-002.5 benchmark.

6. Add machine-readable eval outputs.
   MVP-003 should write per-question result JSONL/CSV including top-k sources, matched rank, scores, and failure category.

7. Preserve the fresh `--basetemp` pytest command in verification docs.
   Avoid making local verification dependent on deleting a OneDrive-synced `.pytest_tmp` folder.

## G. What Should Not Be Changed

1. Do not change MVP-002.5 benchmark questions before measuring MVP-003.
2. Do not change expected source mappings to improve metrics.
3. Do not add embeddings before metadata/tokenization baseline improvements are measured.
4. Do not add a vector DB before the lexical failure causes are understood.
5. Do not add LLM answer generation as a retrieval fix.
6. Do not weaken compliance blocking to improve answer coverage.
7. Do not remove source provenance fields from chunks or retrieval results.
8. Do not collapse duplicate sources without preserving original source paths and provenance.
9. Do not treat `overall_pass_rate` as an answer-quality metric.
10. Do not claim production-grade RAG, legal approval, regulatory approval, or wet-lab validation.

## H. Recommended Roadmap

### MVP-003: Deterministic Retrieval Upgrade

Goal: improve lexical retrieval without embeddings or external APIs.

Recommended scope:

- Unicode-aware Korean/English tokenization.
- Metadata-enriched indexing over filename, path, title, source type, source priority, and registry notes.
- Field weighting for title/path/filename versus body text.
- Optional deterministic query expansion from source aliases and registry metadata.
- Per-question eval output artifact with top-k results and failure categories.
- Regression threshold: preserve all current tests and improve Source@5 materially against the frozen benchmark.

Do not include embeddings, vector DB, LLM answer generation, or UI in MVP-003.

### MVP-004: Structure-Aware Ingestion and Chunking

Goal: improve evidence granularity and section retrieval.

Recommended scope:

- Heading-aware Markdown/DOCX chunking.
- Slide-aware PPTX chunking with slide number provenance.
- PDF page-aware chunks with page metadata where extractable.
- Better HWPX structure extraction if feasible.
- Chunk fields for `section_title`, `page_start`, `page_end`, `slide_number`, and `parent_source_path`.
- Data quality report linking parse status and retrieval performance.

### MVP-005: Hybrid Retrieval Readiness

Goal: prepare for advanced retrieval only after deterministic baselines are strong.

Recommended scope:

- Compare deterministic lexical, metadata-weighted lexical, and optional reranking approaches.
- Add retrieval regression dashboards or persisted reports.
- Only then evaluate embeddings/vector DB as an experimental backend behind the same eval harness.
- Add compliance-focused retrieval evals for CITES, Nagoya, LMO/GMO, biosafety, legal, investor, and external-communication categories.
- Keep source registry, provenance, disclosure levels, and human-approval gates mandatory for all retrieval backends.

## I. Verdict

CONDITIONAL PASS.

The repository is ready for audit and ready to begin MVP-003 planning. It is not ready for production retrieval claims. MVP-003 can start only if the MVP-002.5 benchmark is frozen, current metrics remain the baseline, and the first MVP-003 work targets deterministic retrieval weaknesses rather than jumping to embeddings, vector DB, UI, or LLM generation.

The most important next action is a failure taxonomy pass over the 20 failing MVP-002.5 questions, followed by a deterministic metadata/tokenization retrieval upgrade measured against the unchanged benchmark.
