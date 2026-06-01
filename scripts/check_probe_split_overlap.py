from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.check_eval_leakage import normalize_for_leakage  # noqa: E402


@dataclass(frozen=True)
class SplitRecord:
    split: str
    row: int
    source_line_index: int | None
    raw: str
    norm: str
    words: tuple[str, ...]
    shingles: frozenset[tuple[str, ...]]


@dataclass(frozen=True)
class NearPair:
    left_split: str
    left_row: int
    left_source_line_index: int | None
    right_split: str
    right_row: int
    right_source_line_index: int | None
    shared_shingles: int
    containment: float
    jaccard: float


@dataclass
class PairOverlapReport:
    left_split: str
    right_split: str
    left_lines: int
    right_lines: int
    raw_exact_pairs: int = 0
    normalized_exact_pairs: int = 0
    near_pairs: list[NearPair] = field(default_factory=list)

    @property
    def max_containment(self) -> float:
        if not self.near_pairs:
            return 0.0
        return max(pair.containment for pair in self.near_pairs)

    @property
    def max_jaccard(self) -> float:
        if not self.near_pairs:
            return 0.0
        return max(pair.jaccard for pair in self.near_pairs)


def _format_float(value: float) -> str:
    return f"{value:.4f}"


def make_word_shingles(
    words: tuple[str, ...],
    *,
    ngram_size: int,
    min_near_words: int,
) -> frozenset[tuple[str, ...]]:
    if len(words) < min_near_words:
        return frozenset()
    size = min(ngram_size, len(words))
    return frozenset(
        tuple(words[index : index + size])
        for index in range(0, len(words) - size + 1)
    )


def _load_source_line_indexes(manifest_path: Path) -> list[int | None]:
    if not manifest_path.exists():
        return []
    indexes: list[int | None] = []
    with manifest_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                indexes.append(None)
                continue
            value = item.get("source_line_index")
            indexes.append(value if isinstance(value, int) else None)
    return indexes


def load_split_records(
    path: str | Path,
    *,
    split: str,
    ngram_size: int,
    min_near_words: int,
    manifest_path: str | Path | None = None,
) -> list[SplitRecord]:
    source = Path(path)
    if manifest_path is None:
        candidate = source.with_name(f"{split}.manifest.jsonl")
        source_line_indexes = _load_source_line_indexes(candidate)
    else:
        source_line_indexes = _load_source_line_indexes(Path(manifest_path))

    records: list[SplitRecord] = []
    with source.open("r", encoding="utf-8") as handle:
        for row, raw_line in enumerate(handle, start=1):
            raw = raw_line.rstrip("\n")
            norm = normalize_for_leakage(raw)
            words = tuple(norm.split())
            source_line_index = (
                source_line_indexes[row - 1]
                if row - 1 < len(source_line_indexes)
                else None
            )
            records.append(
                SplitRecord(
                    split=split,
                    row=row,
                    source_line_index=source_line_index,
                    raw=raw,
                    norm=norm,
                    words=words,
                    shingles=make_word_shingles(
                        words,
                        ngram_size=ngram_size,
                        min_near_words=min_near_words,
                    ),
                )
            )
    return records


def compare_split_pair(
    left: list[SplitRecord],
    right: list[SplitRecord],
    *,
    near_threshold: float,
) -> PairOverlapReport:
    if not left or not right:
        left_split = left[0].split if left else "left"
        right_split = right[0].split if right else "right"
        return PairOverlapReport(left_split, right_split, len(left), len(right))

    report = PairOverlapReport(left[0].split, right[0].split, len(left), len(right))
    raw_index: dict[str, list[SplitRecord]] = defaultdict(list)
    norm_index: dict[str, list[SplitRecord]] = defaultdict(list)
    shingle_index: dict[tuple[str, ...], list[int]] = defaultdict(list)

    for index, record in enumerate(left):
        if record.raw:
            raw_index[record.raw].append(record)
        if record.norm:
            norm_index[record.norm].append(record)
        for shingle in record.shingles:
            shingle_index[shingle].append(index)

    for record in right:
        report.raw_exact_pairs += len(raw_index.get(record.raw, []))
        normalized_matches = norm_index.get(record.norm, [])
        report.normalized_exact_pairs += len(normalized_matches)
        if normalized_matches or not record.shingles:
            continue

        candidate_counts: Counter[int] = Counter()
        for shingle in record.shingles:
            for left_index in shingle_index.get(shingle, []):
                candidate_counts[left_index] += 1

        for left_index, shared in candidate_counts.items():
            left_record = left[left_index]
            if not left_record.shingles:
                continue
            union = len(left_record.shingles) + len(record.shingles) - shared
            containment = shared / min(len(left_record.shingles), len(record.shingles))
            jaccard = shared / union if union else 0.0
            if containment >= near_threshold:
                report.near_pairs.append(
                    NearPair(
                        left_split=left_record.split,
                        left_row=left_record.row,
                        left_source_line_index=left_record.source_line_index,
                        right_split=record.split,
                        right_row=record.row,
                        right_source_line_index=record.source_line_index,
                        shared_shingles=shared,
                        containment=containment,
                        jaccard=jaccard,
                    )
                )

    report.near_pairs.sort(
        key=lambda pair: (
            pair.containment,
            pair.jaccard,
            pair.shared_shingles,
        ),
        reverse=True,
    )
    return report


def check_split_overlap(
    split_dir: str | Path,
    *,
    ngram_size: int,
    min_near_words: int,
    near_threshold: float,
) -> list[PairOverlapReport]:
    root = Path(split_dir)
    records = {
        split: load_split_records(
            root / f"{split}.txt",
            split=split,
            ngram_size=ngram_size,
            min_near_words=min_near_words,
        )
        for split in ("train", "valid", "test")
    }
    return [
        compare_split_pair(records["train"], records["valid"], near_threshold=near_threshold),
        compare_split_pair(records["train"], records["test"], near_threshold=near_threshold),
        compare_split_pair(records["valid"], records["test"], near_threshold=near_threshold),
    ]


def format_overlap_report(
    reports: list[PairOverlapReport],
    *,
    split_dir: str | Path,
    ngram_size: int,
    min_near_words: int,
    near_threshold: float,
    max_details: int,
) -> str:
    lines = [
        "# v1.8 Local LM Probe Split Overlap",
        "",
        f"Split dir: `{Path(split_dir).as_posix()}`",
        f"Word shingle size: `{ngram_size}`",
        f"Minimum near-check words: `{min_near_words}`",
        f"Near-duplicate containment threshold: `{_format_float(near_threshold)}`",
        "",
        "This report checks raw train/valid/test split hygiene before LM-loss",
        "comparison. It does not include private corpus snippets.",
        "",
        "## Summary",
        "",
        "| Pair | Left lines | Right lines | Raw exact pairs | Normalized exact pairs | Near pairs | Max containment | Max Jaccard |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for report in reports:
        pair = f"{report.left_split}<->{report.right_split}"
        lines.append(
            f"| {pair} | {report.left_lines} | {report.right_lines} | "
            f"{report.raw_exact_pairs} | {report.normalized_exact_pairs} | "
            f"{len(report.near_pairs)} | {_format_float(report.max_containment)} | "
            f"{_format_float(report.max_jaccard)} |"
        )

    lines.extend(
        [
            "",
            "## Details",
            "",
            "Rows and source line indexes are reported instead of text snippets.",
        ]
    )
    for report in reports:
        lines.extend(["", f"### {report.left_split}<->{report.right_split}", ""])
        if (
            report.raw_exact_pairs == 0
            and report.normalized_exact_pairs == 0
            and not report.near_pairs
        ):
            lines.append("No exact or near-duplicate overlap found.")
            continue
        if report.raw_exact_pairs or report.normalized_exact_pairs:
            lines.append(
                f"Exact overlap pairs: raw={report.raw_exact_pairs}, "
                f"normalized={report.normalized_exact_pairs}."
            )
        if not report.near_pairs:
            lines.append("No near-duplicate pairs above threshold.")
            continue
        lines.extend(
            [
                "",
                "| Left row | Left source | Right row | Right source | Shared shingles | Containment | Jaccard |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for pair in report.near_pairs[:max_details]:
            left_source = (
                str(pair.left_source_line_index)
                if pair.left_source_line_index is not None
                else ""
            )
            right_source = (
                str(pair.right_source_line_index)
                if pair.right_source_line_index is not None
                else ""
            )
            lines.append(
                f"| {pair.left_row} | {left_source} | {pair.right_row} | "
                f"{right_source} | {pair.shared_shingles} | "
                f"{_format_float(pair.containment)} | {_format_float(pair.jaccard)} |"
            )
        if len(report.near_pairs) > max_details:
            lines.append("")
            lines.append(f"Additional near pairs omitted: {len(report.near_pairs) - max_details}.")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Check v1.8 local LM probe train/valid/test split overlap.",
    )
    parser.add_argument("--split-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--ngram", type=int, default=8)
    parser.add_argument("--min-near-words", type=int, default=8)
    parser.add_argument("--near-threshold", type=float, default=0.8)
    parser.add_argument("--max-details", type=int, default=20)
    args = parser.parse_args(argv)

    reports = check_split_overlap(
        args.split_dir,
        ngram_size=args.ngram,
        min_near_words=args.min_near_words,
        near_threshold=args.near_threshold,
    )
    report_text = format_overlap_report(
        reports,
        split_dir=args.split_dir,
        ngram_size=args.ngram,
        min_near_words=args.min_near_words,
        near_threshold=args.near_threshold,
        max_details=args.max_details,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_text, encoding="utf-8")
    print(report_text)
    print(f"wrote_report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
