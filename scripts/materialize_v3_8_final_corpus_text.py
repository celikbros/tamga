from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.validate_v3_8_final_corpus_manifest import (
    read_json,
    resolve_path,
    validate_manifest,
)


@dataclass
class MaterializeStats:
    source_path: Path
    output_path: Path
    corpus_format: str
    scanned_lines: int = 0
    written_lines: int = 0
    output_bytes: int = 0
    invalid_json: int = 0
    missing_text: int = 0
    non_string_text: int = 0


def sanitize_text_line(text: str) -> str:
    return text.replace("\r", " ").replace("\n", " ")


def materialize_text_source(*, source_path: Path, output_path: Path) -> MaterializeStats:
    stats = MaterializeStats(
        source_path=source_path,
        output_path=output_path,
        corpus_format="text",
    )
    with source_path.open("r", encoding="utf-8-sig") as source, output_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as target:
        for raw_line in source:
            stats.scanned_lines += 1
            line = raw_line.rstrip("\n")
            if line.endswith("\r"):
                line = line[:-1]
            line = sanitize_text_line(line)
            target.write(line)
            target.write("\n")
            stats.written_lines += 1
            stats.output_bytes += len(line.encode("utf-8")) + 1
    return stats


def inspect_existing_text_source(*, source_path: Path) -> tuple[MaterializeStats, list[str]]:
    stats = MaterializeStats(
        source_path=source_path,
        output_path=source_path,
        corpus_format="text",
    )
    failures: list[str] = []
    carriage_return_lines = 0
    carriage_return_examples: list[int] = []
    with source_path.open("r", encoding="utf-8-sig", newline="") as source:
        for row, raw_line in enumerate(source, start=1):
            stats.scanned_lines += 1
            if "\r" in raw_line:
                carriage_return_lines += 1
                if len(carriage_return_examples) < 10:
                    carriage_return_examples.append(row)
            line = raw_line.rstrip("\n")
            stats.written_lines += 1
            stats.output_bytes += len(line.encode("utf-8")) + 1
    if carriage_return_lines:
        failures.append(
            f"{source_path}: {carriage_return_lines} lines contain carriage returns; "
            f"first examples: {carriage_return_examples}"
        )
    try:
        actual_size = source_path.stat().st_size
    except OSError:
        actual_size = -1
    if actual_size >= 0 and stats.output_bytes != actual_size:
        failures.append(
            f"{source_path}: canonical LF byte count mismatch: "
            f"scanned {stats.output_bytes}, file size {actual_size}"
        )
    return stats, failures


def materialize_jsonl_source(
    *,
    source_path: Path,
    output_path: Path,
    text_field: str,
) -> tuple[MaterializeStats, list[str]]:
    stats = MaterializeStats(
        source_path=source_path,
        output_path=output_path,
        corpus_format="jsonl",
    )
    failures: list[str] = []
    with source_path.open("r", encoding="utf-8-sig") as source, output_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as target:
        for row, raw_line in enumerate(source, start=1):
            stats.scanned_lines += 1
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                stats.invalid_json += 1
                failures.append(f"{source_path}:{row}: invalid JSON: {exc.msg}")
                continue
            if not isinstance(record, dict):
                stats.non_string_text += 1
                failures.append(f"{source_path}:{row}: JSONL record must be an object")
                continue
            if text_field not in record:
                stats.missing_text += 1
                failures.append(f"{source_path}:{row}: missing text field {text_field!r}")
                continue
            value = record.get(text_field)
            if not isinstance(value, str):
                stats.non_string_text += 1
                failures.append(f"{source_path}:{row}: text field {text_field!r} must be a string")
                continue
            text = sanitize_text_line(value)
            target.write(text)
            target.write("\n")
            stats.written_lines += 1
            stats.output_bytes += len(text.encode("utf-8")) + 1
    return stats, failures


def format_report(
    *,
    manifest_path: Path,
    base_dir: Path,
    stats: MaterializeStats | None,
    failures: list[str],
    manifest_warnings: list[str],
) -> str:
    status = "PASS" if not failures else "FAIL"
    lines = [
        "# v3.8 Final Corpus Text Materialization",
        "",
        f"Manifest: `{manifest_path}`",
        f"Base dir: `{base_dir}`",
        f"Status: `{status}`",
        "",
        "This materializes the frozen final corpus into the plain UTF-8 text view",
        "expected by SentencePiece training and production tokenization.",
        "",
    ]
    if stats is not None:
        lines.extend(
            [
                "## Summary",
                "",
                "| Metric | Value |",
                "| --- | ---: |",
                f"| corpus format | `{stats.corpus_format}` |",
                f"| source path | `{stats.source_path}` |",
                f"| output path | `{stats.output_path}` |",
                f"| scanned lines | {stats.scanned_lines} |",
                f"| written lines | {stats.written_lines} |",
                f"| output bytes | {stats.output_bytes} |",
                f"| invalid JSON | {stats.invalid_json} |",
                f"| missing text | {stats.missing_text} |",
                f"| non-string text | {stats.non_string_text} |",
                "",
            ]
        )
    lines.extend(["## Failures", ""])
    if failures:
        lines.extend(f"- {failure}" for failure in failures[:100])
        if len(failures) > 100:
            lines.append(f"- ... {len(failures) - 100} additional failures omitted")
    else:
        lines.append("None.")
    lines.extend(["", "## Manifest Warnings", ""])
    if manifest_warnings:
        lines.extend(f"- {warning}" for warning in manifest_warnings)
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "## Next",
            "",
            "Use the output path as `--input` for `scripts/tokenize_corpus.py` and",
            "as the text corpus view for final SentencePiece retrain.",
            "",
        ]
    )
    return "\n".join(lines)


def materialize_from_manifest(
    *,
    manifest_path: Path,
    base_dir: Path,
    output_path: Path,
) -> tuple[MaterializeStats | None, list[str], list[str]]:
    manifest_failures, manifest_warnings, _facts = validate_manifest(
        manifest_path=manifest_path,
        base_dir=base_dir,
    )
    failures = list(manifest_failures)
    if failures:
        return None, failures, manifest_warnings

    manifest = read_json(manifest_path)
    corpus = manifest["corpus"]
    source_path = resolve_path(corpus["text_path"], base_dir=base_dir)
    corpus_format = str(corpus["format"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.resolve() == output_path.resolve():
        if corpus_format == "text":
            stats, inspect_failures = inspect_existing_text_source(source_path=source_path)
            return stats, inspect_failures, manifest_warnings
        return None, ["output path must differ from source path for jsonl sources"], manifest_warnings

    if corpus_format == "text":
        stats = materialize_text_source(source_path=source_path, output_path=output_path)
        return stats, [], manifest_warnings
    if corpus_format == "jsonl":
        text_field = str(corpus.get("text_field", "text"))
        stats, jsonl_failures = materialize_jsonl_source(
            source_path=source_path,
            output_path=output_path,
            text_field=text_field,
        )
        if jsonl_failures:
            try:
                output_path.unlink()
            except FileNotFoundError:
                pass
        return stats, jsonl_failures, manifest_warnings
    return None, [f"unsupported corpus format: {corpus_format}"], manifest_warnings


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Materialize v3.8 final corpus manifest into a plain text corpus view."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--base-dir", default=".")
    parser.add_argument(
        "--out",
        required=True,
        help="Output UTF-8 text file, one training sample per line.",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v3_8_final_corpus_text_materialization.md",
    )
    args = parser.parse_args(argv)

    stats, failures, manifest_warnings = materialize_from_manifest(
        manifest_path=Path(args.manifest),
        base_dir=Path(args.base_dir),
        output_path=Path(args.out),
    )
    report = format_report(
        manifest_path=Path(args.manifest),
        base_dir=Path(args.base_dir),
        stats=stats,
        failures=failures,
        manifest_warnings=manifest_warnings,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    print(f"wrote_report: {report_out}")
    if stats is not None and not failures:
        print(f"wrote_text: {stats.output_path}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
