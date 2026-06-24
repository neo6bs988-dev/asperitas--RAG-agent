from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from asperitas_agent.eval_metrics import EvalMetricReport
from asperitas_agent.eval_report import summarize_eval_report


SCHEMA_VERSION = "MVP-017C"


class EvalArtifactError(ValueError):
    """Raised when an eval report artifact cannot be written or loaded safely."""


@dataclass(frozen=True)
class EvalReportArtifact:
    artifact_id: str
    schema_version: str
    created_at_utc: str
    report_id: str
    ok: bool
    summary: dict[str, Any]
    report: dict[str, Any]
    metadata: dict[str, Any]
    provenance: dict[str, Any]
    warnings: list[str]
    errors: list[str]

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for field_name in ("artifact_id", "schema_version", "created_at_utc", "report_id"):
            if not str(getattr(self, field_name)).strip():
                errors.append(f"{field_name} is required")
        if self.schema_version != SCHEMA_VERSION:
            errors.append(f"unsupported schema_version: {self.schema_version}")
        for field_name in ("summary", "report", "metadata", "provenance"):
            if not isinstance(getattr(self, field_name), dict):
                errors.append(f"{field_name} must be an object")
        for field_name in ("warnings", "errors"):
            if not isinstance(getattr(self, field_name), list):
                errors.append(f"{field_name} must be a list")
        if self.summary.get("report_id") != self.report_id:
            errors.append("summary report_id must match artifact report_id")
        if self.report.get("report_id") != self.report_id:
            errors.append("report report_id must match artifact report_id")
        try:
            json.dumps(self.to_dict(), sort_keys=True)
        except (TypeError, ValueError) as exc:
            errors.append(f"artifact must be JSON-safe: {exc}")
        return tuple(errors)

    def require_valid(self) -> None:
        errors = self.validate()
        if errors:
            raise EvalArtifactError("; ".join(errors))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_eval_report_artifact(report: EvalMetricReport, metadata: dict[str, Any] | None = None) -> EvalReportArtifact:
    summary = summarize_eval_report(report)
    artifact = EvalReportArtifact(
        artifact_id=f"{report.report_id}:{SCHEMA_VERSION}",
        schema_version=SCHEMA_VERSION,
        created_at_utc=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        report_id=report.report_id,
        ok=bool(summary["ok"]),
        summary=summary,
        report=report.to_dict(),
        metadata=dict(metadata or {}),
        provenance={
            "generator": "asperitas_agent.eval_artifacts",
            "automatic_scoring_performed": False,
            "retrieval_executed": False,
            "llm_judge_executed": False,
        },
        warnings=list(summary["warnings"]),
        errors=list(summary["errors"]),
    )
    artifact.require_valid()
    return artifact


def write_eval_report_artifact(
    artifact: EvalReportArtifact,
    path: str | Path,
    overwrite: bool = False,
    create_dirs: bool = False,
) -> Path:
    if path is None or not str(path).strip():
        raise EvalArtifactError("explicit output path is required")
    artifact.require_valid()
    output_path = Path(path)
    if output_path.exists() and not overwrite:
        raise EvalArtifactError(f"output path already exists: {output_path}")
    if not output_path.parent.exists():
        if not create_dirs:
            raise EvalArtifactError(f"parent directory does not exist: {output_path.parent}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def load_eval_report_artifact(path: str | Path) -> EvalReportArtifact:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise EvalArtifactError(f"could not read artifact: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise EvalArtifactError(f"malformed artifact JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise EvalArtifactError("artifact JSON must be an object")
    required_fields = (
        "artifact_id",
        "schema_version",
        "created_at_utc",
        "report_id",
        "ok",
        "summary",
        "report",
        "metadata",
        "provenance",
        "warnings",
        "errors",
    )
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise EvalArtifactError(f"artifact missing fields: {', '.join(missing)}")
    artifact = EvalReportArtifact(
        artifact_id=str(payload["artifact_id"]),
        schema_version=str(payload["schema_version"]),
        created_at_utc=str(payload["created_at_utc"]),
        report_id=str(payload["report_id"]),
        ok=bool(payload["ok"]),
        summary=payload["summary"],
        report=payload["report"],
        metadata=payload["metadata"],
        provenance=payload["provenance"],
        warnings=payload["warnings"],
        errors=payload["errors"],
    )
    artifact.require_valid()
    return artifact
