from __future__ import annotations

from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import BoundaryScore, boundary_score, count_words  # noqa: E402
from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    PrototypeEncoding,
    append_sp_encoded_segment,
    append_suffix_surface,
    append_word_surface,
    encode_protected_surface,
    load_sp_processor,
    selected_piece_strings,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.report_protected_spans import is_span_preserved  # noqa: E402
from scripts.report_stress_public import StressCase, load_stress_cases  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402

SP_WORD_START = "\u2581"
SKIP_PIECES = {"<unk>", "<s>", "</s>", "<pad>"}


@dataclass(frozen=True)
class VocabEntry:
    piece: str
    surface: str
    score: float
    word_start: bool


@dataclass(frozen=True)
class SegmentResult:
    surfaces: tuple[str, ...]
    sp_pieces: tuple[str, ...]
    model_token_count: int
    crossed_boundaries: int
    score: float


@dataclass(frozen=True)
class BoundaryBiasedVocab:
    entries_by_surface: dict[str, VocabEntry]
    start_entries_by_surface: dict[str, VocabEntry]
    max_entry_len: int
    max_start_entry_len: int

    @classmethod
    def from_vocab_file(cls, path: Path) -> "BoundaryBiasedVocab":
        regular: dict[str, VocabEntry] = {}
        start: dict[str, VocabEntry] = {}
        with path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.rstrip("\n")
                if not line:
                    continue
                fields = line.split("\t")
                if len(fields) < 2:
                    raise ValueError(f"{path}:{line_number}: expected piece<TAB>score")
                piece = fields[0]
                if piece in SKIP_PIECES or SP_WORD_START in piece[1:]:
                    continue
                try:
                    score = float(fields[1])
                except ValueError as exc:
                    raise ValueError(f"{path}:{line_number}: invalid score") from exc

                word_start = piece.startswith(SP_WORD_START)
                surface = piece[1:] if word_start else piece
                if not surface:
                    continue
                entry = VocabEntry(
                    piece=piece,
                    surface=surface,
                    score=score,
                    word_start=word_start,
                )
                bucket = start if word_start else regular
                previous = bucket.get(surface)
                if previous is None or entry.score > previous.score:
                    bucket[surface] = entry

        return cls(
            entries_by_surface=regular,
            start_entries_by_surface=start,
            max_entry_len=max((len(surface) for surface in regular), default=0),
            max_start_entry_len=max((len(surface) for surface in start), default=0),
        )

    def candidates_at(self, surface: str, position: int) -> list[VocabEntry]:
        if position >= len(surface):
            return []
        matches: list[VocabEntry] = []
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


@dataclass(frozen=True)
class ModelCaseResult:
    model_name: str
    category: str
    text: str
    expected: list[str]
    logical_tokens: list[str]
    model_token_count: int
    boundary: BoundaryScore
    crossed_boundaries: int

    @property
    def exact_match(self) -> bool:
        return self.logical_tokens == self.expected


@dataclass(frozen=True)
class EvalSummary:
    model_name: str
    dataset: str
    examples: int
    avg_logical_tokens_example: float
    avg_model_tokens_example: float
    avg_model_tokens_word: float
    boundary_f1: float
    exact_match: str
    crossed_boundaries: int


@dataclass(frozen=True)
class ProtectedSummary:
    model_name: str
    examples: int
    protected_preserved: int
    protected_total: int
    avg_model_tokens_example: float

    @property
    def break_rate(self) -> float:
        if self.protected_total == 0:
            return 0.0
        return 1.0 - (self.protected_preserved / self.protected_total)


@dataclass(frozen=True)
class SplitPressureSummary:
    model_name: str
    split: str
    lines: int
    raw_bytes: int
    model_tokens: int

    @property
    def tokens_per_raw_byte(self) -> float:
        return self.model_tokens / self.raw_bytes if self.raw_bytes else 0.0


def crossed_boundary_count(start: int, end: int, boundaries: tuple[int, ...]) -> int:
    return sum(1 for boundary in boundaries if start < boundary < end)


def viterbi_segment(
    surface: str,
    *,
    boundaries: tuple[int, ...],
    vocab: BoundaryBiasedVocab,
    boundary_lambda: float,
    fallback_score: float = -100.0,
) -> SegmentResult:
    if not surface:
        return SegmentResult((), (), 0, 0, 0.0)

    best: list[tuple[float, tuple[VocabEntry, ...], int] | None] = [None] * (
        len(surface) + 1
    )
    best[0] = (0.0, (), 0)

    for position in range(len(surface)):
        state = best[position]
        if state is None:
            continue
        current_score, current_tokens, current_crossed = state
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
            crossed = crossed_boundary_count(position, end, boundaries)
            score = current_score + entry.score - boundary_lambda * crossed
            tokens = (*current_tokens, entry)
            total_crossed = current_crossed + crossed
            previous = best[end]
            if previous is None or _is_better_path(score, tokens, previous):
                best[end] = (score, tokens, total_crossed)

    final = best[-1]
    if final is None:
        fallback = tuple(surface)
        return SegmentResult(fallback, fallback, len(fallback), 0, fallback_score * len(surface))
    score, entries, crossed = final
    return SegmentResult(
        surfaces=tuple(entry.surface for entry in entries),
        sp_pieces=tuple(entry.piece for entry in entries),
        model_token_count=len(entries),
        crossed_boundaries=crossed,
        score=score,
    )


def _is_better_path(
    score: float,
    tokens: tuple[VocabEntry, ...],
    previous: tuple[float, tuple[VocabEntry, ...], int],
) -> bool:
    previous_score, previous_tokens, _previous_crossed = previous
    if not math.isclose(score, previous_score, rel_tol=0.0, abs_tol=1e-9):
        return score > previous_score
    return len(tokens) < len(previous_tokens)


def append_biased_segment(
    *,
    logical_tokens: list[str],
    surface: str,
    starts_after_space: bool,
    soft_boundaries: tuple[int, ...],
    vocab: BoundaryBiasedVocab,
    boundary_lambda: float,
) -> SegmentResult:
    result = viterbi_segment(
        surface,
        boundaries=soft_boundaries,
        vocab=vocab,
        boundary_lambda=boundary_lambda,
    )
    for index, piece_surface in enumerate(result.surfaces):
        append_word_surface(
            logical_tokens,
            piece_surface,
            word_start=index == 0 and starts_after_space,
        )
    return result


def encode_boundary_biased(
    text: str,
    *,
    processor,
    vocab: BoundaryBiasedVocab,
    selected_pieces: list[str],
    boundary_lambda: float,
    numeric_sp_passthrough: bool,
) -> PrototypeEncoding:
    pieces = analyze_line(text, TurkishTokenizer(preserve_whitespace=True))
    logical_tokens: list[str] = []
    segment = ""
    segment_boundaries: list[int] = []
    starts_after_space = True
    pending_space = True
    model_token_count = 0
    protected_piece_tokens = 0
    protected_byte_tokens = 0

    def flush() -> None:
        nonlocal segment, model_token_count, segment_boundaries
        if not segment:
            return
        result = append_biased_segment(
            logical_tokens=logical_tokens,
            surface=segment,
            starts_after_space=starts_after_space,
            soft_boundaries=tuple(segment_boundaries),
            vocab=vocab,
            boundary_lambda=boundary_lambda,
        )
        model_token_count += result.model_token_count
        segment = ""
        segment_boundaries = []

    for piece in pieces:
        if piece.kind == "whitespace":
            flush()
            pending_space = True
            continue

        if piece.kind.startswith("protected:"):
            flush()
            append_word_surface(logical_tokens, piece.surface, word_start=pending_space)
            if numeric_sp_passthrough and piece.kind == "protected:numeric_like":
                model_token_count += len(processor.EncodeAsPieces(piece.surface))
            else:
                piece_count, byte_count = encode_protected_surface(piece.surface, selected_pieces)
                protected_piece_tokens += piece_count
                protected_byte_tokens += byte_count
                model_token_count += piece_count + byte_count
            pending_space = False
            continue

        if piece.kind == "apostrophe":
            flush()
            logical_tokens.append(piece.surface)
            model_token_count += len(processor.EncodeAsPieces(piece.surface))
            pending_space = False
            continue

        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            append_suffix_surface(logical_tokens, piece.surface)
            model_token_count += len(processor.EncodeAsPieces(piece.surface))
            pending_space = False
            continue

        if piece.boundary_before == "soft":
            segment_boundaries.append(len(segment))
            segment += piece.surface
            continue

        if piece.boundary_before == "hard":
            flush()
            segment = piece.surface
            segment_boundaries = []
            starts_after_space = pending_space
            pending_space = False
            continue

        segment += piece.surface

    flush()
    return PrototypeEncoding(
        logical_tokens=logical_tokens,
        model_token_count=model_token_count,
        protected_piece_tokens=protected_piece_tokens,
        protected_byte_tokens=protected_byte_tokens,
    )


def encode_reference_finite_numeric(
    text: str,
    *,
    processor,
    selected_pieces: list[str],
    numeric_sp_passthrough: bool,
) -> PrototypeEncoding:
    pieces = analyze_line(text, TurkishTokenizer(preserve_whitespace=True))
    logical_tokens: list[str] = []
    segment = ""
    starts_after_space = True
    pending_space = True
    model_token_count = 0
    protected_piece_tokens = 0
    protected_byte_tokens = 0

    def flush() -> None:
        nonlocal segment, model_token_count
        if segment:
            model_token_count += append_sp_encoded_segment(
                logical_tokens=logical_tokens,
                surface=segment,
                starts_after_space=starts_after_space,
                processor=processor,
            )
            segment = ""

    for piece in pieces:
        if piece.kind == "whitespace":
            flush()
            pending_space = True
            continue

        if piece.kind.startswith("protected:"):
            flush()
            append_word_surface(logical_tokens, piece.surface, word_start=pending_space)
            if numeric_sp_passthrough and piece.kind == "protected:numeric_like":
                model_token_count += len(processor.EncodeAsPieces(piece.surface))
            else:
                piece_count, byte_count = encode_protected_surface(piece.surface, selected_pieces)
                protected_piece_tokens += piece_count
                protected_byte_tokens += byte_count
                model_token_count += piece_count + byte_count
            pending_space = False
            continue

        if piece.kind == "apostrophe":
            flush()
            logical_tokens.append(piece.surface)
            model_token_count += len(processor.EncodeAsPieces(piece.surface))
            pending_space = False
            continue

        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            append_suffix_surface(logical_tokens, piece.surface)
            model_token_count += len(processor.EncodeAsPieces(piece.surface))
            pending_space = False
            continue

        if piece.boundary_before == "soft":
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
    return PrototypeEncoding(
        logical_tokens=logical_tokens,
        model_token_count=model_token_count,
        protected_piece_tokens=protected_piece_tokens,
        protected_byte_tokens=protected_byte_tokens,
    )


def evaluate_eval_cases(
    *,
    model_name: str,
    cases: list[EvalCase],
    encoder,
) -> list[ModelCaseResult]:
    results: list[ModelCaseResult] = []
    for case in cases:
        encoding = encoder(case.text)
        score = boundary_score(encoding.logical_tokens, case.expected)
        results.append(
            ModelCaseResult(
                model_name=model_name,
                category=case.category,
                text=case.text,
                expected=case.expected,
                logical_tokens=encoding.logical_tokens,
                model_token_count=encoding.model_token_count,
                boundary=score,
                crossed_boundaries=0,
            )
        )
    return results


def micro_boundary(results: list[ModelCaseResult]) -> BoundaryScore:
    correct = sum(result.boundary.correct for result in results)
    predicted = sum(result.boundary.predicted for result in results)
    gold = sum(result.boundary.gold for result in results)
    precision = correct / predicted if predicted else (1.0 if gold == 0 else 0.0)
    recall = correct / gold if gold else (1.0 if predicted == 0 else 0.0)
    denominator = precision + recall
    f1 = 0.0 if denominator == 0 else 2 * precision * recall / denominator
    return BoundaryScore(precision, recall, f1, correct, predicted, gold)


def summarize_eval(
    *,
    model_name: str,
    dataset: str,
    results: list[ModelCaseResult],
) -> EvalSummary:
    examples = len(results)
    words = sum(count_words(result.text) for result in results)
    model_tokens = sum(result.model_token_count for result in results)
    logical_tokens = sum(len(result.logical_tokens) for result in results)
    exact = sum(result.exact_match for result in results)
    return EvalSummary(
        model_name=model_name,
        dataset=dataset,
        examples=examples,
        avg_logical_tokens_example=logical_tokens / examples if examples else 0.0,
        avg_model_tokens_example=model_tokens / examples if examples else 0.0,
        avg_model_tokens_word=model_tokens / words if words else 0.0,
        boundary_f1=micro_boundary(results).f1,
        exact_match=f"{exact}/{examples}",
        crossed_boundaries=sum(result.crossed_boundaries for result in results),
    )


def evaluate_protected_cases(
    *,
    model_name: str,
    cases: list[StressCase],
    encoder,
) -> ProtectedSummary:
    preserved = 0
    total = 0
    model_tokens = 0
    for case in cases:
        encoding = encoder(case.text)
        model_tokens += encoding.model_token_count
        for span in case.protected_spans:
            total += 1
            if is_span_preserved(span, encoding.logical_tokens):
                preserved += 1
    return ProtectedSummary(
        model_name=model_name,
        examples=len(cases),
        protected_preserved=preserved,
        protected_total=total,
        avg_model_tokens_example=model_tokens / len(cases) if cases else 0.0,
    )


def evaluate_split_pressure(
    *,
    model_name: str,
    split: str,
    path: Path,
    encoder,
    progress: int,
) -> SplitPressureSummary:
    lines = 0
    raw_bytes = 0
    model_tokens = 0
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            text = raw_line.rstrip("\n")
            encoding = encoder(text)
            lines += 1
            raw_bytes += len(text.encode("utf-8"))
            model_tokens += encoding.model_token_count
            if progress > 0 and lines % progress == 0:
                print(
                    f"pressure {model_name} split={split}: "
                    f"{lines:,} lines tokens={model_tokens:,}",
                    flush=True,
                )
    return SplitPressureSummary(
        model_name=model_name,
        split=split,
        lines=lines,
        raw_bytes=raw_bytes,
        model_tokens=model_tokens,
    )


def category_f1(results: list[ModelCaseResult]) -> dict[str, float]:
    grouped: dict[str, list[ModelCaseResult]] = {}
    for result in results:
        grouped.setdefault(result.category, []).append(result)
    return {
        category: micro_boundary(category_results).f1
        for category, category_results in sorted(grouped.items())
    }


def format_report(
    *,
    sp_model: Path,
    sp_vocab: Path,
    selected_pieces: Path,
    eval_summaries: list[EvalSummary],
    protected_summaries: list[ProtectedSummary],
    split_pressures: list[SplitPressureSummary],
    category_scores: dict[str, dict[str, float]],
    lambdas: list[float],
) -> str:
    lines = [
        "# v2.0 Boundary-Biased Unigram Decode Sweep",
        "",
        f"SP model: `{sp_model.as_posix()}`",
        f"SP vocab: `{sp_vocab.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces.as_posix()}`",
        f"Lambdas: `{', '.join(str(item) for item in lambdas)}`",
        "",
        "This is a diagnostic decode-time sweep. It does not train a tokenizer",
        "and it does not change the SP64 vocabulary. Normal text is decoded with",
        "a Viterbi lattice that subtracts a lambda penalty when a candidate piece",
        "crosses custom-teacher soft morphology boundaries. Protected spans remain",
        "hard-routed; numeric-like protected spans use the SP passthrough floor.",
        "",
        "## Eval Summary",
        "",
        "| Dataset | Model | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in eval_summaries:
        lines.append(
            f"| {row.dataset} | `{row.model_name}` | {row.examples} | "
            f"{row.avg_logical_tokens_example:.4f} | "
            f"{row.avg_model_tokens_example:.4f} | "
            f"{row.avg_model_tokens_word:.4f} | "
            f"{row.boundary_f1:.4f} | {row.exact_match} |"
        )

    lines.extend(
        [
            "",
            "## Protected Stress",
            "",
            "| Model | Examples | Protected preserved | Break rate | Avg model tokens/example |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in protected_summaries:
        lines.append(
            f"| `{row.model_name}` | {row.examples} | "
            f"{row.protected_preserved}/{row.protected_total} | "
            f"{row.break_rate:.4f} | {row.avg_model_tokens_example:.4f} |"
        )

    if split_pressures:
        lines.extend(
            [
                "",
                "## Split Token Pressure",
                "",
                "Counts exclude per-line EOS tokens. Tiny-LM encoded split reports",
                "will be slightly higher by roughly one EOS token per line.",
                "",
                "| Split | Model | Lines | Raw bytes | Model tokens | Tokens/raw byte |",
                "| --- | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in split_pressures:
            lines.append(
                f"| {row.split} | `{row.model_name}` | {row.lines} | "
                f"{row.raw_bytes} | {row.model_tokens} | "
                f"{row.tokens_per_raw_byte:.6f} |"
            )

    lines.extend(["", "## Challenge Category F1", ""])
    model_names = list(category_scores)
    categories = sorted(
        {category for scores in category_scores.values() for category in scores}
    )
    lines.append("| Category | " + " | ".join(f"`{name}`" for name in model_names) + " |")
    lines.append("| --- | " + " | ".join("---:" for _ in model_names) + " |")
    for category in categories:
        lines.append(
            f"| {category} | "
            + " | ".join(
                f"{category_scores[name].get(category, 0.0):.4f}" for name in model_names
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- If increasing lambda raises Challenge F1 at near-flat token pressure,",
            "  decode preference is a real bottleneck and a constrained objective is",
            "  worth building.",
            "- If lambda mostly raises token pressure or fails to improve F1, the",
            "  current SP64 vocabulary/decoder is not easily rescued by boundary",
            "  bias alone.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_lambdas(values: list[str]) -> list[float]:
    lambdas: list[float] = []
    for value in values:
        for part in value.split(","):
            if part.strip():
                lambdas.append(float(part))
    return lambdas


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Sweep decode-time morphology boundary penalties over SP64 Unigram.",
    )
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--sp-vocab",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--gold", default="data/eval/tr_gold_expanded.tsv")
    parser.add_argument("--challenge", default="data/eval/tr_challenge.tsv")
    parser.add_argument("--stress", default="data/eval/tr_stress_public.tsv")
    parser.add_argument(
        "--split-dir",
        default=(
            "artifacts/private/v1_8_local_lm_probe/"
            "celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split"
        ),
    )
    parser.add_argument(
        "--split",
        dest="splits",
        action="append",
        default=[],
        help="Raw split name for token-pressure reporting. Repeatable.",
    )
    parser.add_argument("--pressure-progress", type=int, default=0)
    parser.add_argument(
        "--lambda",
        dest="lambdas",
        action="append",
        default=[],
        help="Boundary penalty lambda. Can be repeated or comma-separated.",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_boundary_biased_unigram_sweep.md",
    )
    args = parser.parse_args(argv)

    lambdas = parse_lambdas(args.lambdas) or [0.0, 0.25, 0.5, 1.0, 2.0, 4.0]
    sp_model = Path(args.sp_model)
    sp_vocab = Path(args.sp_vocab)
    selected_path = Path(args.selected_pieces)
    processor = load_sp_processor(sp_model)
    selected = selected_piece_strings(selected_path)
    vocab = BoundaryBiasedVocab.from_vocab_file(sp_vocab)

    gold_cases = load_cases(args.gold)
    challenge_cases = load_cases(args.challenge)
    stress_cases = load_stress_cases(args.stress)
    pressure_splits = args.splits or ["valid", "test"]
    split_dir = Path(args.split_dir) if args.split_dir else None

    models: list[tuple[str, object]] = []
    models.append(
        (
            "finite_protected_sp64_numeric_sp_floor",
            lambda text: encode_reference_finite_numeric(
                text,
                processor=processor,
                selected_pieces=selected,
                numeric_sp_passthrough=True,
            ),
        )
    )
    for boundary_lambda in lambdas:
        name = f"boundary_biased_lambda_{boundary_lambda:g}"
        models.append(
            (
                name,
                lambda text, boundary_lambda=boundary_lambda: encode_boundary_biased(
                    text,
                    processor=processor,
                    vocab=vocab,
                    selected_pieces=selected,
                    boundary_lambda=boundary_lambda,
                    numeric_sp_passthrough=True,
                ),
            )
        )

    eval_summaries: list[EvalSummary] = []
    protected_summaries: list[ProtectedSummary] = []
    split_pressures: list[SplitPressureSummary] = []
    category_scores: dict[str, dict[str, float]] = {}
    for model_name, encoder in models:
        gold_results = evaluate_eval_cases(
            model_name=model_name,
            cases=gold_cases,
            encoder=encoder,
        )
        challenge_results = evaluate_eval_cases(
            model_name=model_name,
            cases=challenge_cases,
            encoder=encoder,
        )
        eval_summaries.append(
            summarize_eval(model_name=model_name, dataset="gold", results=gold_results)
        )
        eval_summaries.append(
            summarize_eval(
                model_name=model_name,
                dataset="challenge",
                results=challenge_results,
            )
        )
        protected_summaries.append(
            evaluate_protected_cases(
                model_name=model_name,
                cases=stress_cases,
                encoder=encoder,
            )
        )
        category_scores[model_name] = category_f1(challenge_results)
        if split_dir is not None:
            for split in pressure_splits:
                split_path = split_dir / f"{split}.txt"
                if not split_path.exists():
                    raise FileNotFoundError(split_path)
                split_pressures.append(
                    evaluate_split_pressure(
                        model_name=model_name,
                        split=split,
                        path=split_path,
                        encoder=encoder,
                        progress=args.pressure_progress,
                    )
                )

    report = format_report(
        sp_model=sp_model,
        sp_vocab=sp_vocab,
        selected_pieces=selected_path,
        eval_summaries=eval_summaries,
        protected_summaries=protected_summaries,
        split_pressures=split_pressures,
        category_scores=category_scores,
        lambdas=lambdas,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
