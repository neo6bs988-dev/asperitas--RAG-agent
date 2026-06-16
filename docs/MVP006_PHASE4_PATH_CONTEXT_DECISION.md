# MVP-006 Phase 4 Path Context Decision

Date: 2026-06-16

Related issue: #26

## Decision

Represent folder/path expectations with a separate optional eval field:

```json
"expected_path_context": "P1_RND_PROJECTS"
```

Do not store folder/path expectations in chunk `section`, `section_heading`, or `heading_context` unless the source itself actually contains that text as local heading structure.

## Why

`MVP0025-Q010` asks where the R&D projects copy of the 2026 PTMC project is stored.

The expected source is:

```text
01_RAW_SOURCES/P1_RND_PROJECTS/2026 PTMC project.pptx
```

The expected signal `P1_RND_PROJECTS` is present in the source path. It is not present in the expected source's chunk `section`, `section_heading`, `section_path`, `heading_context`, or chunk text.

Therefore `P1_RND_PROJECTS` is source folder/path provenance context, not semantic chunk section context.

## Options Considered

1. Store folder/path context in `section` or `section_heading`.
   - Rejected. This would create fake chunk headings and weaken the meaning of section match.

2. Store folder/path context in `heading_context`.
   - Rejected. Heading context should describe document-local heading ancestry, not repository folder provenance.

3. Add `expected_path_context`.
   - Accepted. This preserves the distinction between chunk-local section evidence and source-level path provenance.

4. Treat `expected_chunk_or_section` as section-or-path.
   - Rejected. This would make section metrics ambiguous and hide fixture quality problems.

## Implementation

`expected_path_context` is optional and backward-compatible.

Eval scoring now checks:

- `expected_chunk_or_section` against chunk-local fields: title, section, section heading, section path, heading context, and text.
- `expected_path_context` against `source_file`.

Overall pass requires every applicable gate to pass:

- source file
- source priority
- evidence label
- section match, when a section expectation is provided
- path context match, when a path expectation is provided

## Q010 Fixture Update

Before:

```json
"expected_chunk_or_section": "P1_RND_PROJECTS"
```

After:

```json
"expected_chunk_or_section": "",
"expected_path_context": "P1_RND_PROJECTS"
```

## Metrics Impact

Dataset: `eval/retrieval_questions.jsonl`

Top-k: 5

| Mode | Before overall | After overall | Before section | After section | Path context |
|---|---:|---:|---:|---:|---:|
| baseline | 34.4% | 34.4% | 34.4% | 35.5% | 0.0% |
| mvp003 | 90.6% | 93.8% | 90.6% | 93.5% | 100.0% |
| vector | 53.1% | 56.2% | 53.1% | 54.8% | 100.0% |
| hybrid | 96.9% | 100.0% | 96.9% | 100.0% | 100.0% |

The retrieval behavior did not change. The metric change comes from correcting the eval representation for folder/path provenance.

## Regression Check

No source priority, evidence label, section, or metadata gate was relaxed.

Path context does not satisfy section expectations. A question with `expected_chunk_or_section` still requires chunk-local section evidence.

## Next Task

MVP-006 Phase 5: decide whether hybrid can graduate from experimental to accepted eval mode, or whether another failure analysis pass is needed before MVP-007 reranker work.
