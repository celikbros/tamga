from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.simulate_v3_2_binary_dataloader import (
    format_report as format_dataloader_report,
)
from scripts.simulate_v3_2_binary_dataloader import simulate
from scripts.validate_v3_2_smoke_fixture import (
    format_report as format_fixture_report,
)
from scripts.validate_v3_2_smoke_fixture import validate_fixture
from scripts.validate_v3_8_tokenized_package import (
    format_report as format_checksum_report,
)
from scripts.validate_v3_8_tokenized_package import validate_package


@contextmanager
def pushd(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def write_report(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def status_for(failures: list[str]) -> str:
    return "PASS" if not failures else "FAIL"


def format_summary(
    *,
    manifest_path: Path,
    config_path: Path,
    base_dir: Path,
    batch_size: int,
    seq_len: int,
    dataloader_max_batches: int | None,
    gate_results: dict[str, tuple[list[str], list[str], dict[str, Any], Path]],
) -> str:
    overall_status = (
        "PASS"
        if all(not failures for failures, _warnings, _facts, _path in gate_results.values())
        else "FAIL"
    )
    lines = [
        "# v3.8 Tokenized Package Gate Summary",
        "",
        f"Manifest: `{manifest_path}`",
        f"Config: `{config_path}`",
        f"Base dir: `{base_dir}`",
        f"Batch shape: `batch_size={batch_size}`, `seq_len={seq_len}`",
        "Dataloader batch limit: "
        f"`{dataloader_max_batches if dataloader_max_batches is not None else 'all'}`",
        f"Status: `{overall_status}`",
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
    lines.append("")
    return "\n".join(lines)


def run_gates(
    *,
    manifest_path: Path,
    config_path: Path,
    base_dir: Path,
    report_dir: Path,
    batch_size: int,
    seq_len: int,
    dataloader_max_batches: int | None = 4096,
) -> tuple[dict[str, tuple[list[str], list[str], dict[str, Any], Path]], Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, tuple[list[str], list[str], dict[str, Any], Path]] = {}

    checksum_failures, checksum_warnings, checksum_facts = validate_package(
        manifest_path=manifest_path,
        base_dir=base_dir,
    )
    checksum_report_path = report_dir / "checksum_validation.md"
    write_report(
        checksum_report_path,
        format_checksum_report(
            manifest_path=manifest_path,
            base_dir=base_dir,
            failures=checksum_failures,
            warnings=checksum_warnings,
            facts=checksum_facts,
        ),
    )
    results["checksum"] = (
        checksum_failures,
        checksum_warnings,
        checksum_facts,
        checksum_report_path,
    )

    with pushd(base_dir):
        fixture_failures, fixture_warnings, fixture_facts = validate_fixture(
            manifest_path=manifest_path,
            config_path=config_path,
        )
    fixture_report_path = report_dir / "fixture_validation.md"
    write_report(
        fixture_report_path,
        format_fixture_report(
            manifest_path=manifest_path,
            config_path=config_path,
            failures=fixture_failures,
            warnings=fixture_warnings,
            facts=fixture_facts,
        ),
    )
    results["fixture"] = (
        fixture_failures,
        fixture_warnings,
        fixture_facts,
        fixture_report_path,
    )

    with pushd(base_dir):
        dataloader_facts, dataloader_failures, dataloader_warnings = simulate(
            manifest_path=manifest_path,
            config_path=config_path,
            batch_size=batch_size,
            seq_len=seq_len,
            max_batches=dataloader_max_batches,
        )
    dataloader_report_path = report_dir / "dataloader_simulation.md"
    write_report(
        dataloader_report_path,
        format_dataloader_report(
            manifest_path=manifest_path,
            config_path=config_path,
            batch_size=batch_size,
            seq_len=seq_len,
            max_batches=dataloader_max_batches,
            facts=dataloader_facts,
            failures=dataloader_failures,
            warnings=dataloader_warnings,
        ),
    )
    results["dataloader"] = (
        dataloader_failures,
        dataloader_warnings,
        dataloader_facts,
        dataloader_report_path,
    )

    summary_path = report_dir / "gate_summary.md"
    write_report(
        summary_path,
        format_summary(
            manifest_path=manifest_path,
            config_path=config_path,
            base_dir=base_dir,
            batch_size=batch_size,
            seq_len=seq_len,
            dataloader_max_batches=dataloader_max_batches,
            gate_results=results,
        ),
    )
    return results, summary_path


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Run the standard v3.8 tokenized package validation gates."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Base directory for relative paths recorded in manifest.json.",
    )
    parser.add_argument(
        "--report-dir",
        default="artifacts/v3_8_tokenized_package_gates",
    )
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seq-len", type=int, default=128)
    parser.add_argument(
        "--dataloader-max-batches",
        type=int,
        default=4096,
        help="Evenly sample this many dataloader batches; 0 scans the full stream.",
    )
    args = parser.parse_args(argv)

    if (
        args.batch_size <= 0
        or args.seq_len <= 0
        or args.dataloader_max_batches < 0
    ):
        raise ValueError(
            "--batch-size and --seq-len must be positive; "
            "--dataloader-max-batches cannot be negative"
        )

    results, summary_path = run_gates(
        manifest_path=Path(args.manifest),
        config_path=Path(args.config),
        base_dir=Path(args.base_dir),
        report_dir=Path(args.report_dir),
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        dataloader_max_batches=args.dataloader_max_batches or None,
    )
    summary = summary_path.read_text(encoding="utf-8")
    print(summary)
    print(f"wrote_summary: {summary_path}")
    return 0 if all(not failures for failures, _warnings, _facts, _path in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
