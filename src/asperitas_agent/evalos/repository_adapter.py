from __future__ import annotations

from typing import Any

from .shadow_analysis import analyze_shadow_results
from .shadow_release import decide_shadow_release
from .shadow_runner import run_shadow_case


def build_repository_synthetic_inputs() -> tuple[
    list[Any],
    list[Any],
]:
    from asperitas_agent.schemas import Chunk, SourceRecord

    records = [
        SourceRecord(
            source_id="EVALOS-V14-P1",
            title="EvalOS v1.4 Synthetic Source One",
            original_filename="evalos-v14-one.md",
            path=(
                "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/"
                "evalos-v14-one.md"
            ),
            source_priority="P1",
            source_type="internal",
            disclosure_level="internal",
            license_status="internal_use",
            verification_status="verified_internal",
            date="2026-07-21",
            author_or_owner="Asperitas",
            use_case="no_effect_shadow",
            checksum="a" * 64,
            parse_status="parsed",
        ),
        SourceRecord(
            source_id="EVALOS-V14-P2",
            title="EvalOS v1.4 Synthetic Source Two",
            original_filename="evalos-v14-two.md",
            path=(
                "01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/"
                "evalos-v14-two.md"
            ),
            source_priority="P1",
            source_type="internal",
            disclosure_level="internal",
            license_status="internal_use",
            verification_status="verified_internal",
            date="2026-07-21",
            author_or_owner="Asperitas",
            use_case="no_effect_shadow",
            checksum="b" * 64,
            parse_status="parsed",
        ),
    ]
    chunks = [
        Chunk(
            chunk_id="EVALOS-V14-P1::chunk-0001",
            source_id=records[0].source_id,
            title=records[0].title,
            text=(
                "Asperitas uses source-grounded evidence and "
                "deterministic evaluation controls."
            ),
            page_start=None,
            page_end=None,
            char_start=0,
            char_end=77,
            source_priority="P1",
            source_type="internal",
            disclosure_level="internal",
            evidence_label="Document-Supported Fact",
            verification_status="verified_internal",
            risk_tags=[],
            checksum="c" * 64,
            section="Overview",
            section_heading="Overview",
            section_path=["Overview"],
            section_level=1,
        ),
        Chunk(
            chunk_id="EVALOS-V14-P2::chunk-0002",
            source_id=records[1].source_id,
            title=records[1].title,
            text=(
                "No-effect shadow evaluation must not mutate "
                "runtime inputs or create external effects."
            ),
            page_start=None,
            page_end=None,
            char_start=0,
            char_end=85,
            source_priority="P1",
            source_type="internal",
            disclosure_level="internal",
            evidence_label="Document-Supported Fact",
            verification_status="verified_internal",
            risk_tags=[],
            checksum="d" * 64,
            section="Controls",
            section_heading="Controls",
            section_path=["Controls"],
            section_level=1,
        ),
    ]
    return records, chunks


def run_repository_no_effect_shadow(
    *,
    cases: list[dict[str, Any]],
    policy: dict[str, Any],
    secret: bytes,
    exact_repository_head_verified: bool = False,
) -> dict[str, Any]:
    from asperitas_agent.agent_runner import ask_agent

    def records_factory() -> list[Any]:
        records, _ = build_repository_synthetic_inputs()
        return records

    def chunks_factory() -> list[Any]:
        _, chunks = build_repository_synthetic_inputs()
        return chunks

    results = []
    for case in cases:
        results.extend(
            run_shadow_case(
                case,
                policy,
                variants={
                    "incumbent": ask_agent,
                    "candidate": ask_agent,
                },
                records_factory=records_factory,
                chunks_factory=chunks_factory,
                secret=secret,
            )
        )

    analysis = analyze_shadow_results(results, policy)
    decision = decide_shadow_release(
        analysis=analysis,
        policy=policy,
        actual_repository_agent_executed=True,
        exact_repository_head_verified=exact_repository_head_verified,
        approved_shadow_storage_configured=False,
    )
    return {
        "schema_version": "asperitas-evalos-v1.4-repository-run",
        "decision": decision,
        "analysis": analysis,
        "results": results,
        "truth_boundary": (
            "The repository ask_agent function was executed only against "
            "synthetic in-memory records and chunks. No external effect, "
            "provider export, network egress, private holdout, or production "
            "traffic was permitted."
        ),
    }
