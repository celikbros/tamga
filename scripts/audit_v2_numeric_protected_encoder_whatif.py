from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_v2_protected_route_cost_classes import classify_numeric_like  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    encode_protected_surface,
    load_sp_processor,
    selected_piece_strings,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass
class NumericClassStats:
    occurrences: int = 0
    bytes: int = 0
    current_tokens: int = 0
    sp_tokens: int = 0
    digit2_tokens: int = 0
    digit4_tokens: int = 0
    unique_surfaces: set[str] = field(default_factory=set)

    def add(
        self,
        *,
        surface: str,
        current_tokens: int,
        sp_tokens: int,
        digit2_tokens: int,
        digit4_tokens: int,
    ) -> None:
        self.occurrences += 1
        self.bytes += len(surface.encode("utf-8"))
        self.current_tokens += current_tokens
        self.sp_tokens += sp_tokens
        self.digit2_tokens += digit2_tokens
        self.digit4_tokens += digit4_tokens
        self.unique_surfaces.add(surface)


@dataclass
class SplitWhatIf:
    split: str
    lines: int = 0
    raw_bytes: int = 0
    current_finite_tokens: int = 0
    current_numeric_tokens: int = 0
    numeric_sp_tokens: int = 0
    numeric_digit2_tokens: int = 0
    numeric_digit4_tokens: int = 0
    class_stats: dict[str, NumericClassStats] = field(
        default_factory=lambda: defaultdict(NumericClassStats)
    )

    @property
    def current_tpb(self) -> float:
        return self.current_finite_tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def sp_numeric_tpb(self) -> float:
        return self._whatif_tpb(self.numeric_sp_tokens)

    @property
    def digit2_tpb(self) -> float:
        return self._whatif_tpb(self.numeric_digit2_tokens)

    @property
    def digit4_tpb(self) -> float:
        return self._whatif_tpb(self.numeric_digit4_tokens)

    def _whatif_tpb(self, replacement_numeric_tokens: int) -> float:
        if not self.raw_bytes:
            return 0.0
        total = (
            self.current_finite_tokens
            - self.current_numeric_tokens
            + replacement_numeric_tokens
        )
        return total / self.raw_bytes


def digit_chunk_tokens(surface: str, *, chunk_size: int) -> int:
    """Estimate a tiny lossless numeric codec using digit chunks plus literals."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    tokens = 0
    for part in re.findall(r"\d+|\D", surface):
        if part.isdigit():
            tokens += math.ceil(len(part) / chunk_size)
            continue
        if len(part) == 1 and ord(part) < 128:
            tokens += 1
        else:
            tokens += len(part.encode("utf-8"))
    return tokens


def _sp_piece_count(processor, surface: str) -> int:
    return len(processor.EncodeAsIds(surface)) if surface else 0


def _eos_token_count(processor) -> int:
    eos_id = processor.eos_id() if hasattr(processor, "eos_id") else -1
    return 1 if int(eos_id) >= 0 else 0


def audit_split(
    *,
    split: str,
    path: Path,
    processor,
    selected_pieces: list[str],
    max_lines: int | None,
    progress: int,
    examples: dict[str, list[dict[str, object]]],
    examples_per_class: int,
) -> SplitWhatIf:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    stats = SplitWhatIf(split=split)
    eos_tokens = _eos_token_count(processor)
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            if max_lines is not None and stats.lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            stats.lines += 1
            stats.raw_bytes += len(text.encode("utf-8"))
            stats.current_finite_tokens += eos_tokens

            segment = ""

            def flush() -> None:
                nonlocal segment
                if not segment:
                    return
                stats.current_finite_tokens += _sp_piece_count(processor, segment)
                segment = ""

            for piece in analyze_line(text, tokenizer):
                if piece.kind == "whitespace":
                    flush()
                    continue

                if piece.kind.startswith("protected:"):
                    flush()
                    current_piece_tokens, current_byte_tokens = encode_protected_surface(
                        piece.surface,
                        selected_pieces,
                    )
                    current_tokens = current_piece_tokens + current_byte_tokens
                    stats.current_finite_tokens += current_tokens
                    if piece.kind != "protected:numeric_like":
                        continue
                    sp_tokens = _sp_piece_count(processor, piece.surface)
                    digit2_tokens = digit_chunk_tokens(piece.surface, chunk_size=2)
                    digit4_tokens = digit_chunk_tokens(piece.surface, chunk_size=4)
                    label = classify_numeric_like(piece.surface)

                    stats.current_numeric_tokens += current_tokens
                    stats.numeric_sp_tokens += sp_tokens
                    stats.numeric_digit2_tokens += digit2_tokens
                    stats.numeric_digit4_tokens += digit4_tokens
                    stats.class_stats[label].add(
                        surface=piece.surface,
                        current_tokens=current_tokens,
                        sp_tokens=sp_tokens,
                        digit2_tokens=digit2_tokens,
                        digit4_tokens=digit4_tokens,
                    )

                    bucket = examples[label]
                    if len(bucket) < examples_per_class:
                        bucket.append(
                            {
                                "split": split,
                                "line_no": line_no,
                                "class": label,
                                "surface": piece.surface,
                                "current_tokens": current_tokens,
                                "sp_tokens": sp_tokens,
                                "digit2_tokens": digit2_tokens,
                                "digit4_tokens": digit4_tokens,
                                "text": text,
                            }
                        )
                    continue

                if piece.kind == "apostrophe":
                    flush()
                    stats.current_finite_tokens += _sp_piece_count(processor, piece.surface)
                    continue

                if piece.kind == "suffix" and piece.boundary_before == "hard":
                    flush()
                    stats.current_finite_tokens += _sp_piece_count(processor, piece.surface)
                    continue

                if piece.boundary_before == "hard":
                    flush()
                    segment = piece.surface
                    continue

                segment += piece.surface

            flush()

            if progress > 0 and stats.lines % progress == 0:
                print(
                    f"audited {split} {stats.lines:,} lines "
                    f"current_tpb={stats.current_tpb:.6f} "
                    f"numeric_sp_tpb={stats.sp_numeric_tpb:.6f}",
                    flush=True,
                )
    return stats


def _fmt(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def _combined_class_stats(audits: list[SplitWhatIf]) -> dict[str, NumericClassStats]:
    combined: dict[str, NumericClassStats] = defaultdict(NumericClassStats)
    for audit in audits:
        for label, stats in audit.class_stats.items():
            target = combined[label]
            target.occurrences += stats.occurrences
            target.bytes += stats.bytes
            target.current_tokens += stats.current_tokens
            target.sp_tokens += stats.sp_tokens
            target.digit2_tokens += stats.digit2_tokens
            target.digit4_tokens += stats.digit4_tokens
            target.unique_surfaces.update(stats.unique_surfaces)
    return combined


def format_report(
    *,
    split_dir: Path,
    sp_model: Path,
    selected_pieces: Path,
    audits: list[SplitWhatIf],
    examples_out: Path,
) -> str:
    lines = [
        "# v2.0 Numeric Protected Encoder What-If Audit",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"SP model: `{sp_model.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces.as_posix()}`",
        f"Private examples: `{examples_out.as_posix()}`",
        "",
        "This audit does not change tokenizer behavior. It estimates how much",
        "finite protected token pressure would drop if `numeric_like` used a",
        "different lossless sub-encoder.",
        "",
        "Policies:",
        "",
        "- `current`: current finite protected pieces plus UTF-8 byte fallback.",
        "- `sp_numeric`: encode numeric surfaces with the SP64 model as an upper",
        "  bound for compression, while still treating the span as logically",
        "  protected in the wrapper.",
        "- `digit2`: a small numeric codec with 2-digit chunks plus literal",
        "  punctuation/letters.",
        "- `digit4`: an optimistic 4-digit chunk codec used only as an upper",
        "  bound; it would require a much larger finite numeric inventory.",
        "",
        "## Split What-If Summary",
        "",
        "| Split | Lines | Raw bytes | Current finite tpb | Numeric current tokens | Numeric SP tokens | Numeric digit2 tokens | Numeric digit4 tokens | SP numeric what-if tpb | Digit2 what-if tpb | Digit4 what-if tpb |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for audit in audits:
        lines.append(
            f"| {audit.split} | {audit.lines} | {audit.raw_bytes} | "
            f"{_fmt(audit.current_tpb)} | {audit.current_numeric_tokens} | "
            f"{audit.numeric_sp_tokens} | {audit.numeric_digit2_tokens} | "
            f"{audit.numeric_digit4_tokens} | {_fmt(audit.sp_numeric_tpb)} | "
            f"{_fmt(audit.digit2_tpb)} | {_fmt(audit.digit4_tpb)} |"
        )

    combined = _combined_class_stats(audits)
    lines.extend(
        [
            "",
            "## Numeric Class Cost",
            "",
            "| Class | Count | Unique | Bytes | Current tokens | SP tokens | Digit2 tokens | Digit4 tokens | Current-SP delta | Current-Digit2 delta |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for label, stats in sorted(
        combined.items(),
        key=lambda item: (item[1].current_tokens - item[1].sp_tokens, item[1].occurrences),
        reverse=True,
    ):
        lines.append(
            f"| `{label}` | {stats.occurrences} | {len(stats.unique_surfaces)} | "
            f"{stats.bytes} | {stats.current_tokens} | {stats.sp_tokens} | "
            f"{stats.digit2_tokens} | {stats.digit4_tokens} | "
            f"{stats.current_tokens - stats.sp_tokens} | "
            f"{stats.current_tokens - stats.digit2_tokens} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation Gate",
            "",
            "If `sp_numeric` recovers most wrapper cost, numeric routing should be",
            "redesigned before MorphBPE work. If `digit2` is close to SP, a tiny",
            "lossless numeric codec is a better production-shaped option than",
            "letting normal SP pieces own protected number spans.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_examples(path: Path, examples: dict[str, list[dict[str, object]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for label, rows in sorted(examples.items()):
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Audit numeric protected route what-if encoder policies."
    )
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--split", action="append", choices=["train", "valid", "test"])
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument("--examples-per-class", type=int, default=5)
    parser.add_argument(
        "--examples-out",
        default="artifacts/private/v2_0_numeric_protected_encoder_whatif_examples.jsonl",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_numeric_protected_encoder_whatif.md",
    )
    args = parser.parse_args(argv)

    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")
    if args.examples_per_class < 0:
        raise ValueError("--examples-per-class must be non-negative")

    split_dir = Path(args.split_dir)
    sp_model = Path(args.sp_model)
    selected_pieces_path = Path(args.selected_pieces)
    processor = load_sp_processor(sp_model)
    selected = selected_piece_strings(selected_pieces_path)
    examples: dict[str, list[dict[str, object]]] = defaultdict(list)
    splits = args.split or ["train", "valid", "test"]

    audits = [
        audit_split(
            split=split,
            path=split_dir / f"{split}.txt",
            processor=processor,
            selected_pieces=selected,
            max_lines=args.max_lines,
            progress=args.progress,
            examples=examples,
            examples_per_class=args.examples_per_class,
        )
        for split in splits
    ]

    examples_out = Path(args.examples_out)
    write_examples(examples_out, examples)
    report = format_report(
        split_dir=split_dir,
        sp_model=sp_model,
        selected_pieces=selected_pieces_path,
        audits=audits,
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
