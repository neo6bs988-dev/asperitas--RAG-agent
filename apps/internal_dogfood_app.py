from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from asperitas_agent.chat_workflow import chat_workflow_result_to_dict, run_chat_workflow, summarize_chat_workflow
from asperitas_agent.failure_log import (
    FAILURE_CATEGORIES,
    FAILURE_SEVERITIES,
    FAILURE_STATUSES,
    build_failure_record,
    failure_record_to_dict,
    write_failure_jsonl,
)


PAGE_TITLE = "Asperitas V1.1 Internal Dogfood"
DEFAULT_FAILURE_LOG_PATH = "09_LOGS/failure_logs/v1_1b_dogfood_failures.jsonl"
INTERNAL_ONLY_BANNER = (
    "Internal/local dry-run only. No real answer provider is wired. "
    "Not public SaaS. Not production deployment."
)
REDACTION_WARNING = (
    "Before saving, confirm free-text fields do not include secrets, raw private files, "
    "environment variables, credentials, or unredacted sensitive data."
)


def _stable_id(value: str, fallback: str) -> str:
    normalized = "_".join(value.strip().lower().split())
    return normalized or fallback


def build_dogfood_payload(
    question: str,
    session_id: str,
    expected_behavior: str = "",
    notes: str = "",
) -> dict[str, Any]:
    clean_question = str(question).strip()
    clean_session_id = _stable_id(str(session_id), "local_internal_dogfood")
    return {
        "request_id": f"{clean_session_id}_dogfood_request",
        "trace_id": f"{clean_session_id}_dogfood_trace",
        "question": clean_question,
        "required_skills": (),
        "available_skills": (),
        "source_status": {"mode": "internal_dogfood", "dry_run_only": True, "no_new_sources": True},
        "eval_gate": {"mode": "internal_dogfood", "dry_run_only": True},
        "metadata": {
            "session_id": clean_session_id,
            "expected_behavior": str(expected_behavior).strip(),
            "notes": str(notes).strip(),
            "ui": "v1_1b_streamlit_internal_dogfood",
            "answer_provider_wired": False,
        },
    }


def run_internal_dogfood_once(payload: dict[str, Any]) -> dict[str, Any]:
    result = run_chat_workflow(payload, answer_provider=None)
    result_dict = chat_workflow_result_to_dict(result)
    result_dict["dogfood_summary"] = summarize_chat_workflow(result)
    return result_dict


def actual_behavior_from_dogfood_result(result: dict[str, Any]) -> str:
    warnings = "; ".join(str(item) for item in result.get("warnings", ()))
    errors = "; ".join(str(item) for item in result.get("errors", ()))
    parts = [
        f"status={result.get('status')}",
        f"ok={result.get('ok')}",
        f"dry_run={result.get('dry_run')}",
        f"blocked={result.get('blocked')}",
    ]
    if warnings:
        parts.append(f"warnings={warnings}")
    if errors:
        parts.append(f"errors={errors}")
    return "; ".join(parts)


def build_failure_record_from_dogfood_result(
    payload: dict[str, Any],
    dogfood_result: dict[str, Any],
    category: str,
    severity: str,
    status: str,
    actual_behavior: str | None = None,
) -> dict[str, Any]:
    metadata = dict(payload.get("metadata") or {})
    expected_behavior = str(metadata.get("expected_behavior") or "Expected internal dogfood dry-run behavior to match operator expectation.")
    record = build_failure_record(
        query=str(payload.get("question", "")),
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior or actual_behavior_from_dogfood_result(dogfood_result),
        category=category,
        severity=severity,
        status=status,
        session_id=str(metadata.get("session_id") or "local_internal_dogfood"),
        source_context={
            "source_status": dict(payload.get("source_status") or {}),
            "no_new_sources": True,
        },
        security_result=dict(dogfood_result.get("security_report") or {}),
        workflow_result={
            "workflow_run": dict(dogfood_result.get("workflow_run") or {}),
            "workflow_inspection": dict(dogfood_result.get("workflow_inspection") or {}),
            "workflow_acceptance": dict(dogfood_result.get("workflow_acceptance") or {}),
        },
        dry_run_result=dict(dogfood_result),
        reproduction_steps=(
            "Run streamlit run apps/internal_dogfood_app.py --server.address 127.0.0.1 --server.port 8501",
            "Submit the question in internal dry-run mode.",
            "Review status, warnings, security, workflow, and audit summaries.",
        ),
        redaction_notes="User acknowledged the UI redaction warning before explicit save.",
        metadata={"notes": str(metadata.get("notes") or ""), "ui": "v1_1b_streamlit_internal_dogfood"},
    )
    return failure_record_to_dict(record)


def save_failure_record_explicit(
    record: dict[str, Any],
    output_path: str | Path,
    redaction_acknowledged: bool,
    append: bool = True,
    create_dirs: bool = True,
) -> Path:
    if not redaction_acknowledged:
        raise PermissionError("redaction acknowledgement is required before saving a failure log")
    if not output_path:
        raise ValueError("output_path is required for explicit save")
    failure_record = build_failure_record(**_record_kwargs(record))
    return write_failure_jsonl(failure_record, output_path, append=append, create_dirs=create_dirs)


def _record_kwargs(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": str(record.get("schema_version", "")),
        "failure_id": str(record.get("failure_id", "")),
        "created_at_utc": str(record.get("created_at_utc", "")),
        "session_id": str(record.get("session_id", "")),
        "query": str(record.get("query", "")),
        "expected_behavior": str(record.get("expected_behavior", "")),
        "actual_behavior": str(record.get("actual_behavior", "")),
        "category": str(record.get("category", "")),
        "severity": str(record.get("severity", "")),
        "status": str(record.get("status", "")),
        "source_context": dict(record.get("source_context") or {}),
        "security_result": dict(record.get("security_result") or {}),
        "workflow_result": dict(record.get("workflow_result") or {}),
        "dry_run_result": dict(record.get("dry_run_result") or {}),
        "reproduction_steps": tuple(record.get("reproduction_steps") or ()),
        "proposed_fix": str(record.get("proposed_fix", "")),
        "redaction_notes": str(record.get("redaction_notes", "")),
        "metadata": dict(record.get("metadata") or {}),
    }


def _render_streamlit_app(st: Any) -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon="A", layout="wide")
    st.title(PAGE_TITLE)
    st.error(INTERNAL_ONLY_BANNER)

    with st.form("dogfood_run_form"):
        question = st.text_area("question")
        session_id = st.text_input("session_id", value="local_internal_dogfood")
        expected_behavior = st.text_area("optional expected behavior")
        notes = st.text_area("optional notes")
        run_clicked = st.form_submit_button("Run internal dry-run")

    if run_clicked:
        payload = build_dogfood_payload(question, session_id, expected_behavior, notes)
        result = run_internal_dogfood_once(payload)
        st.session_state["dogfood_payload"] = payload
        st.session_state["dogfood_result"] = result

    result = st.session_state.get("dogfood_result")
    payload = st.session_state.get("dogfood_payload")
    if result and payload:
        st.subheader("Dry-run status")
        st.json(result.get("dogfood_summary") or {})
        st.subheader("Warnings")
        st.write(result.get("warnings") or [])
        st.subheader("Security / workflow / audit")
        st.json(
            {
                "security_report": result.get("security_report"),
                "workflow_acceptance": result.get("workflow_acceptance"),
                "audit_event_count": len(result.get("audit_events") or []),
            }
        )

        st.subheader("Failure log")
        st.warning(REDACTION_WARNING)
        category = st.selectbox("category", FAILURE_CATEGORIES, index=FAILURE_CATEGORIES.index("dry_run_provider_needed"))
        severity = st.selectbox("severity", FAILURE_SEVERITIES, index=FAILURE_SEVERITIES.index("medium"))
        failure_status = st.selectbox("status", FAILURE_STATUSES)
        actual_behavior = st.text_area("actual behavior", value=actual_behavior_from_dogfood_result(result))
        output_path = st.text_input("output path", value=DEFAULT_FAILURE_LOG_PATH)
        redaction_acknowledged = st.checkbox("I reviewed and redacted free-text fields before saving.")
        if st.button("Save failure log JSONL"):
            record = build_failure_record_from_dogfood_result(payload, result, category, severity, failure_status, actual_behavior)
            saved_path = save_failure_record_explicit(record, output_path, redaction_acknowledged)
            st.success(f"Saved failure log: {saved_path}")
            st.code(json.dumps(record, ensure_ascii=False, indent=2), language="json")


def main() -> None:
    try:
        import streamlit as st  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        print("Streamlit is not installed. Install optional local UI dependencies to run the app.")
        return
    _render_streamlit_app(st)


if __name__ == "__main__":
    main()
