from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.materialize_v2_candidate_serialization import (  # noqa: E402
    CandidateStats,
    materialize_candidate_serialization,
)
from scripts.materialize_v2_soft_morph_artifacts import (  # noqa: E402
    SoftMorphStats,
    materialize_soft_morph_artifacts,
)


@dataclass(frozen=True)
class SplitResult:
    split: str
    soft_stats: SoftMorphStats
    candidate_stats: CandidateStats
    boundary_jsonl: Path
    candidate_jsonl: Path
    train_view: Path


def materialize_split_views(
    *,
    split_dir: Path,
    selected_seed: Path,
    private_root: Path,
    splits: tuple[str, ...],
    progress: int,
) -> list[SplitResult]:
    results: list[SplitResult] = []
    soft_root = private_root / "v2_0_soft_morph"
    candidate_root = private_root / "v2_0_candidate"
    for split in splits:
        input_path = split_dir / f"{split}.txt"
        boundary_jsonl = soft_root / f"soft_morph_boundaries.{split}.jsonl"
        seed_out = soft_root / f"soft_morph_seed_vocab.{split}.diagnostic.tsv"
        candidate_jsonl = candidate_root / f"protected_hard_soft_morph_seeded_sp64.{split}.jsonl"
        train_view = candidate_root / f"protected_hard_soft_morph_seeded_sp64.{split}.txt"

        print(f"Materializing soft boundaries for split={split}", flush=True)
        soft_stats = materialize_soft_morph_artifacts(
            input_path=input_path,
            jsonl_out=boundary_jsonl,
            seed_out=seed_out,
            max_lines=None,
            progress=progress,
        )
        print(f"Materializing candidate serialization for split={split}", flush=True)
        candidate_stats = materialize_candidate_serialization(
            boundary_jsonl=boundary_jsonl,
            selected_seed=selected_seed,
            jsonl_out=candidate_jsonl,
            train_view_out=train_view,
            max_lines=None,
            progress=progress,
        )
        results.append(
            SplitResult(
                split=split,
                soft_stats=soft_stats,
                candidate_stats=candidate_stats,
                boundary_jsonl=boundary_jsonl,
                candidate_jsonl=candidate_jsonl,
                train_view=train_view,
            )
        )
    return results


def format_report(
    *,
    split_dir: Path,
    selected_seed: Path,
    results: list[SplitResult],
) -> str:
    lines = [
        "# v2.0 Candidate Split Views",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"Selected seed TSV: `{selected_seed.as_posix()}`",
        "",
        "This report completes Phase 1 candidate serialization for non-train",
        "splits. The selected seed policy is still train-derived; valid/test",
        "diagnostic seed TSV files are private diagnostics only.",
        "",
        "## Summary",
        "",
        "| Split | Lines | Raw bytes | Soft pieces/byte | Train-view bytes/raw byte | Hard segments/raw byte | Selected piece rate | Unselected word_start pieces | Boundary JSONL | Candidate JSONL | Train view |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for result in results:
        soft = result.soft_stats
        candidate = result.candidate_stats
        lines.append(
            f"| {result.split} | {candidate.lines} | {candidate.raw_bytes} | "
            f"{soft.pieces_per_byte:.6f} | "
            f"{candidate.train_view_bytes_per_raw_byte:.6f} | "
            f"{candidate.hard_segments_per_raw_byte:.6f} | "
            f"{candidate.selected_piece_rate:.6f} | "
            f"{candidate.unselected_word_start_pieces} | "
            f"`{result.boundary_jsonl.as_posix()}` | "
            f"`{result.candidate_jsonl.as_posix()}` | "
            f"`{result.train_view.as_posix()}` |"
        )

    lines.extend(
        [
            "",
            "## Gate",
            "",
            "The next learned-tokenizer prototype should train on the train view and",
            "measure token pressure on the valid/test train views before any tiny-LM",
            "screening.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Materialize v2.0 candidate views for valid/test splits.")
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument(
        "--selected-seed",
        default="artifacts/private/v2_0_soft_morph/protected_hard_soft_morph_seeded_sp64.selected_seed.tsv",
    )
    parser.add_argument("--private-root", default="artifacts/private")
    parser.add_argument("--split", action="append", default=[])
    parser.add_argument("--progress", type=int, default=1000)
    parser.add_argument("--report-out", default="artifacts/v2_0_candidate_split_views.md")
    args = parser.parse_args(argv)

    splits = tuple(args.split or ["valid", "test"])
    results = materialize_split_views(
        split_dir=Path(args.split_dir),
        selected_seed=Path(args.selected_seed),
        private_root=Path(args.private_root),
        splits=splits,
        progress=args.progress,
    )
    report = format_report(
        split_dir=Path(args.split_dir),
        selected_seed=Path(args.selected_seed),
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
