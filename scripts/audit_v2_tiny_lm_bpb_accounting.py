from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunSpec:
    name: str
    report: Path
    stats: Path
    metrics: Path | None = None


@dataclass(frozen=True)
class TrainingRow:
    tokenizer: str
    vocab_size: int
    steps: int
    tokens_seen: int
    approx_bytes_seen: float
    final_valid_bpb: float
    test_bpb: float


@dataclass(frozen=True)
class SplitStats:
    tokens_per_byte: float
    tokens: int
    bytes: int
    lines: int


def _parse_number(value: str) -> float:
    return float(value.replace(",", "").strip())


def parse_training_row(report: Path, tokenizer: str) -> TrainingRow:
    for line in report.read_text(encoding="utf-8").splitlines():
        if not line.startswith(f"| {tokenizer} |"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 12:
            continue
        return TrainingRow(
            tokenizer=cells[0],
            vocab_size=int(_parse_number(cells[2])),
            steps=int(_parse_number(cells[6])),
            tokens_seen=int(_parse_number(cells[7])),
            approx_bytes_seen=_parse_number(cells[8]),
            final_valid_bpb=_parse_number(cells[10]),
            test_bpb=_parse_number(cells[11]),
        )
    raise ValueError(f"training row for {tokenizer!r} not found in {report}")


def load_split_stats(stats: Path, tokenizer: str) -> dict[str, SplitStats]:
    for raw in stats.read_text(encoding="utf-8").splitlines():
        item = json.loads(raw)
        if item.get("tokenizer") != tokenizer:
            continue
        return {
            name: SplitStats(
                tokens_per_byte=float(split["tokens_per_byte"]),
                tokens=int(split["tokens"]),
                bytes=int(split["bytes"]),
                lines=int(split["lines"]),
            )
            for name, split in item["splits"].items()
        }
    raise ValueError(f"encoded stats for {tokenizer!r} not found in {stats}")


def load_last_train_loss_bits(metrics: Path | None) -> float | None:
    if metrics is None or not metrics.exists():
        return None
    last = None
    for raw in metrics.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            last = json.loads(raw)
    if not last or "train_loss_nats_per_token" not in last:
        return None
    return float(last["train_loss_nats_per_token"]) / math.log(2)


def default_specs() -> list[RunSpec]:
    root = Path("artifacts/private")
    public = Path("artifacts")
    return [
        RunSpec(
            name="finite_protected_sp64_numeric_sp_floor",
            report=public / "v2_0_tiny_lm_context_free_ladder_sp64_floor_2mbytes.md",
            stats=root / "v2_0_tiny_lm_context_free_ladder_sp64_floor_2mbytes" / "encoded_stats.jsonl",
            metrics=(
                root
                / "v2_0_tiny_lm_context_free_ladder_sp64_floor_2mbytes"
                / "finite_protected_sp64_numeric_sp_floor"
                / "metrics.jsonl"
            ),
        ),
        RunSpec(
            name="finite_protected_pruned_ge070_nonword",
            report=public / "v2_0_tiny_lm_context_free_ladder_pruned_ge070_nonword_2mbytes.md",
            stats=root
            / "v2_0_tiny_lm_context_free_ladder_pruned_ge070_nonword_2mbytes"
            / "encoded_stats.jsonl",
            metrics=(
                root
                / "v2_0_tiny_lm_context_free_ladder_pruned_ge070_nonword_2mbytes"
                / "finite_protected_pruned_ge070_nonword"
                / "metrics.jsonl"
            ),
        ),
        RunSpec(
            name="finite_protected_teacher_distilled_16000",
            report=public / "v2_0_tiny_lm_context_free_ladder_teacher_distilled_16000_2mbytes.md",
            stats=root
            / "v2_0_tiny_lm_context_free_ladder_teacher_distilled_16000_2mbytes"
            / "encoded_stats.jsonl",
            metrics=(
                root
                / "v2_0_tiny_lm_context_free_ladder_teacher_distilled_16000_2mbytes"
                / "finite_protected_teacher_distilled_16000"
                / "metrics.jsonl"
            ),
        ),
        RunSpec(
            name="finite_protected_teacher_distilled_2000",
            report=public / "v2_0_tiny_lm_context_free_ladder_teacher_distilled_2000_2mbytes.md",
            stats=root
            / "v2_0_tiny_lm_context_free_ladder_teacher_distilled_2000_2mbytes"
            / "encoded_stats.jsonl",
            metrics=(
                root
                / "v2_0_tiny_lm_context_free_ladder_teacher_distilled_2000_2mbytes"
                / "finite_protected_teacher_distilled_2000"
                / "metrics.jsonl"
            ),
        ),
    ]


def format_report(specs: list[RunSpec]) -> str:
    lines = [
        "# v2.0 Tiny-LM BPB Accounting Audit",
        "",
        "This audit checks whether the context-free BPB ladder is being read as",
        "a mature language-model result. It converts BPB back to implied bits per",
        "token and compares it with the uniform-vocabulary reference.",
        "",
        "Important: cross-entropy can exceed the uniform reference during early",
        "training if the random/tied-output model assigns extremely low",
        "probability to the observed token. Therefore, exceeding the uniform",
        "reference is not a mathematical impossibility. It is evidence that the",
        "2M-byte runs are still in an undertrained / early-convergence regime.",
        "",
        "## Summary",
        "",
        "| Tokenizer | Vocab | Uniform bits/token | Valid bits/token | Test bits/token | Final train bits/token | Test BPB | Test tokens/byte | Notes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for spec in specs:
        if not spec.report.exists() or not spec.stats.exists():
            lines.append(
                f"| {spec.name} |  |  |  |  |  |  |  | missing report or stats |"
            )
            continue
        row = parse_training_row(spec.report, spec.name)
        split_stats = load_split_stats(spec.stats, spec.name)
        valid_tpb = split_stats["valid"].tokens_per_byte
        test_tpb = split_stats["test"].tokens_per_byte
        uniform = math.log2(row.vocab_size)
        valid_bits = row.final_valid_bpb / valid_tpb
        test_bits = row.test_bpb / test_tpb
        train_bits = load_last_train_loss_bits(spec.metrics)
        note = (
            "above uniform; undertrained regime"
            if test_bits > uniform
            else "below uniform"
        )
        train_cell = "" if train_bits is None else f"{train_bits:.4f}"
        lines.append(
            f"| {spec.name} | {row.vocab_size} | {uniform:.4f} | "
            f"{valid_bits:.4f} | {test_bits:.4f} | {train_cell} | "
            f"{row.test_bpb:.6f} | {test_tpb:.6f} | {note} |"
        )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            "The ladder is useful as an early learning-curve calibration, but the",
            "absolute BPB endpoints should not be treated as converged tokenizer",
            "quality. The high implied bits/token values support the advisors'",
            "warning that the current 2M-byte runs mostly measure early learning",
            "speed and estimation geometry.",
            "",
            "The teacher-distilled 16k row remains interesting because its BPB is",
            "better under the same early-regime harness. However, attribution is",
            "not settled until a non-morphology matched-control score model is run.",
            "",
            "## Next Control",
            "",
            "Run a same-vocabulary self-distilled control:",
            "",
            "```text",
            "fixed SP64 vocabulary",
            "same finite protected wrapper",
            "same 16k train-line score re-estimation",
            "official SP segmentation counts instead of morphology-teacher counts",
            "```",
            "",
            "If teacher_distilled_16000 beats this matched control materially, the",
            "gain is more likely morphology-specific. If not, the BPB gain is",
            "probably score concentration / estimation geometry rather than",
            "morphology.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit tiny-LM BPB accounting.")
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_tiny_lm_context_free_ladder_bpb_accounting_audit.md",
    )
    args = parser.parse_args()

    report = format_report(default_specs())
    out = Path(args.report_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
