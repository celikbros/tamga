from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_real_tokenizers import (  # noqa: E402
    RealBaselineSpec,
    canonicalize_external_tokens,
    encode_with_spec,
)
from scripts.compare_tokenizers import BoundaryScore, boundary_score, count_words  # noqa: E402
from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER  # noqa: E402
from scripts.report_protected_spans import is_span_preserved  # noqa: E402
from scripts.report_stress_public import StressCase, load_stress_cases  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.tokenizer import WORD_START  # noqa: E402

SP_WORD_STARTS = ("▁", "â–", "Ä ")


@dataclass(frozen=True)
class Segment:
    surface: str
    starts_after_space: bool


@dataclass(frozen=True)
class ModelCaseResult:
    model_name: str
    category: str
    text: str
    expected: list[str]
    tokens: list[str]
    status: str
    reason: str
    boundary: BoundaryScore

    @property
    def exact_match(self) -> bool:
        return self.status == "ok" and self.tokens == self.expected


@dataclass(frozen=True)
class SummaryRow:
    model_name: str
    status: str
    examples: int
    avg_tokens_example: float
    avg_tokens_word: float
    boundary_f1: float
    exact_match: str
    reason: str = ""


@dataclass(frozen=True)
class ProtectedSummary:
    model_name: str
    status: str
    examples: int
    protected_preserved: int
    protected_total: int
    break_rate: float
    avg_tokens_example: float
    reason: str = ""


def _empty_boundary() -> BoundaryScore:
    return BoundaryScore(
        precision=0.0,
        recall=0.0,
        f1=0.0,
        correct=0,
        predicted=0,
        gold=0,
    )


def strip_sp_word_start(token: str) -> str:
    for prefix in SP_WORD_STARTS:
        if token.startswith(prefix) and len(token) > len(prefix):
            return token[len(prefix) :]
    return token


def raw_soft_marker_segments(text: str) -> list[Segment]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    pieces = analyze_line(text, tokenizer)
    segments: list[Segment] = []
    segment = ""
    starts_after_space = True
    pending_space = True

    def flush() -> None:
        nonlocal segment
        if segment:
            segments.append(Segment(surface=segment, starts_after_space=starts_after_space))
            segment = ""

    for piece in pieces:
        if piece.kind == "whitespace":
            flush()
            pending_space = True
            continue

        if piece.boundary_before == "soft":
            segment += SOFT_MARKER + piece.surface
            continue

        if piece.boundary_before == "hard":
            flush()
            segment = piece.surface
            starts_after_space = pending_space
            pending_space = False
            continue

        segment += piece.surface

    flush()
    return segments


def _append_surface_token(tokens: list[str], surface: str, *, word_start: bool, suffix: bool) -> None:
    if not surface:
        return
    if suffix:
        tokens.append("+" + surface)
    elif word_start:
        tokens.append(WORD_START + surface)
    else:
        tokens.append(surface)


def encode_soft_marker_sentencepiece(text: str, processor) -> list[str]:
    logical_tokens: list[str] = []
    for segment in raw_soft_marker_segments(text):
        pieces = processor.EncodeAsPieces(segment.surface)
        first_output_in_segment = True
        suffix_mode = False
        for piece in pieces:
            surface = strip_sp_word_start(piece)
            if not surface:
                continue
            parts = surface.split(SOFT_MARKER)
            for index, part in enumerate(parts):
                if index > 0:
                    suffix_mode = True
                _append_surface_token(
                    logical_tokens,
                    part,
                    word_start=first_output_in_segment and segment.starts_after_space and not suffix_mode,
                    suffix=suffix_mode,
                )
                if part:
                    first_output_in_segment = False
    return logical_tokens


def _micro_boundary(results: list[ModelCaseResult]) -> BoundaryScore:
    correct = 0
    predicted = 0
    gold = 0
    for result in results:
        if result.status != "ok":
            continue
        correct += result.boundary.correct
        predicted += result.boundary.predicted
        gold += result.boundary.gold
    precision = correct / predicted if predicted else (1.0 if gold == 0 else 0.0)
    recall = correct / gold if gold else (1.0 if predicted == 0 else 0.0)
    denominator = precision + recall
    f1 = 0.0 if denominator == 0 else 2 * precision * recall / denominator
    return BoundaryScore(precision, recall, f1, correct, predicted, gold)


def summarize_results(results: list[ModelCaseResult]) -> SummaryRow:
    if not results:
        return SummaryRow("", "skipped", 0, 0.0, 0.0, 0.0, "0/0")
    model_name = results[0].model_name
    status = "ok" if all(result.status == "ok" for result in results) else "skipped"
    reason = next((result.reason for result in results if result.reason), "")
    if status != "ok":
        return SummaryRow(model_name, status, len(results), 0.0, 0.0, 0.0, "0/0", reason)
    token_count = sum(len(result.tokens) for result in results)
    word_count = sum(count_words(result.text) for result in results)
    boundary = _micro_boundary(results)
    exact = sum(result.exact_match for result in results)
    return SummaryRow(
        model_name=model_name,
        status=status,
        examples=len(results),
        avg_tokens_example=token_count / len(results) if results else 0.0,
        avg_tokens_word=token_count / word_count if word_count else 0.0,
        boundary_f1=boundary.f1,
        exact_match=f"{exact}/{len(results)}",
        reason=reason,
    )


def evaluate_cases_for_models(
    cases: list[EvalCase],
    *,
    processor,
    sp64_model: Path,
) -> dict[str, list[ModelCaseResult]]:
    specs = [
        RealBaselineSpec(name="custom_tr_morph", kind="custom"),
        RealBaselineSpec(name="sp_unigram_64000_train_only", kind="sentencepiece", value=str(sp64_model)),
    ]
    output: dict[str, list[ModelCaseResult]] = {spec.name: [] for spec in specs}
    output["protected_hard_soft_marker_raw_sp64"] = []

    for case in cases:
        for spec in specs:
            encoding = encode_with_spec(spec, case.text, local_files_only=True)
            boundary_tokens = (
                canonicalize_external_tokens(encoding.tokens)
                if spec.kind == "sentencepiece"
                else encoding.tokens
            )
            output[spec.name].append(
                ModelCaseResult(
                    model_name=spec.name,
                    category=case.category,
                    text=case.text,
                    expected=case.expected,
                    tokens=encoding.tokens,
                    status=encoding.status,
                    reason=encoding.reason,
                    boundary=(
                        boundary_score(boundary_tokens, case.expected)
                        if encoding.status == "ok"
                        else _empty_boundary()
                    ),
                )
            )

        tokens = encode_soft_marker_sentencepiece(case.text, processor)
        output["protected_hard_soft_marker_raw_sp64"].append(
            ModelCaseResult(
                model_name="protected_hard_soft_marker_raw_sp64",
                category=case.category,
                text=case.text,
                expected=case.expected,
                tokens=tokens,
                status="ok",
                reason="marker-aware boundary diagnostic",
                boundary=boundary_score(tokens, case.expected),
            )
        )

    return output


def protected_summary_for_model(
    *,
    model_name: str,
    cases: list[StressCase],
    tokens_by_text: dict[str, list[str]],
) -> ProtectedSummary:
    protected_total = 0
    protected_preserved = 0
    token_count = 0
    for case in cases:
        tokens = tokens_by_text[case.text]
        token_count += len(tokens)
        for span in case.protected_spans:
            protected_total += 1
            if is_span_preserved(span, tokens):
                protected_preserved += 1
    broken = protected_total - protected_preserved
    return ProtectedSummary(
        model_name=model_name,
        status="ok",
        examples=len(cases),
        protected_preserved=protected_preserved,
        protected_total=protected_total,
        break_rate=broken / protected_total if protected_total else 0.0,
        avg_tokens_example=token_count / len(cases) if cases else 0.0,
    )


def evaluate_protected(
    cases: list[StressCase],
    *,
    processor,
    sp64_model: Path,
) -> list[ProtectedSummary]:
    custom = TurkishTokenizer()
    sp_spec = RealBaselineSpec(
        name="sp_unigram_64000_train_only",
        kind="sentencepiece",
        value=str(sp64_model),
    )
    token_maps = {
        "custom_tr_morph": {case.text: custom.encode(case.text) for case in cases},
        "sp_unigram_64000_train_only": {
            case.text: encode_with_spec(sp_spec, case.text, local_files_only=True).tokens
            for case in cases
        },
        "protected_hard_soft_marker_raw_sp64": {
            case.text: encode_soft_marker_sentencepiece(case.text, processor)
            for case in cases
        },
    }
    return [
        protected_summary_for_model(
            model_name=model_name,
            cases=cases,
            tokens_by_text=tokens_by_text,
        )
        for model_name, tokens_by_text in token_maps.items()
    ]


def category_f1(results: list[ModelCaseResult]) -> dict[str, float]:
    grouped: dict[str, list[ModelCaseResult]] = {}
    for result in results:
        grouped.setdefault(result.category, []).append(result)
    return {
        category: _micro_boundary(category_results).f1
        for category, category_results in sorted(grouped.items())
    }


def format_eval_table(title: str, model_results: dict[str, list[ModelCaseResult]]) -> list[str]:
    rows = [summarize_results(results) for results in model_results.values()]
    lines = [
        f"## {title}",
        "",
        "| Model | Status | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.model_name} | {row.status} | {row.examples} | "
            f"{row.avg_tokens_example:.4f} | {row.avg_tokens_word:.4f} | "
            f"{row.boundary_f1:.4f} | {row.exact_match} | {row.reason} |"
        )

    categories = sorted(
        {
            result.category
            for results in model_results.values()
            for result in results
        }
    )
    if categories:
        lines.extend(["", "### Category F1", ""])
        model_names = list(model_results.keys())
        lines.append("| Category | " + " | ".join(model_names) + " |")
        lines.append("| --- | " + " | ".join("---:" for _ in model_names) + " |")
        scores = {
            model_name: category_f1(results)
            for model_name, results in model_results.items()
        }
        for category in categories:
            lines.append(
                f"| {category} | "
                + " | ".join(
                    f"{scores[model_name].get(category, 0.0):.4f}"
                    for model_name in model_names
                )
                + " |"
            )
    return lines


def format_protected_table(rows: list[ProtectedSummary]) -> list[str]:
    lines = [
        "## Protected Span Stress",
        "",
        "| Model | Status | Examples | Protected preserved | Break rate | Avg tokens/example | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.model_name} | {row.status} | {row.examples} | "
            f"{row.protected_preserved}/{row.protected_total} | "
            f"{row.break_rate:.4f} | {row.avg_tokens_example:.4f} | {row.reason} |"
        )
    return lines


def format_report(
    *,
    candidate_model: Path,
    sp64_model: Path,
    gold_results: dict[str, list[ModelCaseResult]],
    challenge_results: dict[str, list[ModelCaseResult]],
    multilingual_results: dict[str, list[ModelCaseResult]],
    protected_rows: list[ProtectedSummary],
) -> str:
    lines = [
        "# v2.0 Raw-Soft-Marker Candidate Intrinsic Eval",
        "",
        f"Candidate model: `{candidate_model.as_posix()}`",
        f"SP64 reference: `{sp64_model.as_posix()}`",
        "",
        "This is an intrinsic visible-set diagnostic. It is not hidden eval and",
        "not an LLM result. Candidate boundary F1 is marker-aware: private-use",
        "soft markers inside SentencePiece pieces are interpreted as morphology",
        "boundary hints for this diagnostic.",
        "",
    ]
    lines.extend(format_eval_table("Gold Expanded", gold_results))
    lines.append("")
    lines.extend(format_eval_table("Challenge", challenge_results))
    lines.append("")
    lines.extend(format_eval_table("Multilingual Smoke", multilingual_results))
    lines.append("")
    lines.extend(format_protected_table(protected_rows))
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "Proceed to tiny-LM only if token pressure, protected spans, and visible",
            "boundary diagnostics are all acceptable. A compression pass alone is",
            "not enough.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Evaluate v2 soft-marker candidate intrinsic behavior.")
    parser.add_argument(
        "--candidate-model",
        default="artifacts/private/v2_0_candidate_sentencepiece/protected_hard_soft_marker_raw_sp64_unigram_64000.model",
    )
    parser.add_argument(
        "--sp64-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument("--gold", default="data/eval/tr_gold_expanded.tsv")
    parser.add_argument("--challenge", default="data/eval/tr_challenge.tsv")
    parser.add_argument("--multilingual", default="data/eval/multilingual_smoke.tsv")
    parser.add_argument("--stress", default="data/eval/tr_stress_public.tsv")
    parser.add_argument("--report-out", default="artifacts/v2_0_raw_soft_marker_candidate_intrinsic_eval.md")
    args = parser.parse_args(argv)

    import sentencepiece as spm  # type: ignore[import-not-found]

    processor = spm.SentencePieceProcessor()
    processor.Load(str(args.candidate_model))

    candidate_model = Path(args.candidate_model)
    sp64_model = Path(args.sp64_model)
    gold_results = evaluate_cases_for_models(
        load_cases(args.gold),
        processor=processor,
        sp64_model=sp64_model,
    )
    challenge_results = evaluate_cases_for_models(
        load_cases(args.challenge),
        processor=processor,
        sp64_model=sp64_model,
    )
    multilingual_results = evaluate_cases_for_models(
        load_cases(args.multilingual),
        processor=processor,
        sp64_model=sp64_model,
    )
    protected_rows = evaluate_protected(
        load_stress_cases(args.stress),
        processor=processor,
        sp64_model=sp64_model,
    )
    report = format_report(
        candidate_model=candidate_model,
        sp64_model=sp64_model,
        gold_results=gold_results,
        challenge_results=challenge_results,
        multilingual_results=multilingual_results,
        protected_rows=protected_rows,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
