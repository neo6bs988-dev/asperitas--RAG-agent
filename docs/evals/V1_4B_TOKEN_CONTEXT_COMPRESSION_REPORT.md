# V1.4B Token Context Compression Report

## Executive bottom line

V1.4B applies deterministic post-retrieval context compression by compacting whitespace and lowering the evidence excerpt cap after retrieval scoring, preserving citation keys, source IDs, source paths, source priority, evidence labels, section metadata, and source boundaries.

## Token/context delta

- Answer approximate tokens: 9432 -> 9432 (0)
- Retrieved-context approximate tokens: 13215 -> 7983 (-5232)
- Citation count preserved: True
- Evidence count preserved: True
- Source paths preserved: True
- Retrieval scoring changed: False
- Source artifacts mutated: False

## Highest improved cases

- GOLDEN-001 (golden_eval): context -350, answer 0
- GOLDEN-002 (golden_eval): context -350, answer 0
- GOLDEN-003 (golden_eval): context -350, answer 0
- GOLDEN-004 (golden_eval): context -350, answer 0
- GOLDEN-006 (golden_eval): context -350, answer 0

## Regressions

- None detected by this deterministic comparison.

## Quality boundary

This artifact compares deterministic token/context metrics. Answer quality is guarded by the separate V1.3C, V1.3D, golden, retrieval, and pytest validation commands; it is not claimed from this metric alone.
