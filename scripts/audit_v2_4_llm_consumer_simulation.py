from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_v2_1_sidecar_operation_simulation import (  # noqa: E402
    RouteStats,
    Span,
    interval_bytes,
    merge_intervals,
    span_mask,
    sp_token_pieces,
)
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import load_sp_processor  # noqa: E402


DEFAULT_SP_MODEL = Path("artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model")


@dataclass
class ConsumerStats:
    lines: int = 0
    raw_bytes: int = 0
    spans: int = 0
    protected_bytes: int = 0
    copy_failures: int = 0
    redaction_failures: int = 0
    token_mask_failures: int = 0
    union_mask_bytes: int = 0
    union_extra_bytes: int = 0
    crossing_spans: int = 0
    edge_aligned_spans: int = 0
    token_count_sum: int = 0
    max_extra_bytes: int = 0
    routes: dict[str, RouteStats] = field(default_factory=lambda: defaultdict(RouteStats))

    @property
    def failures(self) -> int:
        return self.copy_failures + self.redaction_failures + self.token_mask_failures

    @property
    def protected_bytes_share(self) -> float:
        return self.protected_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def union_extra_bytes_share(self) -> float:
        return self.union_extra_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def union_extra_per_protected_byte(self) -> float:
        return self.union_extra_bytes / self.protected_bytes if self.protected_bytes else 0.0

    @property
    def edge_aligned_rate(self) -> float:
        return self.edge_aligned_spans / self.spans if self.spans else 1.0

    @property
    def crossing_span_rate(self) -> float:
        return self.crossing_spans / self.spans if self.spans else 0.0

    @property
    def avg_tokens_per_span(self) -> float:
        return self.token_count_sum / self.spans if self.spans else 0.0


def load_raw_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle]


def iter_sidecar_records(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def span_from_record(item: dict[str, Any]) -> Span:
    return Span(
        route=str(item["route"]),
        surface=str(item["surface"]),
        char_start=int(item["char_start"]),
        char_end=int(item["char_end"]),
        byte_start=int(item["byte_start"]),
        byte_end=int(item["byte_end"]),
    )


def redact_by_sidecar(text: str, spans: list[Span]) -> str:
    raw_bytes = text.encode("utf-8")
    chunks: list[bytes] = []
    cursor = 0
    for span in sorted(spans, key=lambda item: (item.byte_start, item.byte_end)):
        chunks.append(raw_bytes[cursor : span.byte_start])
        chunks.append(f"<PROTECTED:{span.route}>".encode("ascii"))
        cursor = span.byte_end
    chunks.append(raw_bytes[cursor:])
    return b"".join(chunks).decode("utf-8")


def audit_consumer_line(
    *,
    text: str,
    spans: list[Span],
    processor: Any,
    stats: ConsumerStats,
) -> list[dict[str, object]]:
    samples: list[dict[str, object]] = []
    raw_bytes = text.encode("utf-8")
    stats.lines += 1
    stats.raw_bytes += len(raw_bytes)
    stats.spans += len(spans)
    stats.protected_bytes += sum(span.byte_len for span in spans)

    for span in spans:
        try:
            copied = raw_bytes[span.byte_start : span.byte_end].decode("utf-8")
        except UnicodeDecodeError:
            copied = ""
        if copied != span.surface or text[span.char_start : span.char_end] != span.surface:
            stats.copy_failures += 1
            samples.append({"reason": "copy_failure", "route": span.route, "surface": span.surface})

    try:
        _redacted = redact_by_sidecar(text, spans)
    except Exception as exc:  # pragma: no cover - defensive audit output
        stats.redaction_failures += 1
        samples.append({"reason": f"redaction_error:{type(exc).__name__}"})

    tokens = sp_token_pieces(processor, text)
    mask_intervals: list[tuple[int, int]] = []
    protected_intervals = [(span.byte_start, span.byte_end) for span in spans]
    for span in spans:
        mask = span_mask(span, tokens)
        if mask is None:
            stats.token_mask_failures += 1
            samples.append({"reason": "token_mask_failure", "route": span.route, "surface": span.surface})
            continue
        mask_intervals.append((mask.mask_start, mask.mask_end))
        stats.token_count_sum += mask.token_count
        stats.max_extra_bytes = max(stats.max_extra_bytes, mask.extra_bytes)
        if mask.edge_aligned:
            stats.edge_aligned_spans += 1
        if mask.has_crossing:
            stats.crossing_spans += 1
        route_stats = stats.routes[span.route]
        route_stats.spans += 1
        route_stats.protected_bytes += span.byte_len
        route_stats.summed_mask_bytes += mask.mask_bytes
        route_stats.summed_extra_bytes += mask.extra_bytes
        route_stats.crossing_spans += int(mask.has_crossing)
        route_stats.crossing_tokens += mask.crossing_tokens
        route_stats.edge_aligned_spans += int(mask.edge_aligned)
        route_stats.token_count_sum += mask.token_count
        route_stats.max_extra_bytes = max(route_stats.max_extra_bytes, mask.extra_bytes)
        route_stats.surfaces[span.surface] += 1

    protected_union = interval_bytes(merge_intervals(protected_intervals))
    mask_union = interval_bytes(merge_intervals(mask_intervals))
    stats.union_mask_bytes += mask_union
    stats.union_extra_bytes += max(0, mask_union - protected_union)
    return samples


def audit_consumer(
    *,
    input_path: Path,
    sidecar_path: Path,
    processor: Any,
    progress: int,
    sample_limit: int,
) -> tuple[ConsumerStats, list[dict[str, object]]]:
    raw_lines = load_raw_lines(input_path)
    stats = ConsumerStats()
    samples: list[dict[str, object]] = []
    for index, record in enumerate(iter_sidecar_records(sidecar_path), start=1):
        line_number = int(record["line_number"])
        if line_number > len(raw_lines):
            stats.copy_failures += 1
            samples.append({"reason": "line_number_out_of_range", "line_number": line_number})
            continue
        spans = [span_from_record(item) for item in record["spans"]]
        line_samples = audit_consumer_line(
            text=raw_lines[line_number - 1],
            spans=spans,
            processor=processor,
            stats=stats,
        )
        remaining = max(0, sample_limit - len(samples))
        samples.extend(line_samples[:remaining])
        if progress > 0 and index % progress == 0:
            print(
                f"simulated {index:,} sidecar records spans={stats.spans:,} "
                f"failures={stats.failures:,} extra_mask={stats.union_extra_bytes:,}",
                flush=True,
            )
    return stats, samples[:sample_limit]


def fmt(value: float) -> str:
    return f"{value:.6f}"


def format_report(*, input_path: Path, sidecar_path: Path, stats: ConsumerStats) -> str:
    lines = [
        "# v2.4 LLM Consumer Simulation",
        "",
        f"Input: `{input_path.as_posix()}`",
        f"Sidecar: `{sidecar_path.as_posix()}`",
        "",
        "This audit simulates three downstream operations over the frozen sidecar:",
        "",
        "```text",
        "copy protected bytes by sidecar offsets",
        "redact protected spans in raw text",
        "map protected byte spans to conservative overlapping SP tokens for masking",
        "```",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| lines | {stats.lines} |",
        f"| raw bytes | {stats.raw_bytes} |",
        f"| protected spans | {stats.spans} |",
        f"| protected bytes/raw byte | {fmt(stats.protected_bytes_share)} |",
        f"| copy failures | {stats.copy_failures} |",
        f"| redaction failures | {stats.redaction_failures} |",
        f"| token-mask failures | {stats.token_mask_failures} |",
        f"| total failures | {stats.failures} |",
        f"| conservative mask bytes | {stats.union_mask_bytes} |",
        f"| extra mask bytes | {stats.union_extra_bytes} |",
        f"| extra mask bytes/raw byte | {fmt(stats.union_extra_bytes_share)} |",
        f"| extra/protected byte | {fmt(stats.union_extra_per_protected_byte)} |",
        f"| edge-aligned span rate | {fmt(stats.edge_aligned_rate)} |",
        f"| crossing span rate | {fmt(stats.crossing_span_rate)} |",
        f"| avg tokens/span | {fmt(stats.avg_tokens_per_span)} |",
        f"| max extra bytes/span | {stats.max_extra_bytes} |",
        f"| status | {'PASS' if stats.failures == 0 else 'FAIL'} |",
        "",
        "## Route Summary",
        "",
        "| Route | Spans | Extra/protected byte | Edge-aligned span rate | Avg tokens/span | Max extra bytes/span | Top surfaces |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for route, route_stats in sorted(stats.routes.items()):
        top = ", ".join(
            f"`{surface}`:{count}" for surface, count in route_stats.surfaces.most_common(5)
        )
        lines.append(
            f"| `{route}` | {route_stats.spans} | "
            f"{fmt(route_stats.extra_per_protected_byte)} | "
            f"{fmt(route_stats.edge_aligned_rate)} | "
            f"{fmt(route_stats.avg_tokens_per_span)} | "
            f"{route_stats.max_extra_bytes} | {top} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The frozen sidecar supports the simulated LLM consumer operations."
                if stats.failures == 0
                else "The frozen sidecar failed one or more simulated LLM consumer operations."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Run v2.4 LLM consumer sidecar simulation.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--sidecar-in", required=True)
    parser.add_argument("--sp-model", default=str(DEFAULT_SP_MODEL))
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument("--sample-limit", type=int, default=25)
    parser.add_argument("--samples-out", default="artifacts/private/v2_4_llm_consumer_simulation.samples.jsonl")
    parser.add_argument("--report-out", default="artifacts/v2_4_llm_consumer_simulation.md")
    args = parser.parse_args(argv)

    processor = load_sp_processor(Path(args.sp_model))
    stats, samples = audit_consumer(
        input_path=Path(args.input),
        sidecar_path=Path(args.sidecar_in),
        processor=processor,
        progress=args.progress,
        sample_limit=args.sample_limit,
    )
    samples_out = Path(args.samples_out)
    write_jsonl(samples_out, samples)
    report = format_report(input_path=Path(args.input), sidecar_path=Path(args.sidecar_in), stats=stats)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    print(f"wrote_samples: {samples_out}")
    return 0 if stats.failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
