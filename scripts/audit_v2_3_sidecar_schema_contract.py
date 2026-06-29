from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import argparse
import json
import sys
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA_VERSION = "v2.2-sidecar-jsonl-1"
EXPECTED_TOKENIZER = "sp64_protected_passthrough_sidecar"
KNOWN_ROUTES = frozenset(
    {
        "numeric_like",
        "file_like",
        "apostrophe_surface",
        "non_turkish_latin_word",
        "greek_word",
        "arabic_word",
        "percent_encoded",
        "cyrillic_word",
        "uzbek_apostrophe_word",
        "azerbaijani_word",
    }
)
REQUIRED_RECORD_FIELDS = frozenset(
    {
        "schema_version",
        "tokenizer",
        "split",
        "line_number",
        "raw_bytes",
        "token_count",
        "fallback_source_tokens",
        "spans",
    }
)
REQUIRED_SPAN_FIELDS = frozenset(
    {"route", "byte_start", "byte_end", "char_start", "char_end", "surface"}
)


@dataclass
class SchemaStats:
    records: int = 0
    spans: int = 0
    json_failures: int = 0
    missing_field_failures: int = 0
    type_failures: int = 0
    schema_version_failures: int = 0
    tokenizer_failures: int = 0
    line_order_failures: int = 0
    raw_line_failures: int = 0
    offset_failures: int = 0
    surface_failures: int = 0
    span_order_failures: int = 0
    span_overlap_failures: int = 0
    unknown_route_failures: int = 0
    unknown_routes: Counter[str] = field(default_factory=Counter)

    @property
    def failures(self) -> int:
        return (
            self.json_failures
            + self.missing_field_failures
            + self.type_failures
            + self.schema_version_failures
            + self.tokenizer_failures
            + self.line_order_failures
            + self.raw_line_failures
            + self.offset_failures
            + self.surface_failures
            + self.span_order_failures
            + self.span_overlap_failures
            + self.unknown_route_failures
        )

    @property
    def ok(self) -> bool:
        return self.failures == 0


def load_raw_lines(path: Path | None) -> list[str] | None:
    if path is None:
        return None
    with path.open("r", encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle]


def is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_record_types(record: dict[str, Any], stats: SchemaStats) -> bool:
    ok = True
    if not isinstance(record.get("schema_version"), str):
        ok = False
    if not isinstance(record.get("tokenizer"), str):
        ok = False
    if not isinstance(record.get("split"), str):
        ok = False
    if not isinstance(record.get("line_number"), int) or isinstance(
        record.get("line_number"), bool
    ) or record.get("line_number", 0) <= 0:
        ok = False
    for key in ("raw_bytes", "token_count", "fallback_source_tokens"):
        if not is_non_negative_int(record.get(key)):
            ok = False
    if not isinstance(record.get("spans"), list):
        ok = False
    if ok and record["fallback_source_tokens"] > record["token_count"]:
        ok = False
    if not ok:
        stats.type_failures += 1
    return ok


def validate_span(
    *,
    span: Any,
    raw_text: str | None,
    raw_bytes_len: int,
    closed_route_enum: bool,
    stats: SchemaStats,
) -> tuple[int, int] | None:
    if not isinstance(span, dict):
        stats.type_failures += 1
        return None
    missing = REQUIRED_SPAN_FIELDS - set(span)
    if missing:
        stats.missing_field_failures += 1
        return None
    if not isinstance(span["route"], str) or not isinstance(span["surface"], str):
        stats.type_failures += 1
        return None
    for key in ("byte_start", "byte_end", "char_start", "char_end"):
        if not is_non_negative_int(span.get(key)):
            stats.type_failures += 1
            return None

    route = span["route"]
    if route not in KNOWN_ROUTES:
        stats.unknown_routes[route] += 1
        if closed_route_enum:
            stats.unknown_route_failures += 1

    byte_start = span["byte_start"]
    byte_end = span["byte_end"]
    char_start = span["char_start"]
    char_end = span["char_end"]
    if byte_start > byte_end or byte_end > raw_bytes_len or char_start > char_end:
        stats.offset_failures += 1
        return None
    if raw_text is not None and char_end > len(raw_text):
        stats.offset_failures += 1
        return None
    if raw_text is not None:
        raw_bytes = raw_text.encode("utf-8")
        try:
            byte_surface = raw_bytes[byte_start:byte_end].decode("utf-8")
        except UnicodeDecodeError:
            stats.surface_failures += 1
            return (byte_start, byte_end)
        if byte_surface != span["surface"] or raw_text[char_start:char_end] != span["surface"]:
            stats.surface_failures += 1
    return (byte_start, byte_end)


def audit_sidecar(
    *,
    sidecar_path: Path,
    raw_lines: list[str] | None,
    expected_schema_version: str,
    expected_tokenizer: str,
    closed_route_enum: bool,
) -> SchemaStats:
    stats = SchemaStats()
    last_line_by_split: dict[str, int] = {}
    with sidecar_path.open("r", encoding="utf-8") as handle:
        for row_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                stats.json_failures += 1
                continue
            if not isinstance(record, dict):
                stats.type_failures += 1
                continue
            stats.records += 1
            missing = REQUIRED_RECORD_FIELDS - set(record)
            if missing:
                stats.missing_field_failures += 1
                continue
            if not validate_record_types(record, stats):
                continue
            if record["schema_version"] != expected_schema_version:
                stats.schema_version_failures += 1
            if record["tokenizer"] != expected_tokenizer:
                stats.tokenizer_failures += 1

            split = record["split"]
            line_number = record["line_number"]
            if line_number <= last_line_by_split.get(split, 0):
                stats.line_order_failures += 1
            last_line_by_split[split] = line_number

            raw_text: str | None = None
            if raw_lines is not None:
                if line_number > len(raw_lines):
                    stats.raw_line_failures += 1
                else:
                    raw_text = raw_lines[line_number - 1]
                    if len(raw_text.encode("utf-8")) != record["raw_bytes"]:
                        stats.raw_line_failures += 1
            raw_bytes_len = len(raw_text.encode("utf-8")) if raw_text is not None else record["raw_bytes"]

            previous: tuple[int, int] | None = None
            for span in record["spans"]:
                stats.spans += 1
                current = validate_span(
                    span=span,
                    raw_text=raw_text,
                    raw_bytes_len=raw_bytes_len,
                    closed_route_enum=closed_route_enum,
                    stats=stats,
                )
                if current is None:
                    continue
                if previous is not None:
                    if current[0] < previous[0] or (
                        current[0] == previous[0] and current[1] < previous[1]
                    ):
                        stats.span_order_failures += 1
                    if current[0] < previous[1]:
                        stats.span_overlap_failures += 1
                previous = current
    return stats


def fmt_status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def format_report(
    *,
    sidecar_path: Path,
    raw_input_path: Path | None,
    stats: SchemaStats,
    expected_schema_version: str,
    expected_tokenizer: str,
    closed_route_enum: bool,
) -> str:
    lines = [
        "# v2.3 Sidecar Schema Contract Audit",
        "",
        f"Sidecar: `{sidecar_path.as_posix()}`",
        f"Raw input: `{raw_input_path.as_posix() if raw_input_path else 'not provided'}`",
        f"Expected schema version: `{expected_schema_version}`",
        f"Expected tokenizer: `{expected_tokenizer}`",
        f"Closed route enum: `{closed_route_enum}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| records | {stats.records} |",
        f"| spans | {stats.spans} |",
        f"| total failures | {stats.failures} |",
        f"| status | {fmt_status(stats.ok)} |",
        "",
        "## Failure Counts",
        "",
        "| Check | Failures |",
        "| --- | ---: |",
        f"| json | {stats.json_failures} |",
        f"| missing fields | {stats.missing_field_failures} |",
        f"| field types | {stats.type_failures} |",
        f"| schema version | {stats.schema_version_failures} |",
        f"| tokenizer | {stats.tokenizer_failures} |",
        f"| line order | {stats.line_order_failures} |",
        f"| raw line | {stats.raw_line_failures} |",
        f"| offsets | {stats.offset_failures} |",
        f"| surfaces | {stats.surface_failures} |",
        f"| span order | {stats.span_order_failures} |",
        f"| span overlap | {stats.span_overlap_failures} |",
        f"| unknown route | {stats.unknown_route_failures} |",
        "",
    ]
    if stats.unknown_routes:
        lines.extend(
            [
                "## Unknown Routes",
                "",
                "| Route | Count |",
                "| --- | ---: |",
            ]
        )
        for route, count in stats.unknown_routes.most_common():
            lines.append(f"| `{route}` | {count} |")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            (
                "The sidecar JSONL satisfies the v2.3 schema contract."
                if stats.ok
                else "The sidecar JSONL does not satisfy the v2.3 schema contract."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the v2.3 sidecar JSONL schema contract.")
    parser.add_argument("--sidecar-in", required=True)
    parser.add_argument("--input")
    parser.add_argument("--expected-schema-version", default=EXPECTED_SCHEMA_VERSION)
    parser.add_argument("--expected-tokenizer", default=EXPECTED_TOKENIZER)
    parser.add_argument("--closed-route-enum", action="store_true")
    parser.add_argument("--report-out", default="artifacts/v2_3_sidecar_schema_contract_audit.md")
    args = parser.parse_args(argv)

    sidecar_path = Path(args.sidecar_in)
    raw_input_path = Path(args.input) if args.input else None
    stats = audit_sidecar(
        sidecar_path=sidecar_path,
        raw_lines=load_raw_lines(raw_input_path),
        expected_schema_version=args.expected_schema_version,
        expected_tokenizer=args.expected_tokenizer,
        closed_route_enum=args.closed_route_enum,
    )
    report = format_report(
        sidecar_path=sidecar_path,
        raw_input_path=raw_input_path,
        stats=stats,
        expected_schema_version=args.expected_schema_version,
        expected_tokenizer=args.expected_tokenizer,
        closed_route_enum=args.closed_route_enum,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0 if stats.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
