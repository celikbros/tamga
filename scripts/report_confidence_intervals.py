from __future__ import annotations

from dataclasses import dataclass
import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_bpe_sweep import micro_boundary  # noqa: E402
from scripts.compare_real_tokenizers import (  # noqa: E402
    RealBaselineSpec,
    RealCaseResult,
    build_specs,
    evaluate_real_baselines,
    summarize_model,
)
from scripts.compare_tokenizers import count_words  # noqa: E402
from scripts.evaluate_tokenizer import load_cases  # noqa: E402


@dataclass(frozen=True)
class MetricInterval:
    point: float
    lower: float
    upper: float


@dataclass(frozen=True)
class ModelConfidenceRow:
    model_name: str
    status: str
    exact_match_rate: MetricInterval
    boundary_f1: MetricInterval
    avg_tokens_word: MetricInterval
    reason: str = ""


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def interval(values: list[float], *, point: float) -> MetricInterval:
    if not values:
        return MetricInterval(point, 0.0, 0.0)
    return MetricInterval(
        point=point,
        lower=percentile(values, 0.025),
        upper=percentile(values, 0.975),
    )


def exact_match_rate(results: list[RealCaseResult]) -> float:
    if not results:
        return 0.0
    return sum(result.exact_match for result in results) / len(results)


def avg_tokens_per_word(results: list[RealCaseResult]) -> float:
    words = sum(count_words(result.text) for result in results)
    if not words:
        return 0.0
    return sum(len(result.tokens) for result in results) / words


def boundary_f1(results: list[RealCaseResult]) -> float:
    if not results:
        return 0.0
    return micro_boundary(results).f1  # type: ignore[arg-type]


def bootstrap_model(
    results: list[RealCaseResult],
    *,
    samples: int,
    seed: int,
) -> ModelConfidenceRow:
    if not results:
        empty = MetricInterval(0.0, 0.0, 0.0)
        return ModelConfidenceRow("", "skipped", empty, empty, empty)

    summary = summarize_model(results)
    if summary.status != "ok":
        empty = MetricInterval(0.0, 0.0, 0.0)
        return ModelConfidenceRow(
            model_name=summary.model_name,
            status=summary.status,
            exact_match_rate=empty,
            boundary_f1=empty,
            avg_tokens_word=empty,
            reason=summary.reason,
        )

    rng = random.Random(seed)
    exact_values: list[float] = []
    boundary_values: list[float] = []
    token_values: list[float] = []
    total = len(results)

    for _ in range(samples):
        sample = [results[rng.randrange(total)] for _ in range(total)]
        exact_values.append(exact_match_rate(sample))
        boundary_values.append(boundary_f1(sample))
        token_values.append(avg_tokens_per_word(sample))

    return ModelConfidenceRow(
        model_name=summary.model_name,
        status=summary.status,
        exact_match_rate=interval(
            exact_values,
            point=exact_match_rate(results),
        ),
        boundary_f1=interval(
            boundary_values,
            point=boundary_f1(results),
        ),
        avg_tokens_word=interval(
            token_values,
            point=avg_tokens_per_word(results),
        ),
    )


def bootstrap_report(
    model_results: dict[str, list[RealCaseResult]],
    *,
    samples: int,
    seed: int,
) -> list[ModelConfidenceRow]:
    rows: list[ModelConfidenceRow] = []
    for index, results in enumerate(model_results.values()):
        rows.append(
            bootstrap_model(
                results,
                samples=samples,
                seed=seed + index * 1009,
            )
        )
    return rows


def _fmt_interval(value: MetricInterval) -> str:
    return f"{value.point:.4f} [{value.lower:.4f}, {value.upper:.4f}]"


def format_text_report(rows: list[ModelConfidenceRow], *, samples: int) -> str:
    lines = [
        "CONFIDENCE INTERVALS",
        f"bootstrap_samples\t{samples}",
        "model_name\tstatus\texact_match_rate\tboundary_f1\tavg_tokens/word\treason",
    ]
    for row in rows:
        lines.append(
            f"{row.model_name}\t{row.status}\t"
            f"{_fmt_interval(row.exact_match_rate)}\t"
            f"{_fmt_interval(row.boundary_f1)}\t"
            f"{_fmt_interval(row.avg_tokens_word)}\t"
            f"{row.reason}"
        )
    return "\n".join(lines)


def format_markdown(rows: list[ModelConfidenceRow], *, samples: int) -> str:
    lines = [
        "# Metric Confidence Intervals",
        "",
        f"Bootstrap samples: `{samples}`",
        "",
        "| Model | Status | Exact match rate | Boundary F1 | Avg tokens/word | Notes |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.model_name} | {row.status} | "
            f"{_fmt_interval(row.exact_match_rate)} | "
            f"{_fmt_interval(row.boundary_f1)} | "
            f"{_fmt_interval(row.avg_tokens_word)} | {row.reason} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Intervals are non-parametric bootstrap 95% intervals over examples.",
            "- These intervals reflect dataset sampling uncertainty, not annotation uncertainty.",
            "- Small smoke sets can have wide or unstable intervals; interpret them cautiously.",
        ]
    )
    return "\n".join(lines) + "\n"


def default_specs() -> list[RealBaselineSpec]:
    return [
        RealBaselineSpec(name="custom_tr_morph", kind="custom"),
        RealBaselineSpec(name="unicode_char", kind="unicode_char"),
    ]


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Report bootstrap confidence intervals for tokenizer metrics.",
    )
    parser.add_argument("gold_tsv")
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=13)
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
        "--allow-download",
        action="store_true",
        help="Allow Hugging Face tokenizers to download missing models.",
    )
    parser.add_argument("--markdown-out", help="Optional Markdown report output path")
    args = parser.parse_args(argv)

    if args.samples < 1:
        parser.error("--samples must be at least 1")

    specs = (
        build_specs(args)
        if (args.toy_bpe or args.hf or args.sentencepiece)
        else default_specs()
    )
    model_results = evaluate_real_baselines(
        load_cases(args.gold_tsv),
        specs,
        local_files_only=not args.allow_download,
    )
    rows = bootstrap_report(model_results, samples=args.samples, seed=args.seed)
    print(format_text_report(rows, samples=args.samples))

    if args.markdown_out:
        target = Path(args.markdown_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(format_markdown(rows, samples=args.samples), encoding="utf-8")
        print(f"wrote_markdown: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
