from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SOFT_MARKER = "\ue000"


@dataclass(frozen=True)
class RawSoftMarkerStats:
    split: str
    lines: int
    raw_bytes: int
    view_bytes: int
    segments: int
    soft_markers: int
    hard_boundaries: int
    max_segments_line: int
    jsonl_out: Path
    view_out: Path

    @property
    def view_bytes_per_raw_byte(self) -> float:
        return self.view_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def segments_per_raw_byte(self) -> float:
        return self.segments / self.raw_bytes if self.raw_bytes else 0.0


def build_raw_soft_marker_view(pieces: list[dict[str, object]]) -> tuple[str, int, int, int]:
    segments: list[str] = []
    segment = ""
    soft_markers = 0
    hard_boundaries = 0

    def flush() -> None:
        nonlocal segment
        if segment:
            segments.append(segment)
            segment = ""

    for piece in pieces:
        kind = str(piece.get("kind", ""))
        surface = str(piece.get("surface", ""))
        boundary = str(piece.get("boundary_before", ""))

        if kind == "whitespace":
            flush()
            hard_boundaries += 1
            continue

        if boundary == "soft":
            soft_markers += 1
            segment += SOFT_MARKER + surface
            continue

        if boundary == "hard":
            flush()
            hard_boundaries += 1
            segment = surface
            continue

        segment += surface

    flush()
    return " ".join(segments), len(segments), soft_markers, hard_boundaries


def materialize_split(
    *,
    source_jsonl: Path,
    jsonl_out: Path,
    view_out: Path,
    split: str,
    progress: int,
) -> RawSoftMarkerStats:
    jsonl_out.parent.mkdir(parents=True, exist_ok=True)
    view_out.parent.mkdir(parents=True, exist_ok=True)

    lines = 0
    raw_bytes = 0
    view_bytes = 0
    segments = 0
    soft_markers = 0
    hard_boundaries = 0
    max_segments_line = 0

    with (
        source_jsonl.open("r", encoding="utf-8") as source,
        jsonl_out.open("w", encoding="utf-8", newline="\n") as jsonl_target,
        view_out.open("w", encoding="utf-8", newline="\n") as view_target,
    ):
        for raw_line in source:
            item = json.loads(raw_line)
            text = item["text"]
            train_view, line_segments, line_soft, line_hard = build_raw_soft_marker_view(item["pieces"])

            jsonl_target.write(
                json.dumps(
                    {
                        "text": text,
                        "train_view": train_view,
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
            soft_markers += line_soft
            hard_boundaries += line_hard
            max_segments_line = max(max_segments_line, line_segments)

            if progress > 0 and lines % progress == 0:
                print(
                    f"raw-soft-marker {split}: {lines:,} lines "
                    f"segments={segments:,} soft_markers={soft_markers:,}",
                    flush=True,
                )

    return RawSoftMarkerStats(
        split=split,
        lines=lines,
        raw_bytes=raw_bytes,
        view_bytes=view_bytes,
        segments=segments,
        soft_markers=soft_markers,
        hard_boundaries=hard_boundaries,
        max_segments_line=max_segments_line,
        jsonl_out=jsonl_out,
        view_out=view_out,
    )


def materialize_views(
    *,
    source_root: Path,
    source_candidate: str,
    target_candidate: str,
    splits: tuple[str, ...],
    progress: int,
) -> list[RawSoftMarkerStats]:
    results: list[RawSoftMarkerStats] = []
    for split in splits:
        source_jsonl = source_root / f"{source_candidate}.{split}.jsonl"
        jsonl_out = source_root / f"{target_candidate}.{split}.jsonl"
        view_out = source_root / f"{target_candidate}.{split}.txt"
        print(f"Materializing raw-soft-marker view for split={split}", flush=True)
        results.append(
            materialize_split(
                source_jsonl=source_jsonl,
                jsonl_out=jsonl_out,
                view_out=view_out,
                split=split,
                progress=progress,
            )
        )
    return results


def format_report(
    *,
    source_root: Path,
    source_candidate: str,
    target_candidate: str,
    results: list[RawSoftMarkerStats],
) -> str:
    lines = [
        "# v2.0 Raw-Soft-Marker Candidate Views",
        "",
        f"Source candidate: `{source_candidate}`",
        f"Target candidate: `{target_candidate}`",
        f"Source root: `{source_root.as_posix()}`",
        f"Soft marker: `U+{ord(SOFT_MARKER):04X}`",
        "",
        "This candidate keeps hard boundaries as train-view whitespace and",
        "serializes only soft morphology boundaries with a private-use marker.",
        "It avoids custom token labels such as word-start markers or suffix",
        "prefixes.",
        "",
        "## Summary",
        "",
        "| Split | Lines | Raw bytes | View bytes | View/raw bytes | Segments | Segments/raw byte | Soft markers | Hard boundaries | Max segments/line | JSONL | Train view |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.split} | {result.lines} | {result.raw_bytes} | "
            f"{result.view_bytes} | {result.view_bytes_per_raw_byte:.6f} | "
            f"{result.segments} | {result.segments_per_raw_byte:.6f} | "
            f"{result.soft_markers} | {result.hard_boundaries} | "
            f"{result.max_segments_line} | `{result.jsonl_out.as_posix()}` | "
            f"`{result.view_out.as_posix()}` |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "Train SentencePiece on this view and compare token pressure with",
            "raw-hard and SP64. If pressure is acceptable, run visible intrinsic",
            "boundary diagnostics before tiny-LM.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Materialize raw-surface soft-marker v2.0 views.")
    parser.add_argument("--source-root", default="artifacts/private/v2_0_candidate")
    parser.add_argument("--source-candidate", default="protected_hard_soft_morph_seeded_sp64")
    parser.add_argument("--target-candidate", default="protected_hard_soft_marker_raw_sp64")
    parser.add_argument("--split", action="append", default=[])
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--report-out", default="artifacts/v2_0_raw_soft_marker_candidate_views.md")
    args = parser.parse_args(argv)

    splits = tuple(args.split or ["train", "valid", "test"])
    source_root = Path(args.source_root)
    results = materialize_views(
        source_root=source_root,
        source_candidate=args.source_candidate,
        target_candidate=args.target_candidate,
        splits=splits,
        progress=args.progress,
    )
    report = format_report(
        source_root=source_root,
        source_candidate=args.source_candidate,
        target_candidate=args.target_candidate,
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
