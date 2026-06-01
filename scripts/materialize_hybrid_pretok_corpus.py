from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class HybridPretokStats:
    lines: int
    input_bytes: int
    output_bytes: int
    morph_tokens: int
    max_morph_tokens_line: int

    @property
    def avg_morph_tokens_line(self) -> float:
        return self.morph_tokens / self.lines if self.lines else 0.0

    @property
    def output_bytes_per_input_byte(self) -> float:
        return self.output_bytes / self.input_bytes if self.input_bytes else 0.0


def morph_pretokenize_line(text: str) -> list[str]:
    return TurkishTokenizer().encode(text)


def write_hybrid_pretok_corpus(
    input_path: str | Path,
    output_path: str | Path,
) -> HybridPretokStats:
    source = Path(input_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)

    lines = 0
    input_bytes = 0
    output_bytes = 0
    morph_tokens = 0
    max_morph_tokens_line = 0

    with (
        source.open("r", encoding="utf-8") as src,
        target.open("w", encoding="utf-8", newline="\n") as dst,
    ):
        for raw_line in src:
            text = raw_line.rstrip("\n")
            pieces = morph_pretokenize_line(text)
            output_line = " ".join(pieces)
            dst.write(output_line + "\n")

            lines += 1
            input_bytes += len(text.encode("utf-8"))
            output_bytes += len(output_line.encode("utf-8"))
            morph_tokens += len(pieces)
            max_morph_tokens_line = max(max_morph_tokens_line, len(pieces))

    return HybridPretokStats(
        lines=lines,
        input_bytes=input_bytes,
        output_bytes=output_bytes,
        morph_tokens=morph_tokens,
        max_morph_tokens_line=max_morph_tokens_line,
    )


def format_report(
    *,
    input_path: str | Path,
    output_path: str | Path,
    stats: HybridPretokStats,
) -> str:
    return "\n".join(
        [
            "# v1.8 Hybrid Morph Pretokenized Corpus",
            "",
            f"Input: `{Path(input_path).as_posix()}`",
            f"Output: `{Path(output_path).as_posix()}`",
            "",
            "This private corpus applies the deterministic morphology/protection",
            "tokenizer to the train split and separates its pieces with spaces.",
            "It is used only to train morphology-aware SentencePiece baselines.",
            "",
            "## Summary",
            "",
            "| Lines | Input bytes | Output bytes | Output/Input bytes | Morph tokens | Avg morph tokens/line | Max morph tokens/line |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {stats.lines} | {stats.input_bytes} | {stats.output_bytes} | "
                f"{stats.output_bytes_per_input_byte:.4f} | {stats.morph_tokens} | "
                f"{stats.avg_morph_tokens_line:.4f} | {stats.max_morph_tokens_line} |"
            ),
            "",
            "## Caveat",
            "",
            "This is a hard-boundary intrinsic baseline corpus, not a final LM",
            "serialization format. Generation-oriented hybrid use still needs an",
            "explicit roundtrip-safe serialization/decoder.",
        ]
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Materialize morphology-pretokenized train corpus for hybrid SP baselines.",
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report-out", required=True)
    args = parser.parse_args(argv)

    stats = write_hybrid_pretok_corpus(args.input, args.output)
    report = format_report(input_path=args.input, output_path=args.output, stats=stats)
    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_output: {args.output}")
    print(f"wrote_report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
