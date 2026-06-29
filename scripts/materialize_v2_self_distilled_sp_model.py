from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

from sentencepiece import SentencePieceProcessor, sentencepiece_model_pb2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_score_shifted_sp_model import normal_segments  # noqa: E402
from scripts.materialize_v2_teacher_distilled_sp_model import (  # noqa: E402
    apply_distilled_scores,
    save_vocab,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class SelfDistillStats:
    lines: int
    segments: int
    counted_tokens: int
    counted_piece_types: int
    changed_scores: int
    score_floor: float


def load_model(path: Path) -> sentencepiece_model_pb2.ModelProto:
    model = sentencepiece_model_pb2.ModelProto()
    model.ParseFromString(path.read_bytes())
    return model


def collect_official_sp_counts(
    *,
    train_path: Path,
    model_path: Path,
    max_lines: int | None,
    progress: int,
) -> tuple[Counter[str], int, int]:
    processor = SentencePieceProcessor(model_file=str(model_path))
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    counts: Counter[str] = Counter()
    lines = 0
    segments = 0

    with train_path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if max_lines is not None and lines >= max_lines:
                break
            lines += 1
            text = raw.rstrip("\n")
            for segment in normal_segments(text, tokenizer):
                pieces = processor.encode(segment.surface, out_type=str)
                counts.update(str(piece) for piece in pieces)
                segments += 1
            if progress > 0 and lines % progress == 0:
                print(
                    f"self-distilled {lines:,} lines segments={segments:,} "
                    f"piece_types={len(counts):,}",
                    flush=True,
                )

    return counts, lines, segments


def format_report(
    *,
    source_model: Path,
    train_path: Path,
    out_model: Path,
    out_vocab: Path,
    max_lines: int | None,
    stats: SelfDistillStats,
    top_counts: list[tuple[str, int]],
) -> str:
    lines = [
        "# v2.0 Self-Distilled SP Score Control",
        "",
        f"Source model: `{source_model.as_posix()}`",
        f"Train path: `{train_path.as_posix()}`",
        f"Output model: `{out_model.as_posix()}`",
        f"Output vocab: `{out_vocab.as_posix()}`",
        f"Max lines: `{max_lines if max_lines is not None else 'all'}`",
        "",
        "This is the non-morphology matched control for the teacher-distilled",
        "score bound. It keeps the fixed SP64 vocabulary and re-estimates global",
        "Unigram scores from official SentencePiece segmentations on the same",
        "train-line budget. It does not use morphology teacher boundaries.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| lines | {stats.lines} |",
        f"| segments | {stats.segments} |",
        f"| counted tokens | {stats.counted_tokens} |",
        f"| counted piece types | {stats.counted_piece_types} |",
        f"| changed scores | {stats.changed_scores} |",
        f"| score floor | {stats.score_floor:.4f} |",
        "",
        "## Top Counted Pieces",
        "",
        "| Piece | Count |",
        "| --- | ---: |",
    ]
    for piece, count in top_counts:
        safe_piece = piece.replace("|", "\\|")
        lines.append(f"| `{safe_piece}` | {count} |")
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "Compare this control against `teacher_distilled_16000`. If both improve",
            "BPB similarly versus the protected SP64 floor, the earlier gain is",
            "mostly score re-estimation / effective-vocabulary geometry. If the",
            "teacher-distilled model wins clearly over this control, the morphology",
            "teacher is carrying additional signal.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Materialize a self-distilled SP score-control model."
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
    parser.add_argument("--max-lines", type=int, default=16000)
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--score-floor", type=float, default=-30.0)
    parser.add_argument("--out-model", required=True)
    parser.add_argument("--out-vocab", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    source_model = Path(args.source_model)
    train_path = Path(args.train)
    out_model = Path(args.out_model)
    out_vocab = Path(args.out_vocab)
    report_out = Path(args.report_out)
    out_model.parent.mkdir(parents=True, exist_ok=True)
    out_vocab.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)

    model = load_model(source_model)
    counts, lines, segments = collect_official_sp_counts(
        train_path=train_path,
        model_path=source_model,
        max_lines=args.max_lines,
        progress=args.progress,
    )
    changed_scores, counted_tokens = apply_distilled_scores(
        model,
        counts,
        score_floor=args.score_floor,
    )

    out_model.write_bytes(model.SerializeToString())
    save_vocab(model, out_vocab)
    stats = SelfDistillStats(
        lines=lines,
        segments=segments,
        counted_tokens=counted_tokens,
        counted_piece_types=len(counts),
        changed_scores=changed_scores,
        score_floor=args.score_floor,
    )
    report = format_report(
        source_model=source_model,
        train_path=train_path,
        out_model=out_model,
        out_vocab=out_vocab,
        max_lines=args.max_lines,
        stats=stats,
        top_counts=counts.most_common(40),
    )
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_model: {out_model}")
    print(f"wrote_vocab: {out_vocab}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
