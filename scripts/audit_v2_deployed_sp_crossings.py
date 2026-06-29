from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import count_words  # noqa: E402
from scripts.evaluate_tokenizer import load_cases  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import load_sp_processor  # noqa: E402
from scripts.materialize_v2_score_shifted_sp_model import (  # noqa: E402
    Segment,
    normal_segments,
    piece_surface,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402

META_PIECES = {"<unk>", "<s>", "</s>", "<pad>"}


@dataclass(frozen=True)
class ModelSpec:
    label: str
    path: Path


@dataclass
class PieceCrossingStats:
    count: int = 0
    crossing_occurrences: int = 0
    crossing_count: int = 0

    @property
    def occurrence_crossing_rate(self) -> float:
        return self.crossing_occurrences / self.count if self.count else 0.0

    @property
    def crossing_count_rate(self) -> float:
        return self.crossing_count / self.count if self.count else 0.0


@dataclass(frozen=True)
class ModelAudit:
    label: str
    examples: int
    words: int
    segments: int
    teacher_boundaries: int
    model_pieces: int
    crossed_boundaries: int
    crossing_piece_occurrences: int
    alignment_failures: int
    piece_stats: dict[str, PieceCrossingStats]

    @property
    def crossed_boundary_rate(self) -> float:
        return self.crossed_boundaries / self.teacher_boundaries if self.teacher_boundaries else 0.0

    @property
    def crossing_piece_rate(self) -> float:
        return self.crossing_piece_occurrences / self.model_pieces if self.model_pieces else 0.0

    @property
    def tokens_per_word(self) -> float:
        return self.model_pieces / self.words if self.words else 0.0


def parse_model(value: str) -> ModelSpec:
    if "=" not in value:
        raise argparse.ArgumentTypeError("model must be LABEL=PATH")
    label, raw_path = value.split("=", 1)
    if not label:
        raise argparse.ArgumentTypeError("model label cannot be empty")
    return ModelSpec(label=label, path=Path(raw_path))


def crossing_bucket(rate: float) -> str:
    if rate >= 0.999:
        return "1.00"
    if rate >= 0.70:
        return "0.70-0.99"
    if rate >= 0.40:
        return "0.40-0.69"
    if rate >= 0.20:
        return "0.20-0.39"
    if rate > 0.0:
        return "0.00-0.19"
    return "0.00"


def audit_segment(
    segment: Segment,
    *,
    processor,
    piece_stats: dict[str, PieceCrossingStats],
) -> tuple[int, int, int, int]:
    position = 0
    model_pieces = 0
    crossed_boundaries = 0
    crossing_piece_occurrences = 0
    alignment_failures = 0

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
        crossing_count = sum(1 for boundary in segment.soft_boundaries if position < boundary < end)
        row = piece_stats.setdefault(piece, PieceCrossingStats())
        row.count += 1
        row.crossing_count += crossing_count
        if crossing_count:
            row.crossing_occurrences += 1
            crossing_piece_occurrences += 1
        crossed_boundaries += crossing_count
        model_pieces += 1
        position = end

    return model_pieces, crossed_boundaries, crossing_piece_occurrences, alignment_failures


def audit_model(
    *,
    spec: ModelSpec,
    texts: list[str],
    progress: int,
) -> ModelAudit:
    processor = load_sp_processor(spec.path)
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    piece_stats: dict[str, PieceCrossingStats] = {}
    segments = 0
    teacher_boundaries = 0
    model_pieces = 0
    crossed_boundaries = 0
    crossing_piece_occurrences = 0
    alignment_failures = 0
    words = sum(count_words(text) for text in texts)

    for index, text in enumerate(texts, start=1):
        for segment in normal_segments(text, tokenizer):
            segments += 1
            teacher_boundaries += len(segment.soft_boundaries)
            pieces, crossed, crossing_pieces, failures = audit_segment(
                segment,
                processor=processor,
                piece_stats=piece_stats,
            )
            model_pieces += pieces
            crossed_boundaries += crossed
            crossing_piece_occurrences += crossing_pieces
            alignment_failures += failures
        if progress > 0 and index % progress == 0:
            print(
                f"{spec.label}: audited {index:,} examples "
                f"segments={segments:,} crossed={crossed_boundaries:,}",
                flush=True,
            )

    return ModelAudit(
        label=spec.label,
        examples=len(texts),
        words=words,
        segments=segments,
        teacher_boundaries=teacher_boundaries,
        model_pieces=model_pieces,
        crossed_boundaries=crossed_boundaries,
        crossing_piece_occurrences=crossing_piece_occurrences,
        alignment_failures=alignment_failures,
        piece_stats=piece_stats,
    )


def bucket_rows(audit: ModelAudit) -> list[tuple[str, int, int, int, float]]:
    buckets: dict[str, Counter[str]] = {}
    for piece, stats in audit.piece_stats.items():
        if stats.crossing_count <= 0:
            continue
        bucket = crossing_bucket(stats.occurrence_crossing_rate)
        row = buckets.setdefault(bucket, Counter())
        row["piece_types"] += 1
        row["piece_occurrences"] += stats.count
        row["crossing_occurrences"] += stats.crossing_occurrences
        row["crossing_count"] += stats.crossing_count

    rows: list[tuple[str, int, int, int, float]] = []
    for bucket in ["1.00", "0.70-0.99", "0.40-0.69", "0.20-0.39", "0.00-0.19"]:
        row = buckets.get(bucket, Counter())
        crossing_count = int(row["crossing_count"])
        share = crossing_count / audit.crossed_boundaries if audit.crossed_boundaries else 0.0
        rows.append(
            (
                bucket,
                int(row["piece_types"]),
                int(row["piece_occurrences"]),
                crossing_count,
                share,
            )
        )
    return rows


def format_report(
    *,
    dataset: Path,
    audits: list[ModelAudit],
    top_n: int,
) -> str:
    lines = [
        "# v2.0 Deployed SP Viterbi Crossing Audit",
        "",
        f"Dataset: `{dataset.as_posix()}`",
        "",
        "This report measures crossings from the serialized model's deployed",
        "SentencePiece Viterbi path, not the tilted training posterior.",
        "",
        "## Summary",
        "",
        "| Model | Examples | Segments | Teacher boundaries | Crossed boundaries | Crossed boundary rate | Model pieces | Pieces/word | Crossing piece rate | Alignment failures |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for audit in audits:
        lines.append(
            f"| `{audit.label}` | {audit.examples} | {audit.segments} | "
            f"{audit.teacher_boundaries} | {audit.crossed_boundaries} | "
            f"{audit.crossed_boundary_rate:.6f} | {audit.model_pieces} | "
            f"{audit.tokens_per_word:.4f} | {audit.crossing_piece_rate:.6f} | "
            f"{audit.alignment_failures} |"
        )

    for audit in audits:
        lines.extend(
            [
                "",
                f"## Crossing Attribution: `{audit.label}`",
                "",
                "| Piece crossing-rate bucket | Piece types | Piece occurrences | Crossed boundaries | Share of crossed boundaries |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for bucket, piece_types, piece_occurrences, crossing_count, share in bucket_rows(audit):
            lines.append(
                f"| {bucket} | {piece_types} | {piece_occurrences} | "
                f"{crossing_count} | {share:.6f} |"
            )

        lines.extend(
            [
                "",
                "### Top Crossing Pieces",
                "",
                "| Piece | Count | Crossing occurrences | Crossed boundaries | Occurrence crossing rate | Crossing count rate |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        top = sorted(
            audit.piece_stats.items(),
            key=lambda item: (item[1].crossing_count, item[1].crossing_occurrences),
            reverse=True,
        )[:top_n]
        for piece, stats in top:
            safe_piece = piece.replace("|", "\\|")
            lines.append(
                f"| `{safe_piece}` | {stats.count} | {stats.crossing_occurrences} | "
                f"{stats.crossing_count} | {stats.occurrence_crossing_rate:.6f} | "
                f"{stats.crossing_count_rate:.6f} |"
            )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            "If lambda-trained/distilled models do not reduce deployed Viterbi crossings,",
            "the training posterior signal is not surviving projection into the serialized",
            "Unigram model. If crossings are concentrated in high-rate pieces, inventory",
            "work may help; diffuse medium-rate damage points toward a context-free limit.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Audit deployed SP Viterbi crossings against teacher boundaries."
    )
    parser.add_argument("--dataset", default="data/eval/tr_challenge.tsv")
    parser.add_argument("--model", action="append", type=parse_model, required=True)
    parser.add_argument("--top-n", type=int, default=25)
    parser.add_argument("--progress", type=int, default=0)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    dataset = Path(args.dataset)
    texts = [case.text for case in load_cases(dataset)]
    audits = [
        audit_model(spec=spec, texts=texts, progress=args.progress)
        for spec in args.model
    ]
    report = format_report(dataset=dataset, audits=audits, top_n=args.top_n)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
