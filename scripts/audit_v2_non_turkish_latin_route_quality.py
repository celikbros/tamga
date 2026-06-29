from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


LEGACY_TURKISH_ARTIFACTS = {
    "\u00fd": "legacy_dotless_i",
    "\u00dd": "legacy_capital_dotted_i",
    "\u00fe": "legacy_s_cedilla",
    "\u00de": "legacy_capital_s_cedilla",
    "\u00f0": "legacy_g_breve",
    "\u00d0": "legacy_capital_g_breve",
}

TURKISH_LETTERS = set(
    "abcçdefgğhıijklmnoöprsştuüvyz"
    "ABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
)
TURKISH_LOAN_DIACRITICS = set("âÂîÎûÛôÔêÊ")


@dataclass
class RouteClassStats:
    occurrences: int = 0
    bytes: int = 0
    unique_surfaces: set[str] = field(default_factory=set)

    def add(self, surface: str) -> None:
        self.occurrences += 1
        self.bytes += len(surface.encode("utf-8"))
        self.unique_surfaces.add(surface)


@dataclass
class AuditStats:
    lines: int = 0
    route_occurrences: int = 0
    route_bytes: int = 0
    unique_surfaces: set[str] = field(default_factory=set)
    class_stats: dict[str, RouteClassStats] = field(default_factory=lambda: defaultdict(RouteClassStats))
    legacy_char_counts: Counter[str] = field(default_factory=Counter)
    examples: dict[str, list[dict[str, object]]] = field(default_factory=lambda: defaultdict(list))


def classify_surface(surface: str) -> str:
    if any(char in LEGACY_TURKISH_ARTIFACTS for char in surface):
        return "legacy_turkish_encoding_artifact"
    if surface.isascii():
        return "ascii_unexpected"
    letters = [char for char in surface if char.isalpha()]
    if (
        letters
        and any(char in TURKISH_LOAN_DIACRITICS for char in letters)
        and all(char in TURKISH_LETTERS or char in TURKISH_LOAN_DIACRITICS for char in letters)
    ):
        return "turkish_loan_diacritic"
    if letters and all(char in TURKISH_LETTERS for char in letters):
        return "turkish_letters_only_unexpected"
    return "other_non_turkish_latin"


def audit_split(
    *,
    path: Path,
    split: str,
    max_lines: int | None,
    examples_per_class: int,
    progress: int,
) -> AuditStats:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    stats = AuditStats()
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            if max_lines is not None and stats.lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            stats.lines += 1
            for piece in analyze_line(text, tokenizer):
                if piece.kind != "protected:non_turkish_latin_word":
                    continue
                label = classify_surface(piece.surface)
                stats.route_occurrences += 1
                stats.route_bytes += len(piece.surface.encode("utf-8"))
                stats.unique_surfaces.add(piece.surface)
                stats.class_stats[label].add(piece.surface)
                for char in piece.surface:
                    if char in LEGACY_TURKISH_ARTIFACTS:
                        stats.legacy_char_counts[char] += 1
                if len(stats.examples[label]) < examples_per_class:
                    stats.examples[label].append(
                        {
                            "split": split,
                            "line_no": line_no,
                            "surface": piece.surface,
                            "surface_codepoints": [f"U+{ord(char):04X}" for char in piece.surface],
                            "text": text,
                        }
                    )
            if progress > 0 and stats.lines % progress == 0:
                legacy = stats.class_stats["legacy_turkish_encoding_artifact"].occurrences
                print(
                    f"audited {split} {stats.lines:,} lines "
                    f"non_turkish_latin={stats.route_occurrences:,} legacy={legacy:,}",
                    flush=True,
                )
    return stats


def merge_stats(items: list[AuditStats]) -> AuditStats:
    output = AuditStats()
    for item in items:
        output.lines += item.lines
        output.route_occurrences += item.route_occurrences
        output.route_bytes += item.route_bytes
        output.unique_surfaces.update(item.unique_surfaces)
        output.legacy_char_counts.update(item.legacy_char_counts)
        for label, stats in item.class_stats.items():
            output.class_stats[label].occurrences += stats.occurrences
            output.class_stats[label].bytes += stats.bytes
            output.class_stats[label].unique_surfaces.update(stats.unique_surfaces)
        for label, examples in item.examples.items():
            output.examples[label].extend(examples)
    return output


def write_examples(path: Path, stats: AuditStats, *, examples_per_class: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for label, examples in sorted(stats.examples.items()):
            for example in examples[:examples_per_class]:
                row = {"class": label, **example}
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def format_report(
    *,
    split_dir: Path,
    splits: list[str],
    stats: AuditStats,
    examples_out: Path,
) -> str:
    lines = [
        "# v2.0 Non-Turkish Latin Route Quality Audit",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"Splits: `{', '.join(splits)}`",
        f"Private examples: `{examples_out.as_posix()}`",
        "",
        "This audit checks whether the `non_turkish_latin_word` protected route",
        "is mostly true foreign Latin text or legacy-encoding-corrupted Turkish.",
        "",
        "## Summary",
        "",
        "| Lines | Route occurrences | Route bytes | Unique surfaces |",
        "| ---: | ---: | ---: | ---: |",
        f"| {stats.lines} | {stats.route_occurrences} | {stats.route_bytes} | {len(stats.unique_surfaces)} |",
        "",
        "## Classification",
        "",
        "| Class | Occurrences | Occurrence share | Bytes | Unique surfaces |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for label, item in sorted(
        stats.class_stats.items(),
        key=lambda pair: pair[1].occurrences,
        reverse=True,
    ):
        share = item.occurrences / stats.route_occurrences if stats.route_occurrences else 0.0
        lines.append(
            f"| `{label}` | {item.occurrences} | {_fmt(share)} | "
            f"{item.bytes} | {len(item.unique_surfaces)} |"
        )

    lines.extend(
        [
            "",
            "## Legacy Character Counts",
            "",
            "| Character | Meaning | Count |",
            "| --- | --- | ---: |",
        ]
    )
    for char, meaning in LEGACY_TURKISH_ARTIFACTS.items():
        lines.append(f"| `{char}` | `{meaning}` | {stats.legacy_char_counts[char]} |")

    lines.extend(
        [
            "",
            "## Interpretation Gate",
            "",
            "If legacy Turkish artifacts dominate this route, optimize data cleaning",
            "or route handling before changing the morphology learner.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit non-Turkish Latin protected route quality.")
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument("--split", action="append", choices=["train", "valid", "test"])
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--examples-per-class", type=int, default=20)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument(
        "--examples-out",
        default="artifacts/private/v2_0_non_turkish_latin_route_quality_examples.jsonl",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_non_turkish_latin_route_quality_audit.md",
    )
    args = parser.parse_args(argv)

    split_dir = Path(args.split_dir)
    splits = args.split or ["train", "valid", "test"]
    audits = [
        audit_split(
            path=split_dir / f"{split}.txt",
            split=split,
            max_lines=args.max_lines,
            examples_per_class=args.examples_per_class,
            progress=args.progress,
        )
        for split in splits
    ]
    stats = merge_stats(audits)
    examples_out = Path(args.examples_out)
    write_examples(examples_out, stats, examples_per_class=args.examples_per_class)
    report = format_report(
        split_dir=split_dir,
        splits=splits,
        stats=stats,
        examples_out=examples_out,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_examples: {examples_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
