from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import BoundaryScore, boundary_score, count_words  # noqa: E402
from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from tr_tokenizer.boundary_weighted_bpe import (  # noqa: E402
    encode_boundary_weighted_bpe,
    save_boundary_weighted_bpe,
    train_boundary_weighted_bpe,
)


@dataclass(frozen=True)
class CaseResult:
    model_name: str
    category: str
    text: str
    expected: list[str]
    actual: list[str]
    boundary: BoundaryScore

    @property
    def exact_match(self) -> bool:
        return self.actual == self.expected


@dataclass(frozen=True)
class Summary:
    model_name: str
    dataset: str
    examples: int
    avg_tokens_example: float
    avg_tokens_word: float
    boundary_f1: float
    exact_match: str
    merges: int
    crossing_merges: int


def read_lines(path: Path, max_lines: int | None) -> list[str]:
    lines: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if max_lines is not None and len(lines) >= max_lines:
                break
            text = raw.rstrip("\n")
            if text:
                lines.append(text)
    return lines


def micro_boundary(results: list[CaseResult]) -> BoundaryScore:
    correct = sum(result.boundary.correct for result in results)
    predicted = sum(result.boundary.predicted for result in results)
    gold = sum(result.boundary.gold for result in results)
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


def evaluate(cases: list[EvalCase], *, model_name: str, model: dict) -> list[CaseResult]:
    results: list[CaseResult] = []
    for case in cases:
        actual = encode_boundary_weighted_bpe(case.text, model)
        results.append(
            CaseResult(
                model_name=model_name,
                category=case.category,
                text=case.text,
                expected=case.expected,
                actual=actual,
                boundary=boundary_score(actual, case.expected),
            )
        )
    return results


def summarize(
    *,
    dataset: str,
    results: list[CaseResult],
    model: dict,
) -> Summary:
    if not results:
        return Summary("", dataset, 0, 0.0, 0.0, 0.0, "0/0", 0, 0)
    boundary = micro_boundary(results)
    tokens = sum(len(result.actual) for result in results)
    words = sum(count_words(result.text) for result in results)
    exact = sum(result.exact_match for result in results)
    crossing_merges = sum(
        1 for row in model.get("merge_stats", []) if row.get("crossing_count", 0) > 0
    )
    return Summary(
        model_name=results[0].model_name,
        dataset=dataset,
        examples=len(results),
        avg_tokens_example=tokens / len(results),
        avg_tokens_word=tokens / words if words else 0.0,
        boundary_f1=boundary.f1,
        exact_match=f"{exact}/{len(results)}",
        merges=len(model.get("merges", [])),
        crossing_merges=crossing_merges,
    )


def category_f1(results: list[CaseResult]) -> dict[str, float]:
    grouped: dict[str, list[CaseResult]] = defaultdict(list)
    for result in results:
        grouped[result.category].append(result)
    return {
        category: micro_boundary(items).f1
        for category, items in sorted(grouped.items())
    }


def format_report(
    *,
    train_path: Path,
    max_train_lines: int | None,
    vocab_size: int,
    min_score: float,
    summaries: list[Summary],
    all_results: dict[tuple[str, str], list[CaseResult]],
    model_paths: dict[str, Path],
) -> str:
    lines = [
        "# v2.0 Boundary-Weighted BPE Probe",
        "",
        f"Train corpus: `{train_path.as_posix()}`",
        f"Max train lines: `{max_train_lines if max_train_lines is not None else 'all'}`",
        f"Vocab size: `{vocab_size}`",
        f"Min merge score: `{min_score}`",
        "",
        "This is a research prototype for the training-time objective direction.",
        "It is not a production tokenizer and does not claim LLM readiness.",
        "",
        "## Summary",
        "",
        "| Dataset | Model | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Merges | Crossing merges |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        lines.append(
            f"| {row.dataset} | {row.model_name} | {row.examples} | "
            f"{row.avg_tokens_example:.4f} | {row.avg_tokens_word:.4f} | "
            f"{row.boundary_f1:.4f} | {row.exact_match} | "
            f"{row.merges} | {row.crossing_merges} |"
        )

    lines.extend(["", "## Category F1", ""])
    datasets = sorted({dataset for dataset, _model in all_results})
    for dataset in datasets:
        lines.extend([f"### {dataset}", ""])
        model_names = [model for ds, model in all_results if ds == dataset]
        categories = sorted(
            {
                result.category
                for (ds, _model), results in all_results.items()
                if ds == dataset
                for result in results
            }
        )
        scores = {
            model: category_f1(all_results[(dataset, model)])
            for model in model_names
        }
        lines.append("| Category | " + " | ".join(model_names) + " |")
        lines.append("| --- | " + " | ".join("---:" for _ in model_names) + " |")
        for category in categories:
            lines.append(
                f"| {category} | "
                + " | ".join(f"{scores[model].get(category, 0.0):.4f}" for model in model_names)
                + " |"
            )
        lines.append("")

    lines.extend(["## Model Artifacts", ""])
    for name, path in model_paths.items():
        lines.append(f"- `{name}`: `{path.as_posix()}`")

    lines.extend(
        [
            "",
            "## Gate",
            "",
            "Continue this branch only if boundary penalties move F1 upward",
            "without simply exploding token count. If the useful signal appears,",
            "the next step is a real learned tokenizer objective, not this toy BPE.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Run a toy boundary-weighted BPE objective probe."
    )
    parser.add_argument(
        "--train",
        default=(
            "artifacts/private/v1_8_local_lm_probe/"
            "celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/"
            "filtered_split/train.txt"
        ),
    )
    parser.add_argument("--gold", default="data/eval/tr_gold_expanded.tsv")
    parser.add_argument("--challenge", default="data/eval/tr_challenge.tsv")
    parser.add_argument("--vocab-size", type=int, default=2000)
    parser.add_argument("--max-train-lines", type=int, default=2000)
    parser.add_argument("--min-score", type=float, default=2.0)
    parser.add_argument("--lambda", dest="lambdas", type=float, action="append", default=[])
    parser.add_argument(
        "--model-dir",
        default="artifacts/private/v2_0_boundary_weighted_bpe",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_boundary_weighted_bpe_probe.md",
    )
    args = parser.parse_args(argv)

    lambdas = args.lambdas or [0.0, 2.0, 4.0, 8.0]
    train_path = Path(args.train)
    train_lines = read_lines(train_path, args.max_train_lines)
    datasets = {
        "gold": load_cases(args.gold),
        "challenge": load_cases(args.challenge),
    }

    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[Summary] = []
    all_results: dict[tuple[str, str], list[CaseResult]] = {}
    model_paths: dict[str, Path] = {}

    for boundary_lambda in lambdas:
        model_name = f"boundary_weighted_bpe_lambda{boundary_lambda:g}"
        print(f"training {model_name}", flush=True)
        model = train_boundary_weighted_bpe(
            train_lines,
            vocab_size=args.vocab_size,
            boundary_lambda=boundary_lambda,
            min_score=args.min_score,
        )
        model_path = model_dir / f"{model_name}_vocab{args.vocab_size}.json"
        save_boundary_weighted_bpe(model, model_path)
        model_paths[model_name] = model_path

        for dataset_name, cases in datasets.items():
            results = evaluate(cases, model_name=model_name, model=model)
            all_results[(dataset_name, model_name)] = results
            summaries.append(
                summarize(dataset=dataset_name, results=results, model=model)
            )

    report = format_report(
        train_path=train_path,
        max_train_lines=args.max_train_lines,
        vocab_size=args.vocab_size,
        min_score=args.min_score,
        summaries=summaries,
        all_results=all_results,
        model_paths=model_paths,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
