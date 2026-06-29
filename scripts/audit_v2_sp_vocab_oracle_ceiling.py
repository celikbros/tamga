from __future__ import annotations

from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_v2_sp64_morph_compliant_paths import (  # noqa: E402
    constrained_viterbi_segment,
)
from scripts.compare_tokenizers import BoundaryScore, boundary_score, count_words  # noqa: E402
from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    append_suffix_surface,
    append_word_surface,
)
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
class OracleState:
    score: float
    entries: tuple[VocabEntry, ...]


@dataclass(frozen=True)
class CaseOracleResult:
    model_name: str
    category: str
    text: str
    expected: list[str]
    actual: list[str]
    boundary: BoundaryScore
    crossed_boundaries: int
    teacher_boundaries: int

    @property
    def exact_match(self) -> bool:
        return self.actual == self.expected


@dataclass(frozen=True)
class Summary:
    model_name: str
    examples: int
    avg_tokens_example: float
    avg_tokens_word: float
    boundary_f1: float
    exact_match: str
    crossed_boundaries: int
    teacher_boundaries: int


def _segment_f1(correct: int, predicted: int, gold: int) -> float:
    if predicted == 0 and gold == 0:
        return 1.0
    denominator = predicted + gold
    return 0.0 if denominator == 0 else (2.0 * correct / denominator)


def oracle_best_f1_segment(
    surface: str,
    *,
    boundaries: tuple[int, ...],
    vocab: BoundaryBiasedVocab,
    fallback_score: float = -100.0,
) -> SegmentResult:
    if not surface:
        return SegmentResult((), (), 0, 0, 0.0)

    gold = set(boundaries)
    gold_count = len(gold)
    states: list[dict[tuple[int, int, int], OracleState]] = [
        {} for _ in range(len(surface) + 1)
    ]
    states[0][(0, 0, 0)] = OracleState(score=0.0, entries=())

    for position in range(len(surface)):
        if not states[position]:
            continue
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
        for (correct, predicted, crossed), state in list(states[position].items()):
            for entry in candidates:
                end = position + len(entry.surface)
                is_internal_boundary = end < len(surface)
                correct_inc = 1 if is_internal_boundary and end in gold else 0
                predicted_inc = 1 if is_internal_boundary else 0
                crossed_inc = crossed_boundary_count(position, end, boundaries)
                key = (
                    correct + correct_inc,
                    predicted + predicted_inc,
                    crossed + crossed_inc,
                )
                score = state.score + entry.score
                previous = states[end].get(key)
                entries = (*state.entries, entry)
                if previous is None or score > previous.score or (
                    math.isclose(score, previous.score, rel_tol=0.0, abs_tol=1e-9)
                    and len(entries) < len(previous.entries)
                ):
                    states[end][key] = OracleState(score=score, entries=entries)

    if not states[-1]:
        fallback = tuple(surface)
        return SegmentResult(
            surfaces=fallback,
            sp_pieces=fallback,
            model_token_count=len(fallback),
            crossed_boundaries=0,
            score=fallback_score * len(surface),
        )

    best_key, best_state = max(
        states[-1].items(),
        key=lambda item: (
            _segment_f1(item[0][0], item[0][1], gold_count),
            item[0][0],
            -item[0][1],
            -item[0][2],
            item[1].score,
        ),
    )
    correct, predicted, crossed = best_key
    _ = correct, predicted
    return SegmentResult(
        surfaces=tuple(entry.surface for entry in best_state.entries),
        sp_pieces=tuple(entry.piece for entry in best_state.entries),
        model_token_count=len(best_state.entries),
        crossed_boundaries=crossed,
        score=best_state.score,
    )


def append_segment_tokens(
    tokens: list[str],
    *,
    result: SegmentResult,
    starts_after_space: bool,
) -> None:
    for index, surface in enumerate(result.surfaces):
        append_word_surface(tokens, surface, word_start=index == 0 and starts_after_space)


def encode_case(
    text: str,
    *,
    vocab: BoundaryBiasedVocab,
    mode: str,
) -> tuple[list[str], int, int]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    pieces = analyze_line(text, tokenizer)
    tokens: list[str] = []
    segment = ""
    boundaries: list[int] = []
    starts_after_space = True
    pending_space = True
    crossed_boundaries = 0
    teacher_boundaries = 0

    def flush() -> None:
        nonlocal segment, boundaries, crossed_boundaries, teacher_boundaries
        if not segment:
            return
        boundary_tuple = tuple(boundaries)
        teacher_boundaries += len(boundary_tuple)
        if mode == "lambda0":
            result = viterbi_segment(
                segment,
                boundaries=boundary_tuple,
                vocab=vocab,
                boundary_lambda=0.0,
            )
        elif mode == "no_cross":
            result = constrained_viterbi_segment(
                segment,
                boundaries=boundary_tuple,
                vocab=vocab,
            )
        elif mode == "oracle_best_f1":
            result = oracle_best_f1_segment(
                segment,
                boundaries=boundary_tuple,
                vocab=vocab,
            )
        else:
            raise ValueError(f"unknown mode: {mode}")
        crossed_boundaries += result.crossed_boundaries
        append_segment_tokens(
            tokens,
            result=result,
            starts_after_space=starts_after_space,
        )
        segment = ""
        boundaries = []

    for piece in pieces:
        if piece.kind == "whitespace":
            flush()
            pending_space = True
            continue
        if piece.kind.startswith("protected:"):
            flush()
            append_word_surface(tokens, piece.surface, word_start=pending_space)
            pending_space = False
            continue
        if piece.kind == "apostrophe":
            flush()
            tokens.append(piece.surface)
            pending_space = False
            continue
        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            append_suffix_surface(tokens, piece.surface)
            pending_space = False
            continue
        if piece.boundary_before == "soft":
            boundaries.append(len(segment))
            segment += piece.surface
            continue
        if piece.boundary_before == "hard":
            flush()
            segment = piece.surface
            starts_after_space = pending_space
            pending_space = False
            continue
        segment += piece.surface
    flush()
    return tokens, crossed_boundaries, teacher_boundaries


def evaluate_mode(
    *,
    cases: list[EvalCase],
    vocab: BoundaryBiasedVocab,
    mode: str,
) -> list[CaseOracleResult]:
    rows: list[CaseOracleResult] = []
    for case in cases:
        actual, crossed, teacher_boundaries = encode_case(
            case.text,
            vocab=vocab,
            mode=mode,
        )
        rows.append(
            CaseOracleResult(
                model_name=mode,
                category=case.category,
                text=case.text,
                expected=case.expected,
                actual=actual,
                boundary=boundary_score(actual, case.expected),
                crossed_boundaries=crossed,
                teacher_boundaries=teacher_boundaries,
            )
        )
    return rows


def summarize(results: list[CaseOracleResult]) -> Summary:
    boundary = micro_boundary(results)
    examples = len(results)
    tokens = sum(len(row.actual) for row in results)
    words = sum(count_words(row.text) for row in results)
    exact = sum(row.exact_match for row in results)
    return Summary(
        model_name=results[0].model_name if results else "",
        examples=examples,
        avg_tokens_example=tokens / examples if examples else 0.0,
        avg_tokens_word=tokens / words if words else 0.0,
        boundary_f1=boundary.f1,
        exact_match=f"{exact}/{examples}",
        crossed_boundaries=sum(row.crossed_boundaries for row in results),
        teacher_boundaries=sum(row.teacher_boundaries for row in results),
    )


def micro_boundary(results: list[CaseOracleResult]) -> BoundaryScore:
    correct = sum(row.boundary.correct for row in results)
    predicted = sum(row.boundary.predicted for row in results)
    gold = sum(row.boundary.gold for row in results)
    precision = correct / predicted if predicted else (1.0 if gold == 0 else 0.0)
    recall = correct / gold if gold else (1.0 if predicted == 0 else 0.0)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return BoundaryScore(
        precision=precision,
        recall=recall,
        f1=f1,
        correct=correct,
        predicted=predicted,
        gold=gold,
    )


def category_f1(results: list[CaseOracleResult]) -> dict[str, float]:
    grouped: dict[str, list[CaseOracleResult]] = {}
    for row in results:
        grouped.setdefault(row.category, []).append(row)
    return {
        category: micro_boundary(items).f1
        for category, items in sorted(grouped.items())
    }


def format_report(
    *,
    eval_path: Path,
    vocab_path: Path,
    results_by_mode: dict[str, list[CaseOracleResult]],
) -> str:
    summaries = [summarize(rows) for rows in results_by_mode.values()]
    lines = [
        "# v2.0 SP Vocab Oracle Ceiling Audit",
        "",
        f"Eval: `{eval_path.as_posix()}`",
        f"Vocab: `{vocab_path.as_posix()}`",
        "",
        "This diagnostic estimates whether the existing SP vocabulary can express",
        "morphology-aligned paths before we invest in a custom trainer.",
        "",
        "Modes:",
        "",
        "- `lambda0`: in-family best-score lattice path with no boundary penalty.",
        "- `no_cross`: best-score path that does not cross teacher soft boundaries.",
        "- `oracle_best_f1`: path chosen to maximize internal teacher-boundary F1",
        "  within each segment, with score only as a tie-breaker.",
        "",
        "## Summary",
        "",
        "| Mode | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 vs eval | Exact match | Crossed teacher boundaries | Teacher boundaries |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        lines.append(
            f"| `{row.model_name}` | {row.examples} | {row.avg_tokens_example:.4f} | "
            f"{row.avg_tokens_word:.4f} | {row.boundary_f1:.4f} | "
            f"{row.exact_match} | {row.crossed_boundaries} | {row.teacher_boundaries} |"
        )

    lines.extend(["", "## Category F1", ""])
    modes = list(results_by_mode)
    categories = sorted(
        {row.category for rows in results_by_mode.values() for row in rows}
    )
    scores = {mode: category_f1(rows) for mode, rows in results_by_mode.items()}
    lines.append("| Category | " + " | ".join(f"`{mode}`" for mode in modes) + " |")
    lines.append("| --- | " + " | ".join("---:" for _ in modes) + " |")
    for category in categories:
        lines.append(
            f"| {category} | "
            + " | ".join(f"{scores[mode].get(category, 0.0):.4f}" for mode in modes)
            + " |"
        )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            "If `oracle_best_f1` is still close to SP64, score-side mechanisms cannot",
            "recover much morphology signal. If it is much higher, the vocabulary",
            "already contains useful paths and score/objective work is justified.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Estimate SP vocab morphology oracle ceiling.")
    parser.add_argument("--eval", default="data/eval/tr_challenge.tsv")
    parser.add_argument(
        "--vocab",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_sp_vocab_oracle_ceiling_challenge.md",
    )
    args = parser.parse_args(argv)

    eval_path = Path(args.eval)
    vocab_path = Path(args.vocab)
    cases = load_cases(eval_path)
    vocab = BoundaryBiasedVocab.from_vocab_file(vocab_path)
    results_by_mode = {
        mode: evaluate_mode(cases=cases, vocab=vocab, mode=mode)
        for mode in ("lambda0", "no_cross", "oracle_best_f1")
    }
    report = format_report(
        eval_path=eval_path,
        vocab_path=vocab_path,
        results_by_mode=results_by_mode,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
