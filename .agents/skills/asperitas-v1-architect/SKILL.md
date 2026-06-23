---
name: asperitas-v1-architect
description: Use when planning MVP-016 onward, selecting benchmark patterns, or checking whether a change improves V1 architecture layers.
---

# Asperitas V1 Architect Skill

## Purpose
Move Asperitas Agent from RAG foundation to V1 architecture.

## Required Benchmark Inputs
Before proposing architecture, read:
- `01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/V1_FINAL_BENCHMARK_PACK.md`
- `01_RAW_SOURCES/P6_EXTERNAL_BENCHMARKS/ADDITIONAL_PERFORMANCE_BENCHMARKS.md`
- relevant `.agents/skills/*/SKILL.md`
- `AGENTS.md`

## V1 Layers
Every change must improve at least one:
- Knowledge Layer
- Skills Layer
- Workflow Layer
- RAGAS/Eval Layer
- Audit Layer
- Guardrail Layer
- MCP Expansion Layer

## MVP Sequence
- MVP-016 Skills Framework
- MVP-017 RAGAS-style Eval Layer
- MVP-018 Workflow / Planner Layer
- MVP-019 Audit Trace Layer
- MVP-020 Guardrail Test Layer
- MVP-021 MCP Expansion Plan

## Decision Rules
1. Prefer small testable changes.
2. Preserve MVP-001 to MVP-015 behavior.
3. Preserve source provenance and citation metadata.
4. Add or update tests with every architecture change.
5. Record before/after metrics when evaluation or retrieval changes.
6. Avoid dependency sprawl; benchmark concepts first, dependencies second.
7. Do not claim production completion without artifacts.

## Required Report
1. Objective
2. V1 layer improved
3. Benchmark source applied
4. Files changed
5. Tests run
6. Metrics before and after
7. Risks
8. Remaining gaps
9. Next MVP action
