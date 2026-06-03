from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import count_words  # noqa: E402
from scripts.evaluate_v2_finite_protected_soft_marker_intrinsic import (  # noqa: E402
    encode_finite_protected_soft_marker,
    load_sp_processor,
    selected_piece_strings,
)


@dataclass(frozen=True)
class SplitPressure:
    split: str
    lines: int
    bytes: int
    words: int
    logical_tokens: int
    model_tokens: int
    protected_piece_tokens: int
    protected_byte_tokens: int

    @property
    def model_tokens_per_byte(self) -> float:
        return self.model_tokens / self.bytes if self.bytes else 0.0

    @property
    def logical_tokens_per_byte(self) -> float:
        return self.logical_tokens / self.bytes if self.bytes else 0.0

    @property
    def model_tokens_per_word(self) -> float:
        return self.model_tokens / self.words if self.words else 0.0

    @property
    def protected_byte_token_rate(self) -> float:
        total = self.protected_piece_tokens + self.protected_byte_tokens
        return self.protected_byte_tokens / total if total else 0.0


def measure_split(
    *,
    split: str,
    path: Path,
    processor,
    selected_pieces: list[str],
    progress: int,
) -> SplitPressure:
    lines = 0
    byte_count = 0
    word_count = 0
    logical_tokens = 0
    model_tokens = 0
    protected_piece_tokens = 0
    protected_byte_tokens = 0

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            text = raw_line.rstrip("\n")
            encoded = encode_finite_protected_soft_marker(
                text,
                processor=processor,
                selected_pieces=selected_pieces,
            )
            lines += 1
            byte_count += len(text.encode("utf-8"))
            word_count += count_words(text)
            logical_tokens += len(encoded.logical_tokens)
            model_tokens += encoded.model_token_count
            protected_piece_tokens += encoded.protected_piece_tokens
            protected_byte_tokens += encoded.protected_byte_tokens

            if progress > 0 and lines % progress == 0:
                print(
                    f"measured {split}: {lines:,} lines "
                    f"model_tokens={model_tokens:,} "
                    f"tokens/byte={model_tokens / byte_count if byte_count else 0.0:.6f}",
                    flush=True,
                )

    return SplitPressure(
        split=split,
        lines=lines,
        bytes=byte_count,
        words=word_count,
        logical_tokens=logical_tokens,
        model_tokens=model_tokens,
        protected_piece_tokens=protected_piece_tokens,
        protected_byte_tokens=protected_byte_tokens,
    )


def measure_splits(
    *,
    split_dir: Path,
    soft_marker_model: Path,
    selected_pieces_path: Path,
    splits: tuple[str, ...],
    progress: int,
) -> list[SplitPressure]:
    processor = load_sp_processor(soft_marker_model)
    selected_pieces = selected_piece_strings(selected_pieces_path)
    rows: list[SplitPressure] = []
    for split in splits:
        rows.append(
            measure_split(
                split=split,
                path=split_dir / f"{split}.txt",
                processor=processor,
                selected_pieces=selected_pieces,
                progress=progress,
            )
        )
    return rows


def format_report(
    *,
    split_dir: Path,
    soft_marker_model: Path,
    selected_pieces_path: Path,
    rows: list[SplitPressure],
) -> str:
    lines = [
        "# v2.0 Finite Protected Soft-Marker Token Pressure",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"Soft-marker model: `{soft_marker_model.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces_path.as_posix()}`",
        "",
        "This report measures split-level token pressure for the finite protected",
        "soft-marker prototype before any tiny-LM screening.",
        "",
        "## Token Pressure",
        "",
        "| Split | Lines | Bytes | Words | Logical tokens | Model tokens | Model tokens/byte | Logical tokens/byte | Model tokens/word | Protected piece tokens | Protected byte tokens | Protected byte-token rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.split} | {row.lines} | {row.bytes} | {row.words} | "
            f"{row.logical_tokens} | {row.model_tokens} | "
            f"{row.model_tokens_per_byte:.6f} | {row.logical_tokens_per_byte:.6f} | "
            f"{row.model_tokens_per_word:.4f} | {row.protected_piece_tokens} | "
            f"{row.protected_byte_tokens} | {row.protected_byte_token_rate:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Baseline Anchors",
            "",
            "```text",
            "SP64 baseline valid/test: about 0.1566 / 0.1570 tokens/raw byte",
            "raw-soft-marker candidate valid/test: about 0.2367 / 0.2367 tokens/raw byte",
            "custom lossless+64k valid/test: about 0.4162 / 0.4194 tokens/raw byte",
            "```",
            "",
            "## Gate",
            "",
            "The prototype should be closer to raw-soft-marker/SP64 than to pure",
            "custom lossless pressure before tiny-LM screening.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Measure split-level token pressure for finite-protected soft-marker prototype.",
    )
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument(
        "--soft-marker-model",
        default="artifacts/private/v2_0_candidate_sentencepiece/protected_hard_soft_marker_raw_sp64_unigram_64000.model",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--split", action="append", default=[])
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--report-out", default="artifacts/v2_0_finite_protected_soft_marker_token_pressure.md")
    args = parser.parse_args(argv)

    splits = tuple(args.split or ["train", "valid", "test"])
    rows = measure_splits(
        split_dir=Path(args.split_dir),
        soft_marker_model=Path(args.soft_marker_model),
        selected_pieces_path=Path(args.selected_pieces),
        splits=splits,
        progress=args.progress,
    )
    report = format_report(
        split_dir=Path(args.split_dir),
        soft_marker_model=Path(args.soft_marker_model),
        selected_pieces_path=Path(args.selected_pieces),
        rows=rows,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
