from __future__ import annotations
from collections import Counter
from typing import Any

TRACE_SCHEMA_VERSION = "asperitas.trace.v1.1"
SPAN_TYPES = {
    "invoke_workflow", "invoke_agent", "retrieval", "generate_content",
    "execute_tool", "guardrail", "verification", "state_transition",
    "environment_outcome",
}
ROOT_ATTRS = {
    "gen_ai.agent.id", "gen_ai.agent.name", "gen_ai.agent.version",
    "gen_ai.conversation.id", "gen_ai.provider.name", "gen_ai.workflow.name",
    "asperitas.harness.version", "asperitas.prompt.version",
    "asperitas.eval.case_id", "asperitas.eval.trial_id",
    "asperitas.data.class", "asperitas.effect.ceiling",
}

def validate_trace_envelope(trace: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if trace.get("schema_version") != TRACE_SCHEMA_VERSION:
        errors.append("INVALID_TRACE_SCHEMA_VERSION")
    trace_id = str(trace.get("trace_id", ""))
    if not trace_id.startswith("trace_") or len(trace_id) < 16:
        errors.append("INVALID_TRACE_ID")
    attrs = dict(trace.get("attributes", {}))
    missing = sorted(ROOT_ATTRS - set(attrs))
    if missing:
        errors.append("MISSING_ROOT_ATTRIBUTES:" + ",".join(missing))
    spans = list(trace.get("spans", []))
    if not spans:
        return {"passed": False, "errors": errors + ["NO_SPANS"], "warnings": [], "span_count": 0}
    ids = [str(s.get("span_id", "")) for s in spans]
    if len(ids) != len(set(ids)):
        errors.append("DUPLICATE_SPAN_ID")
    index = {str(s["span_id"]): s for s in spans}
    roots: list[str] = []
    counts: Counter[str] = Counter()
    for span in spans:
        sid = str(span.get("span_id", ""))
        stype = str(span.get("span_type", ""))
        counts[stype] += 1
        if stype not in SPAN_TYPES:
            errors.append(f"INVALID_SPAN_TYPE:{sid}:{stype}")
        start, end = int(span.get("started_at_ms", -1)), int(span.get("ended_at_ms", -1))
        if start < 0 or end < start:
            errors.append(f"INVALID_SPAN_TIME:{sid}")
        parent = span.get("parent_span_id")
        if parent is None:
            roots.append(sid)
        elif str(parent) not in index:
            errors.append(f"ORPHAN_PARENT:{sid}")
        if str(span.get("trace_id")) != trace_id:
            errors.append(f"TRACE_ID_MISMATCH:{sid}")
        sattrs = dict(span.get("attributes", {}))
        if stype == "execute_tool":
            for key in (
                "gen_ai.tool.name", "gen_ai.tool.type", "gen_ai.tool.call.id",
                "asperitas.effect.type", "asperitas.authorization.decision",
                "asperitas.idempotency.key",
            ):
                if key not in sattrs:
                    errors.append(f"MISSING_TOOL_ATTRIBUTE:{sid}:{key}")
        if stype == "retrieval":
            if "gen_ai.data_source.id" not in sattrs:
                errors.append(f"MISSING_RETRIEVAL_SOURCE:{sid}")
            if "asperitas.retrieval.document_ids" not in sattrs:
                errors.append(f"MISSING_RETRIEVAL_DOCUMENT_IDS:{sid}")
        if stype == "environment_outcome":
            if "asperitas.outcome.status" not in sattrs:
                errors.append(f"MISSING_OUTCOME_STATUS:{sid}")
            if "asperitas.outcome.external_effect_count" not in sattrs:
                errors.append(f"MISSING_OUTCOME_EFFECT_COUNT:{sid}")
    if len(roots) != 1:
        errors.append(f"ROOT_SPAN_COUNT:{len(roots)}")
    elif index[roots[0]].get("span_type") != "invoke_workflow":
        errors.append("ROOT_MUST_BE_WORKFLOW")
    required = {
        "invoke_workflow", "invoke_agent", "retrieval", "generate_content",
        "guardrail", "verification", "environment_outcome",
    }
    missing_types = sorted(required - set(counts))
    if missing_types:
        errors.append("MISSING_REQUIRED_SPANS:" + ",".join(missing_types))
    if counts["execute_tool"] == 0:
        warnings.append("NO_TOOL_SPAN")
    return {
        "passed": not errors,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "span_count": len(spans),
        "operation_counts": dict(sorted(counts.items())),
        "root_span_id": roots[0] if len(roots) == 1 else None,
    }
