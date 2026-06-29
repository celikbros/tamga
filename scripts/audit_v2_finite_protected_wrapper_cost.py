from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    encode_protected_surface,
    load_sp_processor,
    processor_encode_ids_lossless_or_byte_fallback,
    processor_piece_size,
    selected_piece_strings,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class LineAudit:
    split: str
    line_no: int
    text: str
    raw_bytes: int
    baseline_sp_tokens: int
    finite_tokens: int
    segment_sp_tokens: int
    protected_piece_tokens: int
    protected_sp_passthrough_tokens: int
    protected_byte_tokens: int
    hard_suffix_tokens: int
    apostrophe_tokens: int
    protected_surface_bytes: int
    protected_pieces: int
    segment_count: int
    route_counts: Counter[str]
    route_bytes: Counter[str]
    route_protected_tokens: Counter[str]
    route_sp_tokens: Counter[str]
    eos_tokens: int

    @property
    def token_delta(self) -> int:
        return self.finite_tokens - self.baseline_sp_tokens

    @property
    def protected_model_tokens(self) -> int:
        return (
            self.protected_piece_tokens
            + self.protected_sp_passthrough_tokens
            + self.protected_byte_tokens
        )


@dataclass
class SplitAudit:
    split: str
    lines: int = 0
    raw_bytes: int = 0
    baseline_sp_tokens: int = 0
    finite_tokens: int = 0
    segment_sp_tokens: int = 0
    protected_piece_tokens: int = 0
    protected_sp_passthrough_tokens: int = 0
    protected_byte_tokens: int = 0
    hard_suffix_tokens: int = 0
    apostrophe_tokens: int = 0
    protected_surface_bytes: int = 0
    protected_pieces: int = 0
    segment_count: int = 0
    route_counts: Counter[str] = field(default_factory=Counter)
    route_bytes: Counter[str] = field(default_factory=Counter)
    route_protected_tokens: Counter[str] = field(default_factory=Counter)
    route_sp_tokens: Counter[str] = field(default_factory=Counter)
    eos_tokens: int = 0
    top_delta_lines: list[LineAudit] = field(default_factory=list)

    @property
    def token_delta(self) -> int:
        return self.finite_tokens - self.baseline_sp_tokens

    @property
    def baseline_tokens_per_byte(self) -> float:
        return self.baseline_sp_tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def finite_tokens_per_byte(self) -> float:
        return self.finite_tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def delta_tokens_per_byte(self) -> float:
        return self.token_delta / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def relative_delta(self) -> float:
        return self.token_delta / self.baseline_sp_tokens if self.baseline_sp_tokens else 0.0

    @property
    def protected_bytes_share(self) -> float:
        return self.protected_surface_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def protected_model_tokens(self) -> int:
        return (
            self.protected_piece_tokens
            + self.protected_sp_passthrough_tokens
            + self.protected_byte_tokens
        )

    @property
    def protected_tokens_per_protected_byte(self) -> float:
        return (
            self.protected_model_tokens / self.protected_surface_bytes
            if self.protected_surface_bytes
            else 0.0
        )


def _sp_piece_count(processor, text: str) -> int:
    return len(processor.EncodeAsIds(text)) if text else 0


def _eos_token_count(processor) -> int:
    eos_id = processor.eos_id() if hasattr(processor, "eos_id") else -1
    return 1 if int(eos_id) >= 0 else 0


def audit_line(
    *,
    split: str,
    line_no: int,
    text: str,
    processor,
    selected_pieces: list[str],
    tokenizer: TurkishTokenizer,
    include_eos: bool = True,
    numeric_sp_passthrough: bool = False,
    sp_passthrough_routes: set[str] | None = None,
) -> LineAudit:
    pieces = analyze_line(text, tokenizer)
    baseline_sp_tokens = len(processor.EncodeAsIds(text))
    raw_bytes = len(text.encode("utf-8"))
    eos_tokens = _eos_token_count(processor) if include_eos else 0

    segment = ""
    segment_sp_tokens = 0
    segment_count = 0
    protected_piece_tokens = 0
    protected_sp_passthrough_tokens = 0
    protected_byte_tokens = 0
    hard_suffix_tokens = 0
    apostrophe_tokens = 0
    protected_surface_bytes = 0
    protected_piece_count = 0
    route_counts: Counter[str] = Counter()
    route_bytes: Counter[str] = Counter()
    route_protected_tokens: Counter[str] = Counter()
    route_sp_tokens: Counter[str] = Counter()
    byte_offset: int | None = None
    passthrough_routes = set(sp_passthrough_routes or set())
    if numeric_sp_passthrough:
        passthrough_routes.add("numeric_like")

    def flush() -> None:
        nonlocal segment, segment_sp_tokens, segment_count
        if not segment:
            return
        segment_sp_tokens += _sp_piece_count(processor, segment)
        segment_count += 1
        segment = ""

    for piece in pieces:
        if piece.kind == "whitespace":
            flush()
            continue

        if piece.kind.startswith("protected:"):
            flush()
            route = piece.kind.removeprefix("protected:")
            route_counts[route] += 1
            protected_piece_count += 1
            surface_bytes = len(piece.surface.encode("utf-8"))
            protected_surface_bytes += surface_bytes
            if route in passthrough_routes:
                if byte_offset is None:
                    byte_offset = processor_piece_size(processor) + len(selected_pieces)
                segment_ids, byte_tokens = processor_encode_ids_lossless_or_byte_fallback(
                    processor,
                    piece.surface,
                    byte_offset=byte_offset,
                )
                sp_tokens = len(segment_ids) - byte_tokens
                protected_sp_passthrough_tokens += sp_tokens
                protected_byte_tokens += byte_tokens
                route_protected_tokens[route] += len(segment_ids)
            else:
                piece_tokens, byte_tokens = encode_protected_surface(
                    piece.surface,
                    selected_pieces,
                )
                protected_piece_tokens += piece_tokens
                protected_byte_tokens += byte_tokens
                route_protected_tokens[route] += piece_tokens + byte_tokens
            route_bytes[route] += surface_bytes
            route_sp_tokens[route] += _sp_piece_count(processor, piece.surface)
            continue

        if piece.kind == "apostrophe":
            flush()
            apostrophe_tokens += _sp_piece_count(processor, piece.surface)
            continue

        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            hard_suffix_tokens += _sp_piece_count(processor, piece.surface)
            continue

        if piece.boundary_before == "hard":
            flush()
            segment = piece.surface
            continue

        segment += piece.surface

    flush()
    finite_tokens = (
        segment_sp_tokens
        + protected_piece_tokens
        + protected_sp_passthrough_tokens
        + protected_byte_tokens
        + hard_suffix_tokens
        + apostrophe_tokens
        + eos_tokens
    )
    baseline_sp_tokens += eos_tokens
    return LineAudit(
        split=split,
        line_no=line_no,
        text=text,
        raw_bytes=raw_bytes,
        baseline_sp_tokens=baseline_sp_tokens,
        finite_tokens=finite_tokens,
        segment_sp_tokens=segment_sp_tokens,
        protected_piece_tokens=protected_piece_tokens,
        protected_sp_passthrough_tokens=protected_sp_passthrough_tokens,
        protected_byte_tokens=protected_byte_tokens,
        hard_suffix_tokens=hard_suffix_tokens,
        apostrophe_tokens=apostrophe_tokens,
        protected_surface_bytes=protected_surface_bytes,
        protected_pieces=protected_piece_count,
        segment_count=segment_count,
        route_counts=route_counts,
        route_bytes=route_bytes,
        route_protected_tokens=route_protected_tokens,
        route_sp_tokens=route_sp_tokens,
        eos_tokens=eos_tokens,
    )


def _keep_top_delta(rows: list[LineAudit], audit: LineAudit, *, limit: int) -> list[LineAudit]:
    if limit <= 0:
        return []
    rows.append(audit)
    rows.sort(key=lambda row: (row.token_delta, row.protected_surface_bytes), reverse=True)
    return rows[:limit]


def audit_split(
    *,
    split: str,
    path: Path,
    processor,
    selected_pieces: list[str],
    max_lines: int | None,
    top_examples: int,
    progress: int,
    numeric_sp_passthrough: bool,
    sp_passthrough_routes: set[str],
) -> SplitAudit:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    stats = SplitAudit(split=split)
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            if max_lines is not None and stats.lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            audit = audit_line(
                split=split,
                line_no=line_no,
                text=text,
                processor=processor,
                selected_pieces=selected_pieces,
                tokenizer=tokenizer,
                numeric_sp_passthrough=numeric_sp_passthrough,
                sp_passthrough_routes=sp_passthrough_routes,
            )
            stats.lines += 1
            stats.raw_bytes += audit.raw_bytes
            stats.baseline_sp_tokens += audit.baseline_sp_tokens
            stats.finite_tokens += audit.finite_tokens
            stats.segment_sp_tokens += audit.segment_sp_tokens
            stats.protected_piece_tokens += audit.protected_piece_tokens
            stats.protected_sp_passthrough_tokens += audit.protected_sp_passthrough_tokens
            stats.protected_byte_tokens += audit.protected_byte_tokens
            stats.hard_suffix_tokens += audit.hard_suffix_tokens
            stats.apostrophe_tokens += audit.apostrophe_tokens
            stats.protected_surface_bytes += audit.protected_surface_bytes
            stats.protected_pieces += audit.protected_pieces
            stats.segment_count += audit.segment_count
            stats.route_counts.update(audit.route_counts)
            stats.route_bytes.update(audit.route_bytes)
            stats.route_protected_tokens.update(audit.route_protected_tokens)
            stats.route_sp_tokens.update(audit.route_sp_tokens)
            stats.eos_tokens += audit.eos_tokens
            stats.top_delta_lines = _keep_top_delta(
                stats.top_delta_lines,
                audit,
                limit=top_examples,
            )
            if progress > 0 and stats.lines % progress == 0:
                print(
                    f"audited {split} {stats.lines:,} lines "
                    f"finite_tpb={stats.finite_tokens_per_byte:.6f}",
                    flush=True,
                )
    return stats


def write_private_examples(path: Path, audits: list[SplitAudit]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for split in audits:
            for row in split.top_delta_lines:
                handle.write(
                    json.dumps(
                        {
                            "split": row.split,
                            "line_no": row.line_no,
                            "text": row.text,
                            "raw_bytes": row.raw_bytes,
                            "baseline_sp_tokens": row.baseline_sp_tokens,
                            "finite_tokens": row.finite_tokens,
                            "token_delta": row.token_delta,
                            "protected_pieces": row.protected_pieces,
                            "protected_surface_bytes": row.protected_surface_bytes,
                            "protected_piece_tokens": row.protected_piece_tokens,
                            "protected_sp_passthrough_tokens": (
                                row.protected_sp_passthrough_tokens
                            ),
                            "protected_byte_tokens": row.protected_byte_tokens,
                            "hard_suffix_tokens": row.hard_suffix_tokens,
                            "apostrophe_tokens": row.apostrophe_tokens,
                            "eos_tokens": row.eos_tokens,
                            "route_counts": dict(row.route_counts),
                            "route_bytes": dict(row.route_bytes),
                            "route_protected_tokens": dict(row.route_protected_tokens),
                            "route_sp_tokens": dict(row.route_sp_tokens),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )


def _fmt(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def _route_table(audits: list[SplitAudit], *, top_n: int) -> list[str]:
    counts: Counter[str] = Counter()
    bytes_by_route: Counter[str] = Counter()
    protected_tokens: Counter[str] = Counter()
    sp_tokens: Counter[str] = Counter()
    for audit in audits:
        counts.update(audit.route_counts)
        bytes_by_route.update(audit.route_bytes)
        protected_tokens.update(audit.route_protected_tokens)
        sp_tokens.update(audit.route_sp_tokens)
    lines = [
        "## Protected Route Cost",
        "",
        "| Route | Count | Bytes | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for route, count in counts.most_common(top_n):
        byte_count = bytes_by_route[route]
        protected = protected_tokens[route]
        sp = sp_tokens[route]
        lines.append(
            f"| `{route}` | {count} | {byte_count} | {protected} | {sp} | "
            f"{protected - sp} | {_fmt(protected / byte_count if byte_count else 0.0)} | "
            f"{_fmt(sp / byte_count if byte_count else 0.0)} |"
        )
    if not counts:
        lines.append("| _none_ | 0 | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 |")
    return lines


def format_report(
    *,
    split_dir: Path,
    sp_model: Path,
    selected_pieces: Path,
    audits: list[SplitAudit],
    examples_out: Path,
    numeric_sp_passthrough: bool,
    sp_passthrough_routes: set[str],
) -> str:
    passthrough_routes = set(sp_passthrough_routes)
    if numeric_sp_passthrough:
        passthrough_routes.add("numeric_like")
    lines = [
        "# v2.0 Finite Protected Wrapper Cost Audit",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"SP model: `{sp_model.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces.as_posix()}`",
        f"Numeric protected SP passthrough: `{numeric_sp_passthrough}`",
        f"SP passthrough routes: `{', '.join(sorted(passthrough_routes)) or 'none'}`",
        f"Private top-delta examples: `{examples_out.as_posix()}`",
        "",
        "This audit decomposes the token-pressure cost of the finite protected",
        "wrapper before any new MorphBPE/constrained-tokenizer work.",
        "",
        "## Split Summary",
        "",
        "| Split | Lines | Raw bytes | SP tokens/raw byte | Finite tokens/raw byte | Delta tokens/raw byte | Relative delta | Protected bytes share | Protected tokens/protected byte |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for audit in audits:
        lines.append(
            f"| {audit.split} | {audit.lines} | {audit.raw_bytes} | "
            f"{_fmt(audit.baseline_tokens_per_byte)} | "
            f"{_fmt(audit.finite_tokens_per_byte)} | "
            f"{_fmt(audit.delta_tokens_per_byte)} | "
            f"{_fmt(audit.relative_delta)} | "
            f"{_fmt(audit.protected_bytes_share)} | "
            f"{_fmt(audit.protected_tokens_per_protected_byte)} |"
        )

    lines.extend(
        [
            "",
            "## Finite Token Components",
            "",
            "| Split | Segment SP tokens | Protected piece tokens | Protected SP passthrough tokens | Protected byte tokens | Hard suffix tokens | Apostrophe tokens | EOS tokens | Segment count | Protected pieces |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for audit in audits:
        lines.append(
            f"| {audit.split} | {audit.segment_sp_tokens} | "
            f"{audit.protected_piece_tokens} | "
            f"{audit.protected_sp_passthrough_tokens} | "
            f"{audit.protected_byte_tokens} | "
            f"{audit.hard_suffix_tokens} | {audit.apostrophe_tokens} | "
            f"{audit.eos_tokens} | {audit.segment_count} | {audit.protected_pieces} |"
        )

    lines.extend(["", "## Highest Public Delta Lines", ""])
    lines.extend(
        [
            "Raw text is omitted from this public report. Full private examples are",
            "written to the JSONL path above.",
            "",
            "| Split | Line | Raw bytes | SP tokens | Finite tokens | Delta | Protected pieces | Protected bytes | Routes |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for audit in audits:
        for row in audit.top_delta_lines:
            routes = ", ".join(f"{key}:{value}" for key, value in row.route_counts.most_common())
            lines.append(
                f"| {row.split} | {row.line_no} | {row.raw_bytes} | "
                f"{row.baseline_sp_tokens} | {row.finite_tokens} | "
                f"{row.token_delta} | {row.protected_pieces} | "
                f"{row.protected_surface_bytes} | `{routes}` |"
            )

    lines.extend([""])
    lines.extend(_route_table(audits, top_n=20))
    lines.extend(
        [
            "",
            "## Interpretation Gate",
            "",
            "If protected bytes are a small share of the corpus but relative token",
            "delta is large, the wrapper needs redesign before MorphBPE work.",
            "If cost is concentrated in a few route kinds, optimize those routes",
            "first.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit finite protected wrapper token-pressure cost.")
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--split", action="append", choices=["train", "valid", "test"])
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--top-examples", type=int, default=10)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument(
        "--numeric-sp-passthrough",
        action="store_true",
        help="Encode numeric-like protected spans with SP while preserving their logical route.",
    )
    parser.add_argument(
        "--sp-passthrough-route",
        action="append",
        default=[],
        help="Protected route to encode with SP while preserving logical route; repeatable.",
    )
    parser.add_argument(
        "--examples-out",
        default="artifacts/private/v2_0_finite_protected_wrapper_cost_top_delta.jsonl",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_finite_protected_wrapper_cost_audit.md",
    )
    args = parser.parse_args(argv)

    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")

    split_dir = Path(args.split_dir)
    sp_model = Path(args.sp_model)
    selected_pieces_path = Path(args.selected_pieces)
    splits = args.split or ["train", "valid", "test"]
    processor = load_sp_processor(sp_model)
    selected = selected_piece_strings(selected_pieces_path)
    sp_passthrough_routes = set(args.sp_passthrough_route)

    audits = [
        audit_split(
            split=split,
            path=split_dir / f"{split}.txt",
            processor=processor,
            selected_pieces=selected,
            max_lines=args.max_lines,
            top_examples=args.top_examples,
            progress=args.progress,
            numeric_sp_passthrough=args.numeric_sp_passthrough,
            sp_passthrough_routes=sp_passthrough_routes,
        )
        for split in splits
    ]

    examples_out = Path(args.examples_out)
    write_private_examples(examples_out, audits)
    report = format_report(
        split_dir=split_dir,
        sp_model=sp_model,
        selected_pieces=selected_pieces_path,
        audits=audits,
        examples_out=examples_out,
        numeric_sp_passthrough=args.numeric_sp_passthrough,
        sp_passthrough_routes=sp_passthrough_routes,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_examples: {examples_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
