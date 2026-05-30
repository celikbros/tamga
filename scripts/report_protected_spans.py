from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_real_tokenizers import (  # noqa: E402
    RealBaselineSpec,
    build_specs,
    encode_with_spec,
)
from scripts.compare_tokenizers import count_words  # noqa: E402
from scripts.report_stress_public import StressCase, load_stress_cases  # noqa: E402
from tr_tokenizer.tokenizer import WORD_START  # noqa: E402


@dataclass(frozen=True)
class ProtectedSpanResult:
    span: str
    preserved: bool


@dataclass(frozen=True)
class ProtectedCaseResult:
    case: StressCase
    model_name: str
    tokens: list[str]
    status: str
    reason: str
    span_results: list[ProtectedSpanResult]

    @property
    def protected_total(self) -> int:
        return len(self.span_results)

    @property
    def protected_preserved(self) -> int:
        return sum(result.preserved for result in self.span_results)

    @property
    def protected_broken(self) -> int:
        return self.protected_total - self.protected_preserved


@dataclass(frozen=True)
class ProtectedModelSummary:
    model_name: str
    status: str
    examples: int
    protected_total: int
    protected_preserved: int
    protected_broken: int
    break_rate: float
    avg_tokens_example: float
    avg_tokens_word: float
    reason: str = ""


def _surface_candidates(token: str) -> set[str]:
    candidates = {token}
    prefixes = (WORD_START, "▁", "Ġ", "##")

    changed = True
    while changed:
        changed = False
        for candidate in list(candidates):
            for prefix in prefixes:
                if candidate.startswith(prefix) and len(candidate) > len(prefix):
                    stripped = candidate[len(prefix) :]
                    if stripped not in candidates:
                        candidates.add(stripped)
                        changed = True

    return candidates


def is_span_preserved(span: str, tokens: list[str]) -> bool:
    surfaces: set[str] = set()
    for token in tokens:
        surfaces.update(_surface_candidates(token))
    return span in surfaces


def evaluate_protected_spans(
    cases: list[StressCase],
    specs: list[RealBaselineSpec],
    *,
    local_files_only: bool = True,
) -> dict[str, list[ProtectedCaseResult]]:
    results: dict[str, list[ProtectedCaseResult]] = {}
    skipped: dict[str, tuple[str, str]] = {}

    for spec in specs:
        model_results: list[ProtectedCaseResult] = []
        for case in cases:
            if spec.name in skipped:
                status, reason = skipped[spec.name]
                tokens: list[str] = []
            else:
                encoding = encode_with_spec(
                    spec,
                    case.text,
                    local_files_only=local_files_only,
                )
                status = encoding.status
                reason = encoding.reason
                tokens = encoding.tokens
                if status != "ok":
                    skipped[spec.name] = (status, reason)

            span_results = (
                [
                    ProtectedSpanResult(
                        span=span,
                        preserved=is_span_preserved(span, tokens),
                    )
                    for span in case.protected_spans
                ]
                if status == "ok"
                else []
            )
            model_results.append(
                ProtectedCaseResult(
                    case=case,
                    model_name=spec.name,
                    tokens=tokens,
                    status=status,
                    reason=reason,
                    span_results=span_results,
                )
            )
        results[spec.name] = model_results

    return results


def summarize_model(results: list[ProtectedCaseResult]) -> ProtectedModelSummary:
    if not results:
        return ProtectedModelSummary("", "skipped", 0, 0, 0, 0, 0.0, 0.0, 0.0)

    model_name = results[0].model_name
    status = "ok" if all(result.status == "ok" for result in results) else "skipped"
    reason = next((result.reason for result in results if result.reason), "")
    if status != "ok":
        return ProtectedModelSummary(
            model_name=model_name,
            status=status,
            examples=len(results),
            protected_total=0,
            protected_preserved=0,
            protected_broken=0,
            break_rate=0.0,
            avg_tokens_example=0.0,
            avg_tokens_word=0.0,
            reason=reason,
        )

    protected_total = sum(result.protected_total for result in results)
    protected_preserved = sum(result.protected_preserved for result in results)
    protected_broken = protected_total - protected_preserved
    token_count = sum(len(result.tokens) for result in results)
    word_count = sum(count_words(result.case.text) for result in results)

    return ProtectedModelSummary(
        model_name=model_name,
        status=status,
        examples=len(results),
        protected_total=protected_total,
        protected_preserved=protected_preserved,
        protected_broken=protected_broken,
        break_rate=protected_broken / protected_total if protected_total else 0.0,
        avg_tokens_example=token_count / len(results) if results else 0.0,
        avg_tokens_word=token_count / word_count if word_count else 0.0,
        reason=reason,
    )


def category_table(
    model_results: dict[str, list[ProtectedCaseResult]],
) -> dict[str, dict[str, tuple[int, int]]]:
    categories = sorted(
        {
            result.case.category
            for results in model_results.values()
            for result in results
        }
    )
    table: dict[str, dict[str, tuple[int, int]]] = {
        category: {} for category in categories
    }

    for model_name, results in model_results.items():
        grouped: dict[str, list[ProtectedCaseResult]] = defaultdict(list)
        for result in results:
            grouped[result.case.category].append(result)

        for category in categories:
            category_results = grouped.get(category, [])
            total = sum(result.protected_total for result in category_results)
            preserved = sum(result.protected_preserved for result in category_results)
            table[category][model_name] = (preserved, total)

    return table


def broken_spans(results: list[ProtectedCaseResult]) -> list[tuple[str, str, str]]:
    broken: list[tuple[str, str, str]] = []
    for result in results:
        for span_result in result.span_results:
            if not span_result.preserved:
                broken.append(
                    (
                        result.case.category,
                        span_result.span,
                        result.case.text,
                    )
                )
    return broken


def _ratio(preserved: int, total: int) -> str:
    if total == 0:
        return "n/a"
    return f"{preserved}/{total} ({preserved / total:.4f})"


def _break_rate(broken: int, total: int) -> str:
    if total == 0:
        return "n/a"
    return f"{broken / total:.4f}"


def format_text_report(model_results: dict[str, list[ProtectedCaseResult]]) -> str:
    rows = [summarize_model(results) for results in model_results.values()]
    lines = [
        "PROTECTED SPAN REPORT",
        "model_name\tstatus\texamples\tprotected_preserved\tprotected_broken\t"
        "protected_break_rate\tavg_tokens/example\tavg_tokens/word\treason",
    ]
    for row in rows:
        lines.append(
            f"{row.model_name}\t{row.status}\t{row.examples}\t"
            f"{row.protected_preserved}/{row.protected_total}\t"
            f"{row.protected_broken}\t{row.break_rate:.4f}\t"
            f"{row.avg_tokens_example:.4f}\t{row.avg_tokens_word:.4f}\t"
            f"{row.reason}"
        )
    return "\n".join(lines)


def format_markdown(model_results: dict[str, list[ProtectedCaseResult]]) -> str:
    rows = [summarize_model(results) for results in model_results.values()]
    model_names = [row.model_name for row in rows]
    table = category_table(model_results)

    lines = [
        "# Protected Span Baseline Report",
        "",
        "Tokenizer behavior is not changed by this report.",
        "",
        "## Summary",
        "",
        "| Model | Status | Examples | Protected preserved | Broken | Break rate | Avg tokens/example | Avg tokens/word | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.model_name} | {row.status} | {row.examples} | "
            f"{_ratio(row.protected_preserved, row.protected_total)} | "
            f"{row.protected_broken} | "
            f"{_break_rate(row.protected_broken, row.protected_total)} | "
            f"{row.avg_tokens_example:.4f} | {row.avg_tokens_word:.4f} | "
            f"{row.reason} |"
        )

    lines.extend(
        [
            "",
            "## Category Summary",
            "",
            "| Category | " + " | ".join(model_names) + " |",
            "| --- | " + " | ".join("---:" for _ in model_names) + " |",
        ]
    )
    for category, scores in table.items():
        if all(total == 0 for _, total in scores.values()):
            continue
        lines.append(
            f"| {category} | "
            + " | ".join(
                _ratio(*scores.get(model_name, (0, 0)))
                for model_name in model_names
            )
            + " |"
        )

    lines.extend(["", "## Broken Protected Spans", ""])
    any_broken = False
    for model_name, results in model_results.items():
        broken = broken_spans(results)
        if not broken:
            continue
        any_broken = True
        lines.extend([f"### {model_name}", ""])
        for category, span, text in broken:
            lines.append(f"- `{category}` span `{span}` in `{text}`")
        lines.append("")

    if not any_broken:
        lines.append("No broken protected spans.")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- A span is preserved when it appears as a single tokenizer token after removing common word-start markers.",
            "- This is stricter than boundary F1 and is intended for code/file/URL/number and explicitly protected smoke spans.",
            "- It should not be read as a general word-level quality metric.",
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
        description="Report protected-span break rates for tokenizer baselines.",
    )
    parser.add_argument("stress_tsv", help="category<TAB>text<TAB>protected_spans_json")
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

    specs = (
        build_specs(args)
        if (args.toy_bpe or args.hf or args.sentencepiece)
        else default_specs()
    )
    model_results = evaluate_protected_spans(
        load_stress_cases(args.stress_tsv),
        specs,
        local_files_only=not args.allow_download,
    )
    print(format_text_report(model_results))

    if args.markdown_out:
        target = Path(args.markdown_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(format_markdown(model_results), encoding="utf-8")
        print(f"wrote_markdown: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
