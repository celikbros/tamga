from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

import sentencepiece as spm
from sentencepiece import sentencepiece_model_pb2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_score_shifted_sp_model import (  # noqa: E402
    Segment,
    normal_segments,
    piece_surface,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402

SP_WORD_START = "\u2581"
META_PIECES = {"<unk>", "<s>", "</s>", "<pad>"}
NEG_INF = float("-inf")


@dataclass(frozen=True)
class Entry:
    piece: str
    surface: str
    score: float
    word_start: bool


@dataclass(frozen=True)
class Edge:
    start: int
    end: int
    entry: Entry
    score: float
    crossings: int


@dataclass(frozen=True)
class IterationStats:
    iteration: int
    lines: int
    segments: int
    skipped_segments: int
    expected_piece_types: int
    expected_piece_mass: float
    expected_crossings: float
    changed_piece_scores: int
    avg_log_likelihood: float

    @property
    def avg_expected_crossings_per_segment(self) -> float:
        return self.expected_crossings / self.segments if self.segments else 0.0


@dataclass(frozen=True)
class WeightedVocab:
    entries_by_surface: dict[str, Entry]
    start_entries_by_surface: dict[str, Entry]
    max_entry_len: int
    max_start_entry_len: int

    @classmethod
    def from_model(cls, model: sentencepiece_model_pb2.ModelProto) -> "WeightedVocab":
        regular: dict[str, Entry] = {}
        start: dict[str, Entry] = {}
        for piece in model.pieces:
            if piece.piece in META_PIECES or SP_WORD_START in piece.piece[1:]:
                continue
            surface = piece_surface(piece.piece)
            if not surface:
                continue
            entry = Entry(
                piece=piece.piece,
                surface=surface,
                score=float(piece.score),
                word_start=piece.piece.startswith(SP_WORD_START),
            )
            bucket = start if entry.word_start else regular
            previous = bucket.get(surface)
            if previous is None or entry.score > previous.score:
                bucket[surface] = entry
        return cls(
            entries_by_surface=regular,
            start_entries_by_surface=start,
            max_entry_len=max((len(surface) for surface in regular), default=0),
            max_start_entry_len=max((len(surface) for surface in start), default=0),
        )

    def candidates_at(self, surface: str, position: int) -> list[Entry]:
        matches: list[Entry] = []
        max_len = min(self.max_entry_len, len(surface) - position)
        for length in range(1, max_len + 1):
            entry = self.entries_by_surface.get(surface[position : position + length])
            if entry is not None:
                matches.append(entry)
        if position == 0:
            max_start_len = min(self.max_start_entry_len, len(surface))
            for length in range(1, max_start_len + 1):
                entry = self.start_entries_by_surface.get(surface[:length])
                if entry is not None:
                    matches.append(entry)
        return matches


def logaddexp(left: float, right: float) -> float:
    if left == NEG_INF:
        return right
    if right == NEG_INF:
        return left
    if right > left:
        left, right = right, left
    return left + math.log1p(math.exp(right - left))


def crossed_count(start: int, end: int, boundaries: tuple[int, ...]) -> int:
    return sum(1 for boundary in boundaries if start < boundary < end)


def lattice_edges(
    segment: Segment,
    *,
    vocab: WeightedVocab,
    boundary_lambda: float,
) -> list[list[Edge]]:
    surface = segment.surface
    edges: list[list[Edge]] = [[] for _ in range(len(surface) + 1)]
    for position in range(len(surface)):
        candidates = vocab.candidates_at(surface, position)
        for entry in candidates:
            end = position + len(entry.surface)
            crossing = crossed_count(position, end, segment.soft_boundaries)
            score = entry.score - boundary_lambda * crossing
            edges[position].append(Edge(position, end, entry, score, crossing))
    return edges


def expected_counts_for_segment(
    segment: Segment,
    *,
    vocab: WeightedVocab,
    boundary_lambda: float,
) -> tuple[dict[str, float], float, float]:
    surface = segment.surface
    if not surface:
        return {}, 0.0, 0.0
    edges = lattice_edges(segment, vocab=vocab, boundary_lambda=boundary_lambda)
    forward = [NEG_INF] * (len(surface) + 1)
    forward[0] = 0.0
    for position in range(len(surface)):
        if forward[position] == NEG_INF:
            continue
        for edge in edges[position]:
            forward[edge.end] = logaddexp(
                forward[edge.end],
                forward[position] + edge.score,
            )
    z = forward[-1]
    if z == NEG_INF:
        return {}, NEG_INF, 0.0

    backward = [NEG_INF] * (len(surface) + 1)
    backward[-1] = 0.0
    for position in range(len(surface) - 1, -1, -1):
        value = NEG_INF
        for edge in edges[position]:
            value = logaddexp(value, edge.score + backward[edge.end])
        backward[position] = value

    counts: dict[str, float] = defaultdict(float)
    expected_crossings = 0.0
    for position, position_edges in enumerate(edges):
        if forward[position] == NEG_INF:
            continue
        for edge in position_edges:
            if backward[edge.end] == NEG_INF:
                continue
            posterior = math.exp(forward[position] + edge.score + backward[edge.end] - z)
            counts[edge.entry.piece] += posterior
            expected_crossings += posterior * edge.crossings
    return dict(counts), z, expected_crossings


def load_model(path: Path) -> sentencepiece_model_pb2.ModelProto:
    model = sentencepiece_model_pb2.ModelProto()
    model.ParseFromString(path.read_bytes())
    return model


def save_vocab(model: sentencepiece_model_pb2.ModelProto, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for piece in model.pieces:
            handle.write(f"{piece.piece}\t{piece.score}\n")


def train_iteration(
    *,
    model: sentencepiece_model_pb2.ModelProto,
    train_path: Path,
    boundary_lambda: float,
    max_lines: int | None,
    progress: int,
    iteration: int,
    score_floor: float,
) -> IterationStats:
    vocab = WeightedVocab.from_model(model)
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    expected: dict[str, float] = defaultdict(float)
    lines = 0
    segments = 0
    skipped_segments = 0
    total_log_likelihood = 0.0
    total_expected_crossings = 0.0
    with train_path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if max_lines is not None and lines >= max_lines:
                break
            lines += 1
            text = raw.rstrip("\n")
            for segment in normal_segments(text, tokenizer):
                counts, log_z, expected_crossings = expected_counts_for_segment(
                    segment,
                    vocab=vocab,
                    boundary_lambda=boundary_lambda,
                )
                if log_z == NEG_INF:
                    skipped_segments += 1
                    continue
                segments += 1
                total_log_likelihood += log_z
                total_expected_crossings += expected_crossings
                for piece, value in counts.items():
                    expected[piece] += value
            if progress > 0 and lines % progress == 0:
                print(
                    f"iteration={iteration} scanned {lines:,} lines "
                    f"segments={segments:,} expected_types={len(expected):,}",
                    flush=True,
                )

    total_mass = sum(expected.values())
    changed = 0
    if total_mass > 0:
        for piece in model.pieces:
            piece_name = piece.piece
            if piece_name in expected:
                new_score = max(score_floor, math.log(expected[piece_name] / total_mass))
                if not math.isclose(float(piece.score), new_score, rel_tol=0.0, abs_tol=1e-9):
                    changed += 1
                piece.score = new_score

    return IterationStats(
        iteration=iteration,
        lines=lines,
        segments=segments,
        skipped_segments=skipped_segments,
        expected_piece_types=len(expected),
        expected_piece_mass=total_mass,
        expected_crossings=total_expected_crossings,
        changed_piece_scores=changed,
        avg_log_likelihood=total_log_likelihood / segments if segments else 0.0,
    )


def format_report(
    *,
    source_model: Path,
    train_path: Path,
    out_model: Path,
    out_vocab: Path,
    boundary_lambda: float,
    iterations: int,
    max_lines: int | None,
    rows: list[IterationStats],
) -> str:
    lines = [
        "# v2.0 Boundary-Weighted Unigram EM Prototype",
        "",
        f"Source model: `{source_model.as_posix()}`",
        f"Train path: `{train_path.as_posix()}`",
        f"Output model: `{out_model.as_posix()}`",
        f"Output vocab: `{out_vocab.as_posix()}`",
        f"Boundary lambda: `{boundary_lambda}`",
        f"Iterations: `{iterations}`",
        f"Max lines: `{max_lines if max_lines is not None else 'all'}`",
        "",
        "This is a small prototype, not a production trainer. It updates existing",
        "SP64 Unigram scores using expected counts from a boundary-weighted",
        "lattice over normal-text segments.",
        "",
        "## Iterations",
        "",
        "| Iteration | Lines | Segments | Skipped segments | Expected piece types | Expected mass | Expected crossings | Avg expected crossings/segment | Changed scores | Avg log Z/segment |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.iteration} | {row.lines} | {row.segments} | "
            f"{row.skipped_segments} | {row.expected_piece_types} | "
            f"{row.expected_piece_mass:.4f} | {row.expected_crossings:.4f} | "
            f"{row.avg_expected_crossings_per_segment:.6f} | "
            f"{row.changed_piece_scores} | {row.avg_log_likelihood:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "Evaluate this model as a diagnostic. Continue only if lambda curves",
            "produce a material bare-F1 gain outside the current visible-eval noise",
            "floor without unacceptable token pressure.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Materialize a prototype boundary-weighted Unigram EM model."
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
    parser.add_argument("--boundary-lambda", type=float, default=1.0)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--max-lines", type=int, default=500)
    parser.add_argument("--progress", type=int, default=100)
    parser.add_argument("--score-floor", type=float, default=-30.0)
    parser.add_argument("--out-model", required=True)
    parser.add_argument("--out-vocab", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    source_model = Path(args.sp_model)
    train_path = Path(args.train)
    out_model = Path(args.out_model)
    out_vocab = Path(args.out_vocab)
    report_out = Path(args.report_out)
    out_model.parent.mkdir(parents=True, exist_ok=True)
    out_vocab.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)

    model = load_model(source_model)
    rows: list[IterationStats] = []
    for iteration in range(1, args.iterations + 1):
        rows.append(
            train_iteration(
                model=model,
                train_path=train_path,
                boundary_lambda=args.boundary_lambda,
                max_lines=args.max_lines,
                progress=args.progress,
                iteration=iteration,
                score_floor=args.score_floor,
            )
        )

    out_model.write_bytes(model.SerializeToString())
    save_vocab(model, out_vocab)
    report = format_report(
        source_model=source_model,
        train_path=train_path,
        out_model=out_model,
        out_vocab=out_vocab,
        boundary_lambda=args.boundary_lambda,
        iterations=args.iterations,
        max_lines=args.max_lines,
        rows=rows,
    )
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_model: {out_model}")
    print(f"wrote_vocab: {out_vocab}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
