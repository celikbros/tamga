from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

from sentencepiece import sentencepiece_model_pb2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_v2_sp64_morph_compliant_paths import constrained_viterbi_segment  # noqa: E402
from scripts.materialize_v2_score_shifted_sp_model import normal_segments  # noqa: E402
from scripts.sweep_v2_boundary_biased_unigram import BoundaryBiasedVocab  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402

META_PIECES = {"<unk>", "<s>", "</s>", "<pad>"}


@dataclass(frozen=True)
class DistillStats:
    lines: int
    segments: int
    skipped_segments: int
    counted_tokens: int
    counted_piece_types: int
    missing_piece_tokens: int
    changed_scores: int
    score_floor: float


def load_model(path: Path) -> sentencepiece_model_pb2.ModelProto:
    model = sentencepiece_model_pb2.ModelProto()
    model.ParseFromString(path.read_bytes())
    return model


def save_vocab(model: sentencepiece_model_pb2.ModelProto, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for piece in model.pieces:
            handle.write(f"{piece.piece}\t{piece.score}\n")


def collect_teacher_counts(
    *,
    train_path: Path,
    vocab: BoundaryBiasedVocab,
    piece_names: set[str],
    max_lines: int | None,
    progress: int,
) -> tuple[Counter[str], int, int, int, int]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    counts: Counter[str] = Counter()
    lines = 0
    segments = 0
    skipped_segments = 0
    missing_piece_tokens = 0

    with train_path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if max_lines is not None and lines >= max_lines:
                break
            lines += 1
            text = raw.rstrip("\n")
            for segment in normal_segments(text, tokenizer):
                result = constrained_viterbi_segment(
                    segment.surface,
                    boundaries=segment.soft_boundaries,
                    vocab=vocab,
                )
                if not result.sp_pieces:
                    skipped_segments += 1
                    continue
                segments += 1
                for piece in result.sp_pieces:
                    if piece in piece_names:
                        counts[piece] += 1
                    else:
                        missing_piece_tokens += 1
            if progress > 0 and lines % progress == 0:
                print(
                    f"distilled {lines:,} lines segments={segments:,} "
                    f"piece_types={len(counts):,} missing_tokens={missing_piece_tokens:,}",
                    flush=True,
                )

    return counts, lines, segments, skipped_segments, missing_piece_tokens


def apply_distilled_scores(
    model: sentencepiece_model_pb2.ModelProto,
    counts: Counter[str],
    *,
    score_floor: float,
) -> tuple[int, int]:
    total = sum(counts.values())
    changed = 0
    if total <= 0:
        return 0, 0

    for piece in model.pieces:
        if piece.piece in META_PIECES:
            continue
        count = counts.get(piece.piece, 0)
        new_score = math.log(count / total) if count > 0 else score_floor
        if not math.isclose(float(piece.score), new_score, rel_tol=0.0, abs_tol=1e-9):
            changed += 1
        piece.score = new_score
    return changed, total


def format_report(
    *,
    source_model: Path,
    source_vocab: Path,
    train_path: Path,
    out_model: Path,
    out_vocab: Path,
    max_lines: int | None,
    stats: DistillStats,
    top_counts: list[tuple[str, int]],
) -> str:
    lines = [
        "# v2.0 Teacher-Distilled SP Score Probe",
        "",
        f"Source model: `{source_model.as_posix()}`",
        f"Source vocab: `{source_vocab.as_posix()}`",
        f"Train path: `{train_path.as_posix()}`",
        f"Output model: `{out_model.as_posix()}`",
        f"Output vocab: `{out_vocab.as_posix()}`",
        f"Max lines: `{max_lines if max_lines is not None else 'all'}`",
        "",
        "This probe fits global Unigram scores to teacher-compliant no-cross",
        "paths over the fixed SP64 vocabulary. It is a score-space upper-bound",
        "diagnostic, not a production trainer.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| lines | {stats.lines} |",
        f"| segments | {stats.segments} |",
        f"| skipped segments | {stats.skipped_segments} |",
        f"| counted tokens | {stats.counted_tokens} |",
        f"| counted piece types | {stats.counted_piece_types} |",
        f"| missing piece tokens | {stats.missing_piece_tokens} |",
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
            "If this model still behaves like SP64 on deployed Viterbi, then global",
            "score space is exhausted for this vocabulary. If it jumps toward the",
            "oracle ceiling, the previous EM/score-shift probes were underpowered.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Materialize a teacher-distilled SP model over fixed SP64 vocab."
    )
    parser.add_argument(
        "--source-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--source-vocab",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab",
    )
    parser.add_argument(
        "--train",
        default=(
            "artifacts/private/v1_8_local_lm_probe/"
            "celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/"
            "filtered_split/train.txt"
        ),
    )
    parser.add_argument("--max-lines", type=int, default=2000)
    parser.add_argument("--progress", type=int, default=500)
    parser.add_argument("--score-floor", type=float, default=-30.0)
    parser.add_argument("--out-model", required=True)
    parser.add_argument("--out-vocab", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    source_model = Path(args.source_model)
    source_vocab = Path(args.source_vocab)
    train_path = Path(args.train)
    out_model = Path(args.out_model)
    out_vocab = Path(args.out_vocab)
    report_out = Path(args.report_out)
    out_model.parent.mkdir(parents=True, exist_ok=True)
    out_vocab.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)

    model = load_model(source_model)
    piece_names = {piece.piece for piece in model.pieces}
    vocab = BoundaryBiasedVocab.from_vocab_file(source_vocab)
    counts, lines, segments, skipped_segments, missing_piece_tokens = collect_teacher_counts(
        train_path=train_path,
        vocab=vocab,
        piece_names=piece_names,
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
    stats = DistillStats(
        lines=lines,
        segments=segments,
        skipped_segments=skipped_segments,
        counted_tokens=counted_tokens,
        counted_piece_types=len(counts),
        missing_piece_tokens=missing_piece_tokens,
        changed_scores=changed_scores,
        score_floor=args.score_floor,
    )
    report = format_report(
        source_model=source_model,
        source_vocab=source_vocab,
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
