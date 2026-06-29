from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import random
import sys
from pathlib import Path


@dataclass(frozen=True)
class SplitStats:
    name: str
    lines: int
    bytes: int
    path: Path


def parse_parts(raw: str) -> tuple[int, int, int]:
    pieces = raw.split(":")
    if len(pieces) != 3:
        raise argparse.ArgumentTypeError("split parts must look like 8:1:1")
    values = tuple(int(piece) for piece in pieces)
    if any(value <= 0 for value in values):
        raise argparse.ArgumentTypeError("split parts must be positive")
    return values  # type: ignore[return-value]


def assign_split(index: int, total: int, parts: tuple[int, int, int]) -> str:
    train_part, valid_part, _test_part = parts
    train_cut = train_part / sum(parts)
    valid_cut = (train_part + valid_part) / sum(parts)
    position = index / total
    if position < train_cut:
        return "train"
    if position < valid_cut:
        return "valid"
    return "test"


def write_report(
    *,
    input_path: Path,
    output_dir: Path,
    seed: int,
    parts: tuple[int, int, int],
    rows: list[SplitStats],
    report_out: Path,
) -> None:
    lines = [
        "# v3.1 Ablation Split",
        "",
        f"Input: `{input_path.as_posix()}`",
        f"Output dir: `{output_dir.as_posix()}`",
        f"Seed: `{seed}`",
        f"Split parts: `{parts[0]}:{parts[1]}:{parts[2]}`",
        "",
        "This split is for local vocab-size ablation only. It is not the final",
        "Gardaş tokenizer training corpus.",
        "",
        "## Summary",
        "",
        "| Split | Lines | Bytes | Path |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.name} | {row.lines} | {row.bytes} | `{row.path.as_posix()}` |"
        )
    lines.append("")
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Create a deterministic text split for v3.1 vocab ablation.")
    parser.add_argument(
        "--input",
        default="C:/CELIK-GARDASH/datasets/tokenizer_v3_0/real_mix_60k_sample.txt",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/private/v3_1_vocab_ablation_split",
    )
    parser.add_argument("--seed", type=int, default=20260618)
    parser.add_argument("--parts", type=parse_parts, default=parse_parts("8:1:1"))
    parser.add_argument("--report-out", default="artifacts/v3_1_vocab_ablation_split.md")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    lines = [line.rstrip("\n") for line in input_path.open("r", encoding="utf-8")]
    indices = list(range(len(lines)))
    random.Random(args.seed).shuffle(indices)
    assignments: dict[str, list[str]] = {"train": [], "valid": [], "test": []}
    for rank, line_index in enumerate(indices):
        split = assign_split(rank, len(indices), args.parts)
        assignments[split].append(lines[line_index])

    rows: list[SplitStats] = []
    for split, split_lines in assignments.items():
        path = output_dir / f"{split}.txt"
        manifest_path = output_dir / f"{split}.manifest.jsonl"
        byte_count = 0
        with (
            path.open("w", encoding="utf-8", newline="\n") as text_out,
            manifest_path.open("w", encoding="utf-8", newline="\n") as manifest_out,
        ):
            for local_index, text in enumerate(split_lines, start=1):
                text_out.write(text)
                text_out.write("\n")
                raw_bytes = len(text.encode("utf-8"))
                byte_count += raw_bytes
                manifest_out.write(
                    json.dumps(
                        {
                            "local_line": local_index,
                            "raw_bytes": raw_bytes,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        rows.append(SplitStats(split, len(split_lines), byte_count, path))

    report_out = Path(args.report_out)
    write_report(
        input_path=input_path,
        output_dir=output_dir,
        seed=args.seed,
        parts=args.parts,
        rows=rows,
        report_out=report_out,
    )
    print(report_out.read_text(encoding="utf-8"))
    print(f"wrote_split_dir: {output_dir}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
