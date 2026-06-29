from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import math
import sys
from pathlib import Path

import sentencepiece as spm
from sentencepiece import sentencepiece_model_pb2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402

SP_WORD_START = "\u2581"
META_PIECES = {"<unk>", "<s>", "</s>", "<pad>"}


@dataclass
class PieceStats:
    count: int = 0
    crossing_count: int = 0

    @property
    def crossing_rate(self) -> float:
        return self.crossing_count / self.count if self.count else 0.0


@dataclass(frozen=True)
class Segment:
    surface: str
    soft_boundaries: tuple[int, ...]


@dataclass(frozen=True)
class Adjustment:
    piece: str
    original_score: float
    adjusted_score: float
    count: int
    crossing_count: int
    crossing_rate: float

    @property
    def delta(self) -> float:
        return self.adjusted_score - self.original_score


def save_stats(stats: dict[str, PieceStats], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        piece: {"count": row.count, "crossing_count": row.crossing_count}
        for piece, row in sorted(stats.items())
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_stats(path: Path) -> dict[str, PieceStats]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        piece: PieceStats(
            count=int(row.get("count", 0)),
            crossing_count=int(row.get("crossing_count", 0)),
        )
        for piece, row in payload.items()
    }


def piece_surface(piece: str) -> str:
    if piece.startswith(SP_WORD_START):
        return piece[len(SP_WORD_START) :]
    return piece


def crosses_boundary(start: int, end: int, boundaries: tuple[int, ...]) -> bool:
    return any(start < boundary < end for boundary in boundaries)


def normal_segments(text: str, tokenizer: TurkishTokenizer) -> list[Segment]:
    pieces = analyze_line(text, tokenizer)
    segments: list[Segment] = []
    surface = ""
    boundaries: list[int] = []

    def flush() -> None:
        nonlocal surface, boundaries
        if surface:
            segments.append(Segment(surface=surface, soft_boundaries=tuple(boundaries)))
        surface = ""
        boundaries = []

    for piece in pieces:
        if piece.kind == "whitespace":
            flush()
            continue
        if piece.kind.startswith("protected:"):
            flush()
            continue
        if piece.kind == "apostrophe":
            flush()
            continue
        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            continue
        if piece.boundary_before == "soft":
            boundaries.append(len(surface))
            surface += piece.surface
            continue
        if piece.boundary_before == "hard":
            flush()
            surface = piece.surface
            continue
        surface += piece.surface
    flush()
    return segments


def collect_piece_stats(
    *,
    train_path: Path,
    processor: spm.SentencePieceProcessor,
    max_lines: int | None,
    progress: int,
) -> tuple[dict[str, PieceStats], int, int]:
    stats: dict[str, PieceStats] = {}
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    lines = 0
    alignment_failures = 0
    segments_seen = 0
    with train_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if max_lines is not None and lines >= max_lines:
                break
            lines += 1
            text = raw_line.rstrip("\n")
            for segment in normal_segments(text, tokenizer):
                segments_seen += 1
                position = 0
                for piece in processor.EncodeAsPieces(segment.surface):
                    if piece in META_PIECES:
                        continue
                    surface = piece_surface(piece)
                    if not surface:
                        continue
                    end = position + len(surface)
                    if segment.surface[position:end] != surface:
                        found = segment.surface.find(surface, position)
                        if found < 0:
                            alignment_failures += 1
                            break
                        position = found
                        end = position + len(surface)
                    row = stats.setdefault(piece, PieceStats())
                    row.count += 1
                    if crosses_boundary(position, end, segment.soft_boundaries):
                        row.crossing_count += 1
                    position = end
            if progress > 0 and lines % progress == 0:
                print(
                    f"scanned {lines:,} lines pieces={len(stats):,} "
                    f"alignment_failures={alignment_failures:,}",
                    flush=True,
                )
    return stats, lines, alignment_failures


def load_model(path: Path) -> sentencepiece_model_pb2.ModelProto:
    model = sentencepiece_model_pb2.ModelProto()
    model.ParseFromString(path.read_bytes())
    return model


def save_vocab(model: sentencepiece_model_pb2.ModelProto, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for piece in model.pieces:
            handle.write(f"{piece.piece}\t{piece.score}\n")


def adjust_model_scores(
    model: sentencepiece_model_pb2.ModelProto,
    stats: dict[str, PieceStats],
    *,
    penalty_lambda: float,
    min_count: int,
    min_crossing_count: int,
    min_crossing_rate: float,
    min_surface_len: int,
    max_penalty: float,
    penalty_mode: str,
) -> list[Adjustment]:
    adjustments: list[Adjustment] = []
    max_crossing_count = max((row.crossing_count for row in stats.values()), default=1)
    for piece in model.pieces:
        if piece.piece in META_PIECES:
            continue
        surface = piece_surface(piece.piece)
        if len(surface) < min_surface_len:
            continue
        row = stats.get(piece.piece)
        if row is None or row.count < min_count:
            continue
        if row.crossing_count < min_crossing_count:
            continue
        if row.crossing_rate < min_crossing_rate:
            continue
        original_score = piece.score
        if penalty_mode == "rate":
            penalty_basis = row.crossing_rate
        elif penalty_mode == "mass":
            penalty_basis = row.crossing_count / max_crossing_count
        elif penalty_mode == "hybrid":
            penalty_basis = row.crossing_rate * math.sqrt(
                row.crossing_count / max_crossing_count
            )
        else:
            raise ValueError(f"unknown penalty_mode: {penalty_mode}")
        penalty = min(max_penalty, penalty_lambda * penalty_basis)
        piece.score = original_score - penalty
        adjustments.append(
            Adjustment(
                piece=piece.piece,
                original_score=original_score,
                adjusted_score=piece.score,
                count=row.count,
                crossing_count=row.crossing_count,
                crossing_rate=row.crossing_rate,
            )
        )
    adjustments.sort(key=lambda row: (row.crossing_rate, row.count), reverse=True)
    return adjustments


def format_report(
    *,
    source_model: Path,
    train_path: Path,
    out_model: Path,
    out_vocab: Path,
    lines: int,
    stats: dict[str, PieceStats],
    adjustments: list[Adjustment],
    alignment_failures: int,
    penalty_lambda: float,
    min_count: int,
    min_crossing_count: int,
    min_crossing_rate: float,
    min_surface_len: int,
    max_penalty: float,
    penalty_mode: str,
    top_n: int,
) -> str:
    crossing_pieces = sum(1 for row in stats.values() if row.crossing_count > 0)
    lines_out = [
        "# v2.0 Score-Shifted SentencePiece Model",
        "",
        f"Source model: `{source_model.as_posix()}`",
        f"Train path: `{train_path.as_posix()}`",
        f"Output model: `{out_model.as_posix()}`",
        f"Output vocab: `{out_vocab.as_posix()}`",
        "",
        "This is a train-only post-hoc Unigram score-shift probe. It does not",
        "change the vocabulary or add runtime boundary markers. It lowers scores",
        "for pieces that frequently cross custom-teacher soft morphology",
        "boundaries in the train split.",
        "",
        "## Parameters",
        "",
        "| Parameter | Value |",
        "| --- | ---: |",
        f"| penalty_lambda | {penalty_lambda:.6f} |",
        f"| penalty_mode | {penalty_mode} |",
        f"| min_count | {min_count} |",
        f"| min_crossing_count | {min_crossing_count} |",
        f"| min_crossing_rate | {min_crossing_rate:.6f} |",
        f"| min_surface_len | {min_surface_len} |",
        f"| max_penalty | {max_penalty:.6f} |",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| scanned lines | {lines} |",
        f"| observed pieces | {len(stats)} |",
        f"| pieces with crossing evidence | {crossing_pieces} |",
        f"| adjusted pieces | {len(adjustments)} |",
        f"| alignment failures | {alignment_failures} |",
        "",
        "## Top Adjusted Pieces",
        "",
        "| Piece | Count | Crossing count | Crossing rate | Score delta |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in adjustments[:top_n]:
        lines_out.append(
            f"| `{row.piece}` | {row.count} | {row.crossing_count} | "
            f"{row.crossing_rate:.6f} | {row.delta:.6f} |"
        )
    lines_out.extend(
        [
            "",
            "## Next",
            "",
            "Evaluate this model with the finite protected wrapper. Continue only if",
            "it improves normal-text morphology F1 without materially increasing",
            "tokens/raw byte or breaking roundtrip/protected invariants.",
        ]
    )
    return "\n".join(lines_out) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Create a score-shifted SP model from train-only morph crossing stats.",
    )
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--train",
        default=(
            "artifacts/private/v1_8_local_lm_probe/"
            "celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/"
            "filtered_split/train.txt"
        ),
    )
    parser.add_argument("--out-model", required=True)
    parser.add_argument("--out-vocab", required=True)
    parser.add_argument("--report-out", required=True)
    parser.add_argument("--penalty-lambda", type=float, default=0.5)
    parser.add_argument(
        "--penalty-mode",
        choices=["rate", "mass", "hybrid"],
        default="rate",
    )
    parser.add_argument("--min-count", type=int, default=20)
    parser.add_argument("--min-crossing-count", type=int, default=1)
    parser.add_argument("--min-crossing-rate", type=float, default=0.50)
    parser.add_argument("--min-surface-len", type=int, default=2)
    parser.add_argument("--max-penalty", type=float, default=2.0)
    parser.add_argument("--stats-in")
    parser.add_argument("--stats-out")
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument("--top-n", type=int, default=40)
    args = parser.parse_args(argv)

    sp_model = Path(args.sp_model)
    train_path = Path(args.train)
    out_model = Path(args.out_model)
    out_vocab = Path(args.out_vocab)
    report_out = Path(args.report_out)
    out_model.parent.mkdir(parents=True, exist_ok=True)
    out_vocab.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)

    if args.stats_in:
        stats = load_stats(Path(args.stats_in))
        lines = 0
        alignment_failures = 0
    else:
        processor = spm.SentencePieceProcessor(model_file=str(sp_model))
        stats, lines, alignment_failures = collect_piece_stats(
            train_path=train_path,
            processor=processor,
            max_lines=args.max_lines,
            progress=args.progress,
        )
        if args.stats_out:
            save_stats(stats, Path(args.stats_out))
    model = load_model(sp_model)
    adjustments = adjust_model_scores(
        model,
        stats,
        penalty_lambda=args.penalty_lambda,
        min_count=args.min_count,
        min_crossing_count=args.min_crossing_count,
        min_crossing_rate=args.min_crossing_rate,
        min_surface_len=args.min_surface_len,
        max_penalty=args.max_penalty,
        penalty_mode=args.penalty_mode,
    )
    out_model.write_bytes(model.SerializeToString())
    save_vocab(model, out_vocab)
    report = format_report(
        source_model=sp_model,
        train_path=train_path,
        out_model=out_model,
        out_vocab=out_vocab,
        lines=lines,
        stats=stats,
        adjustments=adjustments,
        alignment_failures=alignment_failures,
        penalty_lambda=args.penalty_lambda,
        min_count=args.min_count,
        min_crossing_count=args.min_crossing_count,
        min_crossing_rate=args.min_crossing_rate,
        min_surface_len=args.min_surface_len,
        max_penalty=args.max_penalty,
        penalty_mode=args.penalty_mode,
        top_n=args.top_n,
    )
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_model: {out_model}")
    print(f"wrote_vocab: {out_vocab}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
