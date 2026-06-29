from __future__ import annotations

from dataclasses import dataclass
import argparse
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_tokenizer import load_cases  # noqa: E402
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.sweep_v2_boundary_biased_unigram import (  # noqa: E402
    BoundaryBiasedVocab,
    SegmentResult,
    VocabEntry,
    crossed_boundary_count,
    viterbi_segment,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class SegmentAudit:
    source: str
    line_number: int
    surface: str
    boundaries: tuple[int, ...]
    unconstrained_tokens: int
    constrained_tokens: int
    unconstrained_score: float
    constrained_score: float
    unconstrained_crossed: int

    @property
    def score_delta(self) -> float:
        return self.unconstrained_score - self.constrained_score

    @property
    def token_delta(self) -> int:
        return self.constrained_tokens - self.unconstrained_tokens

    @property
    def same_token_count(self) -> bool:
        return self.token_delta == 0


def constrained_viterbi_segment(
    surface: str,
    *,
    boundaries: tuple[int, ...],
    vocab: BoundaryBiasedVocab,
    fallback_score: float = -100.0,
) -> SegmentResult:
    if not surface:
        return SegmentResult((), (), 0, 0, 0.0)

    best: list[tuple[float, tuple[VocabEntry, ...]] | None] = [None] * (
        len(surface) + 1
    )
    best[0] = (0.0, ())

    for position in range(len(surface)):
        state = best[position]
        if state is None:
            continue
        current_score, current_tokens = state
        candidates = vocab.candidates_at(surface, position)
        if not candidates:
            candidates = [
                VocabEntry(
                    piece=surface[position],
                    surface=surface[position],
                    score=fallback_score,
                    word_start=False,
                )
            ]

        for entry in candidates:
            end = position + len(entry.surface)
            if crossed_boundary_count(position, end, boundaries):
                continue
            score = current_score + entry.score
            tokens = (*current_tokens, entry)
            previous = best[end]
            if previous is None or score > previous[0] or (
                math.isclose(score, previous[0], rel_tol=0.0, abs_tol=1e-9)
                and len(tokens) < len(previous[1])
            ):
                best[end] = (score, tokens)

    final = best[-1]
    if final is None:
        fallback = tuple(surface)
        return SegmentResult(
            fallback,
            fallback,
            len(fallback),
            0,
            fallback_score * len(surface),
        )

    score, entries = final
    return SegmentResult(
        surfaces=tuple(entry.surface for entry in entries),
        sp_pieces=tuple(entry.piece for entry in entries),
        model_token_count=len(entries),
        crossed_boundaries=0,
        score=score,
    )


def iter_soft_morph_segments(text: str) -> list[tuple[str, tuple[int, ...]]]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    pieces = analyze_line(text, tokenizer)
    segments: list[tuple[str, tuple[int, ...]]] = []
    segment = ""
    boundaries: list[int] = []

    def flush() -> None:
        nonlocal segment, boundaries
        if segment and boundaries:
            segments.append((segment, tuple(boundaries)))
        segment = ""
        boundaries = []

    for piece in pieces:
        if piece.kind == "whitespace" or piece.kind.startswith("protected:"):
            flush()
            continue
        if piece.kind == "apostrophe" or (
            piece.kind == "suffix" and piece.boundary_before == "hard"
        ):
            flush()
            continue
        if piece.boundary_before == "soft":
            boundaries.append(len(segment))
            segment += piece.surface
            continue
        if piece.boundary_before == "hard":
            flush()
            segment = piece.surface
            continue
        segment += piece.surface

    flush()
    return segments


def audit_texts(
    *,
    texts: list[tuple[str, str]],
    vocab: BoundaryBiasedVocab,
    progress: int,
) -> list[SegmentAudit]:
    rows: list[SegmentAudit] = []
    for line_number, (source, text) in enumerate(texts, start=1):
        for surface, boundaries in iter_soft_morph_segments(text):
            unconstrained = viterbi_segment(
                surface,
                boundaries=boundaries,
                vocab=vocab,
                boundary_lambda=0.0,
            )
            constrained = constrained_viterbi_segment(
                surface,
                boundaries=boundaries,
                vocab=vocab,
            )
            rows.append(
                SegmentAudit(
                    source=source,
                    line_number=line_number,
                    surface=surface,
                    boundaries=boundaries,
                    unconstrained_tokens=unconstrained.model_token_count,
                    constrained_tokens=constrained.model_token_count,
                    unconstrained_score=unconstrained.score,
                    constrained_score=constrained.score,
                    unconstrained_crossed=unconstrained.crossed_boundaries,
                )
            )
        if progress > 0 and line_number % progress == 0:
            print(
                f"audited {line_number:,} texts segments={len(rows):,}",
                flush=True,
            )
    return rows


def load_eval_texts(path: Path, *, source: str) -> list[tuple[str, str]]:
    return [(source, case.text) for case in load_cases(path)]


def load_plain_texts(path: Path, *, source: str, max_lines: int | None) -> list[tuple[str, str]]:
    output: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for index, raw in enumerate(handle):
            if max_lines is not None and index >= max_lines:
                break
            output.append((source, raw.rstrip("\n")))
    return output


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def format_report(
    *,
    vocab_path: Path,
    rows: list[SegmentAudit],
    top_n: int,
) -> str:
    crossed = [row for row in rows if row.unconstrained_crossed > 0]
    token_deltas = [float(row.token_delta) for row in rows]
    score_deltas = [row.score_delta for row in rows]
    crossed_score_deltas = [row.score_delta for row in crossed]
    top_rows = sorted(rows, key=lambda row: (row.score_delta, row.token_delta), reverse=True)[
        :top_n
    ]

    lines = [
        "# v2.0 Rung-0 SP64 Morph-Compliant Path Audit",
        "",
        f"Vocab: `{vocab_path.as_posix()}`",
        "",
        "This diagnostic asks whether the existing SP64 vocabulary already has",
        "paths that avoid high-confidence custom morphology boundaries.",
        "",
        "If constrained paths are close to unconstrained paths, a soft training",
        "prior may be enough. If constrained paths are much more expensive, the",
        "vocabulary itself needs reshaping.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| soft-boundary segments | {len(rows)} |",
        f"| unconstrained crosses >=1 boundary | {len(crossed)} |",
        f"| crossing share | {len(crossed) / len(rows) if rows else 0.0:.6f} |",
        f"| avg token delta constrained-unconstrained | {_mean(token_deltas):.4f} |",
        f"| median token delta | {_median(token_deltas):.4f} |",
        f"| avg score delta unconstrained-constrained | {_mean(score_deltas):.4f} |",
        f"| median score delta | {_median(score_deltas):.4f} |",
        f"| avg score delta on crossed segments | {_mean(crossed_score_deltas):.4f} |",
        "",
        "## Largest Score Deltas",
        "",
        "| Source | Line | Surface | Boundaries | Unconstrained tokens | Constrained tokens | Crossed | Score delta | Token delta |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in top_rows:
        surface = row.surface.replace("|", "\\|")
        lines.append(
            f"| {row.source} | {row.line_number} | `{surface}` | "
            f"`{list(row.boundaries)}` | {row.unconstrained_tokens} | "
            f"{row.constrained_tokens} | {row.unconstrained_crossed} | "
            f"{row.score_delta:.4f} | {row.token_delta} |"
        )

    lines.extend(
        [
            "",
            "## Gate",
            "",
            "Use this as a diagnostic only. It is not an eval score and not an",
            "LLM result.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Audit SP64 constrained morphology-compliant Viterbi paths.",
    )
    parser.add_argument(
        "--vocab",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab",
    )
    parser.add_argument("--eval", action="append", default=None)
    parser.add_argument(
        "--plain-text",
        action="append",
        default=[],
        help="Optional raw text file to sample in addition to eval TSVs.",
    )
    parser.add_argument("--max-plain-lines", type=int, default=200)
    parser.add_argument("--top-n", type=int, default=30)
    parser.add_argument("--progress", type=int, default=0)
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_sp64_morph_compliant_path_audit.md",
    )
    args = parser.parse_args(argv)

    vocab_path = Path(args.vocab)
    vocab = BoundaryBiasedVocab.from_vocab_file(vocab_path)
    texts: list[tuple[str, str]] = []
    eval_paths = args.eval or ["data/eval/tr_challenge.tsv"]
    for eval_path in eval_paths:
        path = Path(eval_path)
        texts.extend(load_eval_texts(path, source=path.stem))
    for plain_path in args.plain_text:
        path = Path(plain_path)
        texts.extend(
            load_plain_texts(
                path,
                source=path.stem,
                max_lines=args.max_plain_lines,
            )
        )

    rows = audit_texts(texts=texts, vocab=vocab, progress=args.progress)
    report = format_report(vocab_path=vocab_path, rows=rows, top_n=args.top_n)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
