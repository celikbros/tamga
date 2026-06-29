from __future__ import annotations

from dataclasses import dataclass
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_v2_finite_protected_sp64_intrinsic import load_sp_processor  # noqa: E402


SP_WORD_START = "\u2581"


@dataclass(frozen=True)
class MorphPolicyEntry:
    token: str
    surface: str
    total_count: int
    recommendation: str
    action: str
    reason: str
    soft_share: float
    hard_share: float
    exact_collision_rate: float


@dataclass(frozen=True)
class SurfaceCoverage:
    model_name: str
    token: str
    surface: str
    total_count: int
    action: str
    recommendation: str
    exact_piece: bool
    word_start_piece: bool
    standalone_piece_count: int
    standalone_pieces: tuple[str, ...]

    @property
    def has_vocab_surface(self) -> bool:
        return self.exact_piece or self.word_start_piece

    @property
    def standalone_single_piece(self) -> bool:
        return self.standalone_piece_count == 1 and (
            strip_word_start(self.standalone_pieces[0]) == self.surface
        )


@dataclass
class ModelSummary:
    model_name: str
    entries: int
    occurrences: int
    exact_piece_entries: int = 0
    exact_piece_occurrences: int = 0
    vocab_surface_entries: int = 0
    vocab_surface_occurrences: int = 0
    single_piece_entries: int = 0
    single_piece_occurrences: int = 0
    weighted_piece_count: int = 0

    @property
    def exact_piece_occurrence_share(self) -> float:
        return self.exact_piece_occurrences / self.occurrences if self.occurrences else 0.0

    @property
    def vocab_surface_occurrence_share(self) -> float:
        return self.vocab_surface_occurrences / self.occurrences if self.occurrences else 0.0

    @property
    def single_piece_occurrence_share(self) -> float:
        return self.single_piece_occurrences / self.occurrences if self.occurrences else 0.0

    @property
    def weighted_avg_piece_count(self) -> float:
        return self.weighted_piece_count / self.occurrences if self.occurrences else 0.0


def strip_word_start(piece: str) -> str:
    return piece[len(SP_WORD_START) :] if piece.startswith(SP_WORD_START) else piece


def load_policy(path: Path, *, action_filter: set[str] | None = None) -> list[MorphPolicyEntry]:
    rows: list[MorphPolicyEntry] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for raw in reader:
            action = raw["action"]
            if action_filter is not None and action not in action_filter:
                continue
            rows.append(
                MorphPolicyEntry(
                    token=raw["token"],
                    surface=raw["surface"],
                    total_count=int(raw["total_count"]),
                    recommendation=raw["recommendation"],
                    action=action,
                    reason=raw["reason"],
                    soft_share=float(raw["soft_share"]),
                    hard_share=float(raw["hard_share"]),
                    exact_collision_rate=float(raw["exact_collision_rate"]),
                )
            )
    return rows


def processor_vocab(processor) -> set[str]:
    size = int(processor.GetPieceSize())
    return {str(processor.IdToPiece(index)) for index in range(size)}


def coverage_for_entry(
    *,
    model_name: str,
    entry: MorphPolicyEntry,
    processor,
    vocab: set[str],
) -> SurfaceCoverage:
    pieces = tuple(str(piece) for piece in processor.EncodeAsPieces(entry.surface))
    return SurfaceCoverage(
        model_name=model_name,
        token=entry.token,
        surface=entry.surface,
        total_count=entry.total_count,
        action=entry.action,
        recommendation=entry.recommendation,
        exact_piece=entry.surface in vocab,
        word_start_piece=f"{SP_WORD_START}{entry.surface}" in vocab,
        standalone_piece_count=len(pieces),
        standalone_pieces=pieces,
    )


def summarize(model_name: str, rows: list[SurfaceCoverage]) -> ModelSummary:
    summary = ModelSummary(
        model_name=model_name,
        entries=len(rows),
        occurrences=sum(row.total_count for row in rows),
    )
    for row in rows:
        if row.exact_piece:
            summary.exact_piece_entries += 1
            summary.exact_piece_occurrences += row.total_count
        if row.has_vocab_surface:
            summary.vocab_surface_entries += 1
            summary.vocab_surface_occurrences += row.total_count
        if row.standalone_single_piece:
            summary.single_piece_entries += 1
            summary.single_piece_occurrences += row.total_count
        summary.weighted_piece_count += row.total_count * row.standalone_piece_count
    return summary


def write_private_rows(path: Path, rows_by_model: dict[str, list[SurfaceCoverage]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for rows in rows_by_model.values():
            for row in rows:
                handle.write(
                    json.dumps(
                        {
                            "model": row.model_name,
                            "token": row.token,
                            "surface": row.surface,
                            "total_count": row.total_count,
                            "action": row.action,
                            "recommendation": row.recommendation,
                            "exact_piece": row.exact_piece,
                            "word_start_piece": row.word_start_piece,
                            "standalone_single_piece": row.standalone_single_piece,
                            "standalone_piece_count": row.standalone_piece_count,
                            "standalone_pieces": list(row.standalone_pieces),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )


def _fmt(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def _top_uncovered(rows: list[SurfaceCoverage], *, limit: int) -> list[SurfaceCoverage]:
    return sorted(
        (row for row in rows if not row.standalone_single_piece),
        key=lambda row: row.total_count,
        reverse=True,
    )[:limit]


def _top_missing_exact(rows: list[SurfaceCoverage], *, limit: int) -> list[SurfaceCoverage]:
    return sorted(
        (row for row in rows if not row.exact_piece),
        key=lambda row: row.total_count,
        reverse=True,
    )[:limit]


def format_report(
    *,
    policy_path: Path,
    model_paths: dict[str, Path],
    rows_by_model: dict[str, list[SurfaceCoverage]],
    private_rows_out: Path,
    top_uncovered: int,
) -> str:
    summaries = [summarize(name, rows) for name, rows in rows_by_model.items()]
    lines = [
        "# v2.0 Morph Surface Vocabulary Coverage",
        "",
        f"Policy TSV: `{policy_path.as_posix()}`",
        f"Private row diagnostics: `{private_rows_out.as_posix()}`",
        "",
        "This audit separates vocabulary availability from decode preference.",
        "It does not train a tokenizer and does not use challenge labels.",
        "",
        "## Models",
        "",
        "| Model | Path |",
        "| --- | --- |",
    ]
    for name, path in model_paths.items():
        lines.append(f"| `{name}` | `{path.as_posix()}` |")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| Model | Entries | Occurrences | Exact-piece occurrence share | Vocab-surface occurrence share | Standalone-single occurrence share | Weighted avg standalone pieces |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for summary in summaries:
        lines.append(
            f"| `{summary.model_name}` | {summary.entries} | {summary.occurrences} | "
            f"{_fmt(summary.exact_piece_occurrence_share)} | "
            f"{_fmt(summary.vocab_surface_occurrence_share)} | "
            f"{_fmt(summary.single_piece_occurrence_share)} | "
            f"{_fmt(summary.weighted_avg_piece_count)} |"
        )

    for model_name, rows in rows_by_model.items():
        lines.extend(
            [
                "",
                f"## Top Not Standalone-Encoded: `{model_name}`",
                "",
                "These surfaces may still exist as exact vocab pieces. This table",
                "shows decode preference on standalone suffix strings, not strict",
                "vocab absence.",
                "",
                "| Token | Surface | Count | Action | Recommendation | Standalone pieces |",
                "| --- | --- | ---: | --- | --- | --- |",
            ]
        )
        for row in _top_uncovered(rows, limit=top_uncovered):
            pieces = " ".join(f"`{piece}`" for piece in row.standalone_pieces)
            lines.append(
                f"| `{row.token}` | `{row.surface}` | {row.total_count} | "
                f"`{row.action}` | `{row.recommendation}` | {pieces} |"
            )
        if not _top_uncovered(rows, limit=1):
            lines.append("| _none_ |  | 0 |  |  |  |")

        lines.extend(
            [
                "",
                f"## Top Missing Exact Vocab Piece: `{model_name}`",
                "",
                "| Token | Surface | Count | Action | Recommendation | Standalone pieces |",
                "| --- | --- | ---: | --- | --- | --- |",
            ]
        )
        for row in _top_missing_exact(rows, limit=top_uncovered):
            pieces = " ".join(f"`{piece}`" for piece in row.standalone_pieces)
            lines.append(
                f"| `{row.token}` | `{row.surface}` | {row.total_count} | "
                f"`{row.action}` | `{row.recommendation}` | {pieces} |"
            )
        if not _top_missing_exact(rows, limit=1):
            lines.append("| _none_ |  | 0 |  |  |  |")

    lines.extend(
        [
            "",
            "## Interpretation Gate",
            "",
            "If high-value morph surfaces already exist as exact vocab pieces,",
            "the next problem is decode preference, not vocabulary coverage. If",
            "they are not available, seed/UDS/vocab construction remains the",
            "bottleneck.",
            "",
            "`finite_protected_sp64_numeric_sp_floor` uses the same normal-text SP64",
            "vocabulary as `sp64`; numeric routing changes protected number spans,",
            "not morph surface vocabulary coverage.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit morph surface vocab coverage.")
    parser.add_argument(
        "--policy",
        default="artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv",
    )
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        help="Model spec as name=path. Defaults to sp64 and safe_uds7.",
    )
    parser.add_argument("--action", action="append", default=["seed_bias"])
    parser.add_argument("--top-uncovered", type=int, default=20)
    parser.add_argument(
        "--private-rows-out",
        default="artifacts/private/v2_0_morph_vocab_coverage.rows.jsonl",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_morph_vocab_coverage.md",
    )
    args = parser.parse_args(argv)

    if args.top_uncovered < 0:
        raise ValueError("--top-uncovered must be non-negative")

    model_specs = args.model or [
        "sp64=artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
        "safe_uds7=artifacts/private/v2_0_safe_uds/safe_uds_unigram_64000.model",
    ]
    model_paths: dict[str, Path] = {}
    for spec in model_specs:
        if "=" not in spec:
            raise ValueError(f"--model must be name=path, got {spec!r}")
        name, raw_path = spec.split("=", 1)
        if not name:
            raise ValueError(f"--model has empty name: {spec!r}")
        model_paths[name] = Path(raw_path)

    policy_path = Path(args.policy)
    entries = load_policy(policy_path, action_filter=set(args.action) if args.action else None)
    rows_by_model: dict[str, list[SurfaceCoverage]] = {}
    for name, path in model_paths.items():
        processor = load_sp_processor(path)
        vocab = processor_vocab(processor)
        rows_by_model[name] = [
            coverage_for_entry(
                model_name=name,
                entry=entry,
                processor=processor,
                vocab=vocab,
            )
            for entry in entries
        ]

    private_rows_out = Path(args.private_rows_out)
    write_private_rows(private_rows_out, rows_by_model)
    report = format_report(
        policy_path=policy_path,
        model_paths=model_paths,
        rows_by_model=rows_by_model,
        private_rows_out=private_rows_out,
        top_uncovered=args.top_uncovered,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_private_rows: {private_rows_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
