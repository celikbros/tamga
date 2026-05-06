from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class EvalCase:
    text: str
    expected: list[str]
    category: str = "default"


@dataclass(frozen=True)
class CaseResult:
    text: str
    expected: list[str]
    actual: list[str]
    category: str = "default"

    @property
    def exact_match(self) -> bool:
        return self.expected == self.actual

    @property
    def correct_tokens(self) -> int:
        return sum((Counter(self.expected) & Counter(self.actual)).values())

    @property
    def expected_only(self) -> list[str]:
        return list((Counter(self.expected) - Counter(self.actual)).elements())

    @property
    def actual_only(self) -> list[str]:
        return list((Counter(self.actual) - Counter(self.expected)).elements())


@dataclass(frozen=True)
class EvalReport:
    results: list[CaseResult]

    @property
    def exact_matches(self) -> int:
        return sum(result.exact_match for result in self.results)

    @property
    def total_expected_tokens(self) -> int:
        return sum(len(result.expected) for result in self.results)

    @property
    def total_actual_tokens(self) -> int:
        return sum(len(result.actual) for result in self.results)

    @property
    def total_correct_tokens(self) -> int:
        return sum(result.correct_tokens for result in self.results)

    @property
    def precision(self) -> float:
        if self.total_actual_tokens == 0:
            return 0.0
        return self.total_correct_tokens / self.total_actual_tokens

    @property
    def recall(self) -> float:
        if self.total_expected_tokens == 0:
            return 0.0
        return self.total_correct_tokens / self.total_expected_tokens

    @property
    def f1(self) -> float:
        denominator = self.precision + self.recall
        if denominator == 0:
            return 0.0
        return 2 * self.precision * self.recall / denominator

    @property
    def by_category(self) -> dict[str, "EvalReport"]:
        reports: dict[str, list[CaseResult]] = {}
        for result in self.results:
            reports.setdefault(result.category, []).append(result)
        return {
            category: EvalReport(results)
            for category, results in sorted(reports.items())
        }


def load_cases(path: str | Path) -> list[EvalCase]:
    cases: list[EvalCase] = []
    source = Path(path)

    with source.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue

            fields = line.split("\t")
            if len(fields) == 2:
                category = "default"
                text, expected_json = fields
            elif len(fields) == 3:
                category, text, expected_json = fields
            else:
                raise ValueError(
                    f"{source}:{line_number}: expected text<TAB>json "
                    "or category<TAB>text<TAB>json"
                )

            expected = json.loads(expected_json)
            if not isinstance(expected, list) or not all(
                isinstance(token, str) for token in expected
            ):
                raise ValueError(
                    f"{source}:{line_number}: expected_tokens_json must be a string list"
                )

            cases.append(EvalCase(text=text, expected=expected, category=category))

    return cases


def evaluate_case(case: EvalCase, tokenizer: TurkishTokenizer | None = None) -> CaseResult:
    tokenizer = tokenizer or TurkishTokenizer()
    return CaseResult(
        category=case.category,
        text=case.text,
        expected=case.expected,
        actual=tokenizer.encode(case.text),
    )


def evaluate_cases(
    cases: list[EvalCase],
    tokenizer: TurkishTokenizer | None = None,
) -> EvalReport:
    tokenizer = tokenizer or TurkishTokenizer()
    return EvalReport([evaluate_case(case, tokenizer) for case in cases])


def format_tokens(tokens: list[str]) -> str:
    return json.dumps(tokens, ensure_ascii=False, separators=(",", ":"))


def print_report(report: EvalReport) -> None:
    failures = [result for result in report.results if not result.exact_match]

    for result in failures:
        print("MISMATCH")
        print(f"category: {result.category}")
        print(f"text:     {result.text}")
        print(f"expected: {format_tokens(result.expected)}")
        print(f"actual:   {format_tokens(result.actual)}")
        print(f"expected_only: {format_tokens(result.expected_only)}")
        print(f"actual_only:   {format_tokens(result.actual_only)}")
        print()

    total = len(report.results)
    print("SUMMARY")
    print(f"examples:    {total}")
    print(f"exact_match: {report.exact_matches}/{total}")
    print(f"precision:   {report.precision:.4f}")
    print(f"recall:      {report.recall:.4f}")
    print(f"f1:          {report.f1:.4f}")

    if report.by_category:
        print()
        print("CATEGORY SUMMARY")
        for category, category_report in report.by_category.items():
            category_total = len(category_report.results)
            print(
                f"{category}: "
                f"exact_match={category_report.exact_matches}/{category_total} "
                f"f1={category_report.f1:.4f}"
            )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Evaluate tr-tokenizer on a TSV file.")
    parser.add_argument("tsv_path", help="Path to text<TAB>expected_tokens_json data")
    args = parser.parse_args(argv)

    report = evaluate_cases(load_cases(args.tsv_path))
    print_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
