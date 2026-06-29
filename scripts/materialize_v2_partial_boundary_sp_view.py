from __future__ import annotations

from dataclasses import dataclass
import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402

BOUNDARY_MARKER = "\ue000"


@dataclass(frozen=True)
class ViewStats:
    lines: int
    raw_bytes: int
    view_bytes: int
    marked_lines: int
    inserted_markers: int

    @property
    def view_raw_ratio(self) -> float:
        return self.view_bytes / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def marked_line_rate(self) -> float:
        return self.marked_lines / self.lines if self.lines else 0.0


def marked_line(text: str, *, marker: str) -> tuple[str, int]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    output: list[str] = []
    inserted = 0
    for piece in analyze_line(text, tokenizer):
        if piece.boundary_before == "soft":
            output.append(marker)
            inserted += 1
        output.append(piece.surface)
    return "".join(output), inserted


def materialize_train_view(
    *,
    input_path: Path,
    output_path: Path,
    rho: float,
    seed: int,
    marker: str,
    progress: int,
) -> ViewStats:
    rng = random.Random(seed)
    lines = 0
    raw_bytes = 0
    view_bytes = 0
    marked_lines = 0
    inserted_markers = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as source, output_path.open(
        "w",
        encoding="utf-8",
        newline="\n",
    ) as target:
        for raw in source:
            text = raw.rstrip("\n")
            lines += 1
            raw_bytes += len(text.encode("utf-8"))
            if rng.random() < rho:
                view, inserted = marked_line(text, marker=marker)
                if inserted:
                    marked_lines += 1
                    inserted_markers += inserted
            else:
                view = text
            view_bytes += len(view.encode("utf-8"))
            target.write(view + "\n")
            if progress > 0 and lines % progress == 0:
                print(
                    f"materialized {lines:,} lines marked={marked_lines:,} "
                    f"markers={inserted_markers:,}",
                    flush=True,
                )

    return ViewStats(
        lines=lines,
        raw_bytes=raw_bytes,
        view_bytes=view_bytes,
        marked_lines=marked_lines,
        inserted_markers=inserted_markers,
    )


def write_config(
    *,
    config_out: Path,
    candidate_name: str,
    train_view: Path,
    split_dir: Path,
    model_prefix: Path,
    report_out: Path,
    marker: str,
    vocab_size: int,
) -> None:
    config_out.parent.mkdir(parents=True, exist_ok=True)
    config_out.write_text(
        "\n".join(
            [
                "[settings]",
                f'candidate_name = "{candidate_name}"',
                f'train_view = "{train_view.as_posix()}"',
                f'valid_view = "{(split_dir / "valid.txt").as_posix()}"',
                f'test_view = "{(split_dir / "test.txt").as_posix()}"',
                f'model_prefix = "{model_prefix.as_posix()}"',
                'model_type = "unigram"',
                f"vocab_size = {vocab_size}",
                f'report_out = "{report_out.as_posix()}"',
                'normalization_rule_name = "identity"',
                "character_coverage = 1.0",
                "hard_vocab_limit = false",
                "split_by_whitespace = true",
                "remove_extra_whitespaces = false",
                "train_extremely_large_corpus = false",
                "max_sentence_length = 16384",
                f'pretokenization_delimiter = "{marker}"',
                "",
            ]
        ),
        encoding="utf-8",
    )


def format_report(
    *,
    input_path: Path,
    output_path: Path,
    stats: ViewStats,
    rho: float,
    seed: int,
    marker: str,
    config_out: Path | None,
) -> str:
    lines = [
        "# v2.0 Partial-Boundary SentencePiece Train View",
        "",
        f"Input: `{input_path.as_posix()}`",
        f"Output: `{output_path.as_posix()}`",
        f"rho: `{rho}`",
        f"seed: `{seed}`",
        f"marker: `{marker}`",
        "",
        "This view inserts a train-only pretokenization delimiter at custom",
        "soft morphology boundaries for only a fraction of training lines.",
        "Validation/test text remains delimiter-free.",
        "",
        "## Summary",
        "",
        "| Lines | Raw bytes | View bytes | View/raw bytes | Marked lines | Marked line rate | Inserted markers |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| {stats.lines} | {stats.raw_bytes} | {stats.view_bytes} | "
            f"{stats.view_raw_ratio:.6f} | {stats.marked_lines} | "
            f"{stats.marked_line_rate:.6f} | {stats.inserted_markers} |"
        ),
        "",
    ]
    if config_out is not None:
        lines.extend(["Config:", "", f"`{config_out.as_posix()}`", ""])
    lines.extend(
        [
            "## Next",
            "",
            "Train with `scripts/run_v2_candidate_sentencepiece_probe.py` and",
            "compare token pressure plus intrinsic morphology/protected reports",
            "against the repaired finite protected numeric-SP floor.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Create a partial-boundary SentencePiece train view."
    )
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument("--rho", type=float, required=True)
    parser.add_argument("--seed", type=int, default=20260610)
    parser.add_argument("--marker", default=BOUNDARY_MARKER)
    parser.add_argument("--candidate-name", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--report-out", required=True)
    parser.add_argument("--config-out")
    parser.add_argument("--model-prefix")
    parser.add_argument("--sp-report-out")
    parser.add_argument("--vocab-size", type=int, default=64000)
    parser.add_argument("--progress", type=int, default=0)
    args = parser.parse_args(argv)

    if not 0.0 <= args.rho <= 1.0:
        raise ValueError("--rho must be between 0 and 1")

    split_dir = Path(args.split_dir)
    input_path = split_dir / "train.txt"
    output_path = Path(args.out)
    stats = materialize_train_view(
        input_path=input_path,
        output_path=output_path,
        rho=args.rho,
        seed=args.seed,
        marker=args.marker,
        progress=args.progress,
    )

    config_out = Path(args.config_out) if args.config_out else None
    if config_out is not None:
        model_prefix = (
            Path(args.model_prefix)
            if args.model_prefix
            else output_path.with_suffix("")
        )
        sp_report_out = (
            Path(args.sp_report_out)
            if args.sp_report_out
            else Path("artifacts") / f"{args.candidate_name}_sentencepiece_probe.md"
        )
        write_config(
            config_out=config_out,
            candidate_name=args.candidate_name,
            train_view=output_path,
            split_dir=split_dir,
            model_prefix=model_prefix,
            report_out=sp_report_out,
            marker=args.marker,
            vocab_size=args.vocab_size,
        )

    report = format_report(
        input_path=input_path,
        output_path=output_path,
        stats=stats,
        rho=args.rho,
        seed=args.seed,
        marker=args.marker,
        config_out=config_out,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_view: {output_path}")
    print(f"wrote_report: {report_out}")
    if config_out is not None:
        print(f"wrote_config: {config_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
