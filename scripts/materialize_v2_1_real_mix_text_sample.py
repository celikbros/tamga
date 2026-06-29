from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceConfig:
    path: Path
    max_lines: int | None
    source_label: str


@dataclass
class SourceStats:
    source_label: str
    path: Path
    scanned: int = 0
    written: int = 0
    skipped_invalid_json: int = 0
    skipped_missing_text: int = 0
    skipped_empty_text: int = 0
    bytes_written: int = 0


def _positive_int_or_none(value: str) -> int | None:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def parse_source(raw: str) -> SourceConfig:
    path_raw = raw
    max_lines: int | None = None
    label: str | None = None

    head, sep, maybe_label = raw.rpartition(":")
    if sep and maybe_label and head:
        head2, sep2, maybe_limit = head.rpartition(":")
        if sep2 and maybe_limit.isdigit():
            path_raw = head2
            max_lines = _positive_int_or_none(maybe_limit)
            label = maybe_label
        elif maybe_label.isdigit():
            path_raw = head
            max_lines = _positive_int_or_none(maybe_label)

    path = Path(path_raw)
    return SourceConfig(path, max_lines, label or path.stem)


def text_from_record(record: Any, field: str) -> str | None:
    if not isinstance(record, dict):
        return None
    value = record.get(field)
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def iter_sampled_records(
    *,
    source: SourceConfig,
    text_field: str,
    rng: random.Random,
    sample_probability: float,
) -> tuple[list[str], SourceStats]:
    stats = SourceStats(source_label=source.source_label, path=source.path)
    output: list[str] = []
    with source.path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if source.max_lines is not None and stats.scanned >= source.max_lines:
                break
            stats.scanned += 1
            if sample_probability < 1.0 and rng.random() > sample_probability:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                stats.skipped_invalid_json += 1
                continue
            text = text_from_record(record, text_field)
            if text is None:
                if isinstance(record, dict) and text_field not in record:
                    stats.skipped_missing_text += 1
                else:
                    stats.skipped_empty_text += 1
                continue
            output.append(text)
            stats.written += 1
            stats.bytes_written += len(text.encode("utf-8")) + 1
    return output, stats


def write_report(
    *,
    report_out: Path,
    output_path: Path,
    sources: list[SourceStats],
    text_field: str,
    seed: int,
    sample_probability: float,
) -> None:
    total_scanned = sum(row.scanned for row in sources)
    total_written = sum(row.written for row in sources)
    total_bytes = sum(row.bytes_written for row in sources)
    lines = [
        "# v2.1 Real-Mix Text Sample Materialization",
        "",
        f"Output: `{output_path.as_posix()}`",
        f"Text field: `{text_field}`",
        f"Seed: `{seed}`",
        f"Sample probability: `{sample_probability:.6f}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| scanned lines | {total_scanned} |",
        f"| written text lines | {total_written} |",
        f"| output bytes | {total_bytes} |",
        "",
        "## Sources",
        "",
        "| Source | Path | Scanned | Written | Bytes written | Invalid JSON | Missing text | Empty/non-string text |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in sources:
        lines.append(
            f"| `{row.source_label}` | `{row.path.as_posix()}` | {row.scanned} | "
            f"{row.written} | {row.bytes_written} | {row.skipped_invalid_json} | "
            f"{row.skipped_missing_text} | {row.skipped_empty_text} |"
        )
    lines.extend(
        [
            "",
            "## Next",
            "",
            "Use the output file as `--input` for route-density and operation",
            "simulation audits. This materialization writes raw text lines only;",
            "JSON syntax and metadata are not included in the tokenizer audit input.",
        ]
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Materialize a raw text sample from JSONL corpus files for v2.1 audits."
    )
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help=(
            "JSONL source as path[:max_lines[:label]]. Example: "
            "data/train/private/celik_ai/trt_news_corpus.jsonl:20000:trt"
        ),
    )
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--seed", type=int, default=20260613)
    parser.add_argument("--sample-probability", type=float, default=1.0)
    parser.add_argument(
        "--out",
        default="artifacts/private/v2_1_real_mix/real_mix_sample.txt",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_1_real_mix_text_sample_materialization.md",
    )
    args = parser.parse_args(argv)

    if not (0.0 < args.sample_probability <= 1.0):
        raise ValueError("--sample-probability must be in (0, 1]")

    rng = random.Random(args.seed)
    sources = [parse_source(raw) for raw in args.source]
    all_texts: list[str] = []
    stats_rows: list[SourceStats] = []
    for source in sources:
        texts, stats = iter_sampled_records(
            source=source,
            text_field=args.text_field,
            rng=rng,
            sample_probability=args.sample_probability,
        )
        all_texts.extend(texts)
        stats_rows.append(stats)

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for text in all_texts:
            handle.write(text.replace("\r", " ").replace("\n", " "))
            handle.write("\n")

    report_out = Path(args.report_out)
    write_report(
        report_out=report_out,
        output_path=output_path,
        sources=stats_rows,
        text_field=args.text_field,
        seed=args.seed,
        sample_probability=args.sample_probability,
    )
    print(report_out.read_text(encoding="utf-8"))
    print(f"wrote_text: {output_path}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
