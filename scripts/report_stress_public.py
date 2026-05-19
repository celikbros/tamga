from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.tokenizer import WORD_START  # noqa: E402


@dataclass(frozen=True)
class StressCase:
    category: str
    text: str
    protected_spans: list[str]


@dataclass(frozen=True)
class ProtectedSpanResult:
    span: str
    preserved: bool


@dataclass(frozen=True)
class StressResult:
    case: StressCase
    tokens: list[str]
    decoded: str
    protected_results: list[ProtectedSpanResult]

    @property
    def roundtrip_exact(self) -> bool:
        return self.decoded == self.case.text

    @property
    def protected_total(self) -> int:
        return len(self.protected_results)

    @property
    def protected_preserved(self) -> int:
        return sum(result.preserved for result in self.protected_results)


@dataclass(frozen=True)
class StressReport:
    results: list[StressResult]

    @property
    def total_examples(self) -> int:
        return len(self.results)

    @property
    def roundtrip_exact(self) -> int:
        return sum(result.roundtrip_exact for result in self.results)

    @property
    def protected_total(self) -> int:
        return sum(result.protected_total for result in self.results)

    @property
    def protected_preserved(self) -> int:
        return sum(result.protected_preserved for result in self.results)

    @property
    def by_category(self) -> dict[str, list[StressResult]]:
        grouped: dict[str, list[StressResult]] = defaultdict(list)
        for result in self.results:
            grouped[result.case.category].append(result)
        return dict(sorted(grouped.items()))

    @property
    def broken_protected_spans(self) -> list[tuple[StressResult, ProtectedSpanResult]]:
        broken: list[tuple[StressResult, ProtectedSpanResult]] = []
        for result in self.results:
            for span_result in result.protected_results:
                if not span_result.preserved:
                    broken.append((result, span_result))
        return broken


def _token_surface(token: str) -> str:
    if token.startswith(WORD_START):
        return token[len(WORD_START) :]
    return token


def is_span_preserved(span: str, tokens: list[str]) -> bool:
    return span in {_token_surface(token) for token in tokens}


def load_stress_cases(path: str | Path) -> list[StressCase]:
    cases: list[StressCase] = []
    source = Path(path)

    with source.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue

            fields = line.split("\t")
            if len(fields) != 3:
                raise ValueError(
                    f"{source}:{line_number}: expected "
                    "category<TAB>text<TAB>protected_spans_json"
                )

            category, text, protected_json = fields
            protected_spans = json.loads(protected_json)
            if not isinstance(protected_spans, list) or not all(
                isinstance(span, str) for span in protected_spans
            ):
                raise ValueError(
                    f"{source}:{line_number}: protected_spans_json must be a string list"
                )

            cases.append(
                StressCase(
                    category=category,
                    text=text,
                    protected_spans=protected_spans,
                )
            )

    return cases


def evaluate_stress_cases(
    cases: list[StressCase],
    tokenizer: TurkishTokenizer | None = None,
) -> StressReport:
    tokenizer = tokenizer or TurkishTokenizer()
    results: list[StressResult] = []

    for case in cases:
        tokens = tokenizer.encode(case.text)
        protected_results = [
            ProtectedSpanResult(span=span, preserved=is_span_preserved(span, tokens))
            for span in case.protected_spans
        ]
        results.append(
            StressResult(
                case=case,
                tokens=tokens,
                decoded=tokenizer.decode(tokens),
                protected_results=protected_results,
            )
        )

    return StressReport(results)


def _ratio(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "n/a"
    return f"{numerator}/{denominator} ({numerator / denominator:.4f})"


def _json_tokens(tokens: list[str]) -> str:
    return json.dumps(tokens, ensure_ascii=False, separators=(",", ":"))


def _category_row(category: str, results: list[StressResult]) -> str:
    examples = len(results)
    roundtrip = sum(result.roundtrip_exact for result in results)
    protected_total = sum(result.protected_total for result in results)
    protected_preserved = sum(result.protected_preserved for result in results)
    avg_tokens = sum(len(result.tokens) for result in results) / examples
    return (
        f"| {category} | {examples} | {_ratio(roundtrip, examples)} | "
        f"{_ratio(protected_preserved, protected_total)} | {avg_tokens:.2f} |"
    )


def render_markdown(report: StressReport) -> str:
    lines: list[str] = [
        "# Public Stress Report",
        "",
        "Tokenizer behavior is not changed by this report.",
        "",
        "## SUMMARY",
        "",
        f"- examples: {report.total_examples}",
        f"- roundtrip_exact: {_ratio(report.roundtrip_exact, report.total_examples)}",
        f"- protected_spans_preserved: "
        f"{_ratio(report.protected_preserved, report.protected_total)}",
        "",
        "## CATEGORY SUMMARY",
        "",
        "| category | examples | roundtrip_exact | protected_preserved | avg_tokens |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for category, results in report.by_category.items():
        lines.append(_category_row(category, results))

    lines.extend(["", "## BROKEN PROTECTED SPANS", ""])
    if report.broken_protected_spans:
        for result, span_result in report.broken_protected_spans:
            lines.extend(
                [
                    f"- category: `{result.case.category}`",
                    f"  text: `{result.case.text}`",
                    f"  broken_span: `{span_result.span}`",
                    f"  tokens: `{_json_tokens(result.tokens)}`",
                ]
            )
    else:
        lines.append("No broken protected spans.")

    lines.extend(["", "## SAMPLE TOKENIZATIONS", ""])
    for result in report.results:
        lines.extend(
            [
                f"### {result.case.category}",
                "",
                f"Text: `{result.case.text}`",
                "",
                "Tokens:",
                "",
                "```json",
                _json_tokens(result.tokens),
                "```",
                "",
                f"Decoded: `{result.decoded}`",
                "",
                f"Roundtrip exact: `{result.roundtrip_exact}`",
                "",
            ]
        )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Report public tokenizer stress behavior.")
    parser.add_argument("tsv_path", help="category<TAB>text<TAB>protected_spans_json")
    parser.add_argument("--markdown-out", help="Optional Markdown report path")
    args = parser.parse_args(argv)

    report = evaluate_stress_cases(load_stress_cases(args.tsv_path))
    markdown = render_markdown(report)
    print(markdown)

    if args.markdown_out:
        output_path = Path(args.markdown_out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
