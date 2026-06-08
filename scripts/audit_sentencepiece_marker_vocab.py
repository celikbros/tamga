from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER  # noqa: E402


SP_WORD_STARTS = ("\u2581",)


@dataclass(frozen=True)
class MarkerVocabAudit:
    name: str
    model: Path
    vocab_size: int
    marker: str
    marker_piece_count: int
    marker_piece_rate: float
    exact_marker_count: int
    marker_with_surface_count: int
    marker_prefix_count: int
    marker_suffix_count: int
    marker_internal_count: int
    examples: list[str]


def ensure_sentencepiece():
    if importlib.util.find_spec("sentencepiece") is None:
        raise RuntimeError("sentencepiece is not installed")
    import sentencepiece as spm  # type: ignore[import-not-found]

    return spm


def visible_piece(piece: str, marker: str) -> str:
    return piece.replace(marker, "<M>")


def surface_without_marker(piece: str, marker: str) -> str:
    surface = piece.replace(marker, "")
    for prefix in SP_WORD_STARTS:
        surface = surface.replace(prefix, "")
    return surface


def audit_pieces(
    *,
    name: str,
    model: Path,
    pieces: list[str],
    marker: str,
    max_examples: int,
) -> MarkerVocabAudit:
    marker_pieces = [piece for piece in pieces if marker in piece]
    exact_marker_count = sum(1 for piece in marker_pieces if piece == marker)
    marker_with_surface_count = sum(
        1 for piece in marker_pieces if surface_without_marker(piece, marker)
    )
    marker_prefix_count = 0
    marker_suffix_count = 0
    marker_internal_count = 0
    for piece in marker_pieces:
        stripped = piece.lstrip("\u2581")
        if stripped.startswith(marker) and stripped != marker:
            marker_prefix_count += 1
        elif stripped.endswith(marker) and stripped != marker:
            marker_suffix_count += 1
        elif marker in stripped and stripped != marker:
            marker_internal_count += 1

    return MarkerVocabAudit(
        name=name,
        model=model,
        vocab_size=len(pieces),
        marker=marker,
        marker_piece_count=len(marker_pieces),
        marker_piece_rate=len(marker_pieces) / len(pieces) if pieces else 0.0,
        exact_marker_count=exact_marker_count,
        marker_with_surface_count=marker_with_surface_count,
        marker_prefix_count=marker_prefix_count,
        marker_suffix_count=marker_suffix_count,
        marker_internal_count=marker_internal_count,
        examples=[visible_piece(piece, marker) for piece in marker_pieces[:max_examples]],
    )


def audit_model(
    *,
    name: str,
    model: Path,
    marker: str,
    max_examples: int,
) -> MarkerVocabAudit:
    spm = ensure_sentencepiece()
    processor = spm.SentencePieceProcessor()
    processor.Load(str(model))
    pieces = [processor.IdToPiece(index) for index in range(processor.GetPieceSize())]
    return audit_pieces(
        name=name,
        model=model,
        pieces=pieces,
        marker=marker,
        max_examples=max_examples,
    )


def parse_model(raw: str) -> tuple[str, Path]:
    if "=" in raw:
        name, path = raw.split("=", 1)
        return name, Path(path)
    path = Path(raw)
    return path.stem, path


def format_report(rows: list[MarkerVocabAudit]) -> str:
    lines = [
        "# SentencePiece Marker Vocabulary Audit",
        "",
        "This checks whether train-only marker models learned vocabulary pieces",
        "containing the private-use soft-boundary marker. Marker-containing pieces",
        "consume vocab capacity and are not directly usable when normal encode",
        "strips markers from raw text.",
        "",
        "## Summary",
        "",
        "| Model | Vocab | Marker pieces | Marker piece rate | Exact marker | Marker+surface | Prefix | Suffix | Internal |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.name} | {row.vocab_size} | {row.marker_piece_count} | "
            f"{row.marker_piece_rate:.6f} | {row.exact_marker_count} | "
            f"{row.marker_with_surface_count} | {row.marker_prefix_count} | "
            f"{row.marker_suffix_count} | {row.marker_internal_count} |"
        )
    lines.extend(["", "## Examples", ""])
    for row in rows:
        lines.append(f"### {row.name}")
        if row.examples:
            for piece in row.examples:
                lines.append(f"- `{piece}`")
        else:
            lines.append("No marker-containing pieces.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit marker-containing SentencePiece vocab pieces.")
    parser.add_argument("--model", action="append", required=True, help="NAME=path or path")
    parser.add_argument("--marker", default=SOFT_MARKER)
    parser.add_argument("--max-examples", type=int, default=20)
    parser.add_argument("--report-out", default="artifacts/v2_0_sentencepiece_marker_vocab_audit.md")
    args = parser.parse_args(argv)

    rows = [
        audit_model(
            name=name,
            model=model,
            marker=args.marker,
            max_examples=args.max_examples,
        )
        for name, model in (parse_model(raw) for raw in args.model)
    ]
    report = format_report(rows)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
