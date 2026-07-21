from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .real_agent_bridge import canonical_sha256, invoke_no_effect_agent
from .shadow_contracts import ShadowCase, ShadowPolicy
from .shadow_trace import build_shadow_trace


def _semantic_trace_signature(
    trace: dict[str, Any],
) -> list[dict[str, Any]]:
    id_to_type = {
        str(span["span_id"]): str(span["span_type"])
        for span in trace["spans"]
    }
    signature = []
    for span in trace["spans"]:
        attributes = dict(span.get("attributes", {}))
        parent_id = span.get("parent_span_id")
        signature.append(
            {
                "span_type": str(span["span_type"]),
                "parent_span_type": (
                    None
                    if parent_id is None
                    else id_to_type.get(str(parent_id))
                ),
                "operation": attributes.get("gen_ai.operation.name"),
                "guardrail_decision": attributes.get(
                    "asperitas.guardrail.decision"
                ),
                "verification_label": attributes.get(
                    "gen_ai.evaluation.score.label"
                ),
                "outcome_status": attributes.get(
                    "asperitas.outcome.status"
                ),
                "external_effect_count": attributes.get(
                    "asperitas.outcome.external_effect_count"
                ),
            }
        )
    return signature


def run_shadow_case(
    case_value: dict[str, Any],
    policy_value: dict[str, Any],
    *,
    variants: dict[str, Callable[..., Any]],
    records_factory: Callable[[], list[Any]],
    chunks_factory: Callable[[], list[Any]],
    secret: bytes,
    call_kwargs: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    case = ShadowCase.from_dict(case_value)
    policy = ShadowPolicy.from_dict(policy_value)
    results: list[dict[str, Any]] = []

    for variant_name, callable_ in sorted(variants.items()):
        for repetition in range(case.repetitions):
            records = records_factory()
            chunks = chunks_factory()
            trial_id = (
                f"{case.case_id}-{variant_name}-{repetition + 1:03d}"
            )
            invocation = invoke_no_effect_agent(
                callable_,
                query=case.query,
                top_k=case.top_k,
                records=records,
                chunks=chunks,
                call_kwargs=call_kwargs,
            )
            trace_bundle = build_shadow_trace(
                invocation,
                case_id=case.case_id,
                trial_id=trial_id,
                conversation_id=f"shadow-{case.case_id}",
                data_class=case.data_class,
                secret=secret,
                capture_content=policy.content_capture_enabled,
            )
            response = invocation["response"]
            metadata = dict(response["metadata"])
            citation_integrity = bool(
                dict(metadata.get("citation_integrity", {})).get(
                    "citations_subset_of_evidence",
                    False,
                )
            )
            status_ok = str(response["status"]) in case.expected_statuses
            evidence_ok = (
                int(response["evidence_count"]) > 0
                if case.require_evidence
                else True
            )
            citation_ok = (
                citation_integrity
                if case.require_citation_integrity
                else True
            )
            mutation_count = int(
                invocation["input_mutation"]["records_mutated"]
            ) + int(invocation["input_mutation"]["chunks_mutated"])
            hard_pass = (
                status_ok
                and evidence_ok
                and citation_ok
                and trace_bundle["envelope_report"]["passed"]
                and trace_bundle["privacy_report"]["passed"]
                and invocation["external_effect_count"] == 0
                and invocation["network_egress_count"] == 0
                and invocation["provider_export_count"] == 0
                and (
                    not policy.mutation_prohibited
                    or mutation_count == 0
                )
            )
            semantic_response = {
                key: value
                for key, value in response.items()
                if key != "metadata"
            }
            semantic_response["metadata"] = {
                key: value
                for key, value in metadata.items()
                if key not in {"latency_ms", "timestamp"}
            }
            results.append(
                {
                    "trial_id": trial_id,
                    "case_id": case.case_id,
                    "variant": variant_name,
                    "risk": case.risk,
                    "slices": case.slices,
                    "passed": hard_pass,
                    "status": str(response["status"]),
                    "response_sha256": canonical_sha256(
                        semantic_response
                    ),
                    "trace_signature_sha256": canonical_sha256(
                        _semantic_trace_signature(
                            trace_bundle["sanitized_trace"]
                        )
                    ),
                    "citation_integrity": citation_integrity,
                    "trace_valid": trace_bundle[
                        "envelope_report"
                    ]["passed"],
                    "privacy_valid": trace_bundle[
                        "privacy_report"
                    ]["passed"],
                    "evidence_count": int(response["evidence_count"]),
                    "latency_ms": float(invocation["latency_ms"]),
                    "external_effect_count": int(
                        invocation["external_effect_count"]
                    ),
                    "network_egress_count": int(
                        invocation["network_egress_count"]
                    ),
                    "provider_export_count": int(
                        invocation["provider_export_count"]
                    ),
                    "input_mutation_count": mutation_count,
                    "sanitized_trace": trace_bundle[
                        "sanitized_trace"
                    ],
                }
            )

    return results
