from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class DetectorCase:
    category: str
    text: str
    expected: tuple[str, ...]


@dataclass
class DetectorStats:
    cases: int = 0
    expected: int = 0
    detected: int = 0
    true_positive: int = 0
    false_positive: int = 0
    false_negative: int = 0
    by_category: Counter[str] | None = None
    misses_by_category: Counter[str] | None = None
    false_positive_by_category: Counter[str] | None = None

    def __post_init__(self) -> None:
        if self.by_category is None:
            self.by_category = Counter()
        if self.misses_by_category is None:
            self.misses_by_category = Counter()
        if self.false_positive_by_category is None:
            self.false_positive_by_category = Counter()

    @property
    def precision(self) -> float:
        return self.true_positive / self.detected if self.detected else 1.0

    @property
    def recall(self) -> float:
        return self.true_positive / self.expected if self.expected else 1.0

    @property
    def f1(self) -> float:
        denominator = self.precision + self.recall
        return 2 * self.precision * self.recall / denominator if denominator else 0.0


def default_cases() -> list[DetectorCase]:
    cases: list[DetectorCase] = []

    bases = ["github.com", "README.md", "config_v2.json", "file_v2.0.txt"]
    suffixes = ["'daki", "'de", "'yi", "'nin"]
    for base in bases:
        for suffix in suffixes:
            cases.append(
                DetectorCase(
                    "protected_suffix_attachment",
                    f"{base}{suffix} kullandim.",
                    (base,),
                )
            )

    percent_bases = ["%20", "%3A", "%2F", "%C3%BC"]
    for base in percent_bases:
        for suffix in ["'si", "'de", "'yi"]:
            cases.append(
                DetectorCase(
                    "percent_encoded_suffix",
                    f"URL icinde {base}{suffix} goruldu.",
                    (base,),
                )
            )

    numeric_bases = ["3", "12", "2026", "14:30", "19.05.2026"]
    for base in numeric_bases:
        for suffix in ["'uncu", "'inci", "'de", "'si"]:
            cases.append(
                DetectorCase(
                    "numeric_suffix_attachment",
                    f"Deger {base}{suffix} olarak yazildi.",
                    (base,),
                )
            )

    punctuation_cases = [
        ("(github.com)", "github.com"),
        ("[README.md]", "README.md"),
        ('"config_v2.json"', "config_v2.json"),
        ("https://example.com/tr/sayfa.", "https://example.com/tr/sayfa"),
        ("https://example.com/a?b=1, devam", "https://example.com/a?b=1"),
        ("file_v2.0.txt; sonra", "file_v2.0.txt"),
    ]
    for text, span in punctuation_cases:
        cases.append(("span_adjacent_punctuation", text, (span,)))  # type: ignore[arg-type]

    edge_cases = [
        ("github.com", "github.com"),
        ("README.md son", "README.md"),
        ("bas https://example.com", "https://example.com"),
        ("3'uncu", "3"),
    ]
    for text, span in edge_cases:
        cases.append(("span_at_line_edge", text, (span,)))  # type: ignore[arg-type]

    nested_cases = [
        ("https://example.com/file_v2.0.txt indirildi.", "https://example.com/file_v2.0.txt"),
        ("pkg>=1.2.3 dosyada.", "pkg>=1.2.3"),
        ("tokenizers>=0.19 ve transformers>=4.40", "tokenizers>=0.19", "transformers>=4.40"),
    ]
    for item in nested_cases:
        cases.append(DetectorCase("nested_or_comparator", item[0], tuple(item[1:])))

    return [
        item if isinstance(item, DetectorCase) else DetectorCase(*item)
        for item in cases
    ]


def detected_surfaces(text: str) -> list[str]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    return [
        piece.surface
        for piece in analyze_line(text, tokenizer)
        if piece.kind.startswith("protected:")
    ]


def score_case(case: DetectorCase) -> tuple[Counter[str], Counter[str], Counter[str]]:
    expected = Counter(case.expected)
    detected = Counter(detected_surfaces(case.text))
    true_positive = expected & detected
    false_positive = detected - expected
    false_negative = expected - detected
    return true_positive, false_positive, false_negative


def format_report(stats: DetectorStats, failures: list[dict[str, object]]) -> str:
    lines = [
        "# v2.1 Sidecar Detector Adversarial Battery",
        "",
        "This generated battery stresses protected-span detection before any",
        "pre-split training run. Under pre-split semantics, detector decisions",
        "affect model-token boundaries, so detector failures are training-time",
        "failures rather than metadata-only failures.",
        "",
        "## Summary",
        "",
        "| Cases | Expected spans | Detected spans | TP | FP | FN | Precision | Recall | F1 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| {stats.cases} | {stats.expected} | {stats.detected} | "
            f"{stats.true_positive} | {stats.false_positive} | {stats.false_negative} | "
            f"{stats.precision:.6f} | {stats.recall:.6f} | {stats.f1:.6f} |"
        ),
        "",
        "## Category Summary",
        "",
        "| Category | Cases | Missed expected spans | False positive spans |",
        "| --- | ---: | ---: | ---: |",
    ]
    assert stats.by_category is not None
    assert stats.misses_by_category is not None
    assert stats.false_positive_by_category is not None
    for category in sorted(stats.by_category):
        lines.append(
            f"| `{category}` | {stats.by_category[category]} | "
            f"{stats.misses_by_category[category]} | "
            f"{stats.false_positive_by_category[category]} |"
        )

    lines.extend(["", "## Failure Samples", ""])
    if not failures:
        lines.append("No detector mismatches.")
    else:
        for sample in failures[:50]:
            lines.append(f"- category `{sample['category']}`")
            lines.append(f"  - text: `{sample['text']}`")
            lines.append(f"  - expected: `{sample['expected']}`")
            lines.append(f"  - detected: `{sample['detected']}`")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Run v2.1 generated protected-span detector battery."
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_1_sidecar_detector_adversarial_battery.md",
    )
    parser.add_argument(
        "--jsonl-out",
        default="artifacts/private/v2_1_sidecar_detector_adversarial_battery.jsonl",
    )
    args = parser.parse_args(argv)

    stats = DetectorStats()
    failures: list[dict[str, object]] = []
    cases = default_cases()
    for case in cases:
        detected = detected_surfaces(case.text)
        tp, fp, fn = score_case(case)
        expected_count = len(case.expected)
        detected_count = len(detected)
        stats.cases += 1
        stats.expected += expected_count
        stats.detected += detected_count
        stats.true_positive += sum(tp.values())
        stats.false_positive += sum(fp.values())
        stats.false_negative += sum(fn.values())
        assert stats.by_category is not None
        assert stats.misses_by_category is not None
        assert stats.false_positive_by_category is not None
        stats.by_category[case.category] += 1
        stats.misses_by_category[case.category] += sum(fn.values())
        stats.false_positive_by_category[case.category] += sum(fp.values())
        if fp or fn:
            failures.append(
                {
                    "category": case.category,
                    "text": case.text,
                    "expected": list(case.expected),
                    "detected": detected,
                    "false_positive": dict(fp),
                    "false_negative": dict(fn),
                }
            )

    report = format_report(stats, failures)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")

    jsonl_out = Path(args.jsonl_out)
    jsonl_out.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_out.open("w", encoding="utf-8") as handle:
        for failure in failures:
            handle.write(json.dumps(failure, ensure_ascii=False) + "\n")

    print(report)
    print(f"wrote_report: {report_out}")
    print(f"wrote_jsonl: {jsonl_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
