from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_tokenizer import (  # noqa: E402
    EvalReport,
    evaluate_cases,
    format_tokens,
    load_cases,
)


def render_eval_report(report: EvalReport, title: str) -> str:
    total = len(report.results)
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Examples | {total} |",
        f"| Exact match | {report.exact_matches}/{total} |",
        f"| Precision | {report.precision:.4f} |",
        f"| Recall | {report.recall:.4f} |",
        f"| F1 | {report.f1:.4f} |",
        "",
        "## Category Summary",
        "",
        "| Category | Exact match | F1 |",
        "| --- | ---: | ---: |",
    ]

    for category, category_report in report.by_category.items():
        category_total = len(category_report.results)
        lines.append(
            f"| {category} | {category_report.exact_matches}/{category_total} "
            f"| {category_report.f1:.4f} |"
        )

    failures = [result for result in report.results if not result.exact_match]
    lines.extend(["", "## Mismatches", ""])
    if not failures:
        lines.append("No mismatches.")
        return "\n".join(lines) + "\n"

    for result in failures:
        lines.extend(
            [
                f"### {result.category}: {result.text}",
                "",
                f"- Expected: `{format_tokens(result.expected)}`",
                f"- Actual: `{format_tokens(result.actual)}`",
                f"- Expected only: `{format_tokens(result.expected_only)}`",
                f"- Actual only: `{format_tokens(result.actual_only)}`",
                "",
            ]
        )

    return "\n".join(lines) + "\n"


def write_eval_report(input_path: str | Path, output_path: str | Path) -> None:
    source = Path(input_path)
    report = evaluate_cases(load_cases(source))
    markdown = render_eval_report(report, title=f"Evaluation Report: {source.name}")
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Write an evaluation report as Markdown.")
    parser.add_argument("input_tsv")
    parser.add_argument("output_md")
    args = parser.parse_args(argv)

    write_eval_report(args.input_tsv, args.output_md)
    print(f"wrote: {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
