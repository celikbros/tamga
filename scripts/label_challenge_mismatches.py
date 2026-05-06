from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.analyze_mismatches import (  # noqa: E402
    find_over_splitting,
    find_under_splitting,
)
from scripts.evaluate_tokenizer import (  # noqa: E402
    CaseResult,
    EvalCase,
    evaluate_cases,
    format_tokens,
    load_cases,
)

LABELS = {
    "exact_match",
    "safe_rule_candidate",
    "needs_lexicon",
    "needs_context",
    "hybrid_candidate",
    "do_not_fix_yet",
}


@dataclass(frozen=True)
class LabeledCase:
    category: str
    text: str
    expected: list[str]
    actual: list[str]
    label: str
    reason: str
    next_step: str

    @property
    def exact_match(self) -> bool:
        return self.expected == self.actual


def classify_result(result: CaseResult) -> tuple[str, str, str]:
    if result.exact_match:
        return (
            "exact_match",
            "expected and actual tokens match",
            "keep as regression evidence",
        )

    over_splitting = find_over_splitting(result.expected, result.actual)
    under_splitting = find_under_splitting(result.expected, result.actual)

    if result.category == "ambiguity":
        return (
            "needs_context",
            "surface form can have multiple analyses without context",
            "do not add a broad rule before ambiguity policy is decided",
        )

    if result.category == "negative_word":
        return (
            "do_not_fix_yet",
            "fixing this class risks false-positive splits in common words",
            "expand negative regressions and keep the conservative core",
        )

    if result.category in {"numbers_dates", "punctuation", "proper_name"}:
        return (
            "safe_rule_candidate",
            "remaining issue is isolated to punctuation/apostrophe/token-boundary flow",
            "add a narrow fixture before any tokenizer change",
        )

    if result.category in {"softening", "suffix_chain", "informal"}:
        label = "needs_lexicon"
        reason = "expected-only stems or suffixes suggest a guarded lexicon gap"
        if over_splitting:
            reason = "over-splitting also appears; add regressions before lexicon changes"
        return (
            label,
            reason,
            "batch small surface-stem additions with negative-word regressions",
        )

    if result.category in {"verb_future", "code_mixed"}:
        return (
            "hybrid_candidate",
            "productive chain is likely better handled by morphology-aware fallback",
            "defer to MorphBPE/hybrid design unless a very narrow rule is obvious",
        )

    if result.category in {"verb_past", "question"}:
        if under_splitting and not over_splitting:
            return (
                "needs_lexicon",
                "under-splitting points to a missing guarded stem or verb pattern",
                "consider a small lexicon batch with frozen regression checks",
            )
        return (
            "hybrid_candidate",
            "mixed mismatch pattern crosses lexical and suffix decisions",
            "label examples manually before adding rules",
        )

    return (
        "hybrid_candidate",
        "unclassified mismatch pattern",
        "inspect manually before tokenizer changes",
    )


def label_results(results: list[CaseResult]) -> list[LabeledCase]:
    labeled: list[LabeledCase] = []
    for result in results:
        label, reason, next_step = classify_result(result)
        if label not in LABELS:
            raise ValueError(f"unknown label: {label}")
        labeled.append(
            LabeledCase(
                category=result.category,
                text=result.text,
                expected=result.expected,
                actual=result.actual,
                label=label,
                reason=reason,
                next_step=next_step,
            )
        )
    return labeled


def label_cases(cases: list[EvalCase]) -> list[LabeledCase]:
    return label_results(evaluate_cases(cases).results)


def tsv_escape(value: str) -> str:
    return value.replace("\t", " ").replace("\n", " ")


def render_labeled_tsv(labeled_cases: list[LabeledCase]) -> str:
    lines = [
        "label\tcategory\ttext\texpected_tokens_json\tactual_tokens_json\treason\tnext_step"
    ]
    for case in labeled_cases:
        lines.append(
            "\t".join(
                [
                    case.label,
                    case.category,
                    tsv_escape(case.text),
                    format_tokens(case.expected),
                    format_tokens(case.actual),
                    tsv_escape(case.reason),
                    tsv_escape(case.next_step),
                ]
            )
        )
    return "\n".join(lines) + "\n"


def label_file(input_path: str | Path, output_path: str | Path) -> list[LabeledCase]:
    labeled_cases = label_cases(load_cases(input_path))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_labeled_tsv(labeled_cases), encoding="utf-8")
    return labeled_cases


def count_by_label(labeled_cases: list[LabeledCase]) -> Counter[str]:
    return Counter(case.label for case in labeled_cases)


def count_by_category_and_label(
    labeled_cases: list[LabeledCase],
) -> dict[str, Counter[str]]:
    table: dict[str, Counter[str]] = {}
    for case in labeled_cases:
        table.setdefault(case.category, Counter())[case.label] += 1
    return dict(sorted(table.items()))


def render_markdown(labeled_cases: list[LabeledCase], title: str) -> str:
    label_counts = count_by_label(labeled_cases)
    category_table = count_by_category_and_label(labeled_cases)
    mismatches = [case for case in labeled_cases if not case.exact_match]

    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Examples | {len(labeled_cases)} |",
        f"| Exact match | {label_counts.get('exact_match', 0)}/{len(labeled_cases)} |",
        f"| Mismatches | {len(mismatches)} |",
        "",
        "## Label Summary",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    for label in sorted(LABELS):
        lines.append(f"| {label} | {label_counts.get(label, 0)} |")

    labels = sorted(LABELS)
    lines.extend(
        [
            "",
            "## Category x Label",
            "",
            "| Category | " + " | ".join(labels) + " |",
            "| --- | " + " | ".join("---:" for _ in labels) + " |",
        ]
    )
    for category, counts in category_table.items():
        lines.append(
            f"| {category} | "
            + " | ".join(str(counts.get(label, 0)) for label in labels)
            + " |"
        )

    lines.extend(
        [
            "",
            "## Mismatch Decisions",
            "",
            "| Label | Category | Text | Reason | Next step |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for case in mismatches:
        lines.append(
            f"| {case.label} | {case.category} | {case.text} | "
            f"{case.reason} | {case.next_step} |"
        )

    lines.extend(
        [
            "",
            "## v1.3 Candidate View",
            "",
            "- Start with `safe_rule_candidate` only if a fixture can isolate the behavior.",
            "- Batch `needs_lexicon` examples and protect negative regressions first.",
            "- Keep `needs_context` and `do_not_fix_yet` out of deterministic rules.",
            "- Treat `hybrid_candidate` as MorphBPE design input.",
        ]
    )

    return "\n".join(lines) + "\n"


def write_markdown_report(
    labeled_cases: list[LabeledCase],
    output_path: str | Path,
    *,
    title: str,
) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown(labeled_cases, title), encoding="utf-8")


def print_summary(labeled_cases: list[LabeledCase]) -> None:
    label_counts = count_by_label(labeled_cases)
    category_table = count_by_category_and_label(labeled_cases)

    print("LABEL SUMMARY")
    for label in sorted(LABELS):
        print(f"{label}: {label_counts.get(label, 0)}")

    print()
    print("CATEGORY X LABEL")
    labels = sorted(LABELS)
    print("category\t" + "\t".join(labels))
    for category, counts in category_table.items():
        print(
            category
            + "\t"
            + "\t".join(str(counts.get(label, 0)) for label in labels)
        )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Label challenge mismatches for v1.2 error taxonomy."
    )
    parser.add_argument("input_tsv")
    parser.add_argument("output_tsv")
    parser.add_argument("--markdown-out", help="Optional Markdown report path")
    args = parser.parse_args(argv)

    labeled_cases = label_file(args.input_tsv, args.output_tsv)
    if args.markdown_out:
        write_markdown_report(
            labeled_cases,
            args.markdown_out,
            title=f"v1.2 Error Taxonomy: {Path(args.input_tsv).name}",
        )

    print(f"wrote: {args.output_tsv}")
    if args.markdown_out:
        print(f"wrote_markdown: {args.markdown_out}")
    print()
    print_summary(labeled_cases)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
