from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import BoundaryScore, boundary_score, count_words  # noqa: E402
from scripts.compare_bpe_sweep import micro_boundary  # noqa: E402
from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.baseline_bpe import encode_bpe, load_bpe  # noqa: E402
from tr_tokenizer.external_baselines import (  # noqa: E402
    BaselineEncoding,
    encode_huggingface,
    encode_sentencepiece,
    encode_tokenizers_json,
    encode_unicode_chars,
    parse_named_spec,
)


@dataclass(frozen=True)
class RealBaselineSpec:
    name: str
    kind: str
    value: str = ""


@dataclass(frozen=True)
class RealCaseResult:
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
class RealSummaryRow:
    model_name: str
    status: str
    avg_tokens_example: float
    avg_tokens_word: float
    boundary_f1: float
    exact_match: str
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


def canonicalize_external_tokens(tokens: list[str]) -> list[str]:
    canonical: list[str] = []
    for token in tokens:
        if not token:
            continue

        # Common subword conventions. This is an approximate view used only for
        # character-boundary comparison; raw tokens are still reported.
        if token.startswith("Ġ") and len(token) > 1:
            canonical.append("▁" + token[1:])
        elif token.startswith("##") and len(token) > 2:
            canonical.append(token[2:])
        elif token.startswith("▁"):
            canonical.append(token)
        elif token in {"<0x0A>", "Ċ"}:
            continue
        else:
            canonical.append(token)
    return canonical


def _encoding_for_spec(
    spec: RealBaselineSpec,
    text: str,
    *,
    local_files_only: bool,
) -> BaselineEncoding:
    if spec.kind == "custom":
        return BaselineEncoding(name=spec.name, tokens=TurkishTokenizer().encode(text))
    if spec.kind == "unicode_char":
        return encode_unicode_chars(text, name=spec.name)
    if spec.kind == "toy_bpe":
        return BaselineEncoding(name=spec.name, tokens=encode_bpe(text, load_bpe(spec.value)))
    if spec.kind == "hf":
        return encode_huggingface(
            text,
            model_id=spec.value,
            name=spec.name,
            local_files_only=local_files_only,
        )
    if spec.kind == "sentencepiece":
        return encode_sentencepiece(text, model_path=spec.value, name=spec.name)
    if spec.kind == "tokenizers_json":
        return encode_tokenizers_json(text, tokenizer_path=spec.value, name=spec.name)
    raise ValueError(f"unknown baseline kind: {spec.kind}")


def encode_with_spec(
    spec: RealBaselineSpec,
    text: str,
    *,
    local_files_only: bool = True,
) -> BaselineEncoding:
    return _encoding_for_spec(spec, text, local_files_only=local_files_only)


def _boundary_tokens(spec: RealBaselineSpec, tokens: list[str]) -> list[str]:
    if spec.kind in {"hf", "sentencepiece", "tokenizers_json"}:
        return canonicalize_external_tokens(tokens)
    return tokens


def evaluate_real_baselines(
    cases: list[EvalCase],
    specs: list[RealBaselineSpec],
    *,
    local_files_only: bool = True,
) -> dict[str, list[RealCaseResult]]:
    results: dict[str, list[RealCaseResult]] = {}
    skipped: dict[str, tuple[str, str]] = {}

    for spec in specs:
        model_results: list[RealCaseResult] = []

        for case in cases:
            if spec.name in skipped:
                status, reason = skipped[spec.name]
                encoding = BaselineEncoding(
                    name=spec.name,
                    tokens=[],
                    status=status,
                    reason=reason,
                )
            else:
                encoding = _encoding_for_spec(
                    spec,
                    case.text,
                    local_files_only=local_files_only,
                )
                if encoding.status != "ok":
                    skipped[spec.name] = (encoding.status, encoding.reason)

            boundary = (
                boundary_score(_boundary_tokens(spec, encoding.tokens), case.expected)
                if encoding.status == "ok"
                else _empty_boundary()
            )
            model_results.append(
                RealCaseResult(
                    model_name=spec.name,
                    category=case.category,
                    text=case.text,
                    expected=case.expected,
                    tokens=encoding.tokens,
                    status=encoding.status,
                    reason=encoding.reason,
                    boundary=boundary,
                )
            )

        results[spec.name] = model_results

    return results


def summarize_model(results: list[RealCaseResult]) -> RealSummaryRow:
    if not results:
        return RealSummaryRow("", "skipped", 0.0, 0.0, 0.0, "0/0")

    model_name = results[0].model_name
    status = "ok" if all(result.status == "ok" for result in results) else "skipped"
    reason = next((result.reason for result in results if result.reason), "")
    if status != "ok":
        return RealSummaryRow(
            model_name=model_name,
            status=status,
            avg_tokens_example=0.0,
            avg_tokens_word=0.0,
            boundary_f1=0.0,
            exact_match="0/0",
            reason=reason,
        )

    token_count = sum(len(result.tokens) for result in results)
    word_count = sum(count_words(result.text) for result in results)
    exact = sum(result.exact_match for result in results)
    boundary = micro_boundary(results)  # type: ignore[arg-type]
    total = len(results)
    return RealSummaryRow(
        model_name=model_name,
        status=status,
        avg_tokens_example=token_count / total if total else 0.0,
        avg_tokens_word=token_count / word_count if word_count else 0.0,
        boundary_f1=boundary.f1,
        exact_match=f"{exact}/{total}",
    )


def category_f1(results: list[RealCaseResult]) -> dict[str, float]:
    grouped: dict[str, list[RealCaseResult]] = {}
    for result in results:
        if result.status == "ok":
            grouped.setdefault(result.category, []).append(result)

    scores: dict[str, float] = {}
    for category, category_results in sorted(grouped.items()):
        scores[category] = micro_boundary(category_results).f1  # type: ignore[arg-type]
    return scores


def format_report(
    summary_rows: list[RealSummaryRow],
    category_table: dict[str, dict[str, float]],
) -> str:
    lines = ["SUMMARY"]
    lines.append(
        "model_name\tstatus\tavg_tokens/example\tavg_tokens/word\tboundary_f1\texact_match_vs_gold\treason"
    )
    for row in summary_rows:
        lines.append(
            f"{row.model_name}\t{row.status}\t{row.avg_tokens_example:.4f}\t"
            f"{row.avg_tokens_word:.4f}\t{row.boundary_f1:.4f}\t"
            f"{row.exact_match}\t{row.reason}"
        )

    model_names = [row.model_name for row in summary_rows]
    lines.append("")
    lines.append("CATEGORY SUMMARY")
    lines.append("category\t" + "\t".join(f"{model}_f1" for model in model_names))
    for category, scores in category_table.items():
        lines.append(
            category
            + "\t"
            + "\t".join(f"{scores.get(model, 0.0):.4f}" for model in model_names)
        )
    return "\n".join(lines)


def format_markdown(
    summary_rows: list[RealSummaryRow],
    category_table: dict[str, dict[str, float]],
) -> str:
    model_names = [row.model_name for row in summary_rows]
    lines = [
        "# Real Tokenizer Baseline Report",
        "",
        "## Summary",
        "",
        "| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row.model_name} | {row.status} | {row.avg_tokens_example:.4f} | "
            f"{row.avg_tokens_word:.4f} | {row.boundary_f1:.4f} | "
            f"{row.exact_match} | {row.reason} |"
        )

    lines.extend(
        [
            "",
            "## Category Summary",
            "",
            "| Category | " + " | ".join(f"{model} F1" for model in model_names) + " |",
            "| --- | " + " | ".join("---:" for _ in model_names) + " |",
        ]
    )
    for category, scores in category_table.items():
        lines.append(
            f"| {category} | "
            + " | ".join(f"{scores.get(model, 0.0):.4f}" for model in model_names)
            + " |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- External tokenizer boundary F1 is approximate unless offsets are available.",
            "- Token count alone is not tokenizer quality.",
            "- Skipped models mean optional dependencies or local model files were not available.",
            "- This report must not be used to tune the frozen regression or hidden eval sets.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_specs(args: argparse.Namespace) -> list[RealBaselineSpec]:
    specs = [
        RealBaselineSpec(name="custom_tr_morph", kind="custom"),
        RealBaselineSpec(name="unicode_char", kind="unicode_char"),
    ]

    for raw in args.toy_bpe:
        name, value = parse_named_spec(raw)
        specs.append(RealBaselineSpec(name=name, kind="toy_bpe", value=value))

    for raw in args.hf:
        name, value = parse_named_spec(raw)
        specs.append(RealBaselineSpec(name=name, kind="hf", value=value))

    for raw in args.sentencepiece:
        name, value = parse_named_spec(raw)
        specs.append(RealBaselineSpec(name=name, kind="sentencepiece", value=value))

    for raw in args.tokenizers_json:
        name, value = parse_named_spec(raw)
        specs.append(RealBaselineSpec(name=name, kind="tokenizers_json", value=value))

    return specs


def run_report(
    cases: list[EvalCase],
    specs: list[RealBaselineSpec],
    *,
    local_files_only: bool = True,
) -> tuple[list[RealSummaryRow], dict[str, dict[str, float]]]:
    model_results = evaluate_real_baselines(
        cases,
        specs,
        local_files_only=local_files_only,
    )
    summary_rows = [summarize_model(results) for results in model_results.values()]
    categories = sorted({case.category for case in cases})
    category_table: dict[str, dict[str, float]] = {category: {} for category in categories}

    for model_name, results in model_results.items():
        scores = category_f1(results)
        for category in categories:
            category_table[category][model_name] = scores.get(category, 0.0)

    return summary_rows, category_table


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Compare Tamga with optional real tokenizer baselines.",
    )
    parser.add_argument("gold_tsv")
    parser.add_argument(
        "--toy-bpe",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Add a trained toy BPE model JSON.",
    )
    parser.add_argument(
        "--hf",
        action="append",
        default=[],
        metavar="NAME=MODEL_ID_OR_PATH",
        help="Add a Hugging Face tokenizer. Defaults to local cache only.",
    )
    parser.add_argument(
        "--sentencepiece",
        action="append",
        default=[],
        metavar="NAME=MODEL_PATH",
        help="Add a SentencePiece model file.",
    )
    parser.add_argument(
        "--tokenizers-json",
        action="append",
        default=[],
        metavar="NAME=TOKENIZER_JSON",
        help="Add a Hugging Face tokenizers JSON file.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow Hugging Face tokenizers to download missing models.",
    )
    parser.add_argument("--markdown-out", help="Optional Markdown report output path")
    args = parser.parse_args(argv)

    cases = load_cases(args.gold_tsv)
    summary_rows, category_table = run_report(
        cases,
        build_specs(args),
        local_files_only=not args.allow_download,
    )
    print(format_report(summary_rows, category_table))

    if args.markdown_out:
        target = Path(args.markdown_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(format_markdown(summary_rows, category_table), encoding="utf-8")
        print(f"wrote_markdown: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
