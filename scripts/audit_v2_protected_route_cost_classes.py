from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    encode_protected_surface,
    load_sp_processor,
    selected_piece_strings,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.morphology import split_apostrophe_suffix_chain  # noqa: E402
from tr_tokenizer.normalizer import turkish_lower  # noqa: E402


TARGET_ROUTES = {"numeric_like", "file_like", "apostrophe_surface"}

KNOWN_FILE_EXTENSIONS = {
    "bat",
    "bin",
    "c",
    "cfg",
    "cpp",
    "cs",
    "css",
    "csv",
    "doc",
    "docx",
    "go",
    "h",
    "html",
    "java",
    "js",
    "json",
    "jsonl",
    "log",
    "md",
    "pdf",
    "php",
    "ppt",
    "pptx",
    "py",
    "r",
    "rb",
    "rs",
    "sh",
    "sql",
    "toml",
    "ts",
    "tsv",
    "txt",
    "xml",
    "yaml",
    "yml",
}

SENTENCE_START_HINTS = {
    "abstract",
    "anahtar",
    "araştırma",
    "araştırmada",
    "başlık",
    "bulgular",
    "bu",
    "conclusion",
    "gereç",
    "giriş",
    "in",
    "introduction",
    "keywords",
    "looking",
    "makale",
    "materyal",
    "methods",
    "sonuç",
    "summary",
    "the",
    "this",
    "tüm",
    "yöntem",
}

ENGLISH_APOSTROPHE_SUFFIXES = {"s", "t", "m", "d", "ll", "re", "ve"}
LEXICAL_APOSTROPHE_STEMS = {
    "kur",
    "mu",
    "ibnü",
    "işaratü",
    "sevkü",
    "te",
}
BUFFERED_APOSTROPHE_PREFIXES = ("n", "y")


@dataclass
class ClassStats:
    occurrences: int = 0
    bytes: int = 0
    protected_tokens: int = 0
    sp_tokens: int = 0
    unique_surfaces: set[str] = field(default_factory=set)

    @property
    def delta(self) -> int:
        return self.protected_tokens - self.sp_tokens

    def add(self, *, surface: str, protected_tokens: int, sp_tokens: int) -> None:
        self.occurrences += 1
        self.bytes += len(surface.encode("utf-8"))
        self.protected_tokens += protected_tokens
        self.sp_tokens += sp_tokens
        self.unique_surfaces.add(surface)


@dataclass
class AuditStats:
    lines: int = 0
    route_stats: dict[str, ClassStats] = field(default_factory=lambda: defaultdict(ClassStats))
    class_stats: dict[tuple[str, str], ClassStats] = field(
        default_factory=lambda: defaultdict(ClassStats)
    )
    examples: dict[tuple[str, str], list[dict[str, object]]] = field(
        default_factory=lambda: defaultdict(list)
    )


def _has_alpha(text: str) -> bool:
    return any(char.isalpha() for char in text)


def _has_digit(text: str) -> bool:
    return any(char.isdigit() for char in text)


def classify_numeric_like(surface: str) -> str:
    if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}", surface):
        return "iso_date"
    if re.fullmatch(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", surface):
        return "calendar_date"
    if re.fullmatch(r"\d{1,2}:\d{2}(?::\d{2})?", surface):
        return "time"
    if re.fullmatch(r"\d{4}(?:-\d{2,4})+", surface):
        return "year_range"
    if re.fullmatch(r"\d+(?:-\d+)+", surface):
        return "numeric_range_or_code"
    if re.fullmatch(r"\d+(?:/\d+)+", surface):
        return "slash_number"
    if re.fullmatch(r"\d+(?:[.,]\d+)+", surface):
        return "decimal_or_grouped_number"
    if _has_alpha(surface) and _has_digit(surface):
        if re.fullmatch(r"[A-Za-z]{1,4}\d+(?:[A-Za-z0-9]*)", surface):
            return "short_alnum_code"
        if re.fullmatch(r"\d+[A-Za-z]{1,4}", surface):
            return "number_with_unit_or_suffix"
        return "alnum_mixed_text"
    if re.fullmatch(r"\d+", surface):
        length = len(surface)
        if length == 1:
            return "plain_integer_1_digit"
        if length == 2:
            return "plain_integer_2_digit"
        if length <= 4:
            return "plain_integer_3_4_digit"
        return "plain_integer_long"
    return "other_numeric_like"


def classify_file_like(surface: str) -> str:
    lower = surface.lower()
    parts = surface.split(".")
    final = parts[-1].lower() if len(parts) > 1 else ""

    if re.fullmatch(r"\d+(?:\.\d+)?px", lower):
        return "css_px_value"
    if re.fullmatch(r"[pP]\d?[.,]\d+", surface) or re.fullmatch(
        r"[pP]\.[pP]\d+", surface
    ):
        return "statistical_p_value"
    if "." in surface and all(
        0 < len(part) <= 2 and part[:1].isupper() for part in parts
    ):
        return "dotted_abbreviation_or_version"
    if final in KNOWN_FILE_EXTENSIONS and len(parts) >= 2:
        return "known_file_extension"
    if "_" in surface:
        return "underscore_identifier"
    if "." in surface:
        after_dot = parts[-1]
        if after_dot and (
            after_dot[0].isupper() or turkish_lower(after_dot) in SENTENCE_START_HINTS
        ):
            return "glued_sentence_boundary"
        if all(0 < len(part) <= 4 for part in parts):
            return "dotted_abbreviation_or_version"
        if _has_digit(surface):
            return "dotted_version_or_measurement"
        return "dotted_compound"
    if _has_digit(surface):
        return "identifier_with_digit"
    return "other_file_like"


def _is_parseable_turkish_apostrophe_suffix(suffix: str) -> bool:
    return split_apostrophe_suffix_chain(suffix) is not None


def _is_buffered_turkish_apostrophe_suffix(suffix: str) -> bool:
    lowered = turkish_lower(suffix)
    if not lowered.startswith(BUFFERED_APOSTROPHE_PREFIXES):
        return False
    return _is_parseable_turkish_apostrophe_suffix(suffix[1:])


def classify_apostrophe_surface(surface: str) -> str:
    if "'" not in surface:
        return "no_ascii_apostrophe_unexpected"
    stem, suffix = surface.split("'", 1)
    lowered_stem = turkish_lower(stem)
    lowered_suffix = turkish_lower(suffix)

    if _is_parseable_turkish_apostrophe_suffix(suffix):
        return "turkish_suffix_parseable"
    if _is_buffered_turkish_apostrophe_suffix(suffix):
        return "turkish_buffered_suffix_candidate"
    if lowered_suffix in ENGLISH_APOSTROPHE_SUFFIXES:
        return "english_contraction_or_possessive"
    if lowered_stem in LEXICAL_APOSTROPHE_STEMS or len(stem) <= 4:
        return "lexical_transliteration_apostrophe"
    if any(char.isascii() and char.isalpha() for char in surface):
        return "foreign_or_mixed_apostrophe"
    return "other_apostrophe_surface"


def classify_surface(route: str, surface: str) -> str:
    if route == "numeric_like":
        return classify_numeric_like(surface)
    if route == "file_like":
        return classify_file_like(surface)
    if route == "apostrophe_surface":
        return classify_apostrophe_surface(surface)
    return "unsupported_route"


def audit_split(
    *,
    path: Path,
    split: str,
    processor,
    selected_pieces: list[str],
    max_lines: int | None,
    examples_per_class: int,
    progress: int,
) -> AuditStats:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    stats = AuditStats()
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            if max_lines is not None and stats.lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            stats.lines += 1
            for piece in analyze_line(text, tokenizer):
                if not piece.kind.startswith("protected:"):
                    continue
                route = piece.kind.removeprefix("protected:")
                if route not in TARGET_ROUTES:
                    continue
                protected_piece_tokens, protected_byte_tokens = encode_protected_surface(
                    piece.surface,
                    selected_pieces,
                )
                protected_tokens = protected_piece_tokens + protected_byte_tokens
                sp_tokens = len(processor.EncodeAsIds(piece.surface))
                label = classify_surface(route, piece.surface)

                stats.route_stats[route].add(
                    surface=piece.surface,
                    protected_tokens=protected_tokens,
                    sp_tokens=sp_tokens,
                )
                key = (route, label)
                stats.class_stats[key].add(
                    surface=piece.surface,
                    protected_tokens=protected_tokens,
                    sp_tokens=sp_tokens,
                )
                if len(stats.examples[key]) < examples_per_class:
                    stats.examples[key].append(
                        {
                            "split": split,
                            "line_no": line_no,
                            "route": route,
                            "class": label,
                            "surface": piece.surface,
                            "surface_codepoints": [
                                f"U+{ord(char):04X}" for char in piece.surface
                            ],
                            "protected_tokens": protected_tokens,
                            "sp_tokens": sp_tokens,
                            "text": text,
                        }
                    )
            if progress > 0 and stats.lines % progress == 0:
                count = sum(item.occurrences for item in stats.route_stats.values())
                print(
                    f"audited {split} {stats.lines:,} lines "
                    f"target_route_occurrences={count:,}",
                    flush=True,
                )
    return stats


def merge_stats(items: list[AuditStats]) -> AuditStats:
    output = AuditStats()
    for item in items:
        output.lines += item.lines
        for route, stats in item.route_stats.items():
            output.route_stats[route].occurrences += stats.occurrences
            output.route_stats[route].bytes += stats.bytes
            output.route_stats[route].protected_tokens += stats.protected_tokens
            output.route_stats[route].sp_tokens += stats.sp_tokens
            output.route_stats[route].unique_surfaces.update(stats.unique_surfaces)
        for key, stats in item.class_stats.items():
            output.class_stats[key].occurrences += stats.occurrences
            output.class_stats[key].bytes += stats.bytes
            output.class_stats[key].protected_tokens += stats.protected_tokens
            output.class_stats[key].sp_tokens += stats.sp_tokens
            output.class_stats[key].unique_surfaces.update(stats.unique_surfaces)
        for key, examples in item.examples.items():
            output.examples[key].extend(examples)
    return output


def write_examples(path: Path, stats: AuditStats, *, examples_per_class: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for key, examples in sorted(stats.examples.items()):
            for example in examples[:examples_per_class]:
                handle.write(json.dumps(example, ensure_ascii=False) + "\n")


def _fmt(value: float) -> str:
    return f"{value:.6f}"


def _stats_row(stats: ClassStats) -> str:
    token_ratio = stats.protected_tokens / stats.bytes if stats.bytes else 0.0
    sp_ratio = stats.sp_tokens / stats.bytes if stats.bytes else 0.0
    return (
        f"{stats.occurrences} | {stats.bytes} | {len(stats.unique_surfaces)} | "
        f"{stats.protected_tokens} | {stats.sp_tokens} | {stats.delta} | "
        f"{_fmt(token_ratio)} | {_fmt(sp_ratio)}"
    )


def format_report(
    *,
    split_dir: Path,
    splits: list[str],
    sp_model: Path,
    selected_pieces: Path,
    stats: AuditStats,
    examples_out: Path,
) -> str:
    lines = [
        "# v2.0 Protected Route Cost Class Audit",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"Splits: `{', '.join(splits)}`",
        f"SP model: `{sp_model.as_posix()}`",
        f"Selected protected pieces: `{selected_pieces.as_posix()}`",
        f"Private examples: `{examples_out.as_posix()}`",
        "",
        "This audit breaks the remaining high-cost finite-protected routes into",
        "actionable subclasses before changing the wrapper or starting MorphBPE",
        "work.",
        "",
        "## Route Summary",
        "",
        "| Route | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for route, item in sorted(
        stats.route_stats.items(),
        key=lambda pair: pair[1].delta,
        reverse=True,
    ):
        lines.append(f"| `{route}` | {_stats_row(item)} |")

    lines.extend(["", "## Class Summary", ""])
    for route in sorted(TARGET_ROUTES):
        lines.extend(
            [
                f"### `{route}`",
                "",
                "| Class | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        rows = [
            (key[1], value)
            for key, value in stats.class_stats.items()
            if key[0] == route
        ]
        for label, item in sorted(rows, key=lambda pair: pair[1].delta, reverse=True):
            lines.append(f"| `{label}` | {_stats_row(item)} |")
        if not rows:
            lines.append("| _none_ | 0 | 0 | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 |")
        lines.append("")

    lines.extend(
        [
            "## Interpretation Gate",
            "",
            "- `glued_sentence_boundary` and `alnum_mixed_text` point to corpus quality",
            "  or pretokenization cleanup rather than tokenizer innovation.",
            "- `turkish_buffered_suffix_candidate` points to missing apostrophe suffix",
            "  handling, not a learned-vocabulary problem.",
            "- Classes where protected tokens are much higher than SP tokens should be",
            "  optimized before constrained/MorphBPE work.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit high-cost protected route subclasses.")
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
    parser.add_argument("--examples-per-class", type=int, default=20)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument(
        "--examples-out",
        default="artifacts/private/v2_0_protected_route_cost_class_examples.jsonl",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_protected_route_cost_class_audit.md",
    )
    args = parser.parse_args(argv)

    split_dir = Path(args.split_dir)
    sp_model = Path(args.sp_model)
    selected_pieces_path = Path(args.selected_pieces)
    splits = args.split or ["train", "valid", "test"]
    processor = load_sp_processor(sp_model)
    selected = selected_piece_strings(selected_pieces_path)

    audits = [
        audit_split(
            path=split_dir / f"{split}.txt",
            split=split,
            processor=processor,
            selected_pieces=selected,
            max_lines=args.max_lines,
            examples_per_class=args.examples_per_class,
            progress=args.progress,
        )
        for split in splits
    ]
    stats = merge_stats(audits)
    examples_out = Path(args.examples_out)
    write_examples(examples_out, stats, examples_per_class=args.examples_per_class)
    report = format_report(
        split_dir=split_dir,
        splits=splits,
        sp_model=sp_model,
        selected_pieces=selected_pieces_path,
        stats=stats,
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
