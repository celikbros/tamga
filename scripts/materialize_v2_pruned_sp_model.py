from __future__ import annotations

from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_v2_finite_protected_sp64_intrinsic import load_sp_processor  # noqa: E402
from scripts.materialize_v2_score_shifted_sp_model import (  # noqa: E402
    META_PIECES,
    PieceStats,
    collect_piece_stats,
    load_model,
    load_stats,
    piece_surface,
    save_stats,
    save_vocab,
)


@dataclass(frozen=True)
class PrunedPiece:
    piece: str
    count: int
    crossing_count: int
    crossing_rate: float
    original_score: float
    new_score: float


def in_scope(piece: str, scope: str) -> bool:
    is_word_start = piece.startswith("\u2581")
    if scope == "all":
        return True
    if scope == "word_start":
        return is_word_start
    if scope == "non_word_start":
        return not is_word_start
    raise ValueError(f"unknown piece scope: {scope}")


def select_and_floor_pieces(
    model,
    stats: dict[str, PieceStats],
    *,
    min_count: int,
    min_crossing_count: int,
    min_crossing_rate: float,
    min_surface_len: int,
    piece_scope: str,
    score_floor: float,
) -> list[PrunedPiece]:
    selected: list[PrunedPiece] = []
    for piece in model.pieces:
        piece_name = piece.piece
        if piece_name in META_PIECES:
            continue
        if not in_scope(piece_name, piece_scope):
            continue
        surface = piece_surface(piece_name)
        if len(surface) < min_surface_len:
            continue
        row = stats.get(piece_name)
        if row is None:
            continue
        if row.count < min_count:
            continue
        if row.crossing_count < min_crossing_count:
            continue
        if row.crossing_rate < min_crossing_rate:
            continue
        original_score = float(piece.score)
        new_score = min(original_score, score_floor)
        if not math.isclose(original_score, new_score, rel_tol=0.0, abs_tol=1e-9):
            piece.score = new_score
        selected.append(
            PrunedPiece(
                piece=piece_name,
                count=row.count,
                crossing_count=row.crossing_count,
                crossing_rate=row.crossing_rate,
                original_score=original_score,
                new_score=new_score,
            )
        )
    return selected


def format_report(
    *,
    source_model: Path,
    stats_path: Path | None,
    out_model: Path,
    out_vocab: Path,
    selected: list[PrunedPiece],
    params: dict[str, str],
) -> str:
    lines = [
        "# v2.0 Pruned/Floored SP Model",
        "",
        f"Source model: `{source_model.as_posix()}`",
        f"Stats path: `{stats_path.as_posix() if stats_path else 'computed'}`",
        f"Output model: `{out_model.as_posix()}`",
        f"Output vocab: `{out_vocab.as_posix()}`",
        "",
        "This probe floors train-side high-crossing pieces. It is an inventory",
        "diagnostic over a standard SentencePiece artifact, not a production",
        "tokenizer claim.",
        "",
        "## Parameters",
        "",
        "| Parameter | Value |",
        "| --- | ---: |",
    ]
    for key, value in params.items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| selected pieces | {len(selected)} |",
            "",
            "## Top Selected Pieces",
            "",
            "| Piece | Count | Crossing count | Crossing rate | Original score | New score |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    top = sorted(
        selected,
        key=lambda row: (row.crossing_count, row.count),
        reverse=True,
    )[:80]
    for row in top:
        safe_piece = row.piece.replace("|", "\\|")
        lines.append(
            f"| `{safe_piece}` | {row.count} | {row.crossing_count} | "
            f"{row.crossing_rate:.6f} | {row.original_score:.6f} | "
            f"{row.new_score:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "Continue only if deployed crossings fall and F1/token pressure moves to",
            "a better frontier than score-only distillation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Floor high-crossing SentencePiece pieces using train-side stats."
    )
    parser.add_argument(
        "--source-model",
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
    parser.add_argument("--stats-in")
    parser.add_argument("--stats-out")
    parser.add_argument("--min-count", type=int, default=20)
    parser.add_argument("--min-crossing-count", type=int, default=20)
    parser.add_argument("--min-crossing-rate", type=float, default=0.70)
    parser.add_argument("--min-surface-len", type=int, default=2)
    parser.add_argument(
        "--piece-scope",
        choices=["all", "word_start", "non_word_start"],
        default="all",
    )
    parser.add_argument("--score-floor", type=float, default=-30.0)
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--out-model", required=True)
    parser.add_argument("--out-vocab", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    source_model = Path(args.source_model)
    model = load_model(source_model)

    stats_path = Path(args.stats_in) if args.stats_in else None
    if stats_path is not None:
        stats = load_stats(stats_path)
    else:
        processor = load_sp_processor(source_model)
        stats, _lines, _failures = collect_piece_stats(
            train_path=Path(args.train),
            processor=processor,
            max_lines=None,
            progress=args.progress,
        )
        if args.stats_out:
            save_stats(stats, Path(args.stats_out))

    selected = select_and_floor_pieces(
        model,
        stats,
        min_count=args.min_count,
        min_crossing_count=args.min_crossing_count,
        min_crossing_rate=args.min_crossing_rate,
        min_surface_len=args.min_surface_len,
        piece_scope=args.piece_scope,
        score_floor=args.score_floor,
    )

    out_model = Path(args.out_model)
    out_vocab = Path(args.out_vocab)
    report_out = Path(args.report_out)
    out_model.parent.mkdir(parents=True, exist_ok=True)
    out_vocab.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    out_model.write_bytes(model.SerializeToString())
    save_vocab(model, out_vocab)
    report = format_report(
        source_model=source_model,
        stats_path=stats_path,
        out_model=out_model,
        out_vocab=out_vocab,
        selected=selected,
        params={
            "min_count": str(args.min_count),
            "min_crossing_count": str(args.min_crossing_count),
            "min_crossing_rate": f"{args.min_crossing_rate:.6f}",
            "min_surface_len": str(args.min_surface_len),
            "piece_scope": args.piece_scope,
            "score_floor": f"{args.score_floor:.6f}",
        },
    )
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_model: {out_model}")
    print(f"wrote_vocab: {out_vocab}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
