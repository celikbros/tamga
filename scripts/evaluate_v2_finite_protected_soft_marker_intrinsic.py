from __future__ import annotations

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
from scripts.compare_tokenizers import boundary_score  # noqa: E402
from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    ModelCaseResult,
    ProtectedSummary,
    PrototypeEncoding,
    _empty_boundary,
    append_suffix_surface,
    append_word_surface,
    encode_protected_surface,
    format_eval_table,
    format_protected_table,
    load_sp_processor,
    selected_piece_strings,
)
from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER  # noqa: E402
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.report_protected_spans import is_span_preserved  # noqa: E402
from scripts.report_stress_public import StressCase, load_stress_cases  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


SP_WORD_STARTS = ("\u2581", "â–", "Ã¢â€“Â", "Ã„Â ")


def strip_sp_word_start(token: str) -> str:
    for prefix in SP_WORD_STARTS:
        if token.startswith(prefix) and len(token) > len(prefix):
            return token[len(prefix) :]
    return token


def append_marked_sp_segment(
    *,
    logical_tokens: list[str],
    surface: str,
    starts_after_space: bool,
    processor,
) -> int:
    model_count = 0
    first_output_in_segment = True
    suffix_mode = False

    for piece in processor.EncodeAsPieces(surface):
        piece_surface = strip_sp_word_start(piece)
        if not piece_surface:
            continue
        model_count += 1
        parts = piece_surface.split(SOFT_MARKER)
        for index, part in enumerate(parts):
            if index > 0:
                suffix_mode = True
            if not part:
                continue
            if suffix_mode:
                append_suffix_surface(logical_tokens, part)
            else:
                append_word_surface(
                    logical_tokens,
                    part,
                    word_start=first_output_in_segment and starts_after_space,
                )
            first_output_in_segment = False

    return model_count


def encode_finite_protected_soft_marker(
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
            model_token_count += append_marked_sp_segment(
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
    return PrototypeEncoding(
        logical_tokens=logical_tokens,
        model_token_count=model_token_count,
        protected_piece_tokens=protected_piece_tokens,
        protected_byte_tokens=protected_byte_tokens,
    )


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
    output["finite_protected_soft_marker"] = []

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

        prototype = encode_finite_protected_soft_marker(
            case.text,
            processor=processor,
            selected_pieces=selected_pieces,
        )
        output["finite_protected_soft_marker"].append(
            ModelCaseResult(
                model_name="finite_protected_soft_marker",
                category=case.category,
                text=case.text,
                expected=case.expected,
                logical_tokens=prototype.logical_tokens,
                model_token_count=prototype.model_token_count,
                status="ok",
                reason="finite protected pieces + soft-marker model",
                boundary=boundary_score(prototype.logical_tokens, case.expected),
                protected_piece_tokens=prototype.protected_piece_tokens,
                protected_byte_tokens=prototype.protected_byte_tokens,
            )
        )

    return output


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
        "finite_protected_soft_marker": {
            case.text: encode_finite_protected_soft_marker(
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


def format_report(
    *,
    gold_results: dict[str, list[ModelCaseResult]],
    challenge_results: dict[str, list[ModelCaseResult]],
    multilingual_results: dict[str, list[ModelCaseResult]],
    protected_rows: list[ProtectedSummary],
    soft_marker_model: Path,
    sp64_model: Path,
    selected_pieces: Path,
) -> str:
    lines = [
        "# v2.0 Finite Protected Soft-Marker Intrinsic Eval",
        "",
        f"Soft-marker model: `{soft_marker_model.as_posix()}`",
        f"SP64 reference: `{sp64_model.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces.as_posix()}`",
        "",
        "This is an intrinsic prototype, not a final tokenizer. Normal text uses",
        "the train-only soft-marker model. Protected spans use finite selected",
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
            "This prototype is worth tiny-LM screening only if it preserves protected",
            "spans and materially beats SP64 on visible challenge boundary F1 without",
            "returning to pure-custom token pressure.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Evaluate finite-protected + soft-marker intrinsic tokenizer prototype.",
    )
    parser.add_argument(
        "--soft-marker-model",
        default="artifacts/private/v2_0_candidate_sentencepiece/protected_hard_soft_marker_raw_sp64_unigram_64000.model",
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
    parser.add_argument("--report-out", default="artifacts/v2_0_finite_protected_soft_marker_intrinsic_eval.md")
    args = parser.parse_args(argv)

    soft_marker_model = Path(args.soft_marker_model)
    sp64_model = Path(args.sp64_model)
    selected_path = Path(args.selected_pieces)
    processor = load_sp_processor(soft_marker_model)
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
        soft_marker_model=soft_marker_model,
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
