from __future__ import annotations

from typing import Any

from .agent_adapter import adapt_agent_response
from .privacy import audit_sanitized_trace, sanitize_trace
from .trace_schema import validate_trace_envelope


def build_shadow_trace(
    invocation: dict[str, Any],
    *,
    case_id: str,
    trial_id: str,
    conversation_id: str,
    data_class: str,
    secret: bytes,
    capture_content: bool,
) -> dict[str, Any]:
    trace = adapt_agent_response(
        invocation["response"],
        case_id=case_id,
        trial_id=trial_id,
        conversation_id=conversation_id,
        data_class=data_class,
        harness_version="evalos-v1.4-shadow",
        prompt_version=str(
            invocation["response"]["metadata"].get(
                "prompt_version",
                "incumbent-deterministic",
            )
        ),
    )

    trace["attributes"]["asperitas.shadow.mode"] = "NO_EFFECT"
    trace["attributes"]["asperitas.shadow.latency_ms"] = float(
        invocation["latency_ms"]
    )
    trace["attributes"]["asperitas.shadow.records_mutated"] = bool(
        invocation["input_mutation"]["records_mutated"]
    )
    trace["attributes"]["asperitas.shadow.chunks_mutated"] = bool(
        invocation["input_mutation"]["chunks_mutated"]
    )
    trace["attributes"]["asperitas.shadow.network_egress_count"] = int(
        invocation["network_egress_count"]
    )
    trace["attributes"]["asperitas.shadow.provider_export_count"] = int(
        invocation["provider_export_count"]
    )

    outcome_span = next(
        span
        for span in trace["spans"]
        if span["span_type"] == "environment_outcome"
    )
    outcome_span["attributes"][
        "asperitas.outcome.external_effect_count"
    ] = int(invocation["external_effect_count"])
    outcome_span["attributes"][
        "asperitas.outcome.input_mutation_count"
    ] = int(
        invocation["input_mutation"]["records_mutated"]
        or invocation["input_mutation"]["chunks_mutated"]
    )

    envelope_report = validate_trace_envelope(trace)
    sanitized = sanitize_trace(
        trace,
        secret=secret,
        capture_content=capture_content,
    )
    privacy_report = audit_sanitized_trace(sanitized)

    return {
        "raw_trace": trace,
        "sanitized_trace": sanitized,
        "envelope_report": envelope_report,
        "privacy_report": privacy_report,
    }
