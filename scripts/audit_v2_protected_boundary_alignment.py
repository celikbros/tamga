from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_v2_finite_protected_sp64_intrinsic import load_sp_processor  # noqa: E402
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class SpanRecord:
    route: str
    start: int
    end: int
    surface: str


@dataclass
class AlignmentStats:
    split: str
    lines: int = 0
    raw_bytes: int = 0
    protected_spans: int = 0
    protected_edges: int = 0
    aligned_edges: int = 0
    misaligned_edges: int = 0
    crossing_pieces: int = 0
    route_spans: Counter[str] = field(default_factory=Counter)
    route_misaligned_edges: Counter[str] = field(default_factory=Counter)
    route_crossing_pieces: Counter[str] = field(default_factory=Counter)

    @property
    def edge_alignment_rate(self) -> float:
        return self.aligned_edges / self.protected_edges if self.protected_edges else 1.0


def protected_spans(text: str, tokenizer: TurkishTokenizer) -> list[SpanRecord]:
    spans: list[SpanRecord] = []
    offset = 0
    for piece in analyze_line(text, tokenizer):
        start = offset
        end = start + len(piece.surface)
        if piece.kind.startswith("protected:"):
            spans.append(
                SpanRecord(
                    route=piece.kind.removeprefix("protected:"),
                    start=start,
                    end=end,
                    surface=piece.surface,
                )
            )
        offset = end
    if offset != len(text):
        raise ValueError("analyze_line surfaces did not reconstruct input")
    return spans


def sp_piece_offsets(processor: Any, text: str) -> list[tuple[int, int, str]]:
    proto = processor.EncodeAsImmutableProto(text)
    return [(int(piece.begin), int(piece.end), str(piece.piece)) for piece in proto.pieces]


def shifted_sp_piece_offsets(
    processor: Any,
    surface: str,
    *,
    base_offset: int,
) -> list[tuple[int, int, str]]:
    return [
        (base_offset + begin, base_offset + end, piece)
        for begin, end, piece in sp_piece_offsets(processor, surface)
    ]


def isolated_token_piece_offsets(
    *,
    text: str,
    processor: Any,
    tokenizer: TurkishTokenizer,
    passthrough_routes: set[str],
) -> list[tuple[int, int, str]]:
    output: list[tuple[int, int, str]] = []
    segment = ""
    segment_start = 0
    offset = 0

    def flush() -> None:
        nonlocal segment, segment_start
        if not segment:
            return
        output.extend(
            shifted_sp_piece_offsets(
                processor,
                segment,
                base_offset=segment_start,
            )
        )
        segment = ""
        segment_start = offset

    for piece in analyze_line(text, tokenizer):
        start = offset
        end = start + len(piece.surface)
        if piece.kind.startswith("protected:"):
            route = piece.kind.removeprefix("protected:")
            if route in passthrough_routes:
                flush()
                output.extend(
                    shifted_sp_piece_offsets(
                        processor,
                        piece.surface,
                        base_offset=start,
                    )
                )
                offset = end
                segment_start = offset
                continue
        if not segment:
            segment_start = start
        segment += piece.surface
        offset = end

    flush()
    return output


def audit_line(
    *,
    text: str,
    processor: Any,
    tokenizer: TurkishTokenizer,
    passthrough_routes: set[str],
    isolate_sp_passthrough_routes: bool,
    byte_fallback_crossing_pieces: bool,
) -> tuple[list[SpanRecord], set[int], list[tuple[str, int, int, str]]]:
    spans = protected_spans(text, tokenizer)
    protected_edges = {edge for span in spans for edge in (span.start, span.end)}
    token_pieces = (
        isolated_token_piece_offsets(
            text=text,
            processor=processor,
            tokenizer=tokenizer,
            passthrough_routes=passthrough_routes,
        )
        if isolate_sp_passthrough_routes
        else sp_piece_offsets(processor, text)
    )
    if byte_fallback_crossing_pieces:
        edge_safe_pieces: list[tuple[int, int, str]] = []
        for begin, end, piece in token_pieces:
            if any(begin < edge < end for edge in protected_edges):
                for index in range(begin, end):
                    edge_safe_pieces.append((index, index + 1, "<byte_fallback>"))
            else:
                edge_safe_pieces.append((begin, end, piece))
        token_pieces = edge_safe_pieces
    token_edges: set[int] = {0, len(text)}
    for begin, end, _piece in token_pieces:
        token_edges.add(begin)
        token_edges.add(end)

    crossing: list[tuple[str, int, int, str]] = []
    for span in spans:
        for begin, end, piece in token_pieces:
            crosses_start = begin < span.start < end
            crosses_end = begin < span.end < end
            if crosses_start or crosses_end:
                crossing.append((span.route, begin, end, piece))
    return spans, token_edges, crossing


def audit_split(
    *,
    split: str,
    path: Path,
    processor: Any,
    max_lines: int | None,
    sample_limit: int,
    progress: int,
    passthrough_routes: set[str],
    isolate_sp_passthrough_routes: bool,
    byte_fallback_crossing_pieces: bool,
) -> tuple[AlignmentStats, list[dict[str, object]]]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    stats = AlignmentStats(split=split)
    samples: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            if max_lines is not None and stats.lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            stats.lines += 1
            stats.raw_bytes += len(text.encode("utf-8"))
            spans, token_edges, crossing = audit_line(
                text=text,
                processor=processor,
                tokenizer=tokenizer,
                passthrough_routes=passthrough_routes,
                isolate_sp_passthrough_routes=isolate_sp_passthrough_routes,
                byte_fallback_crossing_pieces=byte_fallback_crossing_pieces,
            )
            stats.protected_spans += len(spans)
            for span in spans:
                stats.route_spans[span.route] += 1
                for edge in (span.start, span.end):
                    stats.protected_edges += 1
                    if edge in token_edges:
                        stats.aligned_edges += 1
                    else:
                        stats.misaligned_edges += 1
                        stats.route_misaligned_edges[span.route] += 1
                        if len(samples) < sample_limit:
                            samples.append(
                                {
                                    "kind": "misaligned_edge",
                                    "split": split,
                                    "line_no": line_no,
                                    "route": span.route,
                                    "edge": edge,
                                    "span_start": span.start,
                                    "span_end": span.end,
                                    "surface": span.surface,
                                    "text": text,
                                }
                            )
            for route, begin, end, piece in crossing:
                stats.crossing_pieces += 1
                stats.route_crossing_pieces[route] += 1
                if len(samples) < sample_limit:
                    samples.append(
                        {
                            "kind": "crossing_piece",
                            "split": split,
                            "line_no": line_no,
                            "route": route,
                            "piece": piece,
                            "piece_begin": begin,
                            "piece_end": end,
                            "text": text,
                        }
                    )
            if progress > 0 and stats.lines % progress == 0:
                print(
                    f"audited {split} {stats.lines:,} lines "
                    f"alignment={stats.edge_alignment_rate:.6f}",
                    flush=True,
                )
    return stats, samples


def write_samples(path: Path, samples: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False) + "\n")


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def format_report(
    *,
    split_dir: Path,
    sp_model: Path,
    stats_rows: list[AlignmentStats],
    samples_out: Path,
    passthrough_routes: set[str],
    isolate_sp_passthrough_routes: bool,
    byte_fallback_crossing_pieces: bool,
) -> str:
    lines = [
        "# v2.0 Protected Boundary Alignment Audit",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"SP model: `{sp_model.as_posix()}`",
        f"SP passthrough routes: `{', '.join(sorted(passthrough_routes)) or 'none'}`",
        f"Isolate SP passthrough routes: `{isolate_sp_passthrough_routes}`",
        f"Byte fallback crossing pieces: `{byte_fallback_crossing_pieces}`",
        f"Private samples: `{samples_out.as_posix()}`",
        "",
        "This audit checks whether detected protected-span boundaries align with",
        "SentencePiece token boundaries. Logical sidecar protection is only strong",
        "enough for masking/copy policies if span edges are token-boundary aligned.",
        "",
        "## Split Summary",
        "",
        "| Split | Lines | Protected spans | Protected edges | Aligned edges | Misaligned edges | Edge alignment rate | Crossing pieces |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in stats_rows:
        lines.append(
            f"| {row.split} | {row.lines} | {row.protected_spans} | "
            f"{row.protected_edges} | {row.aligned_edges} | {row.misaligned_edges} | "
            f"{_fmt(row.edge_alignment_rate)} | {row.crossing_pieces} |"
        )

    lines.extend(
        [
            "",
            "## Route Summary",
            "",
            "| Split | Route | Spans | Misaligned edges | Crossing pieces |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in stats_rows:
        routes = sorted(set(row.route_spans) | set(row.route_misaligned_edges) | set(row.route_crossing_pieces))
        for route in routes:
            lines.append(
                f"| {row.split} | `{route}` | {row.route_spans[route]} | "
                f"{row.route_misaligned_edges[route]} | {row.route_crossing_pieces[route]} |"
            )

    lines.extend(
        [
            "",
            "## Gate",
            "",
            "For sidecar/logical protected spans to be a strong tokenizer contract,",
            "the preferred result is:",
            "",
            "```text",
            "misaligned_edges = 0",
            "crossing_pieces = 0",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit SP token alignment to protected span edges.")
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument("--split", action="append", choices=["train", "valid", "test"])
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument(
        "--sp-passthrough-route",
        action="append",
        default=[],
        help="Route treated as SP passthrough for isolated-boundary simulation.",
    )
    parser.add_argument(
        "--isolate-sp-passthrough-routes",
        action="store_true",
        help="Simulate SP encoding each passthrough protected route as a separate segment.",
    )
    parser.add_argument(
        "--byte-fallback-crossing-pieces",
        action="store_true",
        help="Simulate replacing SP pieces that cross protected edges with byte tokens.",
    )
    parser.add_argument(
        "--samples-out",
        default="artifacts/private/v2_0_protected_boundary_alignment_samples.jsonl",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_protected_boundary_alignment_audit.md",
    )
    args = parser.parse_args(argv)

    split_dir = Path(args.split_dir)
    sp_model = Path(args.sp_model)
    processor = load_sp_processor(sp_model)
    splits = args.split or ["valid", "test"]
    passthrough_routes = set(args.sp_passthrough_route)
    stats_rows: list[AlignmentStats] = []
    samples: list[dict[str, object]] = []
    for split in splits:
        stats, split_samples = audit_split(
            split=split,
            path=split_dir / f"{split}.txt",
            processor=processor,
            max_lines=args.max_lines,
            sample_limit=max(0, args.sample_limit - len(samples)),
            progress=args.progress,
            passthrough_routes=passthrough_routes,
            isolate_sp_passthrough_routes=args.isolate_sp_passthrough_routes,
            byte_fallback_crossing_pieces=args.byte_fallback_crossing_pieces,
        )
        stats_rows.append(stats)
        samples.extend(split_samples)

    samples_out = Path(args.samples_out)
    write_samples(samples_out, samples[: args.sample_limit])
    report = format_report(
        split_dir=split_dir,
        sp_model=sp_model,
        stats_rows=stats_rows,
        samples_out=samples_out,
        passthrough_routes=passthrough_routes,
        isolate_sp_passthrough_routes=args.isolate_sp_passthrough_routes,
        byte_fallback_crossing_pieces=args.byte_fallback_crossing_pieces,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    print(f"wrote_samples: {samples_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
