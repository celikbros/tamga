from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_tokenizer import (  # noqa: E402
    CaseResult,
    EvalReport,
    evaluate_cases,
    format_tokens,
    load_cases,
)


@dataclass(frozen=True)
class CategoryAnalysis:
    category: str
    total: int
    mismatches: int
    f1: float
    avg_token_count_diff: float

    @property
    def exact_match(self) -> str:
        return f"{self.total - self.mismatches}/{self.total}"


@dataclass(frozen=True)
class SplitCase:
    category: str
    text: str
    detail: str


@dataclass(frozen=True)
class Recommendation:
    priority: str
    category: str
    suspected_issue: str
    example: str
    suggested_fix: str
    regression_risk: str


@dataclass(frozen=True)
class MismatchAnalysis:
    report: EvalReport
    category_rows: list[CategoryAnalysis]
    expected_only: Counter[str]
    actual_only: Counter[str]
    missing_suffixes: Counter[str]
    missing_stems: Counter[str]
    over_splitting: list[SplitCase]
    under_splitting: list[SplitCase]
    recommendations: list[Recommendation]


def token_surface(token: str) -> str:
    if token.startswith(("▁", "+")):
        return token[1:]
    return token


def find_under_splitting(expected: list[str], actual: list[str]) -> list[str]:
    findings: list[str] = []
    expected_surfaces = [token_surface(token) for token in expected]

    for actual_token in actual:
        actual_surface = token_surface(actual_token)
        if len(actual_surface) <= 1:
            continue
        for start in range(len(expected_surfaces)):
            merged = ""
            for end in range(start, len(expected_surfaces)):
                merged += expected_surfaces[end]
                if len(merged) > len(actual_surface):
                    break
                if end > start and merged == actual_surface:
                    expected_span = expected[start : end + 1]
                    findings.append(
                        f"{format_tokens(expected_span)} collapsed into {actual_token}"
                    )
                    break

    return findings


def find_over_splitting(expected: list[str], actual: list[str]) -> list[str]:
    findings: list[str] = []
    actual_surfaces = [token_surface(token) for token in actual]

    for expected_token in expected:
        expected_surface = token_surface(expected_token)
        if len(expected_surface) <= 1:
            continue
        for start in range(len(actual_surfaces)):
            merged = ""
            for end in range(start, len(actual_surfaces)):
                merged += actual_surfaces[end]
                if len(merged) > len(expected_surface):
                    break
                if end > start and merged == expected_surface:
                    actual_span = actual[start : end + 1]
                    findings.append(
                        f"{expected_token} split as {format_tokens(actual_span)}"
                    )
                    break

    return findings


def analyze_report(report: EvalReport) -> MismatchAnalysis:
    failures = [result for result in report.results if not result.exact_match]
    expected_only: Counter[str] = Counter()
    actual_only: Counter[str] = Counter()
    missing_suffixes: Counter[str] = Counter()
    missing_stems: Counter[str] = Counter()
    over_splitting: list[SplitCase] = []
    under_splitting: list[SplitCase] = []

    for result in failures:
        expected_only.update(result.expected_only)
        actual_only.update(result.actual_only)
        missing_suffixes.update(token for token in result.expected_only if token.startswith("+"))
        missing_stems.update(token for token in result.expected_only if token.startswith("▁"))

        for detail in find_over_splitting(result.expected, result.actual):
            over_splitting.append(
                SplitCase(result.category, result.text, detail)
            )
        for detail in find_under_splitting(result.expected, result.actual):
            under_splitting.append(
                SplitCase(result.category, result.text, detail)
            )

    category_rows = build_category_rows(report)
    recommendations = build_recommendations(report, category_rows)

    return MismatchAnalysis(
        report=report,
        category_rows=category_rows,
        expected_only=expected_only,
        actual_only=actual_only,
        missing_suffixes=missing_suffixes,
        missing_stems=missing_stems,
        over_splitting=over_splitting,
        under_splitting=under_splitting,
        recommendations=recommendations,
    )


def build_category_rows(report: EvalReport) -> list[CategoryAnalysis]:
    rows: list[CategoryAnalysis] = []
    for category, category_report in report.by_category.items():
        total = len(category_report.results)
        mismatches = total - category_report.exact_matches
        diff = sum(
            len(result.actual) - len(result.expected)
            for result in category_report.results
        )
        rows.append(
            CategoryAnalysis(
                category=category,
                total=total,
                mismatches=mismatches,
                f1=category_report.f1,
                avg_token_count_diff=diff / total if total else 0.0,
            )
        )

    return sorted(
        rows,
        key=lambda row: (
            -row.mismatches,
            row.f1,
            -abs(row.avg_token_count_diff),
            row.category,
        ),
    )


def build_recommendations(
    report: EvalReport,
    category_rows: list[CategoryAnalysis],
) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    failures_by_category: dict[str, list[CaseResult]] = {}
    for result in report.results:
        if not result.exact_match:
            failures_by_category.setdefault(result.category, []).append(result)

    for index, row in enumerate(
        [category for category in category_rows if category.mismatches],
        start=1,
    ):
        failures = failures_by_category[row.category]
        example = failures[0].text
        issue, fix, risk = recommendation_for(row.category, failures)
        recommendations.append(
            Recommendation(
                priority=f"P{index}",
                category=row.category,
                suspected_issue=issue,
                example=example,
                suggested_fix=fix,
                regression_risk=risk,
            )
        )

    return recommendations


def recommendation_for(
    category: str,
    failures: list[CaseResult],
) -> tuple[str, str, str]:
    expected_only = Counter(
        token
        for result in failures
        for token in result.expected_only
    )
    missing_suffix = next(
        (token for token, _ in expected_only.most_common() if token.startswith("+")),
        None,
    )
    missing_stem = next(
        (token for token, _ in expected_only.most_common() if token.startswith("▁")),
        None,
    )

    if category == "numbers_dates":
        return (
            "number/date punctuation boundary handling",
            "add guarded number/date pretokenizer tests before any rule change",
            "medium",
        )
    if category == "punctuation":
        return (
            "quoted punctuation or attached punctuation pattern",
            "extend punctuation fixtures first, then add narrow pretokenizer cases",
            "medium",
        )
    if category == "softening":
        stem = f" such as {missing_stem}" if missing_stem else ""
        return (
            f"missing surface stem{stem}",
            "add selected surface stems only with negative-word regressions",
            "medium",
        )
    if category == "proper_name":
        suffix = f" such as {missing_suffix}" if missing_suffix else ""
        return (
            f"apostrophe/proper-name suffix gap{suffix}",
            "expand apostrophe suffix inventory with exact regression examples",
            "low",
        )
    if category == "code_mixed":
        return (
            "code/file mixed token boundary gap",
            "add narrow file-like and mixed-case cases without changing normal words",
            "medium",
        )
    if category == "informal":
        suffix = f" such as {missing_suffix}" if missing_suffix else ""
        return (
            f"uncovered informal surface suffix{suffix}",
            "extend informal-only lexicon layer, not the general splitter",
            "medium",
        )
    if category == "ambiguity":
        return (
            "ambiguous word can be lexical item or stem+suffix",
            "treat as high-risk; add policy before adding rules",
            "high",
        )
    if category == "negative_word":
        return (
            "possible false-positive split risk",
            "prefer negative regressions over broader suffix rules",
            "high",
        )
    if category == "verb_future":
        suffix = f" such as {missing_suffix}" if missing_suffix else ""
        return (
            f"future/ability suffix chain gap{suffix}",
            "add only lexicon-aware verb patterns with frozen regression checks",
            "medium",
        )
    if category == "question":
        return (
            "question clitic or person suffix pattern",
            "separate question-particle layer from general noun suffixing",
            "medium",
        )
    if category == "suffix_chain":
        stem = f" such as {missing_stem}" if missing_stem else ""
        return (
            f"long suffix chain stem/inventory gap{stem}",
            "add a small surface-stem batch and re-run expanded regression",
            "medium",
        )
    if category == "verb_past":
        return (
            "past tense stem alternation gap",
            "add only known verb stems with tense-specific tests",
            "medium",
        )
    return (
        "unclassified mismatch pattern",
        "inspect examples manually before adding tokenizer rules",
        "high",
    )


def md_cell(value: object) -> str:
    return str(value).replace("|", "\\|")


def render_counter_table(counter: Counter[str], limit: int = 20) -> list[str]:
    if not counter:
        return ["No candidates."]

    lines = [
        "| Token | Count |",
        "| --- | ---: |",
    ]
    for token, count in counter.most_common(limit):
        lines.append(f"| `{md_cell(token)}` | {count} |")
    return lines


def render_split_cases(cases: list[SplitCase], limit: int = 30) -> list[str]:
    if not cases:
        return ["No candidates."]

    lines = [
        "| Category | Text | Detail |",
        "| --- | --- | --- |",
    ]
    for case in cases[:limit]:
        lines.append(
            f"| {md_cell(case.category)} | {md_cell(case.text)} | "
            f"`{md_cell(case.detail)}` |"
        )
    return lines


def render_analysis_markdown(
    analysis: MismatchAnalysis,
    title: str = "Challenge Mismatch Analysis",
) -> str:
    report = analysis.report
    total = len(report.results)
    mismatches = total - report.exact_matches
    failures = [result for result in report.results if not result.exact_match]

    lines = [
        f"# {title}",
        "",
        "## Overall Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Examples | {total} |",
        f"| Exact match | {report.exact_matches}/{total} |",
        f"| Mismatches | {mismatches} |",
        f"| Precision | {report.precision:.4f} |",
        f"| Recall | {report.recall:.4f} |",
        f"| F1 | {report.f1:.4f} |",
        "",
        "## Category Summary",
        "",
        "| Category | Exact match | Mismatch count | Token F1 | Avg token count diff |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for row in analysis.category_rows:
        lines.append(
            f"| {md_cell(row.category)} | {row.exact_match} | {row.mismatches} | "
            f"{row.f1:.4f} | {row.avg_token_count_diff:.4f} |"
        )

    lines.extend(["", "## Mismatch List", ""])
    if not failures:
        lines.append("No mismatches.")
    else:
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

    lines.extend(
        [
            "## Most Common Expected-Only Tokens",
            "",
            *render_counter_table(analysis.expected_only),
            "",
            "## Most Common Actual-Only Tokens",
            "",
            *render_counter_table(analysis.actual_only),
            "",
            "## Suspected Missing Suffixes",
            "",
            *render_counter_table(analysis.missing_suffixes),
            "",
            "## Suspected Missing Stems",
            "",
            *render_counter_table(analysis.missing_stems),
            "",
            "## Suspected Over-Splitting Cases",
            "",
            *render_split_cases(analysis.over_splitting),
            "",
            "## Suspected Under-Splitting Cases",
            "",
            *render_split_cases(analysis.under_splitting),
            "",
            "## Risky Fixes",
            "",
            "- Do not add short suffixes such as `+ı`, `+i`, `+ın`, `+in` to the general greedy splitter.",
            "- Do not normalize informal words into standard Turkish; keep surface forms.",
            "- Do not broaden mixed-case/code rules into normal lowercase Turkish words.",
            "- Treat ambiguity examples as policy decisions, not automatic lexicon gaps.",
            "",
            "## v1.1 Recommendation Table",
            "",
            "| Priority | Category | Suspected issue | Example | Suggested fix | Regression risk |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    if not analysis.recommendations:
        lines.append("| - | - | No action needed | - | Keep regression frozen | low |")
    else:
        for recommendation in analysis.recommendations:
            lines.append(
                f"| {md_cell(recommendation.priority)} | "
                f"{md_cell(recommendation.category)} | "
                f"{md_cell(recommendation.suspected_issue)} | "
                f"{md_cell(recommendation.example)} | "
                f"{md_cell(recommendation.suggested_fix)} | "
                f"{md_cell(recommendation.regression_risk)} |"
            )

    return "\n".join(lines) + "\n"


def analyze_file(input_path: str | Path, output_path: str | Path) -> MismatchAnalysis:
    source = Path(input_path)
    analysis = analyze_report(evaluate_cases(load_cases(source)))
    markdown = render_analysis_markdown(
        analysis,
        title=f"Challenge Mismatch Analysis: {source.name}",
    )
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown, encoding="utf-8")
    return analysis


def print_console_summary(analysis: MismatchAnalysis) -> None:
    report = analysis.report
    total = len(report.results)
    mismatches = total - report.exact_matches

    print("OVERALL SUMMARY")
    print(f"examples:    {total}")
    print(f"exact_match: {report.exact_matches}/{total}")
    print(f"mismatches:  {mismatches}")
    print(f"precision:   {report.precision:.4f}")
    print(f"recall:      {report.recall:.4f}")
    print(f"f1:          {report.f1:.4f}")
    print()

    print("CATEGORY SUMMARY")
    print("category\texact_match\tmismatches\tf1\tavg_token_count_diff")
    for row in analysis.category_rows:
        print(
            f"{row.category}\t{row.exact_match}\t{row.mismatches}\t"
            f"{row.f1:.4f}\t{row.avg_token_count_diff:.4f}"
        )
    print()

    print("V1.1 RECOMMENDATIONS")
    print("priority\tcategory\tsuspected_issue\texample\tsuggested_fix\tregression_risk")
    for recommendation in analysis.recommendations:
        print(
            f"{recommendation.priority}\t{recommendation.category}\t"
            f"{recommendation.suspected_issue}\t{recommendation.example}\t"
            f"{recommendation.suggested_fix}\t{recommendation.regression_risk}"
        )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Analyze tokenizer mismatches on a TSV evaluation file."
    )
    parser.add_argument("input_tsv")
    parser.add_argument("output_md")
    args = parser.parse_args(argv)

    analysis = analyze_file(args.input_tsv, args.output_md)
    print(f"wrote: {args.output_md}")
    print()
    print_console_summary(analysis)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
