from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import argparse
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.pretok import (  # noqa: E402
    is_file_like_token,
    is_numeric_like_token,
    is_technical_comparator_token,
    is_url_like_token,
)
from tr_tokenizer.tokenizer import WORD_START  # noqa: E402

TOKEN_KINDS = (
    "suffix",
    "apostrophe",
    "protected_url",
    "protected_file",
    "protected_number",
    "protected_technical",
    "word",
    "punctuation_symbol",
    "other",
)


@dataclass(frozen=True)
class TextCase:
    category: str
    text: str


@dataclass(frozen=True)
class CoverageResult:
    case: TextCase
    tokens: list[str]
    counts: Counter[str]

    @property
    def protected_count(self) -> int:
        return (
            self.counts["protected_url"]
            + self.counts["protected_file"]
            + self.counts["protected_number"]
            + self.counts["protected_technical"]
        )


@dataclass(frozen=True)
class CoverageReport:
    results: list[CoverageResult]

    @property
    def total_examples(self) -> int:
        return len(self.results)

    @property
    def total_tokens(self) -> int:
        return sum(len(result.tokens) for result in self.results)

    @property
    def counts(self) -> Counter[str]:
        total: Counter[str] = Counter()
        for result in self.results:
            total.update(result.counts)
        return total

    @property
    def by_category(self) -> dict[str, list[CoverageResult]]:
        grouped: dict[str, list[CoverageResult]] = defaultdict(list)
        for result in self.results:
            grouped[result.case.category].append(result)
        return dict(sorted(grouped.items()))


def token_surface(token: str) -> str:
    if token.startswith(WORD_START):
        return token[len(WORD_START) :]
    return token


def classify_token(token: str) -> str:
    if token.startswith("+"):
        return "suffix"
    if token == "'":
        return "apostrophe"

    surface = token_surface(token)
    if is_url_like_token(surface):
        return "protected_url"
    if is_file_like_token(surface):
        return "protected_file"
    if is_numeric_like_token(surface):
        return "protected_number"
    if is_technical_comparator_token(surface):
        return "protected_technical"
    if token.startswith(WORD_START):
        return "word"
    if len(surface) == 1 and unicodedata.category(surface)[0] in {"P", "S"}:
        return "punctuation_symbol"
    return "other"


def load_text_cases(path: str | Path) -> list[TextCase]:
    cases: list[TextCase] = []
    source = Path(path)

    with source.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue

            fields = line.split("\t")
            if len(fields) == 2:
                category = "default"
                text = fields[0]
            elif len(fields) == 3:
                category = fields[0]
                text = fields[1]
            else:
                raise ValueError(
                    f"{source}:{line_number}: expected 2 or 3 tab-separated fields"
                )

            cases.append(TextCase(category=category, text=text))

    return cases


def evaluate_coverage(
    cases: list[TextCase],
    tokenizer: TurkishTokenizer | None = None,
) -> CoverageReport:
    tokenizer = tokenizer or TurkishTokenizer()
    results: list[CoverageResult] = []

    for case in cases:
        tokens = tokenizer.encode(case.text)
        counts = Counter(classify_token(token) for token in tokens)
        results.append(CoverageResult(case=case, tokens=tokens, counts=counts))

    return CoverageReport(results)


def _pct(count: int, total: int) -> str:
    if total == 0:
        return "0.0000"
    return f"{count / total:.4f}"


def _category_row(category: str, results: list[CoverageResult]) -> str:
    examples = len(results)
    tokens = sum(len(result.tokens) for result in results)
    counts: Counter[str] = Counter()
    for result in results:
        counts.update(result.counts)

    protected = (
        counts["protected_url"]
        + counts["protected_file"]
        + counts["protected_number"]
        + counts["protected_technical"]
    )
    avg_tokens = tokens / examples if examples else 0.0
    return (
        f"| {category} | {examples} | {tokens} | {avg_tokens:.2f} | "
        f"{counts['suffix']} | {protected} | {counts['word']} | "
        f"{counts['punctuation_symbol']} | {counts['other']} |"
    )


def render_markdown(report: CoverageReport) -> str:
    total_tokens = report.total_tokens
    lines: list[str] = [
        "# Coverage Telemetry Report",
        "",
        "Tokenizer behavior is not changed by this report.",
        "",
        "## SUMMARY",
        "",
        f"- examples: {report.total_examples}",
        f"- tokens: {total_tokens}",
        f"- avg_tokens_per_example: "
        f"{(total_tokens / report.total_examples if report.total_examples else 0.0):.4f}",
        "",
        "## TOKEN KIND COUNTS",
        "",
        "| token_kind | count | share |",
        "| --- | ---: | ---: |",
    ]

    for kind in TOKEN_KINDS:
        count = report.counts[kind]
        lines.append(f"| {kind} | {count} | {_pct(count, total_tokens)} |")

    lines.extend(
        [
            "",
            "## CATEGORY SUMMARY",
            "",
            "| category | examples | tokens | avg_tokens | suffix | protected | word | punctuation_symbol | other |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for category, results in report.by_category.items():
        lines.append(_category_row(category, results))

    lines.extend(["", "## OTHER TOKEN EXAMPLES", ""])
    examples_with_other = [
        result for result in report.results if result.counts["other"] > 0
    ][:10]
    if examples_with_other:
        for result in examples_with_other:
            other_tokens = [
                token for token in result.tokens if classify_token(token) == "other"
            ]
            lines.extend(
                [
                    f"- category: `{result.case.category}`",
                    f"  text: `{result.case.text}`",
                    f"  other_tokens: `{other_tokens}`",
                ]
            )
    else:
        lines.append("No `other` tokens.")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Report tokenizer coverage telemetry.")
    parser.add_argument("tsv_path", help="TSV with text or category/text rows")
    parser.add_argument("--markdown-out", help="Optional Markdown report path")
    args = parser.parse_args(argv)

    report = evaluate_coverage(load_text_cases(args.tsv_path))
    markdown = render_markdown(report)
    print(markdown)

    if args.markdown_out:
        output_path = Path(args.markdown_out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
