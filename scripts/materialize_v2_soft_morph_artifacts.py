from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.pretok import (  # noqa: E402
    is_apostrophe_surface_token,
    is_arabic_word,
    is_azerbaijani_specific_word,
    is_cyrillic_word,
    is_file_like_token,
    is_greek_word,
    is_non_turkish_latin_word,
    is_numeric_like_token,
    is_percent_encoded_token,
    is_technical_comparator_token,
    is_url_like_token,
    is_uzbek_apostrophe_word,
)
from tr_tokenizer.tokenizer import WORD_START  # noqa: E402


PROTECTED_KIND_CHECKS = (
    ("url", is_url_like_token),
    ("uzbek_apostrophe_word", is_uzbek_apostrophe_word),
    ("azerbaijani_word", is_azerbaijani_specific_word),
    ("cyrillic_word", is_cyrillic_word),
    ("arabic_word", is_arabic_word),
    ("greek_word", is_greek_word),
    ("non_turkish_latin_word", is_non_turkish_latin_word),
    ("apostrophe_surface", is_apostrophe_surface_token),
    ("file_like", is_file_like_token),
    ("numeric_like", is_numeric_like_token),
    ("percent_encoded", is_percent_encoded_token),
    ("technical_comparator", is_technical_comparator_token),
)


@dataclass(frozen=True)
class Piece:
    token: str
    surface: str
    kind: str
    boundary_before: str


@dataclass(frozen=True)
class SoftMorphStats:
    lines: int
    bytes: int
    pieces: int
    seed_tokens: int
    unique_seed_tokens: int
    soft_boundaries: int
    hard_boundaries: int
    whitespace_pieces: int
    protected_pieces: int
    suffix_pieces: int
    max_pieces_line: int

    @property
    def pieces_per_byte(self) -> float:
        return self.pieces / self.bytes if self.bytes else 0.0

    @property
    def avg_pieces_line(self) -> float:
        return self.pieces / self.lines if self.lines else 0.0


def source_surface(token: str) -> str:
    if token.startswith(WORD_START) and len(token) > len(WORD_START):
        return token[len(WORD_START) :]
    if token.startswith("+") and len(token) > 1:
        return token[1:]
    return token


def protected_kind(surface: str) -> str | None:
    for kind, check in PROTECTED_KIND_CHECKS:
        if check(surface):
            return kind
    return None


def classify_token(token: str, previous_token: str | None) -> Piece:
    surface = source_surface(token)

    if token.isspace():
        return Piece(token=token, surface=surface, kind="whitespace", boundary_before="hard")

    if token == "'":
        return Piece(token=token, surface=surface, kind="apostrophe", boundary_before="hard")

    if token.startswith("+") and len(token) > 1:
        boundary = "hard" if previous_token == "'" else "soft"
        return Piece(token=token, surface=surface, kind="suffix", boundary_before=boundary)

    kind = protected_kind(surface)
    if kind is not None:
        return Piece(
            token=token,
            surface=surface,
            kind=f"protected:{kind}",
            boundary_before="hard",
        )

    if token.startswith(WORD_START) and len(token) > len(WORD_START):
        return Piece(token=token, surface=surface, kind="word_start", boundary_before="hard")

    return Piece(token=token, surface=surface, kind="punct_or_symbol", boundary_before="hard")


def analyze_line(text: str, tokenizer: TurkishTokenizer) -> list[Piece]:
    pieces: list[Piece] = []
    previous: str | None = None
    for token in tokenizer.encode(text):
        piece = classify_token(token, previous)
        pieces.append(piece)
        previous = token
    return pieces


def materialize_soft_morph_artifacts(
    *,
    input_path: Path,
    jsonl_out: Path,
    seed_out: Path,
    max_lines: int | None,
    progress: int,
) -> SoftMorphStats:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    seed_counts: Counter[str] = Counter()
    lines = 0
    total_bytes = 0
    total_pieces = 0
    soft_boundaries = 0
    hard_boundaries = 0
    whitespace_pieces = 0
    protected_pieces = 0
    suffix_pieces = 0
    max_pieces_line = 0

    jsonl_out.parent.mkdir(parents=True, exist_ok=True)
    seed_out.parent.mkdir(parents=True, exist_ok=True)

    with (
        input_path.open("r", encoding="utf-8") as source,
        jsonl_out.open("w", encoding="utf-8", newline="\n") as target,
    ):
        for raw_line in source:
            if max_lines is not None and lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            pieces = analyze_line(text, tokenizer)

            target.write(
                json.dumps(
                    {
                        "text": text,
                        "pieces": [
                            {
                                "token": piece.token,
                                "surface": piece.surface,
                                "kind": piece.kind,
                                "boundary_before": piece.boundary_before,
                            }
                            for piece in pieces
                        ],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

            lines += 1
            total_bytes += len(text.encode("utf-8"))
            total_pieces += len(pieces)
            max_pieces_line = max(max_pieces_line, len(pieces))

            for piece in pieces:
                if piece.kind != "whitespace":
                    seed_counts[piece.token] += 1
                if piece.boundary_before == "soft":
                    soft_boundaries += 1
                elif piece.boundary_before == "hard":
                    hard_boundaries += 1
                if piece.kind == "whitespace":
                    whitespace_pieces += 1
                if piece.kind.startswith("protected:"):
                    protected_pieces += 1
                if piece.kind == "suffix":
                    suffix_pieces += 1

            if progress > 0 and lines % progress == 0:
                print(
                    f"materialized {lines:,} lines "
                    f"pieces={total_pieces:,} soft={soft_boundaries:,} hard={hard_boundaries:,}",
                    flush=True,
                )

    with seed_out.open("w", encoding="utf-8", newline="\n") as seed_file:
        seed_file.write("token\tcount\n")
        for token, count in seed_counts.most_common():
            seed_file.write(f"{token}\t{count}\n")

    return SoftMorphStats(
        lines=lines,
        bytes=total_bytes,
        pieces=total_pieces,
        seed_tokens=sum(seed_counts.values()),
        unique_seed_tokens=len(seed_counts),
        soft_boundaries=soft_boundaries,
        hard_boundaries=hard_boundaries,
        whitespace_pieces=whitespace_pieces,
        protected_pieces=protected_pieces,
        suffix_pieces=suffix_pieces,
        max_pieces_line=max_pieces_line,
    )


def format_report(
    *,
    input_path: Path,
    jsonl_out: Path,
    seed_out: Path,
    stats: SoftMorphStats,
    max_lines: int | None,
) -> str:
    return "\n".join(
        [
            "# v2.0 Soft Morph Artifact Materialization",
            "",
            f"Input: `{input_path.as_posix()}`",
            f"JSONL output: `{jsonl_out.as_posix()}`",
            f"Seed output: `{seed_out.as_posix()}`",
            f"Max lines: `{max_lines if max_lines is not None else 'all'}`",
            "",
            "This is a prototype artifact, not a production tokenizer. It records",
            "custom morphology boundaries as soft hints while treating whitespace,",
            "punctuation, apostrophes, script guards, and protected spans as hard",
            "boundaries for later learned-vocabulary experiments.",
            "",
            "## Summary",
            "",
            "| Lines | Bytes | Pieces | Pieces/byte | Avg pieces/line | Seed tokens | Unique seed tokens | Soft boundaries | Hard boundaries | Whitespace pieces | Protected pieces | Suffix pieces | Max pieces/line |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| {stats.lines} | {stats.bytes} | {stats.pieces} | "
                f"{stats.pieces_per_byte:.6f} | {stats.avg_pieces_line:.4f} | "
                f"{stats.seed_tokens} | {stats.unique_seed_tokens} | "
                f"{stats.soft_boundaries} | {stats.hard_boundaries} | "
                f"{stats.whitespace_pieces} | {stats.protected_pieces} | "
                f"{stats.suffix_pieces} | {stats.max_pieces_line} |"
            ),
            "",
            "## Boundary Meaning",
            "",
            "- `soft`: morphology-proposed boundary; learned merges may cross it.",
            "- `hard`: whitespace/protected/punctuation/script boundary; learned merges should not cross it in protected-aware candidates.",
            "",
            "## Next Use",
            "",
            "Use the JSONL to prototype soft-boundary learning or seeded-vocabulary",
            "training. Use the seed TSV to inspect the actual custom pieces and",
            "their frequencies before deciding which pieces should be seeded.",
        ]
    ) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Materialize v2.0 soft-morph/protected-hard prototype artifacts.",
    )
    parser.add_argument(
        "--input",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt",
    )
    parser.add_argument(
        "--jsonl-out",
        default="artifacts/private/v2_0_soft_morph/soft_morph_boundaries.train.jsonl",
    )
    parser.add_argument(
        "--seed-out",
        default="artifacts/private/v2_0_soft_morph/soft_morph_seed_vocab.train.tsv",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_soft_morph_materialization.md",
    )
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--progress", type=int, default=1000)
    args = parser.parse_args(argv)

    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")

    input_path = Path(args.input)
    jsonl_out = Path(args.jsonl_out)
    seed_out = Path(args.seed_out)
    report_out = Path(args.report_out)

    stats = materialize_soft_morph_artifacts(
        input_path=input_path,
        jsonl_out=jsonl_out,
        seed_out=seed_out,
        max_lines=args.max_lines,
        progress=args.progress,
    )
    report = format_report(
        input_path=input_path,
        jsonl_out=jsonl_out,
        seed_out=seed_out,
        stats=stats,
        max_lines=args.max_lines,
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_jsonl: {jsonl_out}")
    print(f"wrote_seed: {seed_out}")
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
