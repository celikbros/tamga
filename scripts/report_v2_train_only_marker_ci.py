from __future__ import annotations

from dataclasses import dataclass
import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import boundary_score, count_words  # noqa: E402
from scripts.evaluate_tokenizer import load_cases  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    ModelCaseResult,
    _micro_boundary,
    evaluate_cases_for_models as evaluate_finite_sp64_cases,
    load_sp_processor,
    selected_piece_strings,
)
from scripts.evaluate_v2_marker_stripped_diagnostic import (  # noqa: E402
    encode_finite_protected_marker_stripped,
)
from scripts.report_confidence_intervals import MetricInterval, interval  # noqa: E402


@dataclass(frozen=True)
class CiRow:
    model_name: str
    examples: int
    boundary_f1: MetricInterval
    avg_model_tokens_word: MetricInterval


def boundary_f1(results: list[ModelCaseResult]) -> float:
    return _micro_boundary(results).f1


def avg_model_tokens_word(results: list[ModelCaseResult]) -> float:
    words = sum(count_words(result.text) for result in results)
    if not words:
        return 0.0
    return sum(result.model_token_count for result in results) / words


def bootstrap_rows(
    model_results: dict[str, list[ModelCaseResult]],
    *,
    samples: int,
    seed: int,
) -> list[CiRow]:
    rows: list[CiRow] = []
    for model_index, (model_name, results) in enumerate(model_results.items()):
        rng = random.Random(seed + model_index * 1009)
        f1_values: list[float] = []
        token_values: list[float] = []
        total = len(results)
        for _ in range(samples):
            sample = [results[rng.randrange(total)] for _ in range(total)]
            f1_values.append(boundary_f1(sample))
            token_values.append(avg_model_tokens_word(sample))
        rows.append(
            CiRow(
                model_name=model_name,
                examples=total,
                boundary_f1=interval(f1_values, point=boundary_f1(results)),
                avg_model_tokens_word=interval(
                    token_values,
                    point=avg_model_tokens_word(results),
                ),
            )
        )
    return rows


def add_marker_stripped_model(
    model_results: dict[str, list[ModelCaseResult]],
    *,
    model_name: str,
    model_path: Path,
    cases,
    selected_pieces: list[str],
) -> None:
    processor = load_sp_processor(model_path)
    rows: list[ModelCaseResult] = []
    for case in cases:
        encoded = encode_finite_protected_marker_stripped(
            case.text,
            processor=processor,
            selected_pieces=selected_pieces,
        )
        rows.append(
            ModelCaseResult(
                model_name=model_name,
                category=case.category,
                text=case.text,
                expected=case.expected,
                logical_tokens=encoded.logical_tokens,
                model_token_count=encoded.model_token_count,
                status="ok",
                reason="marker-stripped finite protected routing",
                boundary=boundary_score(encoded.logical_tokens, case.expected),
                protected_piece_tokens=encoded.protected_piece_tokens,
                protected_byte_tokens=encoded.protected_byte_tokens,
            )
        )
    model_results[model_name] = rows


def _fmt(value: MetricInterval) -> str:
    return f"{value.point:.4f} [{value.lower:.4f}, {value.upper:.4f}]"


def format_report(rows: list[CiRow], *, dataset: Path, samples: int) -> str:
    lines = [
        "# v2.0 Train-Only Marker Frontier Confidence Intervals",
        "",
        f"Dataset: `{dataset.as_posix()}`",
        f"Bootstrap samples: `{samples}`",
        "",
        "Intervals are non-parametric bootstrap 95% intervals over examples.",
        "",
        "| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.model_name} | {row.examples} | {_fmt(row.boundary_f1)} | "
            f"{_fmt(row.avg_model_tokens_word)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Use this report to avoid over-reading tiny F1 differences among",
            "train-only marker policies. If intervals overlap heavily, prefer the",
            "lower-token-pressure candidate until downstream/BPB calibration says",
            "otherwise.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Bootstrap CI for v2.0 train-only marker frontier.")
    parser.add_argument("--dataset", default="data/eval/tr_challenge.tsv")
    parser.add_argument(
        "--sp64-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--all-soft-model",
        default="artifacts/private/v2_0_candidate_sentencepiece/protected_hard_soft_marker_raw_sp64_unigram_64000.model",
    )
    parser.add_argument(
        "--suffix-chain2-model",
        default="artifacts/private/v2_0_candidate_sentencepiece/protected_hard_train_only_suffix_chain2_unigram_64000.model",
    )
    parser.add_argument(
        "--high-value-suffix-model",
        default="artifacts/private/v2_0_candidate_sentencepiece/protected_hard_train_only_high_value_suffix_unigram_64000.model",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260608)
    parser.add_argument("--report-out", default="artifacts/v2_0_train_only_marker_frontier_ci.md")
    args = parser.parse_args(argv)

    dataset = Path(args.dataset)
    cases = load_cases(dataset)
    selected = selected_piece_strings(Path(args.selected_pieces))
    sp64_model = Path(args.sp64_model)
    sp64_processor = load_sp_processor(sp64_model)
    model_results = evaluate_finite_sp64_cases(
        cases,
        processor=sp64_processor,
        sp64_model=sp64_model,
        selected_pieces=selected,
    )
    # Custom is useful in the source report but not part of this frontier table.
    model_results.pop("custom_tr_morph", None)
    add_marker_stripped_model(
        model_results,
        model_name="all_soft_marker_stripped",
        model_path=Path(args.all_soft_model),
        cases=cases,
        selected_pieces=selected,
    )
    add_marker_stripped_model(
        model_results,
        model_name="suffix_chain2_marker_stripped",
        model_path=Path(args.suffix_chain2_model),
        cases=cases,
        selected_pieces=selected,
    )
    add_marker_stripped_model(
        model_results,
        model_name="high_value_suffix_marker_stripped",
        model_path=Path(args.high_value_suffix_model),
        cases=cases,
        selected_pieces=selected,
    )
    rows = bootstrap_rows(model_results, samples=args.samples, seed=args.seed)
    report = format_report(rows, dataset=dataset, samples=args.samples)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
