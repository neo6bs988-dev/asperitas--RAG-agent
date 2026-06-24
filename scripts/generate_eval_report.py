from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from asperitas_agent.eval_report import (  # noqa: E402
    EvalReportError,
    build_eval_report,
    load_metric_results,
    load_report_payload,
    summarize_eval_report,
)
from asperitas_agent.eval_artifacts import (  # noqa: E402
    EvalArtifactError,
    build_eval_report_artifact,
    write_eval_report_artifact,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a local eval report from explicit metric results without scoring, retrieval, or LLM judging."
    )
    parser.add_argument("--input", required=True, help="Path to metric_results.json")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--output", help="Optional explicit output path for an eval report artifact JSON file")
    parser.add_argument("--overwrite", action="store_true", help="Allow --output to overwrite an existing file")
    parser.add_argument("--create-dirs", action="store_true", help="Create missing parent directories for --output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = load_report_payload(args.input)
        metadata = dict(payload.get("metadata", {}))
        metadata["report_id"] = payload.get("report_id") or metadata.get("report_id") or "local_eval_report"
        results = load_metric_results(args.input)
        report = build_eval_report(results, metadata=metadata)
        summary = summarize_eval_report(report)
        if args.output:
            artifact = build_eval_report_artifact(report, metadata=metadata)
            artifact_path = write_eval_report_artifact(
                artifact,
                args.output,
                overwrite=args.overwrite,
                create_dirs=args.create_dirs,
            )
            summary["metadata"]["artifact_path"] = str(artifact_path)
    except (EvalReportError, EvalArtifactError) as exc:
        summary = {
            "ok": False,
            "report_id": None,
            "summary": "Local explicit metric-result report could not be generated.",
            "results": [],
            "passed_count": 0,
            "failed_count": 0,
            "report_only_count": 0,
            "strict_count": 0,
            "warnings": [],
            "errors": [str(exc)],
            "metadata": {
                "automatic_scoring_performed": False,
                "retrieval_executed": False,
                "llm_judge_executed": False,
            },
        }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        print(f"ok: {summary['ok']}")
        print(f"report_id: {summary['report_id']}")
        print(f"strict_count: {summary['strict_count']}")
        print(f"report_only_count: {summary['report_only_count']}")
        print(f"errors: {len(summary['errors'])}")
        print(f"warnings: {len(summary['warnings'])}")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
