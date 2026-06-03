from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
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
from scripts.evaluate_v2_protected_encoder import load_selected_pieces  # noqa: E402
from scripts.materialize_v2_soft_morph_artifacts import Piece, analyze_line  # noqa: E402
from scripts.report_protected_spans import is_span_preserved  # noqa: E402
from scripts.report_stress_public import StressCase, load_stress_cases  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.tokenizer import WORD_START  # noqa: E402


SP_WORD_STARTS = ("\u2581", "â–", "Ã¢â€“Â", "Ã„Â ")


@dataclass(frozen=True)
class PrototypeEncoding:
    logical_tokens: list[str]
    model_token_count: int
    protected_piece_tokens: int
    protected_byte_tokens: int


@dataclass(frozen=True)
class ModelCaseResult:
    model_name: str
    category: str
    text: str
    expected: list[str]
    logical_tokens: list[str]
    model_token_count: int
    status: str
    reason: str
    boundary: BoundaryScore
    protected_piece_tokens: int = 0
    protected_byte_tokens: int = 0

    @property
    def exact_match(self) -> bool:
        return self.status == "ok" and self.logical_tokens == self.expected


@dataclass(frozen=True)
class SummaryRow:
    model_name: str
    status: str
    examples: int
    avg_logical_tokens_example: float
    avg_model_tokens_example: float
    avg_model_tokens_word: float
    boundary_f1: float
    exact_match: str
    protected_byte_token_rate: float
    reason: str = ""


@dataclass(frozen=True)
class ProtectedSummary:
    model_name: str
    status: str
    examples: int
    protected_preserved: int
    protected_total: int
    break_rate: float
    avg_model_tokens_example: float
    protected_byte_token_rate: float
    reason: str = ""


def ensure_sentencepiece():
    if importlib.util.find_spec("sentencepiece") is None:
        raise RuntimeError("sentencepiece is not installed")
    import sentencepiece as spm  # type: ignore[import-not-found]

    return spm


def strip_sp_word_start(token: str) -> str:
    for prefix in SP_WORD_STARTS:
        if token.startswith(prefix) and len(token) > len(prefix):
            return token[len(prefix) :]
    return token


def load_sp_processor(model_path: Path):
    spm = ensure_sentencepiece()
    processor = spm.SentencePieceProcessor()
    processor.Load(str(model_path))
    return processor


def selected_piece_strings(selected_path: Path) -> list[str]:
    pieces = [piece.piece for piece in load_selected_pieces(selected_path)]
    return sorted((piece for piece in pieces if piece), key=lambda item: (-len(item), item))


def append_word_surface(tokens: list[str], surface: str, *, word_start: bool) -> None:
    if not surface:
        return
    tokens.append(f"{WORD_START}{surface}" if word_start else surface)


def append_suffix_surface(tokens: list[str], surface: str) -> None:
    if surface:
        tokens.append(f"+{surface}")


def encode_protected_surface(surface: str, selected_pieces: list[str]) -> tuple[int, int]:
    position = 0
    piece_tokens = 0
    byte_tokens = 0
    while position < len(surface):
        match = ""
        for piece in selected_pieces:
            if surface.startswith(piece, position):
                match = piece
                break
        if match:
            piece_tokens += 1
            position += len(match)
            continue

        byte_tokens += len(surface[position].encode("utf-8"))
        position += 1

    return piece_tokens, byte_tokens


def append_sp_encoded_segment(
    *,
    logical_tokens: list[str],
    surface: str,
    starts_after_space: bool,
    processor,
) -> int:
    model_count = 0
    for index, piece in enumerate(processor.EncodeAsPieces(surface)):
        piece_surface = strip_sp_word_start(piece)
        if not piece_surface:
            continue
        append_word_surface(
            logical_tokens,
            piece_surface,
            word_start=index == 0 and starts_after_space,
        )
        model_count += 1
    return model_count


def encode_finite_protected_sp64(
    text: str,
    *,
    processor,
    selected_pieces: list[str],
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
            piece_count, byte_count = encode_protected_surface(piece.surface, selected_pieces)
            protected_piece_tokens += piece_count
            protected_byte_tokens += byte_count
            model_token_count += piece_count + byte_count
            pending_space = False
            continue

        if piece.kind == "apostrophe":
            flush()
            logical_tokens.append(piece.surface)
            model_token_count += 1
            pending_space = False
            continue

        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            append_suffix_surface(logical_tokens, piece.surface)
            model_token_count += 1
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


def _empty_boundary() -> BoundaryScore:
    return BoundaryScore(precision=0.0, recall=0.0, f1=0.0, correct=0, predicted=0, gold=0)


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


def evaluate_cases_for_models(
    cases: list[EvalCase],
    *,
    processor,
    sp64_model: Path,
    selected_pieces: list[str],
) -> dict[str, list[ModelCaseResult]]:
    specs = [
        RealBaselineSpec(name="custom_tr_morph", kind="custom"),
        RealBaselineSpec(name="sp_unigram_64000_train_only", kind="sentencepiece", value=str(sp64_model)),
    ]
    output: dict[str, list[ModelCaseResult]] = {spec.name: [] for spec in specs}
    output["finite_protected_sp64"] = []

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
                    logical_tokens=encoding.tokens,
                    model_token_count=len(encoding.tokens),
                    status=encoding.status,
                    reason=encoding.reason,
                    boundary=(
                        boundary_score(boundary_tokens, case.expected)
                        if encoding.status == "ok"
                        else _empty_boundary()
                    ),
                )
            )

        prototype = encode_finite_protected_sp64(
            case.text,
            processor=processor,
            selected_pieces=selected_pieces,
        )
        output["finite_protected_sp64"].append(
            ModelCaseResult(
                model_name="finite_protected_sp64",
                category=case.category,
                text=case.text,
                expected=case.expected,
                logical_tokens=prototype.logical_tokens,
                model_token_count=prototype.model_token_count,
                status="ok",
                reason="finite protected pieces + normal SP64",
                boundary=boundary_score(prototype.logical_tokens, case.expected),
                protected_piece_tokens=prototype.protected_piece_tokens,
                protected_byte_tokens=prototype.protected_byte_tokens,
            )
        )

    return output


def summarize_results(results: list[ModelCaseResult]) -> SummaryRow:
    if not results:
        return SummaryRow("", "skipped", 0, 0.0, 0.0, 0.0, 0.0, "0/0", 0.0)
    model_name = results[0].model_name
    status = "ok" if all(result.status == "ok" for result in results) else "skipped"
    reason = next((result.reason for result in results if result.reason), "")
    if status != "ok":
        return SummaryRow(model_name, status, len(results), 0.0, 0.0, 0.0, 0.0, "0/0", 0.0, reason)
    logical_count = sum(len(result.logical_tokens) for result in results)
    model_count = sum(result.model_token_count for result in results)
    word_count = sum(count_words(result.text) for result in results)
    protected_piece = sum(result.protected_piece_tokens for result in results)
    protected_byte = sum(result.protected_byte_tokens for result in results)
    protected_total = protected_piece + protected_byte
    boundary = _micro_boundary(results)
    exact = sum(result.exact_match for result in results)
    return SummaryRow(
        model_name=model_name,
        status=status,
        examples=len(results),
        avg_logical_tokens_example=logical_count / len(results) if results else 0.0,
        avg_model_tokens_example=model_count / len(results) if results else 0.0,
        avg_model_tokens_word=model_count / word_count if word_count else 0.0,
        boundary_f1=boundary.f1,
        exact_match=f"{exact}/{len(results)}",
        protected_byte_token_rate=protected_byte / protected_total if protected_total else 0.0,
        reason=reason,
    )


def protected_summary_for_model(
    *,
    model_name: str,
    cases: list[StressCase],
    encodings_by_text: dict[str, PrototypeEncoding | list[str]],
) -> ProtectedSummary:
    protected_total = 0
    protected_preserved = 0
    model_token_count = 0
    protected_piece = 0
    protected_byte = 0
    for case in cases:
        encoding = encodings_by_text[case.text]
        if isinstance(encoding, PrototypeEncoding):
            tokens = encoding.logical_tokens
            model_token_count += encoding.model_token_count
            protected_piece += encoding.protected_piece_tokens
            protected_byte += encoding.protected_byte_tokens
        else:
            tokens = encoding
            model_token_count += len(tokens)
        for span in case.protected_spans:
            protected_total += 1
            if is_span_preserved(span, tokens):
                protected_preserved += 1
    protected_model_total = protected_piece + protected_byte
    broken = protected_total - protected_preserved
    return ProtectedSummary(
        model_name=model_name,
        status="ok",
        examples=len(cases),
        protected_preserved=protected_preserved,
        protected_total=protected_total,
        break_rate=broken / protected_total if protected_total else 0.0,
        avg_model_tokens_example=model_token_count / len(cases) if cases else 0.0,
        protected_byte_token_rate=(
            protected_byte / protected_model_total if protected_model_total else 0.0
        ),
    )


def evaluate_protected(
    cases: list[StressCase],
    *,
    processor,
    sp64_model: Path,
    selected_pieces: list[str],
) -> list[ProtectedSummary]:
    custom = TurkishTokenizer()
    sp_spec = RealBaselineSpec(
        name="sp_unigram_64000_train_only",
        kind="sentencepiece",
        value=str(sp64_model),
    )
    token_maps: dict[str, dict[str, PrototypeEncoding | list[str]]] = {
        "custom_tr_morph": {case.text: custom.encode(case.text) for case in cases},
        "sp_unigram_64000_train_only": {
            case.text: encode_with_spec(sp_spec, case.text, local_files_only=True).tokens
            for case in cases
        },
        "finite_protected_sp64": {
            case.text: encode_finite_protected_sp64(
                case.text,
                processor=processor,
                selected_pieces=selected_pieces,
            )
            for case in cases
        },
    }
    return [
        protected_summary_for_model(
            model_name=model_name,
            cases=cases,
            encodings_by_text=encodings,
        )
        for model_name, encodings in token_maps.items()
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
        "| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.model_name} | {row.status} | {row.examples} | "
            f"{row.avg_logical_tokens_example:.4f} | "
            f"{row.avg_model_tokens_example:.4f} | "
            f"{row.avg_model_tokens_word:.4f} | "
            f"{row.boundary_f1:.4f} | {row.exact_match} | "
            f"{row.protected_byte_token_rate:.6f} | {row.reason} |"
        )

    categories = sorted(
        {result.category for results in model_results.values() for result in results}
    )
    if categories:
        lines.extend(["", "### Category F1", ""])
        model_names = list(model_results.keys())
        lines.append("| Category | " + " | ".join(model_names) + " |")
        lines.append("| --- | " + " | ".join("---:" for _ in model_names) + " |")
        scores = {model_name: category_f1(results) for model_name, results in model_results.items()}
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
        "| Model | Status | Examples | Protected preserved | Break rate | Avg model tokens/example | Protected byte-token rate | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.model_name} | {row.status} | {row.examples} | "
            f"{row.protected_preserved}/{row.protected_total} | "
            f"{row.break_rate:.4f} | {row.avg_model_tokens_example:.4f} | "
            f"{row.protected_byte_token_rate:.6f} | {row.reason} |"
        )
    return lines


def format_report(
    *,
    gold_results: dict[str, list[ModelCaseResult]],
    challenge_results: dict[str, list[ModelCaseResult]],
    multilingual_results: dict[str, list[ModelCaseResult]],
    protected_rows: list[ProtectedSummary],
    sp64_model: Path,
    selected_pieces: Path,
) -> str:
    lines = [
        "# v2.0 Finite Protected SP64 Intrinsic Eval",
        "",
        f"SP64 reference: `{sp64_model.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces.as_posix()}`",
        "",
        "This is an intrinsic prototype, not a final tokenizer. Normal text uses",
        "the train-only SP64 Unigram model. Protected spans use finite selected",
        "pieces with UTF-8 byte fallback. Boundary scoring uses logical protected",
        "span tokens; model token counts include finite protected pieces.",
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
            "This prototype is worth further work only if it preserves protected",
            "spans and improves visible boundary behavior without hiding protected",
            "token pressure.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Evaluate finite-protected + SP64 intrinsic tokenizer prototype.",
    )
    parser.add_argument(
        "--sp64-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--gold", default="data/eval/tr_gold_expanded.tsv")
    parser.add_argument("--challenge", default="data/eval/tr_challenge.tsv")
    parser.add_argument("--multilingual", default="data/eval/multilingual_smoke.tsv")
    parser.add_argument("--stress", default="data/eval/tr_stress_public.tsv")
    parser.add_argument("--report-out", default="artifacts/v2_0_finite_protected_sp64_intrinsic_eval.md")
    args = parser.parse_args(argv)

    sp64_model = Path(args.sp64_model)
    selected_path = Path(args.selected_pieces)
    processor = load_sp_processor(sp64_model)
    selected = selected_piece_strings(selected_path)

    gold_results = evaluate_cases_for_models(
        load_cases(args.gold),
        processor=processor,
        sp64_model=sp64_model,
        selected_pieces=selected,
    )
    challenge_results = evaluate_cases_for_models(
        load_cases(args.challenge),
        processor=processor,
        sp64_model=sp64_model,
        selected_pieces=selected,
    )
    multilingual_results = evaluate_cases_for_models(
        load_cases(args.multilingual),
        processor=processor,
        sp64_model=sp64_model,
        selected_pieces=selected,
    )
    protected_rows = evaluate_protected(
        load_stress_cases(args.stress),
        processor=processor,
        sp64_model=sp64_model,
        selected_pieces=selected,
    )

    report = format_report(
        gold_results=gold_results,
        challenge_results=challenge_results,
        multilingual_results=multilingual_results,
        protected_rows=protected_rows,
        sp64_model=sp64_model,
        selected_pieces=selected_path,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
