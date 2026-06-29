from __future__ import annotations

from dataclasses import dataclass, field
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    load_sp_processor,
    selected_piece_strings,
)
from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    BYTE_VOCAB_SIZE,
    encode_boundary_biased_unigram_line_ids,
    encode_finite_protected_soft_marker_line_ids,
)
from scripts.sweep_v2_boundary_biased_unigram import BoundaryBiasedVocab  # noqa: E402
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass
class CompareStats:
    name: str
    lines: int = 0
    exact: int = 0
    lhs_tokens: int = 0
    rhs_tokens: int = 0
    shorter_rhs: int = 0
    longer_rhs: int = 0
    same_len_diff: int = 0

    @property
    def mismatches(self) -> int:
        return self.lines - self.exact

    @property
    def mismatch_rate(self) -> float:
        return self.mismatches / self.lines if self.lines else 0.0

    @property
    def avg_lhs_tokens(self) -> float:
        return self.lhs_tokens / self.lines if self.lines else 0.0

    @property
    def avg_rhs_tokens(self) -> float:
        return self.rhs_tokens / self.lines if self.lines else 0.0


@dataclass(frozen=True)
class MismatchSample:
    comparison: str
    line_number: int
    text: str
    has_protected: bool
    lhs_len: int
    rhs_len: int
    lhs_head: tuple[str, ...]
    rhs_head: tuple[str, ...]


@dataclass
class AuditResult:
    scanned: int = 0
    protected_lines: int = 0
    stats: dict[str, CompareStats] = field(default_factory=dict)
    samples: list[MismatchSample] = field(default_factory=list)


def line_has_protected(text: str, tokenizer: TurkishTokenizer) -> bool:
    return any(piece.kind.startswith("protected:") for piece in analyze_line(text, tokenizer))


def compare_ids(
    *,
    stats: CompareStats,
    lhs: list[int],
    rhs: list[int],
    comparison: str,
    line_number: int,
    text: str,
    has_protected: bool,
    samples: list[MismatchSample],
    max_samples: int,
    labeler,
) -> None:
    stats.lines += 1
    stats.lhs_tokens += len(lhs)
    stats.rhs_tokens += len(rhs)
    if lhs == rhs:
        stats.exact += 1
        return
    if len(rhs) < len(lhs):
        stats.shorter_rhs += 1
    elif len(rhs) > len(lhs):
        stats.longer_rhs += 1
    else:
        stats.same_len_diff += 1
    if len(samples) < max_samples:
        samples.append(
            MismatchSample(
                comparison=comparison,
                line_number=line_number,
                text=text,
                has_protected=has_protected,
                lhs_len=len(lhs),
                rhs_len=len(rhs),
                lhs_head=tuple(labeler(item) for item in lhs[:40]),
                rhs_head=tuple(labeler(item) for item in rhs[:40]),
            )
        )


def make_id_labeler(*, processor, selected_pieces: list[str]):
    piece_size = int(processor.GetPieceSize())
    byte_offset = piece_size + len(selected_pieces)

    def label(token_id: int) -> str:
        if 0 <= token_id < piece_size:
            return str(processor.IdToPiece(token_id))
        if piece_size <= token_id < byte_offset:
            return f"<prot:{selected_pieces[token_id - piece_size]}>"
        if byte_offset <= token_id < byte_offset + BYTE_VOCAB_SIZE:
            return f"<byte_{token_id - byte_offset:02x}>"
        return f"<id:{token_id}>"

    return label


def audit_alignment(
    *,
    input_path: Path,
    sp_model: Path,
    sp_vocab: Path,
    selected_pieces_path: Path,
    boundary_lambda: float,
    max_lines: int | None,
    max_samples: int,
    progress: int,
) -> AuditResult:
    processor = load_sp_processor(sp_model)
    boundary_vocab = BoundaryBiasedVocab.from_vocab_file(sp_vocab)
    selected = selected_piece_strings(selected_pieces_path)
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    labeler = make_id_labeler(processor=processor, selected_pieces=selected)
    result = AuditResult(
        stats={
            "floor_vs_lambda0_all": CompareStats("floor_vs_lambda0_all"),
            "floor_vs_lambda0_no_protected": CompareStats("floor_vs_lambda0_no_protected"),
            "official_sp_vs_lambda0_no_protected": CompareStats(
                "official_sp_vs_lambda0_no_protected"
            ),
        }
    )

    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if max_lines is not None and result.scanned >= max_lines:
                break
            text = raw_line.rstrip("\n")
            result.scanned += 1
            has_protected = line_has_protected(text, tokenizer)
            if has_protected:
                result.protected_lines += 1

            floor_ids, _floor_bytes = encode_finite_protected_soft_marker_line_ids(
                text,
                processor=processor,
                selected_pieces=selected,
                protected_piece_offset=int(processor.GetPieceSize()),
                insert_soft_markers=False,
                numeric_sp_passthrough=True,
            )
            biased_ids, _biased_bytes = encode_boundary_biased_unigram_line_ids(
                text,
                processor=processor,
                boundary_vocab=boundary_vocab,
                selected_pieces=selected,
                protected_piece_offset=int(processor.GetPieceSize()),
                boundary_lambda=boundary_lambda,
                numeric_sp_passthrough=True,
            )

            compare_ids(
                stats=result.stats["floor_vs_lambda0_all"],
                lhs=floor_ids,
                rhs=biased_ids,
                comparison="floor_vs_lambda0_all",
                line_number=line_number,
                text=text,
                has_protected=has_protected,
                samples=result.samples,
                max_samples=max_samples,
                labeler=labeler,
            )

            if not has_protected:
                compare_ids(
                    stats=result.stats["floor_vs_lambda0_no_protected"],
                    lhs=floor_ids,
                    rhs=biased_ids,
                    comparison="floor_vs_lambda0_no_protected",
                    line_number=line_number,
                    text=text,
                    has_protected=has_protected,
                    samples=result.samples,
                    max_samples=max_samples,
                    labeler=labeler,
                )
                official_ids = [int(item) for item in processor.EncodeAsIds(text)]
                compare_ids(
                    stats=result.stats["official_sp_vs_lambda0_no_protected"],
                    lhs=official_ids,
                    rhs=biased_ids,
                    comparison="official_sp_vs_lambda0_no_protected",
                    line_number=line_number,
                    text=text,
                    has_protected=has_protected,
                    samples=result.samples,
                    max_samples=max_samples,
                    labeler=labeler,
                )

            if progress > 0 and result.scanned % progress == 0:
                print(f"audited {result.scanned:,} lines", flush=True)

    return result


def format_report(
    *,
    input_path: Path,
    sp_model: Path,
    sp_vocab: Path,
    selected_pieces: Path,
    boundary_lambda: float,
    result: AuditResult,
) -> str:
    lines = [
        "# v2.0 Boundary Decoder Alignment Audit",
        "",
        f"Input: `{input_path.as_posix()}`",
        f"SP model: `{sp_model.as_posix()}`",
        f"SP vocab: `{sp_vocab.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces.as_posix()}`",
        f"Boundary lambda: `{boundary_lambda}`",
        "",
        "This audit separates the decoder/pipeline effect from the morphology",
        "penalty effect. It compares the active finite protected floor against",
        "the boundary-biased Viterbi path at lambda 0, and compares official",
        "SentencePiece against lambda 0 on lines without protected spans.",
        "",
        "## Summary",
        "",
        f"- scanned lines: {result.scanned}",
        f"- lines with protected route: {result.protected_lines}",
        "",
        "| Comparison | Lines | Exact | Mismatch rate | Avg lhs tokens | Avg rhs tokens | RHS shorter | RHS longer | Same-len diff |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for stats in result.stats.values():
        lines.append(
            f"| `{stats.name}` | {stats.lines} | {stats.exact}/{stats.lines} | "
            f"{stats.mismatch_rate:.6f} | {stats.avg_lhs_tokens:.4f} | "
            f"{stats.avg_rhs_tokens:.4f} | {stats.shorter_rhs} | "
            f"{stats.longer_rhs} | {stats.same_len_diff} |"
        )

    lines.extend(["", "## Sample Mismatches", ""])
    if not result.samples:
        lines.append("No mismatches in sampled rows.")
    for sample in result.samples:
        lines.extend(
            [
                f"### {sample.comparison} line {sample.line_number}",
                "",
                f"- has_protected: `{sample.has_protected}`",
                f"- lhs_len / rhs_len: `{sample.lhs_len}` / `{sample.rhs_len}`",
                f"- text: `{sample.text}`",
                f"- lhs head: `{' '.join(sample.lhs_head)}`",
                f"- rhs head: `{' '.join(sample.rhs_head)}`",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Audit lambda-0 boundary-biased decoder alignment against SP/floor.",
    )
    parser.add_argument(
        "--input",
        default=(
            "artifacts/private/v1_8_local_lm_probe/"
            "celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/valid.txt"
        ),
    )
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--sp-vocab",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--boundary-lambda", type=float, default=0.0)
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--max-samples", type=int, default=12)
    parser.add_argument("--progress", type=int, default=0)
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_boundary_decoder_alignment_audit.md",
    )
    args = parser.parse_args(argv)

    result = audit_alignment(
        input_path=Path(args.input),
        sp_model=Path(args.sp_model),
        sp_vocab=Path(args.sp_vocab),
        selected_pieces_path=Path(args.selected_pieces),
        boundary_lambda=args.boundary_lambda,
        max_lines=args.max_lines,
        max_samples=args.max_samples,
        progress=args.progress,
    )
    report = format_report(
        input_path=Path(args.input),
        sp_model=Path(args.sp_model),
        sp_vocab=Path(args.sp_vocab),
        selected_pieces=Path(args.selected_pieces),
        boundary_lambda=args.boundary_lambda,
        result=result,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
