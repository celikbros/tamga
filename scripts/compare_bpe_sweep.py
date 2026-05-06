from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import BoundaryScore, boundary_score, count_words  # noqa: E402
from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.baseline_bpe import encode_bpe, load_bpe  # noqa: E402


@dataclass(frozen=True)
class SweepCaseResult:
    category: str
    text: str
    expected: list[str]
    tokens: list[str]
    boundary: BoundaryScore

    @property
    def exact_match(self) -> bool:
        return self.tokens == self.expected


@dataclass(frozen=True)
class SummaryRow:
    model_name: str
    avg_tokens_example: float
    avg_tokens_word: float
    boundary_f1: float
    exact_match: str


def evaluate_custom(cases: list[EvalCase]) -> list[SweepCaseResult]:
    tokenizer = TurkishTokenizer()
    results: list[SweepCaseResult] = []
    for case in cases:
        tokens = tokenizer.encode(case.text)
        results.append(
            SweepCaseResult(
                category=case.category,
                text=case.text,
                expected=case.expected,
                tokens=tokens,
                boundary=boundary_score(tokens, case.expected),
            )
        )
    return results


def evaluate_bpe(
    cases: list[EvalCase],
    model: dict,
) -> list[SweepCaseResult]:
    results: list[SweepCaseResult] = []
    for case in cases:
        tokens = encode_bpe(case.text, model)
        results.append(
            SweepCaseResult(
                category=case.category,
                text=case.text,
                expected=case.expected,
                tokens=tokens,
                boundary=boundary_score(tokens, case.expected),
            )
        )
    return results


def micro_boundary(results: list[SweepCaseResult]) -> BoundaryScore:
    correct = sum(result.boundary.correct for result in results)
    predicted = sum(result.boundary.predicted for result in results)
    gold = sum(result.boundary.gold for result in results)
    precision = correct / predicted if predicted else (1.0 if gold == 0 else 0.0)
    recall = correct / gold if gold else (1.0 if predicted == 0 else 0.0)
    denominator = precision + recall
    f1 = 0.0 if denominator == 0 else 2 * precision * recall / denominator
    return BoundaryScore(precision, recall, f1, correct, predicted, gold)


def summarize_model(model_name: str, results: list[SweepCaseResult]) -> SummaryRow:
    total = len(results)
    token_count = sum(len(result.tokens) for result in results)
    word_count = sum(count_words(result.text) for result in results)
    exact = sum(result.exact_match for result in results)
    boundary = micro_boundary(results)
    return SummaryRow(
        model_name=model_name,
        avg_tokens_example=token_count / total if total else 0.0,
        avg_tokens_word=token_count / word_count if word_count else 0.0,
        boundary_f1=boundary.f1,
        exact_match=f"{exact}/{total}",
    )


def category_f1(results: list[SweepCaseResult]) -> dict[str, float]:
    grouped: dict[str, list[SweepCaseResult]] = {}
    for result in results:
        grouped.setdefault(result.category, []).append(result)
    return {
        category: micro_boundary(category_results).f1
        for category, category_results in sorted(grouped.items())
    }


def run_sweep(
    cases: list[EvalCase],
    bpe_models: list[tuple[str, dict]],
) -> tuple[list[SummaryRow], dict[str, dict[str, float]]]:
    model_results: dict[str, list[SweepCaseResult]] = {
        "custom": evaluate_custom(cases),
    }
    for model_name, model in bpe_models:
        model_results[model_name] = evaluate_bpe(cases, model)

    summary_rows = [
        summarize_model(model_name, results)
        for model_name, results in model_results.items()
    ]

    categories = sorted({case.category for case in cases})
    category_table: dict[str, dict[str, float]] = {category: {} for category in categories}
    for model_name, results in model_results.items():
        scores = category_f1(results)
        for category in categories:
            category_table[category][model_name] = scores.get(category, 0.0)

    return summary_rows, category_table


def format_sweep_report(
    summary_rows: list[SummaryRow],
    category_table: dict[str, dict[str, float]],
) -> str:
    lines = ["SUMMARY"]
    lines.append(
        "model_name\tavg_tokens/example\tavg_tokens/word\tboundary_f1\texact_match_vs_gold"
    )
    for row in summary_rows:
        lines.append(
            f"{row.model_name}\t{row.avg_tokens_example:.4f}\t"
            f"{row.avg_tokens_word:.4f}\t{row.boundary_f1:.4f}\t{row.exact_match}"
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


def format_sweep_markdown(
    summary_rows: list[SummaryRow],
    category_table: dict[str, dict[str, float]],
) -> str:
    model_names = [row.model_name for row in summary_rows]
    lines = [
        "# BPE Sweep Report",
        "",
        "## Summary",
        "",
        "| Model | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row.model_name} | {row.avg_tokens_example:.4f} | "
            f"{row.avg_tokens_word:.4f} | {row.boundary_f1:.4f} | "
            f"{row.exact_match} |"
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
            "- Token count tek basina kalite degildir.",
            "- Boundary F1, gold morfolojik sinirlarla karakter boundary uyumunu olcer.",
            "- Toy BPE production baseline degildir; yalnizca karsilastirma altyapisi icin minimal baseline'dir.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Compare custom tokenizer to BPE sweep.")
    parser.add_argument("gold_tsv")
    parser.add_argument("bpe_models", nargs="+")
    parser.add_argument("--markdown-out", help="Optional Markdown report output path")
    args = parser.parse_args(argv)

    cases = load_cases(args.gold_tsv)
    bpe_models = [
        (Path(path).stem, load_bpe(path))
        for path in args.bpe_models
    ]
    summary_rows, category_table = run_sweep(cases, bpe_models)
    print(format_sweep_report(summary_rows, category_table))

    if args.markdown_out:
        target = Path(args.markdown_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            format_sweep_markdown(summary_rows, category_table),
            encoding="utf-8",
        )
        print(f"wrote_markdown: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
