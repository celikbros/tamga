from __future__ import annotations

from dataclasses import dataclass
import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import count_words  # noqa: E402
from scripts.evaluate_tokenizer import load_cases  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    ModelCaseResult,
    _micro_boundary,
    evaluate_cases_for_models,
    load_sp_processor,
    selected_piece_strings,
)
from scripts.report_confidence_intervals import MetricInterval, interval  # noqa: E402


@dataclass(frozen=True)
class ModelSpec:
    label: str
    path: Path


@dataclass(frozen=True)
class CiRow:
    model_name: str
    examples: int
    boundary_f1: MetricInterval
    avg_model_tokens_word: MetricInterval
    exact_match_rate: MetricInterval


def parse_model(value: str) -> ModelSpec:
    if "=" not in value:
        raise argparse.ArgumentTypeError("model must be LABEL=PATH")
    label, path = value.split("=", 1)
    if not label:
        raise argparse.ArgumentTypeError("model label cannot be empty")
    return ModelSpec(label=label, path=Path(path))


def boundary_f1(results: list[ModelCaseResult]) -> float:
    return _micro_boundary(results).f1


def avg_model_tokens_word(results: list[ModelCaseResult]) -> float:
    words = sum(count_words(row.text) for row in results)
    return sum(row.model_token_count for row in results) / words if words else 0.0


def exact_match_rate(results: list[ModelCaseResult]) -> float:
    return sum(row.exact_match for row in results) / len(results) if results else 0.0


def bootstrap_row(
    *,
    model_name: str,
    results: list[ModelCaseResult],
    samples: int,
    seed: int,
) -> CiRow:
    rng = random.Random(seed)
    total = len(results)
    f1_values: list[float] = []
    token_values: list[float] = []
    exact_values: list[float] = []
    for _ in range(samples):
        sample = [results[rng.randrange(total)] for _ in range(total)]
        f1_values.append(boundary_f1(sample))
        token_values.append(avg_model_tokens_word(sample))
        exact_values.append(exact_match_rate(sample))
    return CiRow(
        model_name=model_name,
        examples=total,
        boundary_f1=interval(f1_values, point=boundary_f1(results)),
        avg_model_tokens_word=interval(
            token_values,
            point=avg_model_tokens_word(results),
        ),
        exact_match_rate=interval(exact_values, point=exact_match_rate(results)),
    )


def evaluate_specs(
    *,
    specs: list[ModelSpec],
    dataset: Path,
    selected_pieces: Path,
    numeric_sp_passthrough: bool,
) -> dict[str, list[ModelCaseResult]]:
    cases = load_cases(dataset)
    selected = selected_piece_strings(selected_pieces)
    output: dict[str, list[ModelCaseResult]] = {}
    for spec in specs:
        processor = load_sp_processor(spec.path)
        rows = evaluate_cases_for_models(
            cases,
            processor=processor,
            sp64_model=spec.path,
            selected_pieces=selected,
            reference_label=f"{spec.label}_bare",
            finite_label=f"{spec.label}_finite",
            numeric_sp_passthrough=numeric_sp_passthrough,
        )
        output[f"{spec.label}_bare"] = rows[f"{spec.label}_bare"]
        output[f"{spec.label}_finite"] = rows[f"{spec.label}_finite"]
    return output


def _fmt(value: MetricInterval) -> str:
    return f"{value.point:.4f} [{value.lower:.4f}, {value.upper:.4f}]"


def format_report(
    *,
    dataset: Path,
    rows: list[CiRow],
    samples: int,
    numeric_sp_passthrough: bool,
) -> str:
    lines = [
        "# v2.0 SP Model Bootstrap CI",
        "",
        f"Dataset: `{dataset.as_posix()}`",
        f"Bootstrap samples: `{samples}`",
        f"Numeric protected SP passthrough: `{numeric_sp_passthrough}`",
        "",
        "Intervals are non-parametric bootstrap 95% intervals over examples.",
        "",
        "| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| `{row.model_name}` | {row.examples} | {_fmt(row.boundary_f1)} | "
            f"{_fmt(row.avg_model_tokens_word)} | {_fmt(row.exact_match_rate)} |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "Use the interval width as the visible-eval noise floor. Do not treat",
            "tiny point-estimate changes as real unless they clear this uncertainty.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Bootstrap CI for SP models and their finite-protected wrappers."
    )
    parser.add_argument("--dataset", default="data/eval/tr_challenge.tsv")
    parser.add_argument(
        "--model",
        action="append",
        type=parse_model,
        required=True,
        help="Model in LABEL=PATH form. Repeatable.",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--numeric-sp-passthrough", action="store_true")
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260610)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    model_results = evaluate_specs(
        specs=args.model,
        dataset=Path(args.dataset),
        selected_pieces=Path(args.selected_pieces),
        numeric_sp_passthrough=args.numeric_sp_passthrough,
    )
    rows = [
        bootstrap_row(
            model_name=name,
            results=results,
            samples=args.samples,
            seed=args.seed + index * 1009,
        )
        for index, (name, results) in enumerate(model_results.items())
    ]
    report = format_report(
        dataset=Path(args.dataset),
        rows=rows,
        samples=args.samples,
        numeric_sp_passthrough=args.numeric_sp_passthrough,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
