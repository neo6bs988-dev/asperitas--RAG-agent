# AGENTS.md Migration - v10.3 to v10.4

## Purpose
Upgrade the repo instruction system from AOS v10.3-era prompt architecture to v10.4 control-plane.

## What Changed
- v10.4 becomes active P0 operating constitution.
- Required prompt slots added: Goal / Scope / Evidence / Constraints / Output / Verification / Stop Rules.
- MVP type and risk class gates added.
- KPI_REPORT added.
- Security/privacy/compliance gates strengthened.
- Production-state non-confusion rules strengthened.
- Token minimization reframed as context compression and negative scope, not reduced reasoning quality.

## What Did Not Change
- Earlier AOS layers remain active as inherited doctrine.
- Source-grounding remains mandatory.
- Human approval remains required for high-risk bio/legal/regulatory/investor/external outputs.
- No production DB/KG/vector/eval/legal/wet-lab completion is claimed by this migration alone.

## Verification
- Confirm files exist.
- Confirm AGENTS.md references v10.4.
- Confirm source registry has P0-AOS-V10-4.
- Confirm prompt lint and Codex handoff templates exist.
- Run repo tests/evals where applicable.
