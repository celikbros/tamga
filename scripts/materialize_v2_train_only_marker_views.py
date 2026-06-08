from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER  # noqa: E402


DEFAULT_HIGH_VALUE_SUFFIXES = {
    "lar",
    "ler",
    "dan",
    "den",
    "tan",
    "ten",
    "da",
    "de",
    "ta",
    "te",
    "ın",
    "in",
    "un",
    "ün",
    "ım",
    "im",
    "um",
    "üm",
    "acak",
    "ecek",
    "acağ",
    "eceğ",
    "yor",
    "mış",
    "miş",
    "muş",
    "müş",
    "dı",
    "di",
    "du",
    "dü",
    "tı",
    "ti",
    "tu",
    "tü",
}


@dataclass(frozen=True)
class MarkerViewStats:
    split: str
    policy: str
    lines: int
    raw_bytes: int
    view_bytes: int
    segments: int
    soft_boundaries_total: int
    soft_markers_kept: int
    soft_boundaries_collapsed: int
    hard_boundaries: int
    suffix_groups: int
    marked_suffix_groups: int
    max_segments_line: int
    jsonl_out: Path
    view_out: Path

    @property
    def view_bytes_per_raw_byte(self) -> float:
        return self.view_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def markers_per_raw_byte(self) -> float:
        return self.soft_markers_kept / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def marker_keep_rate(self) -> float:
        return self.soft_markers_kept / self.soft_boundaries_total if self.soft_boundaries_total else 0.0


def suffix_allowlist(raw: str | None) -> set[str]:
    if not raw:
        return set(DEFAULT_HIGH_VALUE_SUFFIXES)
    return {item.strip() for item in raw.split(",") if item.strip()}


def suffix_chain_marker_indices(
    pieces: list[dict[str, object]],
    *,
    min_suffix_count: int,
) -> tuple[set[int], int, int]:
    markers: set[int] = set()
    suffix_groups = 0
    marked_groups = 0
    group: list[tuple[int, dict[str, object]]] = []

    def flush_group() -> None:
        nonlocal suffix_groups, marked_groups, group
        if not group:
            return
        suffix_indices = [
            index
            for index, piece in group
            if str(piece.get("kind", "")) == "suffix"
            and str(piece.get("boundary_before", "")) == "soft"
        ]
        if suffix_indices:
            suffix_groups += 1
        if len(suffix_indices) >= min_suffix_count:
            markers.update(suffix_indices)
            marked_groups += 1
        group = []

    for index, piece in enumerate(pieces):
        kind = str(piece.get("kind", ""))
        boundary = str(piece.get("boundary_before", ""))
        if kind == "whitespace":
            flush_group()
            continue
        if boundary == "hard":
            flush_group()
            if kind == "word_start":
                group = [(index, piece)]
            continue
        if group:
            group.append((index, piece))

    flush_group()
    return markers, suffix_groups, marked_groups


def high_value_suffix_marker_indices(
    pieces: list[dict[str, object]],
    *,
    allowlist: set[str],
) -> set[int]:
    markers: set[int] = set()
    for index, piece in enumerate(pieces):
        if str(piece.get("kind", "")) != "suffix":
            continue
        if str(piece.get("boundary_before", "")) != "soft":
            continue
        if str(piece.get("surface", "")) in allowlist:
            markers.add(index)
    return markers


def marker_indices_for_policy(
    pieces: list[dict[str, object]],
    *,
    policy: str,
    min_suffix_count: int,
    allowlist: set[str],
) -> tuple[set[int], int, int]:
    if policy == "none":
        return set(), 0, 0
    if policy == "all_soft":
        return {
            index
            for index, piece in enumerate(pieces)
            if str(piece.get("boundary_before", "")) == "soft"
        }, 0, 0
    if policy == "suffix_chain":
        return suffix_chain_marker_indices(pieces, min_suffix_count=min_suffix_count)
    if policy == "high_value_suffix":
        return high_value_suffix_marker_indices(pieces, allowlist=allowlist), 0, 0
    raise ValueError(f"unsupported marker policy: {policy}")


def build_marker_view(
    pieces: list[dict[str, object]],
    *,
    marker_indices: set[int],
) -> tuple[str, int, int, int, int]:
    segments: list[str] = []
    segment = ""
    markers = 0
    soft_total = 0
    hard_boundaries = 0

    def flush() -> None:
        nonlocal segment
        if segment:
            segments.append(segment)
            segment = ""

    for index, piece in enumerate(pieces):
        kind = str(piece.get("kind", ""))
        surface = str(piece.get("surface", ""))
        boundary = str(piece.get("boundary_before", ""))

        if kind == "whitespace":
            flush()
            hard_boundaries += 1
            continue

        if boundary == "soft":
            soft_total += 1
            if index in marker_indices:
                segment += SOFT_MARKER
                markers += 1
            segment += surface
            continue

        if boundary == "hard":
            flush()
            hard_boundaries += 1
            segment = surface
            continue

        segment += surface

    flush()
    return " ".join(segments), len(segments), soft_total, markers, hard_boundaries


def materialize_split(
    *,
    source_jsonl: Path,
    jsonl_out: Path,
    view_out: Path,
    split: str,
    policy: str,
    min_suffix_count: int,
    allowlist: set[str],
    progress: int,
) -> MarkerViewStats:
    jsonl_out.parent.mkdir(parents=True, exist_ok=True)
    view_out.parent.mkdir(parents=True, exist_ok=True)

    lines = 0
    raw_bytes = 0
    view_bytes = 0
    segments = 0
    soft_boundaries_total = 0
    soft_markers_kept = 0
    hard_boundaries = 0
    suffix_groups = 0
    marked_suffix_groups = 0
    max_segments_line = 0

    with (
        source_jsonl.open("r", encoding="utf-8") as source,
        jsonl_out.open("w", encoding="utf-8", newline="\n") as jsonl_target,
        view_out.open("w", encoding="utf-8", newline="\n") as view_target,
    ):
        for raw_line in source:
            item = json.loads(raw_line)
            text = item["text"]
            pieces = item["pieces"]
            marker_indices, line_suffix_groups, line_marked_groups = marker_indices_for_policy(
                pieces,
                policy=policy,
                min_suffix_count=min_suffix_count,
                allowlist=allowlist,
            )
            train_view, line_segments, line_soft, line_markers, line_hard = build_marker_view(
                pieces,
                marker_indices=marker_indices,
            )
            jsonl_target.write(
                json.dumps(
                    {
                        "text": text,
                        "train_view": train_view,
                        "policy": policy,
                        "source_candidate": source_jsonl.as_posix(),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            view_target.write(train_view + "\n")

            lines += 1
            raw_bytes += len(text.encode("utf-8"))
            view_bytes += len(train_view.encode("utf-8"))
            segments += line_segments
            soft_boundaries_total += line_soft
            soft_markers_kept += line_markers
            hard_boundaries += line_hard
            suffix_groups += line_suffix_groups
            marked_suffix_groups += line_marked_groups
            max_segments_line = max(max_segments_line, line_segments)

            if progress > 0 and lines % progress == 0:
                print(
                    f"marker-view {policy} {split}: {lines:,} lines "
                    f"markers={soft_markers_kept:,} keep_rate="
                    f"{soft_markers_kept / soft_boundaries_total if soft_boundaries_total else 0.0:.4f}",
                    flush=True,
                )

    return MarkerViewStats(
        split=split,
        policy=policy,
        lines=lines,
        raw_bytes=raw_bytes,
        view_bytes=view_bytes,
        segments=segments,
        soft_boundaries_total=soft_boundaries_total,
        soft_markers_kept=soft_markers_kept,
        soft_boundaries_collapsed=soft_boundaries_total - soft_markers_kept,
        hard_boundaries=hard_boundaries,
        suffix_groups=suffix_groups,
        marked_suffix_groups=marked_suffix_groups,
        max_segments_line=max_segments_line,
        jsonl_out=jsonl_out,
        view_out=view_out,
    )


def materialize_views(
    *,
    source_root: Path,
    source_candidate: str,
    target_candidate: str,
    policy: str,
    splits: tuple[str, ...],
    min_suffix_count: int,
    allowlist: set[str],
    progress: int,
) -> list[MarkerViewStats]:
    results: list[MarkerViewStats] = []
    for split in splits:
        source_jsonl = source_root / f"{source_candidate}.{split}.jsonl"
        jsonl_out = source_root / f"{target_candidate}.{split}.jsonl"
        view_out = source_root / f"{target_candidate}.{split}.txt"
        print(f"Materializing marker view policy={policy} split={split}", flush=True)
        results.append(
            materialize_split(
                source_jsonl=source_jsonl,
                jsonl_out=jsonl_out,
                view_out=view_out,
                split=split,
                policy=policy,
                min_suffix_count=min_suffix_count,
                allowlist=allowlist,
                progress=progress,
            )
        )
    return results


def format_report(
    *,
    source_root: Path,
    source_candidate: str,
    target_candidate: str,
    policy: str,
    min_suffix_count: int,
    allowlist: set[str],
    results: list[MarkerViewStats],
) -> str:
    lines = [
        "# v2.0 Train-Only Marker View Materialization",
        "",
        f"Source candidate: `{source_candidate}`",
        f"Target candidate: `{target_candidate}`",
        f"Source root: `{source_root.as_posix()}`",
        f"Policy: `{policy}`",
        f"Soft marker: `U+{ord(SOFT_MARKER):04X}`",
        f"Minimum suffix count: `{min_suffix_count}`",
        f"High-value suffix allowlist size: `{len(allowlist)}`",
        "",
        "This materializes markerized SentencePiece training views for",
        "train-only vocabulary shaping. The marker is not intended to be",
        "inserted into normal text at encode time.",
        "",
        "## Summary",
        "",
        "| Split | Lines | Raw bytes | View bytes | View/raw bytes | Segments | Soft boundaries | Markers kept | Marker keep rate | Markers/raw byte | Collapsed soft boundaries | Suffix groups | Marked suffix groups | Hard boundaries | Max segments/line | JSONL | Train view |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.split} | {result.lines} | {result.raw_bytes} | "
            f"{result.view_bytes} | {result.view_bytes_per_raw_byte:.6f} | "
            f"{result.segments} | {result.soft_boundaries_total} | "
            f"{result.soft_markers_kept} | {result.marker_keep_rate:.6f} | "
            f"{result.markers_per_raw_byte:.6f} | "
            f"{result.soft_boundaries_collapsed} | {result.suffix_groups} | "
            f"{result.marked_suffix_groups} | {result.hard_boundaries} | "
            f"{result.max_segments_line} | `{result.jsonl_out.as_posix()}` | "
            f"`{result.view_out.as_posix()}` |"
        )
    lines.extend(
        [
            "",
            "## Next Use",
            "",
            "Train a train-only Unigram model on the train view, then evaluate it",
            "with markers stripped at encode time. Do not run tiny-LM before",
            "token-pressure and visible intrinsic gates pass.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Materialize train-only marker-shaping views.")
    parser.add_argument("--source-root", default="artifacts/private/v2_0_candidate")
    parser.add_argument("--source-candidate", default="protected_hard_soft_morph_seeded_sp64")
    parser.add_argument("--target-candidate", default="protected_hard_train_only_marker")
    parser.add_argument(
        "--policy",
        choices=["none", "all_soft", "suffix_chain", "high_value_suffix"],
        default="suffix_chain",
    )
    parser.add_argument("--min-suffix-count", type=int, default=2)
    parser.add_argument("--suffix-allowlist")
    parser.add_argument("--split", action="append", default=[])
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--report-out", default="artifacts/v2_0_train_only_marker_views.md")
    args = parser.parse_args(argv)

    if args.min_suffix_count <= 0:
        raise ValueError("--min-suffix-count must be positive")

    splits = tuple(args.split or ["train", "valid", "test"])
    source_root = Path(args.source_root)
    allowlist = suffix_allowlist(args.suffix_allowlist)
    results = materialize_views(
        source_root=source_root,
        source_candidate=args.source_candidate,
        target_candidate=args.target_candidate,
        policy=args.policy,
        splits=splits,
        min_suffix_count=args.min_suffix_count,
        allowlist=allowlist,
        progress=args.progress,
    )
    report = format_report(
        source_root=source_root,
        source_candidate=args.source_candidate,
        target_candidate=args.target_candidate,
        policy=args.policy,
        min_suffix_count=args.min_suffix_count,
        allowlist=allowlist,
        results=results,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
