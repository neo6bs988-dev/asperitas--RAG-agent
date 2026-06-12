# MVP-002.5 Retrieval Failure Analysis

Date: 2026-06-12 KST

Project: Asperitas Agent retrieval evaluation baseline

Scope: analysis only. This document does not modify benchmark files, expected source mappings, tests, retrieval code, embeddings, vector DB, external APIs, LLM answer generation, or UI.

## Baseline Under Analysis

- Total questions: 32
- Passed overall: 10
- Failed overall: 22
- Source file match @3: 34.4%
- Source file match @5: 43.8%
- Source priority match: 43.8%
- Evidence label match: 43.8%
- Section match: 31.2%
- Overall pass rate: 31.2%

The evaluation was rerun with:

```powershell
$py = "C:\Users\jbc89\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py .\scripts\run_retrieval_eval.py --json
```

## 1. Failure Category Table

These categories are not mutually exclusive. A single failed question can have a primary cause and one or more contributing causes.

| Failure Category | Estimated Count | Share of 22 Failures | Example Question IDs | Primary Impacted Metrics | Notes |
|---|---:|---:|---|---|---|
| Metadata mismatch / filename not indexed | 14-18 | 64-82% | Q007, Q008, Q009, Q010, Q011, Q012, Q013, Q015, Q020, Q021, Q023, Q025, Q026, Q027, Q030, Q032 | Source@3, Source@5, priority, evidence label | Many questions ask "which source/file/document" but current retrieval scores chunk title and body text only, not full registry metadata, path, filename, folder, aliases, or source family. |
| Weak title/section weighting | 12-16 | 55-73% | Q001, Q003, Q004, Q005, Q006, Q007, Q009, Q010, Q015, Q021, Q027, Q030 | Source@3, section match, overall pass | Relevant title/path terms are not strongly boosted over generic body-text matches. |
| Korean/English mismatch and mixed-language tokenization | 10-14 | 45-64% | Q012, Q015, Q020, Q021, Q023, Q025, Q026, Q027, Q028, Q030, Q032 | Source@5, section match | Korean titles and English paraphrases are weakly aligned. Deterministic tokenization appears insufficient for Korean/English mixed corpora. |
| Overlap between similar company/internal/P0 sources | 8-10 | 36-45% | Q001, Q003, Q004, Q005, Q007, Q008, Q009, Q013, Q015, Q027, Q030 | Source@3, Source@5 | AOS, README, build guide, master constitution, and internal strategy documents share repeated language, causing generic governance or strategy questions to rank the wrong but related source. |
| Section-level retrieval failure | 4 | 18% | Q001, Q003, Q004, Q006 | Section match, overall pass | Expected source appears in top-5, but expected section string is not found in the matched chunk text/title. |
| Duplicate source confusion | 3-4 | 14-18% | Q009, Q010, Q020, Q032 | Source@5, source priority, evidence label | PTMC and SEED exist in multiple locations or nearby categories; exact expected path matters but retrieval has no canonical source-family/duplicate handling. |
| Missing synonym/alias normalization | 8-12 | 36-55% | Q004, Q005, Q011, Q012, Q014, Q021, Q023, Q025, Q026, Q030 | Source@5, section match | Queries use English descriptions, abbreviated names, or translated concepts while expected sources use Korean filenames or variant titles. |
| Chunk boundary issue | 4-6 | 18-27% | Q001, Q003, Q004, Q006, Q023, Q027 | Section match, overall pass | Fixed 1000-character chunks can separate headings, source names, and relevant body content. |
| Source priority/evidence label mismatch as downstream failure | 18 | 82% | All source@5 misses | Priority, evidence label | Priority and evidence label usually fail because expected source file is absent from top-5, not because priority assignment itself is wrong. |
| Retrieval ranking weakness | 18-22 | 82-100% | All failed cases | All retrieval metrics | Current TF-IDF lacks metadata fields, field weighting, language-aware tokenization, and duplicate-aware ranking. |

## 2. Root Cause Analysis

### Root Cause 1: The baseline optimizes body-text lexical overlap, but the benchmark often asks source-identification questions.

Current retrieval uses:

```text
chunk.title + " " + chunk.text
```

It does not score:

- `original_filename`
- registry `path`
- folder path such as `P1_ASPERITAS_INTERNAL` or `P5_INDUSTRY_INTELLIGENCE`
- source priority
- source type
- registry notes
- alternate Korean/English aliases
- canonical document family

This explains many top-5 misses. Questions such as "Which source should answer..." or "Where should retrieval find..." are metadata-heavy. The expected source may be obvious from filename/path, but invisible or weakly represented in the searchable text.

### Root Cause 2: Korean and English are not normalized into a shared retrieval space.

The corpus contains Korean filenames, Korean PDF text, English document names, mixed English/Korean questions, and technical terms such as CRISPR, LMO, R&D, PTMC, IR, SEED, and AI. The current deterministic tokenizer is minimal and does not perform:

- Hangul-aware token segmentation
- Unicode normalization
- Korean spacing normalization
- bilingual synonym expansion
- title translation aliases
- acronym expansion

This causes questions in English to miss Korean-title sources and questions with Korean source terms to over-match unrelated chunks with common synthetic biology terms.

### Root Cause 3: P0 governance documents are highly overlapping.

Several P0 sources repeat source hierarchy, evidence labels, governance constraints, development order, compliance language, and RAG architecture. This causes the retriever to return a nearby governance source, often README, AGENTS, AOS prompt, build guide, or master constitution, while the benchmark expects one exact file.

Examples:

- Q003 expected the v10.3 universal master prompt, but top result was `README.md`.
- Q004 expected `P0_ACTIVE_PROMPT_MASTER_CONSTITUTION.pdf`, but top result was another AOS constitution PDF.
- Q005 expected the Codex AI Agent build guide, but top result was the DB integration guide.

This is not purely a failure of relevance; it is a failure of exact-source disambiguation.

### Root Cause 4: Section matching is fragile.

Four failed questions have the expected source inside top-5 but fail overall because `section_match=false`:

- Q001
- Q003
- Q004
- Q006

The current section logic is literal substring matching against the matched result's title/text. It cannot handle:

- section names split across chunks
- heading/body separation
- equivalent labels such as "source hierarchy" vs "source of truth hierarchy"
- PDF extraction line breaks
- missing section heading in a body-only chunk
- Korean/English translation differences

### Root Cause 5: Fixed-size chunks erase document structure.

Chunks are generated by character range, not by logical sections, pages, slides, headings, tables, or document hierarchy. This matters because the benchmark expects section- or document-level recall, not only arbitrary text overlap.

The current chunker preserves source provenance, but not enough structural provenance for precise section retrieval.

### Root Cause 6: Source priority and evidence label failures are mostly secondary.

The metric shows source priority and evidence label match at 43.8%, equal to Source@5. This indicates priority/evidence label are usually correct when the expected source is found. Failures are mostly caused by not retrieving the expected source at all.

Therefore, MVP-003 should not start by changing priority labels or evidence label rules. It should improve source matching first.

## 3. Example Failed Cases

| Question ID | Expected Source Pattern | Top Result | Likely Cause |
|---|---|---|---|
| Q001 | `AGENTS.md` | `Asperitas_AOS_v10_3_Universal_AI_Tool_Master_Prompt.md` | Source appears in top-5, but section string mismatch; overlapping P0 source hierarchy language. |
| Q003 | v10.3 universal master prompt | `README.md` | P0 governance overlap plus weak title/path weighting. |
| Q004 | master constitution PDF | v10.3 master format constitution PDF | Similar AOS constitution sources; exact-source disambiguation missing. |
| Q005 | Codex AI Agent build guide | DB integration guide | Related Codex/constitution/database wording outranks expected guide. |
| Q007 | Asperitas IR deck | `README.md` | Filename/path metadata not indexed strongly; generic investor/company terms over-match. |
| Q009 | internal PTMC PPTX | Codex AI Agent build guide | PTMC document identity is mostly metadata; PPTX extracted body text may be sparse. |
| Q010 | R&D project PTMC PPTX | scientific PDF top result | Duplicate PTMC source and folder-specific expected path are invisible to retrieval. |
| Q011 | AI X Business Strategy HWPX | scientific paper | HWPX title/source identity not weighted; body text may not contain title strongly. |
| Q021 | LMO regulation trends PDF | AOS v10.0 prompt | Compliance/governance language over-matches LMO topic. |
| Q030 | CRISPR synthetic biology convergence design PDF | Codex AI Agent build guide | CRISPR/source title needs metadata and title weighting; generic design/strategy wording over-matches. |
| Q032 | P5 industry SEED report | DB integration guide | Duplicate SEED/internal-vs-industry source confusion and weak folder/priority weighting. |

## 4. Highest-Impact Fixes

These are MVP-003 recommendations only. They should be measured against the unchanged MVP-002.5 benchmark.

| Fix | Description | Expected Impact | Most Improved Metrics | Estimated Improvement |
|---|---|---|---|---|
| Metadata-enriched indexing | Add title, original filename, registry path, folder, source type, priority, and notes to searchable fields. | Very high | Source@3, Source@5, priority, evidence label | Source@5 +15 to +25 points |
| Field weighting | Weight filename/title/path higher than body text for source-identification questions. | Very high | Source@3, Source@5 | Source@3 +10 to +20 points |
| Korean/English deterministic tokenization | Replace minimal regex with Unicode-aware Hangul/Latin/number tokenization and normalization. | High | Source@5, section match | Source@5 +8 to +15 points |
| Alias/synonym table | Add deterministic aliases for source titles, abbreviations, translated concepts, and canonical document names. | High | Source@5, duplicate disambiguation | Source@5 +8 to +15 points |
| Section-aware chunk metadata | Preserve headings, page/slide labels, and section titles in chunk metadata or prefixed chunk text. | Medium-high | Section match, overall pass | Section match +15 to +25 points |
| Duplicate/canonical source family handling | Add metadata for document family, copy location, and preferred source path without collapsing provenance. | Medium | Source@5, P5/P1 disambiguation | Source@5 +3 to +8 points |
| Eval result artifact | Persist per-question top-k result rows and failure labels. | Indirect high | Debug speed, regression quality | No direct metric gain, but essential for controlled MVP-003 iteration |

## 5. Estimated Metric Improvement by Fix

These estimates assume MVP-002.5 benchmark remains frozen and improvements are deterministic.

| MVP-003 Change | Source@3 | Source@5 | Priority Match | Evidence Label Match | Section Match | Overall Pass |
|---|---:|---:|---:|---:|---:|---:|
| Metadata-enriched indexing only | +10-15 pts | +15-25 pts | +15-25 pts | +15-25 pts | +3-6 pts | +10-18 pts |
| Metadata + field weighting | +15-25 pts | +20-30 pts | +20-30 pts | +20-30 pts | +5-8 pts | +15-22 pts |
| Add Korean/English tokenizer normalization | +3-8 pts | +8-15 pts | +8-15 pts | +8-15 pts | +5-10 pts | +6-12 pts |
| Add alias/source-family normalization | +5-10 pts | +8-15 pts | +8-15 pts | +8-15 pts | +3-8 pts | +6-12 pts |
| Add section-aware chunk metadata | +0-5 pts | +3-8 pts | +3-8 pts | +3-8 pts | +15-25 pts | +8-15 pts |

Reasonable MVP-003 target:

- Source file match @3: 50-55%
- Source file match @5: 65-70%
- Source priority match: 65-70%
- Evidence label match: 65-70%
- Section match: 45-55%
- Overall pass rate: 50-55%

Aggressive but plausible target if metadata, field weighting, tokenizer normalization, and aliases all land cleanly:

- Source file match @5: 70%+
- Overall pass rate: 55%+

## 6. MVP-003 Recommended Priorities

1. Freeze the benchmark.
   Do not edit `eval/retrieval_questions.jsonl` or `eval/expected_sources.jsonl`.

2. Persist eval outputs.
   Add a run artifact in MVP-003 that records top-k results, expected source, matched rank, scores, and failure category. This is not a retrieval improvement, but it is necessary to measure retrieval improvements responsibly.

3. Add metadata-enriched lexical indexing.
   Search across filename, path, title, source type, source priority, and registry notes in addition to chunk body text.

4. Add deterministic field weighting.
   Give filename/path/title matches more influence than generic body matches, especially for "which source" and "where should retrieval find" questions.

5. Add Unicode-aware tokenization.
   Normalize Korean, English, numbers, acronyms, underscores, hyphens, parentheses, and common punctuation.

6. Add deterministic alias normalization.
   Support source-title aliases such as IR deck, PTMC, SEED, LMO, CRISPR, AI roadmap, company introduction, source hierarchy, source of truth hierarchy, and Korean/English title equivalents.

7. Measure after each change.
   Run the same MVP-002.5 eval after every retrieval change and record metric deltas. Do not optimize by editing the benchmark.

## 7. What Should Be Deferred to MVP-004 or Later

### Defer to MVP-004

- Heading-aware chunking
- PDF page-aware chunking and page labels
- PPTX slide-aware chunks
- HWPX structure-aware parsing
- Section-title metadata fields
- Data quality report linking parse quality to retrieval failures

These are important, but MVP-003 should first prove that deterministic metadata and tokenization fixes improve the frozen baseline.

### Defer to MVP-005 or Later

- Embeddings
- Vector database
- Semantic reranking
- LLM answer generation
- UI
- External APIs
- Production RAG claims

These could help semantic paraphrase and deep concept matching, but they should not be used before deterministic lexical and metadata retrieval are strong enough to provide a stable comparison baseline.

## 8. Failures Not Fully Solvable Without Later Semantic Retrieval

Some cases may remain difficult after deterministic MVP-003 improvements:

1. Deep paraphrase questions where the expected source does not contain the query terms or filename terms.
2. Questions requiring conceptual understanding rather than lexical overlap, such as broad strategy implications.
3. Cases where multiple AOS or internal strategy documents contain essentially the same claim and the benchmark requires exact source preference.
4. Korean/English translation equivalents not covered by deterministic alias tables.
5. Poorly extracted PDF/HWPX content where the relevant text is absent, reordered, or garbled.

Embeddings, vector DB, or reranking may eventually help these, but only after MVP-003 creates a stronger deterministic baseline.

## 9. Summary

The biggest failure mode is not that the source registry or compliance labels are wrong. The main issue is that the retrieval baseline is under-indexing the information needed to satisfy the benchmark.

The current TF-IDF baseline primarily sees chunk body text. The benchmark often expects document identity, source path, source folder, exact file version, and section labels. MVP-003 should therefore improve deterministic retrieval in this order:

1. Metadata-enriched indexing
2. Field weighting
3. Korean/English tokenization
4. Alias/source-family normalization
5. Persisted eval output and failure taxonomy

Implementation can start after this analysis if the benchmark remains frozen and MVP-003 avoids embeddings, vector DB, external APIs, LLM generation, and UI.
