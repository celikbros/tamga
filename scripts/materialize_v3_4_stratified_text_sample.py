from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import random
import sys
from pathlib import Path
from typing import Literal


SourceKind = Literal["jsonl", "text"]


@dataclass(frozen=True)
class SourceConfig:
    kind: SourceKind
    path: Path
    label: str
    target_bytes: int


@dataclass
class SourceStats:
    kind: SourceKind
    path: Path
    label: str
    file_bytes: int
    target_bytes: int
    chunks: int
    scanned_bytes: int = 0
    read_lines: int = 0
    written_lines: int = 0
    written_bytes: int = 0
    invalid_json: int = 0
    missing_text: int = 0
    empty_text: int = 0
    short_chunks: int = 0


def parse_size(raw: str) -> int:
    text = raw.strip().lower().replace("_", "")
    multipliers = {
        "k": 1024,
        "kb": 1024,
        "m": 1024 * 1024,
        "mb": 1024 * 1024,
        "g": 1024 * 1024 * 1024,
        "gb": 1024 * 1024 * 1024,
    }
    for suffix, multiplier in sorted(multipliers.items(), key=lambda item: len(item[0]), reverse=True):
        if text.endswith(suffix):
            return int(float(text[: -len(suffix)]) * multiplier)
    return int(text)


def clean_text(text: str) -> str:
    return text.strip().replace("\r", " ").replace("\n", " ")


def text_from_jsonl_line(raw_line: bytes, text_field: str) -> tuple[str | None, str | None]:
    try:
        record = json.loads(raw_line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "invalid_json"
    if not isinstance(record, dict) or text_field not in record:
        return None, "missing_text"
    value = record.get(text_field)
    if not isinstance(value, str):
        return None, "empty_text"
    text = clean_text(value)
    if not text:
        return None, "empty_text"
    return text, None


def iter_offsets(*, file_size: int, chunks: int, rng: random.Random) -> list[int]:
    if chunks <= 1 or file_size <= 0:
        return [0]
    segment = file_size / chunks
    offsets: list[int] = []
    for index in range(chunks):
        start = int(index * segment)
        end = int(min(file_size - 1, (index + 1) * segment - 1))
        if end <= start:
            offsets.append(start)
        else:
            offsets.append(rng.randint(start, end))
    return offsets


def sample_source(
    *,
    source: SourceConfig,
    text_field: str,
    chunks: int,
    rng: random.Random,
) -> tuple[list[str], SourceStats]:
    file_size = source.path.stat().st_size
    effective_chunks = max(1, min(chunks, max(1, source.target_bytes // 4096)))
    stats = SourceStats(
        kind=source.kind,
        path=source.path,
        label=source.label,
        file_bytes=file_size,
        target_bytes=source.target_bytes,
        chunks=effective_chunks,
    )
    if source.target_bytes >= file_size:
        offsets = [0]
        per_chunk_target = source.target_bytes
    else:
        offsets = iter_offsets(file_size=file_size, chunks=effective_chunks, rng=rng)
        per_chunk_target = max(1, source.target_bytes // effective_chunks)

    texts: list[str] = []
    seen: set[str] = set()
    with source.path.open("rb") as handle:
        for offset in offsets:
            handle.seek(offset)
            if offset > 0:
                skipped = handle.readline()
                stats.scanned_bytes += len(skipped)
            chunk_written = 0
            while chunk_written < per_chunk_target:
                raw_line = handle.readline()
                if not raw_line:
                    stats.short_chunks += 1
                    break
                stats.scanned_bytes += len(raw_line)
                stats.read_lines += 1
                if source.kind == "jsonl":
                    text, reason = text_from_jsonl_line(raw_line, text_field)
                    if reason == "invalid_json":
                        stats.invalid_json += 1
                    elif reason == "missing_text":
                        stats.missing_text += 1
                    elif reason == "empty_text":
                        stats.empty_text += 1
                    if text is None:
                        continue
                else:
                    try:
                        text = clean_text(raw_line.decode("utf-8"))
                    except UnicodeDecodeError:
                        stats.invalid_json += 1
                        continue
                    if not text:
                        stats.empty_text += 1
                        continue
                # Keep duplicate lines from dominating random chunk overlaps.
                digest = text[:256]
                if digest in seen:
                    continue
                seen.add(digest)
                texts.append(text)
                line_bytes = len(text.encode("utf-8")) + 1
                stats.written_lines += 1
                stats.written_bytes += line_bytes
                chunk_written += line_bytes
                if stats.written_bytes >= source.target_bytes:
                    break
            if stats.written_bytes >= source.target_bytes:
                break
    return texts, stats


def add_source_args(parser: argparse.ArgumentParser, flag: str, kind: SourceKind) -> None:
    parser.add_argument(
        flag,
        action="append",
        nargs=3,
        metavar=("PATH", "LABEL", "TARGET_BYTES"),
        help=f"{kind} source as PATH LABEL TARGET_BYTES, e.g. corpus.jsonl wiki 128MB",
    )


def parse_sources(args: argparse.Namespace) -> list[SourceConfig]:
    sources: list[SourceConfig] = []
    for raw in args.jsonl_source or []:
        path, label, size = raw
        sources.append(
            SourceConfig(kind="jsonl", path=Path(path), label=label, target_bytes=parse_size(size))
        )
    for raw in args.text_source or []:
        path, label, size = raw
        sources.append(
            SourceConfig(kind="text", path=Path(path), label=label, target_bytes=parse_size(size))
        )
    return sources


def format_bytes(value: int) -> str:
    mib = value / (1024 * 1024)
    return f"{mib:.2f} MiB"


def write_report(
    *,
    report_out: Path,
    output_path: Path,
    seed: int,
    chunks: int,
    stats_rows: list[SourceStats],
) -> None:
    total_written_lines = sum(row.written_lines for row in stats_rows)
    total_written_bytes = sum(row.written_bytes for row in stats_rows)
    total_target_bytes = sum(row.target_bytes for row in stats_rows)
    lines = [
        "# v3.4 Stratified Text Sample Materialization",
        "",
        f"Output: `{output_path.as_posix()}`",
        f"Seed: `{seed}`",
        f"Requested chunks/source: `{chunks}`",
        "",
        "This sample is built from deterministic byte-region chunks instead of",
        "prefix-only source reads. It is intended as a larger tokenizer-training",
        "candidate sample, not as an LLM pretraining dataset.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| target bytes | {total_target_bytes} |",
        f"| target bytes readable | {format_bytes(total_target_bytes)} |",
        f"| written text lines | {total_written_lines} |",
        f"| output bytes | {total_written_bytes} |",
        f"| output bytes readable | {format_bytes(total_written_bytes)} |",
        "",
        "## Sources",
        "",
        "| Source | Kind | File bytes | Target bytes | Written bytes | Written lines | Read lines | Scanned bytes | Invalid JSON/UTF-8 | Missing text | Empty text | Short chunks |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in stats_rows:
        lines.append(
            f"| `{row.label}` | `{row.kind}` | {row.file_bytes} | {row.target_bytes} | "
            f"{row.written_bytes} | {row.written_lines} | {row.read_lines} | "
            f"{row.scanned_bytes} | {row.invalid_json} | {row.missing_text} | "
            f"{row.empty_text} | {row.short_chunks} |"
        )
    lines.extend(
        [
            "",
            "## Next",
            "",
            "Use this text file for v3.4 SentencePiece ablation only after checking",
            "token pressure and route-density on the current v3 sidecar path.",
        ]
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Materialize a v3.4 stratified text sample.")
    add_source_args(parser, "--jsonl-source", "jsonl")
    add_source_args(parser, "--text-source", "text")
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--seed", type=int, default=20260619)
    parser.add_argument("--chunks", type=int, default=64)
    parser.add_argument("--shuffle-output", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    if args.chunks <= 0:
        raise ValueError("--chunks must be positive")
    sources = parse_sources(args)
    if not sources:
        raise ValueError("at least one --jsonl-source or --text-source is required")
    rng = random.Random(args.seed)
    all_texts: list[str] = []
    stats_rows: list[SourceStats] = []
    for source in sources:
        if not source.path.exists():
            raise FileNotFoundError(source.path)
        texts, stats = sample_source(
            source=source,
            text_field=args.text_field,
            chunks=args.chunks,
            rng=rng,
        )
        all_texts.extend(texts)
        stats_rows.append(stats)
    if args.shuffle_output:
        rng.shuffle(all_texts)

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for text in all_texts:
            handle.write(text)
            handle.write("\n")

    report_out = Path(args.report_out)
    write_report(
        report_out=report_out,
        output_path=output_path,
        seed=args.seed,
        chunks=args.chunks,
        stats_rows=stats_rows,
    )
    print(report_out.read_text(encoding="utf-8"))
    print(f"wrote_text: {output_path}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
