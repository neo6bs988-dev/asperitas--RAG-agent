# GUARDRAILS Benchmark Notes

Priority: P6 External Benchmark
Use: output validation, schema checks, structured guardrails.

## Source
- Guardrails AI docs
- URL: https://guardrailsai.com/guardrails/docs

## Patterns to Absorb
- Validate generated outputs against expected structure.
- Use schemas for high-risk or operationally important outputs.
- Fail closed when required fields are missing.

## Asperitas V1 Application
- MVP-019 audit outputs should use required fields.
- Compliance gate outputs should include:
  - risk_domain
  - evidence_status
  - gate_decision
  - human_approval_required
  - safe_next_action
- Answer generation should fail or warn when citation fields are missing.
