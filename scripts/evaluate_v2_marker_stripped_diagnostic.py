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
from scripts.compare_tokenizers import boundary_score, count_words  # noqa: E402
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
    strip_sp_word_start,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.report_protected_spans import is_span_preserved  # noqa: E402
from scripts.report_stress_public import StressCase, load_stress_cases  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class SplitPressure:
    split: str
    lines: int
    bytes: int
    words: int
    model_tokens: int
    protected_piece_tokens: int
    protected_byte_tokens: int

    @property
    def model_tokens_per_byte(self) -> float:
        return self.model_tokens / self.bytes if self.bytes else 0.0

    @property
    def model_tokens_per_word(self) -> float:
        return self.model_tokens / self.words if self.words else 0.0

    @property
    def protected_byte_token_rate(self) -> float:
        total = self.protected_piece_tokens + self.protected_byte_tokens
        return self.protected_byte_tokens / total if total else 0.0


def append_raw_sp_segment(
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


def encode_finite_protected_marker_stripped(
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
            model_token_count += append_raw_sp_segment(
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
            model_token_count += append_raw_sp_segment(
                logical_tokens=[],
                surface=piece.surface,
                starts_after_space=False,
                processor=processor,
            )
            pending_space = False
            continue

        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            append_suffix_surface(logical_tokens, piece.surface)
            model_token_count += append_raw_sp_segment(
                logical_tokens=[],
                surface=piece.surface,
                starts_after_space=False,
                processor=processor,
            )
            pending_space = False
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
    output["finite_protected_marker_stripped"] = []

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

        prototype = encode_finite_protected_marker_stripped(
            case.text,
            processor=processor,
            selected_pieces=selected_pieces,
        )
        output["finite_protected_marker_stripped"].append(
            ModelCaseResult(
                model_name="finite_protected_marker_stripped",
                category=case.category,
                text=case.text,
                expected=case.expected,
                logical_tokens=prototype.logical_tokens,
                model_token_count=prototype.model_token_count,
                status="ok",
                reason="soft-marker model, markers stripped at encode time",
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
        "finite_protected_marker_stripped": {
            case.text: encode_finite_protected_marker_stripped(
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


def measure_split(
    *,
    split: str,
    path: Path,
    processor,
    selected_pieces: list[str],
    progress: int,
    max_lines: int | None,
) -> SplitPressure:
    lines = 0
    byte_count = 0
    word_count = 0
    model_tokens = 0
    protected_piece_tokens = 0
    protected_byte_tokens = 0

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if max_lines is not None and lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            encoded = encode_finite_protected_marker_stripped(
                text,
                processor=processor,
                selected_pieces=selected_pieces,
            )
            lines += 1
            byte_count += len(text.encode("utf-8"))
            word_count += count_words(text)
            model_tokens += encoded.model_token_count
            protected_piece_tokens += encoded.protected_piece_tokens
            protected_byte_tokens += encoded.protected_byte_tokens
            if progress > 0 and lines % progress == 0:
                print(
                    f"measured {split}: {lines:,} lines "
                    f"tokens/byte={model_tokens / byte_count if byte_count else 0.0:.6f}",
                    flush=True,
                )

    return SplitPressure(
        split=split,
        lines=lines,
        bytes=byte_count,
        words=word_count,
        model_tokens=model_tokens,
        protected_piece_tokens=protected_piece_tokens,
        protected_byte_tokens=protected_byte_tokens,
    )


def format_pressure_table(rows: list[SplitPressure]) -> list[str]:
    lines = [
        "## Marker-Stripped Token Pressure",
        "",
        "| Split | Lines | Bytes | Words | Model tokens | Model tokens/byte | Model tokens/word | Protected piece tokens | Protected byte tokens | Protected byte-token rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.split} | {row.lines} | {row.bytes} | {row.words} | "
            f"{row.model_tokens} | {row.model_tokens_per_byte:.6f} | "
            f"{row.model_tokens_per_word:.4f} | {row.protected_piece_tokens} | "
            f"{row.protected_byte_tokens} | {row.protected_byte_token_rate:.6f} |"
        )
    return lines


def format_report(
    *,
    soft_marker_model: Path,
    sp64_model: Path,
    selected_pieces: Path,
    pressure_rows: list[SplitPressure],
    gold_results: dict[str, list[ModelCaseResult]],
    challenge_results: dict[str, list[ModelCaseResult]],
    multilingual_results: dict[str, list[ModelCaseResult]],
    protected_rows: list[ProtectedSummary],
    max_lines: int | None,
) -> str:
    lines = [
        "# v2.0 Marker-Stripped Soft-Marker Diagnostic",
        "",
        f"Soft-marker model: `{soft_marker_model.as_posix()}`",
        f"SP64 reference: `{sp64_model.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces.as_posix()}`",
        f"Max lines per split: `{max_lines if max_lines is not None else 'all'}`",
        "",
        "This diagnostic uses the all-soft-marker-trained Unigram model but does",
        "not insert morphology markers into normal text at encode time. Protected",
        "spans still use the finite protected encoder.",
        "",
    ]
    lines.extend(format_pressure_table(pressure_rows))
    lines.append("")
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
            "If marker-stripped token pressure drops near SP64 while F1 stays above",
            "SP64, prefer train-only vocab shaping over in-stream markers. If F1",
            "collapses, selective in-stream markers remain the next lever.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Evaluate soft-marker-trained model with markers stripped at encode time.",
    )
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
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
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--report-out", default="artifacts/v2_0_marker_stripped_soft_marker_diagnostic.md")
    args = parser.parse_args(argv)

    soft_marker_model = Path(args.soft_marker_model)
    sp64_model = Path(args.sp64_model)
    selected_path = Path(args.selected_pieces)
    processor = load_sp_processor(soft_marker_model)
    selected = selected_piece_strings(selected_path)
    split_dir = Path(args.split_dir)
    pressure_rows = [
        measure_split(
            split=split,
            path=split_dir / f"{split}.txt",
            processor=processor,
            selected_pieces=selected,
            progress=args.progress,
            max_lines=args.max_lines,
        )
        for split in ("train", "valid", "test")
    ]
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
        soft_marker_model=soft_marker_model,
        sp64_model=sp64_model,
        selected_pieces=selected_path,
        pressure_rows=pressure_rows,
        gold_results=gold_results,
        challenge_results=challenge_results,
        multilingual_results=multilingual_results,
        protected_rows=protected_rows,
        max_lines=args.max_lines,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
