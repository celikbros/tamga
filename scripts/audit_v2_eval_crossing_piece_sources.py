from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

from sentencepiece import sentencepiece_model_pb2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_v2_deployed_sp_crossings import parse_model  # noqa: E402
from scripts.evaluate_tokenizer import load_cases  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import load_sp_processor  # noqa: E402
from scripts.materialize_v2_score_shifted_sp_model import (  # noqa: E402
    META_PIECES,
    PieceStats,
    load_stats,
    normal_segments,
    piece_surface,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass
class CrossingPieceSource:
    piece: str
    eval_count: int = 0
    eval_crossing_occurrences: int = 0
    eval_crossed_boundaries: int = 0
    train_count: int = 0
    train_crossing_count: int = 0
    score: float | None = None

    @property
    def train_crossing_rate(self) -> float:
        return self.train_crossing_count / self.train_count if self.train_count else 0.0


@dataclass(frozen=True)
class SourceAudit:
    label: str
    examples: int
    segments: int
    teacher_boundaries: int
    crossed_boundaries: int
    crossing_piece_occurrences: int
    alignment_failures: int
    rows: dict[str, CrossingPieceSource]

    @property
    def crossed_boundary_rate(self) -> float:
        return self.crossed_boundaries / self.teacher_boundaries if self.teacher_boundaries else 0.0


def load_model_scores(path: Path) -> dict[str, float]:
    model = sentencepiece_model_pb2.ModelProto()
    model.ParseFromString(path.read_bytes())
    return {piece.piece: float(piece.score) for piece in model.pieces}


def train_rate_bucket(row: CrossingPieceSource, *, min_reliable_count: int) -> str:
    if row.train_count <= 0:
        return "no_train_stats"
    if row.train_count < min_reliable_count:
        return f"train_count< {min_reliable_count}"
    rate = row.train_crossing_rate
    if rate >= 0.999:
        return "train_rate=1.00"
    if rate >= 0.70:
        return "train_rate=0.70-0.99"
    if rate >= 0.40:
        return "train_rate=0.40-0.69"
    if rate >= 0.20:
        return "train_rate=0.20-0.39"
    if rate > 0.0:
        return "train_rate=0.00-0.19"
    return "train_rate=0.00"


def score_bucket(score: float | None, *, score_floor: float, epsilon: float) -> str:
    if score is None:
        return "score_missing"
    if score <= score_floor + epsilon:
        return "floor_score"
    return "counted_score"


def audit_model(
    *,
    label: str,
    model_path: Path,
    texts: list[str],
    train_stats: dict[str, PieceStats],
    score_floor: float,
    progress: int,
) -> SourceAudit:
    processor = load_sp_processor(model_path)
    scores = load_model_scores(model_path)
    tokenizer = TurkishTokenizer(preserve_whitespace=True)

    rows: dict[str, CrossingPieceSource] = {}
    examples = len(texts)
    segments = 0
    teacher_boundaries = 0
    crossed_boundaries = 0
    crossing_piece_occurrences = 0
    alignment_failures = 0

    for index, text in enumerate(texts, start=1):
        for segment in normal_segments(text, tokenizer):
            segments += 1
            teacher_boundaries += len(segment.soft_boundaries)
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
                crossing_count = sum(
                    1 for boundary in segment.soft_boundaries if position < boundary < end
                )
                if crossing_count:
                    train_row = train_stats.get(piece, PieceStats())
                    row = rows.setdefault(
                        piece,
                        CrossingPieceSource(
                            piece=piece,
                            train_count=train_row.count,
                            train_crossing_count=train_row.crossing_count,
                            score=scores.get(piece),
                        ),
                    )
                    row.eval_count += 1
                    row.eval_crossing_occurrences += 1
                    row.eval_crossed_boundaries += crossing_count
                    crossed_boundaries += crossing_count
                    crossing_piece_occurrences += 1
                position = end
        if progress > 0 and index % progress == 0:
            print(
                f"{label}: audited {index:,} examples crossed={crossed_boundaries:,}",
                flush=True,
            )

    return SourceAudit(
        label=label,
        examples=examples,
        segments=segments,
        teacher_boundaries=teacher_boundaries,
        crossed_boundaries=crossed_boundaries,
        crossing_piece_occurrences=crossing_piece_occurrences,
        alignment_failures=alignment_failures,
        rows=rows,
    )


def bucket_counter_by_train_rate(
    audit: SourceAudit,
    *,
    min_reliable_count: int,
) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in audit.rows.values():
        bucket = train_rate_bucket(row, min_reliable_count=min_reliable_count)
        counter[(bucket, "piece_types")] += 1
        counter[(bucket, "eval_occurrences")] += row.eval_crossing_occurrences
        counter[(bucket, "crossed_boundaries")] += row.eval_crossed_boundaries
    return counter


def bucket_counter_by_score(
    audit: SourceAudit,
    *,
    score_floor: float,
    epsilon: float,
) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in audit.rows.values():
        bucket = score_bucket(row.score, score_floor=score_floor, epsilon=epsilon)
        counter[(bucket, "piece_types")] += 1
        counter[(bucket, "eval_occurrences")] += row.eval_crossing_occurrences
        counter[(bucket, "crossed_boundaries")] += row.eval_crossed_boundaries
    return counter


def format_bucket_table(
    *,
    audit: SourceAudit,
    counter: Counter[str],
    buckets: list[str],
) -> list[str]:
    lines = [
        "| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for bucket in buckets:
        crossed = int(counter[(bucket, "crossed_boundaries")])
        share = crossed / audit.crossed_boundaries if audit.crossed_boundaries else 0.0
        lines.append(
            f"| {bucket} | {int(counter[(bucket, 'piece_types')])} | "
            f"{int(counter[(bucket, 'eval_occurrences')])} | {crossed} | {share:.6f} |"
        )
    return lines


def format_report(
    *,
    dataset: Path,
    stats_path: Path,
    audits: list[SourceAudit],
    min_reliable_count: int,
    score_floor: float,
    score_epsilon: float,
    top_n: int,
) -> str:
    lines = [
        "# v2.0 Eval Crossing Piece Source Audit",
        "",
        f"Dataset: `{dataset.as_posix()}`",
        f"Train stats: `{stats_path.as_posix()}`",
        "",
        "This report re-attributes deployed eval crossings using train-side",
        "crossing statistics. It avoids treating eval one-off crossing rates as",
        "evidence of concentration.",
        "",
        "It also checks whether crossing pieces in a score-distilled model carry",
        "floor scores or counted scores.",
        "",
        "## Summary",
        "",
        "| Model | Examples | Segments | Teacher boundaries | Crossed boundaries | Crossed boundary rate | Crossing piece occurrences | Alignment failures |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for audit in audits:
        lines.append(
            f"| `{audit.label}` | {audit.examples} | {audit.segments} | "
            f"{audit.teacher_boundaries} | {audit.crossed_boundaries} | "
            f"{audit.crossed_boundary_rate:.6f} | {audit.crossing_piece_occurrences} | "
            f"{audit.alignment_failures} |"
        )

    train_buckets = [
        "train_rate=1.00",
        "train_rate=0.70-0.99",
        "train_rate=0.40-0.69",
        "train_rate=0.20-0.39",
        "train_rate=0.00-0.19",
        "train_rate=0.00",
        f"train_count< {min_reliable_count}",
        "no_train_stats",
    ]
    score_buckets = ["counted_score", "floor_score", "score_missing"]

    for audit in audits:
        lines.extend(
            [
                "",
                f"## Train-Side Attribution: `{audit.label}`",
                "",
            ]
        )
        lines.extend(
            format_bucket_table(
                audit=audit,
                counter=bucket_counter_by_train_rate(
                    audit,
                    min_reliable_count=min_reliable_count,
                ),
                buckets=train_buckets,
            )
        )
        lines.extend(
            [
                "",
                f"## Score Attribution: `{audit.label}`",
                "",
            ]
        )
        lines.extend(
            format_bucket_table(
                audit=audit,
                counter=bucket_counter_by_score(
                    audit,
                    score_floor=score_floor,
                    epsilon=score_epsilon,
                ),
                buckets=score_buckets,
            )
        )
        lines.extend(
            [
                "",
                "### Top Crossing Pieces",
                "",
                "| Piece | Eval crossed boundaries | Eval crossing occurrences | Train count | Train crossing count | Train crossing rate | Score |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        top = sorted(
            audit.rows.values(),
            key=lambda row: (row.eval_crossed_boundaries, row.eval_crossing_occurrences),
            reverse=True,
        )[:top_n]
        for row in top:
            safe_piece = row.piece.replace("|", "\\|")
            score = "" if row.score is None else f"{row.score:.6f}"
            lines.append(
                f"| `{safe_piece}` | {row.eval_crossed_boundaries} | "
                f"{row.eval_crossing_occurrences} | {row.train_count} | "
                f"{row.train_crossing_count} | {row.train_crossing_rate:.6f} | "
                f"{score} |"
            )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            "If most eval crossings come from pieces that were high-crossing in the",
            "train statistics, targeted inventory pruning may still have headroom.",
            "If most come from low/zero/unsupported train-rate pieces, the remaining",
            "damage is context-dependent and context-free pruning is near its limit.",
            "",
            "For teacher-distilled score-bound models, crossing pieces with floor",
            "scores would indicate a serialization/scoring problem. Crossing pieces",
            "with counted scores mean the bound is mechanically valid and the limit",
            "is in the global score/inventory family itself.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Attribute eval crossing pieces to train-side stats and model scores."
    )
    parser.add_argument("--dataset", default="data/eval/tr_challenge.tsv")
    parser.add_argument(
        "--stats-in",
        default="artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json",
    )
    parser.add_argument("--model", action="append", type=parse_model, required=True)
    parser.add_argument("--min-reliable-count", type=int, default=20)
    parser.add_argument("--score-floor", type=float, default=-30.0)
    parser.add_argument("--score-epsilon", type=float, default=1e-6)
    parser.add_argument("--top-n", type=int, default=40)
    parser.add_argument("--progress", type=int, default=0)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    dataset = Path(args.dataset)
    stats_path = Path(args.stats_in)
    train_stats = load_stats(stats_path)
    texts = [case.text for case in load_cases(dataset)]
    audits = [
        audit_model(
            label=spec.label,
            model_path=spec.path,
            texts=texts,
            train_stats=train_stats,
            score_floor=args.score_floor,
            progress=args.progress,
        )
        for spec in args.model
    ]
    report = format_report(
        dataset=dataset,
        stats_path=stats_path,
        audits=audits,
        min_reliable_count=args.min_reliable_count,
        score_floor=args.score_floor,
        score_epsilon=args.score_epsilon,
        top_n=args.top_n,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
