from __future__ import annotations
import hashlib
from typing import Any

def _id(prefix: str, seed: str, length: int = 16) -> str:
    return prefix + hashlib.sha256(seed.encode()).hexdigest()[:length]

def adapt_agent_response(
    response: dict[str, Any], *, case_id: str, trial_id: str,
    conversation_id: str, provider_name: str = "asperitas.local",
    agent_version: str = "MVP-008", harness_version: str = "evalos-v1.1",
    prompt_version: str = "deterministic-grounded-v1",
    data_class: str = "INTERNAL",
) -> dict[str, Any]:
    metadata = dict(response["metadata"])
    retriever = dict(metadata.get("retriever", {}))
    evidence = list(response.get("evidence", []))
    document_ids = [str(x.get("chunk_id")) for x in evidence if x.get("chunk_id")]
    source_ids = sorted({str(x.get("source_id")) for x in evidence if x.get("source_id")})
    trace_id = _id("trace_", trial_id, 32)
    span_ids = {
        name: _id("span_", f"{trial_id}:{name}")
        for name in ("workflow", "agent", "retrieval", "generation", "guardrail", "verification", "outcome")
    }
    def span(name: str, parent: str | None, stype: str, start: int, end: int, attrs: dict[str, Any]):
        return {
            "trace_id": trace_id, "span_id": span_ids[name],
            "parent_span_id": None if parent is None else span_ids[parent],
            "span_type": stype, "started_at_ms": start, "ended_at_ms": end,
            "attributes": attrs,
        }
    spans = [
        span("workflow", None, "invoke_workflow", 1000, 1100, {
            "gen_ai.operation.name": "invoke_workflow",
            "gen_ai.workflow.name": "asperitas_grounded_answer",
        }),
        span("agent", "workflow", "invoke_agent", 1001, 1099, {
            "gen_ai.operation.name": "invoke_agent",
            "gen_ai.agent.id": "asperitas-rag-agent",
            "gen_ai.agent.name": "Asperitas RAG Agent",
            "gen_ai.agent.version": agent_version,
        }),
        span("retrieval", "agent", "retrieval", 1002, 1030, {
            "gen_ai.operation.name": "retrieval",
            "gen_ai.data_source.id": ",".join(source_ids) or "none",
            "gen_ai.retrieval.query.text": response["query"],
            "asperitas.retrieval.document_ids": document_ids,
            "asperitas.retriever.name": retriever.get("retriever_name", ""),
            "asperitas.retriever.version": retriever.get("retriever_version", ""),
        }),
        span("generation", "agent", "generate_content", 1031, 1060, {
            "gen_ai.operation.name": "generate_content",
            "gen_ai.output.type": "text",
            "gen_ai.output.messages": [{"role": "assistant", "content": response["answer"]}],
            "asperitas.answer.status": response["status"],
            "asperitas.citations.used": list(response["citations_used"]),
        }),
        span("guardrail", "agent", "guardrail", 1061, 1070, {
            "asperitas.guardrail.decision": dict(response["guardrail"]).get("decision", ""),
            "asperitas.guardrail.should_abstain": dict(response["guardrail"]).get("should_abstain", False),
        }),
        span("verification", "agent", "verification", 1071, 1085, {
            "gen_ai.evaluation.name": "citation_integrity",
            "gen_ai.evaluation.score.label": "pass" if dict(metadata.get("citation_integrity", {})).get("citations_subset_of_evidence") else "fail",
            "gen_ai.evaluation.score.value": 1.0 if dict(metadata.get("citation_integrity", {})).get("citations_subset_of_evidence") else 0.0,
        }),
        span("outcome", "workflow", "environment_outcome", 1086, 1098, {
            "asperitas.outcome.status": response["status"],
            "asperitas.outcome.external_effect_count": 0,
            "asperitas.outcome.evidence_count": int(response["evidence_count"]),
        }),
    ]
    return {
        "schema_version": "asperitas.trace.v1.1",
        "trace_id": trace_id,
        "attributes": {
            "gen_ai.agent.id": "asperitas-rag-agent",
            "gen_ai.agent.name": "Asperitas RAG Agent",
            "gen_ai.agent.version": agent_version,
            "gen_ai.conversation.id": conversation_id,
            "gen_ai.provider.name": provider_name,
            "gen_ai.workflow.name": "asperitas_grounded_answer",
            "asperitas.harness.version": harness_version,
            "asperitas.prompt.version": prompt_version,
            "asperitas.eval.case_id": case_id,
            "asperitas.eval.trial_id": trial_id,
            "asperitas.data.class": data_class,
            "asperitas.effect.ceiling": "READ",
        },
        "spans": spans,
    }
