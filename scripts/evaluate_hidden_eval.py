from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_tokenizer import EvalCase, EvalReport, evaluate_cases  # noqa: E402
from scripts.prepare_hidden_eval_views import load_hidden_rows  # noqa: E402

HiddenRow = tuple[str, str, list[str], list[str], str]


@dataclass(frozen=True)
class HiddenEvalReport:
    policy: EvalReport
    independent: EvalReport

    @property
    def total(self) -> int:
        return len(self.policy.results)


def rows_to_cases(rows: list[HiddenRow], *, which: str) -> list[EvalCase]:
    if which not in {"policy", "independent"}:
        raise ValueError("which must be 'policy' or 'independent'")

    gold_index = 3 if which == "policy" else 2
    return [
        EvalCase(
            category=row[0],
            text=row[1],
            expected=row[gold_index],
        )
        for row in rows
    ]


def evaluate_hidden_rows(rows: list[HiddenRow]) -> HiddenEvalReport:
    if not rows:
        raise ValueError("hidden eval file contains no rows")
    return HiddenEvalReport(
        policy=evaluate_cases(rows_to_cases(rows, which="policy")),
        independent=evaluate_cases(rows_to_cases(rows, which="independent")),
    )


def evaluate_hidden_file(path: str | Path) -> HiddenEvalReport:
    return evaluate_hidden_rows(load_hidden_rows(path))


def _category_names(report: HiddenEvalReport) -> list[str]:
    return sorted(
        set(report.policy.by_category.keys()) | set(report.independent.by_category.keys())
    )


def _exact(report: EvalReport) -> str:
    return f"{report.exact_matches}/{len(report.results)}"


def render_markdown(report: HiddenEvalReport, *, title: str = "Hidden Eval Report") -> str:
    lines = [
        f"# {title}",
        "",
        "This report is aggregate-only. It intentionally omits hidden sentences and",
        "token lists.",
        "",
        "## Summary",
        "",
        "| Metric | Policy | Independent |",
        "| --- | ---: | ---: |",
        f"| Examples | {report.total} | {report.total} |",
        f"| Exact match | {_exact(report.policy)} | {_exact(report.independent)} |",
        f"| Precision | {report.policy.precision:.4f} | {report.independent.precision:.4f} |",
        f"| Recall | {report.policy.recall:.4f} | {report.independent.recall:.4f} |",
        f"| F1 | {report.policy.f1:.4f} | {report.independent.f1:.4f} |",
        "",
        "## Category Summary",
        "",
        "| Category | Policy exact | Policy F1 | Independent exact | Independent F1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for category in _category_names(report):
        policy = report.policy.by_category.get(category, EvalReport([]))
        independent = report.independent.by_category.get(category, EvalReport([]))
        lines.append(
            f"| {category} | {_exact(policy)} | {policy.f1:.4f} | "
            f"{_exact(independent)} | {independent.f1:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Policy fidelity measures whether the implementation follows the documented",
            "  project policy.",
            "- Linguistic agreement measures how the same implementation compares with",
            "  independent morphology annotation.",
            "- A gap between the two is not automatically a bug; it may indicate an",
            "  intentional policy difference that should be discussed.",
        ]
    )
    return "\n".join(lines) + "\n"


def print_summary(report: HiddenEvalReport) -> None:
    print("HIDDEN EVAL SUMMARY")
    print(f"examples:                  {report.total}")
    print(f"policy_exact_match:        {_exact(report.policy)}")
    print(f"policy_f1:                 {report.policy.f1:.4f}")
    print(f"independent_exact_match:   {_exact(report.independent)}")
    print(f"independent_f1:            {report.independent.f1:.4f}")
    print()
    print("CATEGORY SUMMARY")
    print("category\tpolicy_exact\tpolicy_f1\tindependent_exact\tindependent_f1")
    for category in _category_names(report):
        policy = report.policy.by_category.get(category, EvalReport([]))
        independent = report.independent.by_category.get(category, EvalReport([]))
        print(
            f"{category}\t{_exact(policy)}\t{policy.f1:.4f}\t"
            f"{_exact(independent)}\t{independent.f1:.4f}"
        )


def write_markdown(report: HiddenEvalReport, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown(report), encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Evaluate a private hidden eval TSV without printing examples."
    )
    parser.add_argument("input_tsv")
    parser.add_argument("--markdown-out")
    args = parser.parse_args(argv)

    report = evaluate_hidden_file(args.input_tsv)
    print_summary(report)
    if args.markdown_out:
        target = write_markdown(report, args.markdown_out)
        print(f"markdown_report:           {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
