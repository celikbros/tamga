from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


SOFT_MARKER = "\ue000"


@dataclass(frozen=True)
class CandidateStats:
    lines: int
    raw_bytes: int
    train_view_bytes: int
    pieces: int
    selected_pieces: int
    unselected_pieces: int
    unselected_word_start_pieces: int
    whitespace_pieces: int
    protected_pieces: int
    soft_boundaries: int
    hard_segments: int
    max_segments_line: int

    @property
    def selected_piece_rate(self) -> float:
        return self.selected_pieces / self.pieces if self.pieces else 0.0

    @property
    def train_view_bytes_per_raw_byte(self) -> float:
        return self.train_view_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def hard_segments_per_raw_byte(self) -> float:
        return self.hard_segments / self.raw_bytes if self.raw_bytes else 0.0


def load_selected_tokens(path: str | Path) -> set[str]:
    selected: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n")
        if header != "token\tcount\tcategory\treason":
            raise ValueError(f"unexpected selected seed header: {header!r}")
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            token, _count, _category, _reason = line.split("\t", 3)
            selected.add(token)
    return selected


def piece_group(piece: dict[str, str]) -> str:
    kind = piece.get("kind", "")
    if kind == "whitespace":
        return "whitespace"
    if kind == "suffix":
        return "suffix"
    if kind.startswith("protected:"):
        return "protected"
    if kind == "word_start":
        return "word_start"
    if kind in {"apostrophe", "punct_or_symbol"}:
        return kind
    return "other"


def training_token(piece: dict[str, str]) -> str:
    return piece.get("token") or piece.get("surface") or ""


def build_training_view(
    pieces: list[dict[str, str]],
    selected: set[str],
) -> tuple[str, list[dict[str, object]], int]:
    segments: list[str] = []
    segment = ""
    annotated: list[dict[str, object]] = []

    def flush_segment() -> None:
        nonlocal segment
        if segment:
            segments.append(segment)
            segment = ""

    for piece in pieces:
        token = training_token(piece)
        group = piece_group(piece)
        is_selected = token in selected

        annotated.append(
            {
                "token": token,
                "surface": piece.get("surface", ""),
                "kind": piece.get("kind", ""),
                "group": group,
                "boundary_before": piece.get("boundary_before", ""),
                "selected_seed": is_selected,
            }
        )

        if group == "whitespace":
            flush_segment()
            continue

        if piece.get("boundary_before") == "soft" and segment:
            segment += SOFT_MARKER + token
        else:
            flush_segment()
            segment = token

    flush_segment()
    return " ".join(segments), annotated, len(segments)


def materialize_candidate_serialization(
    *,
    boundary_jsonl: Path,
    selected_seed: Path,
    jsonl_out: Path,
    train_view_out: Path,
    max_lines: int | None,
    progress: int,
) -> CandidateStats:
    selected = load_selected_tokens(selected_seed)
    jsonl_out.parent.mkdir(parents=True, exist_ok=True)
    train_view_out.parent.mkdir(parents=True, exist_ok=True)

    lines = 0
    raw_bytes = 0
    train_view_bytes = 0
    total_pieces = 0
    selected_pieces = 0
    unselected_pieces = 0
    unselected_word_start_pieces = 0
    whitespace_pieces = 0
    protected_pieces = 0
    soft_boundaries = 0
    hard_segments = 0
    max_segments_line = 0
    group_counts: Counter[str] = Counter()

    with (
        boundary_jsonl.open("r", encoding="utf-8") as source,
        jsonl_out.open("w", encoding="utf-8", newline="\n") as jsonl_target,
        train_view_out.open("w", encoding="utf-8", newline="\n") as train_target,
    ):
        for raw_line in source:
            if max_lines is not None and lines >= max_lines:
                break
            item = json.loads(raw_line)
            text = item["text"]
            pieces = item["pieces"]
            train_view, annotated, segments_line = build_training_view(pieces, selected)

            jsonl_target.write(
                json.dumps(
                    {
                        "text": text,
                        "train_view": train_view,
                        "pieces": annotated,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            train_target.write(train_view + "\n")

            lines += 1
            raw_bytes += len(text.encode("utf-8"))
            train_view_bytes += len(train_view.encode("utf-8"))
            hard_segments += segments_line
            max_segments_line = max(max_segments_line, segments_line)

            for piece in annotated:
                group = str(piece["group"])
                is_selected = bool(piece["selected_seed"])
                total_pieces += 1
                group_counts[group] += 1
                if piece["boundary_before"] == "soft":
                    soft_boundaries += 1
                if group == "whitespace":
                    whitespace_pieces += 1
                if group == "protected":
                    protected_pieces += 1
                if is_selected:
                    selected_pieces += 1
                elif group != "whitespace":
                    unselected_pieces += 1
                    if group == "word_start":
                        unselected_word_start_pieces += 1

            if progress > 0 and lines % progress == 0:
                print(
                    f"serialized {lines:,} lines "
                    f"segments={hard_segments:,} selected={selected_pieces:,} "
                    f"unselected={unselected_pieces:,}",
                    flush=True,
                )

    return CandidateStats(
        lines=lines,
        raw_bytes=raw_bytes,
        train_view_bytes=train_view_bytes,
        pieces=total_pieces,
        selected_pieces=selected_pieces,
        unselected_pieces=unselected_pieces,
        unselected_word_start_pieces=unselected_word_start_pieces,
        whitespace_pieces=whitespace_pieces,
        protected_pieces=protected_pieces,
        soft_boundaries=soft_boundaries,
        hard_segments=hard_segments,
        max_segments_line=max_segments_line,
    )


def format_report(
    *,
    boundary_jsonl: Path,
    selected_seed: Path,
    jsonl_out: Path,
    train_view_out: Path,
    stats: CandidateStats,
    max_lines: int | None,
) -> str:
    return "\n".join(
        [
            "# v2.0 Candidate Serialization",
            "",
            "Candidate: `protected_hard_soft_morph_seeded_sp64`",
            "",
            f"Boundary JSONL: `{boundary_jsonl.as_posix()}`",
            f"Selected seed TSV: `{selected_seed.as_posix()}`",
            f"Private candidate JSONL: `{jsonl_out.as_posix()}`",
            f"Private train view: `{train_view_out.as_posix()}`",
            f"Max lines: `{max_lines if max_lines is not None else 'all'}`",
            "",
            "The candidate JSONL keeps raw `text` for lossless reconstruction. The",
            "plain train view is only a learned-tokenizer training view; it is not",
            "by itself a complete decoder artifact.",
            "",
            "## Summary",
            "",
            "| Lines | Raw bytes | Train-view bytes | Train-view/raw bytes | Pieces | Selected pieces | Selected piece rate | Unselected non-whitespace pieces | Unselected word_start pieces | Whitespace pieces | Protected pieces | Soft boundaries | Hard segments | Hard segments/raw byte | Max segments/line |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {stats.lines} | {stats.raw_bytes} | {stats.train_view_bytes} | "
                f"{stats.train_view_bytes_per_raw_byte:.6f} | {stats.pieces} | "
                f"{stats.selected_pieces} | {stats.selected_piece_rate:.6f} | "
                f"{stats.unselected_pieces} | {stats.unselected_word_start_pieces} | "
                f"{stats.whitespace_pieces} | {stats.protected_pieces} | "
                f"{stats.soft_boundaries} | {stats.hard_segments} | "
                f"{stats.hard_segments_per_raw_byte:.6f} | "
                f"{stats.max_segments_line} |"
            ),
            "",
            "## Serialization Rules",
            "",
            "- Soft morphology boundaries are represented with `SOFT_MARKER_U+E000` in the train view.",
            "- Hard boundaries become train-view whitespace.",
            "- Whitespace pieces are preserved in the candidate JSONL, but not as separate train-view tokens.",
            "- Selected seed membership is recorded per piece in the candidate JSONL.",
            "",
            "## Gate",
            "",
            "Before training, verify that this train view does not recreate pure-custom",
            "token pressure and that the JSONL remains the source for lossless decode.",
            "The hard-segment/raw-byte value is only a segmentation floor; the learned",
            "tokenizer can still split hard segments into more tokens.",
        ]
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Materialize v2.0 candidate serialization.")
    parser.add_argument(
        "--boundary-jsonl",
        default="artifacts/private/v2_0_soft_morph/soft_morph_boundaries.train.jsonl",
    )
    parser.add_argument(
        "--selected-seed",
        default="artifacts/private/v2_0_soft_morph/protected_hard_soft_morph_seeded_sp64.selected_seed.tsv",
    )
    parser.add_argument(
        "--jsonl-out",
        default="artifacts/private/v2_0_candidate/protected_hard_soft_morph_seeded_sp64.train.jsonl",
    )
    parser.add_argument(
        "--train-view-out",
        default="artifacts/private/v2_0_candidate/protected_hard_soft_morph_seeded_sp64.train.txt",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_candidate_serialization.md",
    )
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--progress", type=int, default=1000)
    args = parser.parse_args(argv)

    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")

    boundary_jsonl = Path(args.boundary_jsonl)
    selected_seed = Path(args.selected_seed)
    jsonl_out = Path(args.jsonl_out)
    train_view_out = Path(args.train_view_out)
    report_out = Path(args.report_out)

    stats = materialize_candidate_serialization(
        boundary_jsonl=boundary_jsonl,
        selected_seed=selected_seed,
        jsonl_out=jsonl_out,
        train_view_out=train_view_out,
        max_lines=args.max_lines,
        progress=args.progress,
    )
    report = format_report(
        boundary_jsonl=boundary_jsonl,
        selected_seed=selected_seed,
        jsonl_out=jsonl_out,
        train_view_out=train_view_out,
        stats=stats,
        max_lines=args.max_lines,
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_jsonl: {jsonl_out}")
    print(f"wrote_train_view: {train_view_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
