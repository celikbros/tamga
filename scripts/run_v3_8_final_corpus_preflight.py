from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v3_8_final_corpus_text import (  # noqa: E402
    format_report as format_materialization_report,
)
from scripts.materialize_v3_8_final_corpus_text import materialize_from_manifest  # noqa: E402
from scripts.validate_v3_8_final_corpus_manifest import (  # noqa: E402
    format_report as format_manifest_report,
)
from scripts.validate_v3_8_final_corpus_manifest import validate_manifest  # noqa: E402


def write_report(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def status_for(failures: list[str]) -> str:
    return "PASS" if not failures else "FAIL"


def format_summary(
    *,
    manifest_path: Path,
    base_dir: Path,
    output_text: Path,
    gate_results: dict[str, tuple[list[str], list[str], dict[str, Any] | None, Path]],
) -> str:
    overall_status = (
        "PASS"
        if all(not failures for failures, _warnings, _facts, _path in gate_results.values())
        else "FAIL"
    )
    lines = [
        "# v3.8 Final Corpus Preflight Summary",
        "",
        f"Manifest: `{manifest_path}`",
        f"Base dir: `{base_dir}`",
        f"Canonical text output: `{output_text}`",
        f"Status: `{overall_status}`",
        "",
        "This preflight validates the final corpus handoff and materializes the",
        "canonical plain-text corpus view used by SP retrain and production",
        "tokenization.",
        "",
        "## Gate Results",
        "",
        "| Gate | Status | Failures | Warnings | Report |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for gate_name, (failures, warnings, _facts, report_path) in gate_results.items():
        lines.append(
            f"| `{gate_name}` | `{status_for(failures)}` | {len(failures)} | "
            f"{len(warnings)} | `{report_path}` |"
        )

    lines.extend(["", "## Failures", ""])
    any_failures = False
    for gate_name, (failures, _warnings, _facts, _report_path) in gate_results.items():
        for failure in failures:
            any_failures = True
            lines.append(f"- `{gate_name}`: {failure}")
    if not any_failures:
        lines.append("None.")

    lines.extend(["", "## Warnings", ""])
    any_warnings = False
    for gate_name, (_failures, warnings, _facts, _report_path) in gate_results.items():
        for warning in warnings:
            any_warnings = True
            lines.append(f"- `{gate_name}`: {warning}")
    if not any_warnings:
        lines.append("None.")

    lines.extend(
        [
            "",
            "## Next",
            "",
            "Use the canonical text output as the input to final SP retrain, route",
            "density/fertility reports, and `scripts/tokenize_corpus.py`.",
            "",
        ]
    )
    return "\n".join(lines)


def run_preflight(
    *,
    manifest_path: Path,
    base_dir: Path,
    output_text: Path,
    report_dir: Path,
) -> tuple[dict[str, tuple[list[str], list[str], dict[str, Any] | None, Path]], Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, tuple[list[str], list[str], dict[str, Any] | None, Path]] = {}

    manifest_failures, manifest_warnings, manifest_facts = validate_manifest(
        manifest_path=manifest_path,
        base_dir=base_dir,
    )
    manifest_report_path = report_dir / "manifest_validation.md"
    write_report(
        manifest_report_path,
        format_manifest_report(
            manifest_path=manifest_path,
            base_dir=base_dir,
            failures=manifest_failures,
            warnings=manifest_warnings,
            facts=manifest_facts,
        ),
    )
    results["manifest"] = (
        manifest_failures,
        manifest_warnings,
        manifest_facts,
        manifest_report_path,
    )

    materialization_report_path = report_dir / "text_materialization.md"
    if manifest_failures:
        materialization_failures = ["skipped because final corpus manifest validation failed"]
        materialization_warnings: list[str] = []
        materialization_stats = None
        write_report(
            materialization_report_path,
            format_materialization_report(
                manifest_path=manifest_path,
                base_dir=base_dir,
                stats=None,
                failures=materialization_failures,
                manifest_warnings=materialization_warnings,
            ),
        )
    else:
        materialization_stats, materialization_failures, materialization_warnings = (
            materialize_from_manifest(
                manifest_path=manifest_path,
                base_dir=base_dir,
                output_path=output_text,
            )
        )
        write_report(
            materialization_report_path,
            format_materialization_report(
                manifest_path=manifest_path,
                base_dir=base_dir,
                stats=materialization_stats,
                failures=materialization_failures,
                manifest_warnings=materialization_warnings,
            ),
        )

    materialization_facts: dict[str, Any] | None = None
    if materialization_stats is not None:
        materialization_facts = {
            "corpus_format": materialization_stats.corpus_format,
            "scanned_lines": materialization_stats.scanned_lines,
            "written_lines": materialization_stats.written_lines,
            "output_bytes": materialization_stats.output_bytes,
        }
    results["materialization"] = (
        materialization_failures,
        materialization_warnings,
        materialization_facts,
        materialization_report_path,
    )

    summary_path = report_dir / "preflight_summary.md"
    write_report(
        summary_path,
        format_summary(
            manifest_path=manifest_path,
            base_dir=base_dir,
            output_text=output_text,
            gate_results=results,
        ),
    )
    return results, summary_path


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Run v3.8 final corpus manifest validation and text materialization."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--base-dir", default=".")
    parser.add_argument("--out-text", required=True)
    parser.add_argument(
        "--report-dir",
        default="artifacts/v3_8_final_corpus_preflight",
    )
    args = parser.parse_args(argv)

    results, summary_path = run_preflight(
        manifest_path=Path(args.manifest),
        base_dir=Path(args.base_dir),
        output_text=Path(args.out_text),
        report_dir=Path(args.report_dir),
    )
    summary = summary_path.read_text(encoding="utf-8")
    print(summary)
    print(f"wrote_summary: {summary_path}")
    return 0 if all(not failures for failures, _warnings, _facts, _path in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
