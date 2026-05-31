from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import re
import string
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_tokenizer import load_cases  # noqa: E402
from scripts.report_baseline_matrix import _load_toml  # noqa: E402


@dataclass(frozen=True)
class CorpusSource:
    name: str
    path: Path
    format: str
    text_field: str = "text"


@dataclass(frozen=True)
class EvalSet:
    name: str
    path: Path


@dataclass(frozen=True)
class ClaimGradeCorpusConfig:
    path: Path
    output_path: Path
    manifest_out: Path
    leakage_out: Path
    max_output_lines: int
    ngram_size: int
    normalize_lowercase: bool
    strip_punctuation: bool
    min_chars: int
    max_chars: int | None
    max_utf8_bytes: int | None
    drop_control_chars: bool
    drop_replacement_char: bool
    drop_mojibake_suspects: bool
    dedupe_exact: bool
    dedupe_normalized: bool
    sources: list[CorpusSource]
    eval_sets: list[EvalSet]


@dataclass(frozen=True)
class SourceStats:
    name: str
    path: Path
    format: str
    bytes: int
    scanned_lines: int
    usable_texts: int
    exact_leaks: int
    normalized_leaks: int
    ngram_leaks: int
    filtered_short: int
    filtered_long: int
    filtered_bytes: int
    filtered_control: int
    filtered_replacement: int
    filtered_mojibake: int
    duplicate_exact: int
    duplicate_normalized: int
    written_lines: int
    truncated: bool


MOJIBAKE_MARKERS = ("Ã", "Ä", "Å", "â€", "ðŸ", "\ufffd")


def _string_field(item: dict[str, Any], field: str, *, context: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} requires string field {field!r}")
    return value


def _int_setting(settings: dict[str, Any], field: str, default: int) -> int:
    value = settings.get(field, default)
    if not isinstance(value, int):
        raise ValueError(f"[settings] field {field!r} must be an integer")
    return value


def _optional_int_setting(
    settings: dict[str, Any],
    field: str,
    default: int | None,
) -> int | None:
    value = settings.get(field, default)
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"[settings] field {field!r} must be an integer")
    if value <= 0:
        return None
    return value


def load_claim_grade_corpus_config(path: str | Path) -> ClaimGradeCorpusConfig:
    config_path = Path(path)
    raw = _load_toml(config_path)
    settings = raw.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("[settings] must be a table")

    sources: list[CorpusSource] = []
    for item in raw.get("sources", []):
        if not isinstance(item, dict) or item.get("enabled", True) is False:
            continue
        name = _string_field(item, "name", context="source")
        format_name = _string_field(item, "format", context=f"source {name}")
        if format_name not in {"text", "jsonl"}:
            raise ValueError(f"source {name} has unsupported format: {format_name}")
        sources.append(
            CorpusSource(
                name=name,
                path=Path(_string_field(item, "path", context=f"source {name}")),
                format=format_name,
                text_field=str(item.get("text_field", "text")),
            )
        )

    eval_sets: list[EvalSet] = []
    for item in raw.get("eval_sets", []):
        if not isinstance(item, dict):
            raise ValueError("[[eval_sets]] entries must be tables")
        name = _string_field(item, "name", context="eval_set")
        eval_sets.append(
            EvalSet(
                name=name,
                path=Path(_string_field(item, "path", context=f"eval_set {name}")),
            )
        )

    return ClaimGradeCorpusConfig(
        path=config_path,
        output_path=Path(
            settings.get("output_path", "data/train/claim_grade/corpus.txt")
        ),
        manifest_out=Path(
            settings.get("manifest_out", "artifacts/v1_7_claim_grade_corpus_manifest.md")
        ),
        leakage_out=Path(
            settings.get("leakage_out", "artifacts/v1_7_claim_grade_leakage_report.md")
        ),
        max_output_lines=_int_setting(settings, "max_output_lines", 100000),
        ngram_size=_int_setting(settings, "ngram_size", 8),
        normalize_lowercase=bool(settings.get("normalize_lowercase", False)),
        strip_punctuation=bool(settings.get("strip_punctuation", True)),
        min_chars=_int_setting(settings, "min_chars", 0),
        max_chars=_optional_int_setting(settings, "max_chars", None),
        max_utf8_bytes=_optional_int_setting(settings, "max_utf8_bytes", None),
        drop_control_chars=bool(settings.get("drop_control_chars", False)),
        drop_replacement_char=bool(settings.get("drop_replacement_char", False)),
        drop_mojibake_suspects=bool(settings.get("drop_mojibake_suspects", False)),
        dedupe_exact=bool(settings.get("dedupe_exact", False)),
        dedupe_normalized=bool(settings.get("dedupe_normalized", False)),
        sources=sources,
        eval_sets=eval_sets,
    )


def normalize_for_leakage(
    text: str,
    *,
    lowercase: bool,
    strip_punctuation: bool,
) -> str:
    normalized = unicodedata.normalize("NFC", text)
    if lowercase:
        # Disabled by default because Turkic I/i/İ/ı can be misleading.
        normalized = normalized.casefold()
    if strip_punctuation:
        translation = str.maketrans("", "", string.punctuation)
        normalized = normalized.translate(translation)
        normalized = "".join(
            char for char in normalized if not unicodedata.category(char).startswith("P")
        )
    return re.sub(r"\s+", " ", normalized).strip()


def word_ngrams(text: str, *, ngram_size: int) -> set[str]:
    words = text.split()
    if len(words) < ngram_size:
        return set()
    return {
        " ".join(words[index : index + ngram_size])
        for index in range(0, len(words) - ngram_size + 1)
    }


def has_control_chars(text: str) -> bool:
    return any(
        unicodedata.category(char) in {"Cc", "Cf"} and char not in "\t\n\r"
        for char in text
    )


def has_mojibake_marker(text: str) -> bool:
    return any(marker in text for marker in MOJIBAKE_MARKERS)


def _iter_source_texts(source: CorpusSource) -> Iterator[str]:
    with source.path.open("r", encoding="utf-8") as handle:
        if source.format == "text":
            for line in handle:
                text = line.strip()
                if text:
                    yield text
        elif source.format == "jsonl":
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = item.get(source.text_field, "")
                if isinstance(text, str) and text.strip():
                    yield text.strip()
        else:  # pragma: no cover - guarded by config loading.
            raise ValueError(f"unsupported source format: {source.format}")


def _load_eval_texts(config: ClaimGradeCorpusConfig) -> list[str]:
    texts: list[str] = []
    for eval_set in config.eval_sets:
        texts.extend(case.text for case in load_cases(eval_set.path))
    return texts


def prepare_corpus(
    config: ClaimGradeCorpusConfig,
    *,
    manifest_only: bool = False,
    max_scan_lines: int | None = None,
) -> tuple[list[SourceStats], list[str]]:
    eval_texts = _load_eval_texts(config)
    exact_eval = {text.strip() for text in eval_texts if text.strip()}
    normalized_eval = {
        normalize_for_leakage(
            text,
            lowercase=config.normalize_lowercase,
            strip_punctuation=config.strip_punctuation,
        )
        for text in eval_texts
        if text.strip()
    }
    eval_ngrams: set[str] = set()
    for text in normalized_eval:
        eval_ngrams.update(word_ngrams(text, ngram_size=config.ngram_size))

    written_total = 0
    leakage_examples: list[str] = []
    stats: list[SourceStats] = []
    exact_seen: set[str] = set()
    normalized_seen: set[str] = set()
    output_handle = None
    if not manifest_only:
        config.output_path.parent.mkdir(parents=True, exist_ok=True)
        output_handle = config.output_path.open("w", encoding="utf-8")

    try:
        for source in config.sources:
            scanned = usable = exact = normalized = ngram = written = 0
            short = long = bytes_long = control = replacement = mojibake = 0
            duplicate_exact = duplicate_normalized = 0
            truncated = False
            for text in _iter_source_texts(source):
                scanned += 1
                if max_scan_lines is not None and scanned > max_scan_lines:
                    truncated = True
                    break

                usable += 1
                normalized_text = normalize_for_leakage(
                    text,
                    lowercase=config.normalize_lowercase,
                    strip_punctuation=config.strip_punctuation,
                )

                if len(text) < config.min_chars:
                    short += 1
                    continue
                if config.max_chars is not None and len(text) > config.max_chars:
                    long += 1
                    continue
                if (
                    config.max_utf8_bytes is not None
                    and len(text.encode("utf-8")) > config.max_utf8_bytes
                ):
                    bytes_long += 1
                    continue
                if config.drop_control_chars and has_control_chars(text):
                    control += 1
                    continue
                if config.drop_replacement_char and "\ufffd" in text:
                    replacement += 1
                    continue
                if config.drop_mojibake_suspects and has_mojibake_marker(text):
                    mojibake += 1
                    continue
                if config.dedupe_exact and text in exact_seen:
                    duplicate_exact += 1
                    continue
                if config.dedupe_exact:
                    exact_seen.add(text)
                if config.dedupe_normalized and normalized_text in normalized_seen:
                    duplicate_normalized += 1
                    continue
                if config.dedupe_normalized:
                    normalized_seen.add(normalized_text)

                exact_hit = text in exact_eval
                normalized_hit = normalized_text in normalized_eval
                ngram_hit = bool(
                    eval_ngrams
                    and word_ngrams(normalized_text, ngram_size=config.ngram_size)
                    & eval_ngrams
                )

                if exact_hit:
                    exact += 1
                if normalized_hit:
                    normalized += 1
                if ngram_hit:
                    ngram += 1
                if exact_hit or normalized_hit or ngram_hit:
                    if len(leakage_examples) < 20:
                        leakage_examples.append(f"{source.name}: {text[:220]}")
                    continue

                if (
                    output_handle is not None
                    and written_total < config.max_output_lines
                ):
                    output_handle.write(text + "\n")
                    written += 1
                    written_total += 1

            stats.append(
                SourceStats(
                    name=source.name,
                    path=source.path,
                    format=source.format,
                    bytes=source.path.stat().st_size if source.path.exists() else 0,
                    scanned_lines=scanned,
                    usable_texts=usable,
                    exact_leaks=exact,
                    normalized_leaks=normalized,
                    ngram_leaks=ngram,
                    filtered_short=short,
                    filtered_long=long,
                    filtered_bytes=bytes_long,
                    filtered_control=control,
                    filtered_replacement=replacement,
                    filtered_mojibake=mojibake,
                    duplicate_exact=duplicate_exact,
                    duplicate_normalized=duplicate_normalized,
                    written_lines=written,
                    truncated=truncated,
                )
            )
    finally:
        if output_handle is not None:
            output_handle.close()

    return stats, leakage_examples


def _format_bytes(size: int) -> str:
    if size >= 1024**3:
        return f"{size / 1024**3:.2f} GiB"
    if size >= 1024**2:
        return f"{size / 1024**2:.2f} MiB"
    return f"{size} B"


def format_manifest(
    config: ClaimGradeCorpusConfig,
    stats: list[SourceStats],
    *,
    manifest_only: bool,
) -> str:
    lines = [
        "# v1.7 Claim-Grade Corpus Manifest",
        "",
        f"Config: `{config.path.as_posix()}`",
        f"Output path: `{config.output_path.as_posix()}`",
        f"Mode: `{'manifest-only' if manifest_only else 'prepare-sample'}`",
        f"Min chars: `{config.min_chars}`",
        f"Max chars: `{config.max_chars if config.max_chars is not None else 'none'}`",
        f"Max UTF-8 bytes: `{config.max_utf8_bytes if config.max_utf8_bytes is not None else 'none'}`",
        f"Drop control chars: `{config.drop_control_chars}`",
        f"Drop replacement char: `{config.drop_replacement_char}`",
        f"Drop mojibake suspects: `{config.drop_mojibake_suspects}`",
        f"Dedupe exact: `{config.dedupe_exact}`",
        f"Dedupe normalized: `{config.dedupe_normalized}`",
        "",
        "Large corpus text is private/local and must not be committed to git.",
        "",
        "## Sources",
        "",
        "| Source | Format | Bytes | Scanned | Usable | Filtered | Duplicates | Written | Truncated |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in stats:
        filtered = (
            row.filtered_short
            + row.filtered_long
            + row.filtered_bytes
            + row.filtered_control
            + row.filtered_replacement
            + row.filtered_mojibake
        )
        duplicates = row.duplicate_exact + row.duplicate_normalized
        lines.append(
            f"| {row.name} | {row.format} | {_format_bytes(row.bytes)} | "
            f"{row.scanned_lines} | {row.usable_texts} | {filtered} | "
            f"{duplicates} | {row.written_lines} | {row.truncated} |"
        )
    lines.extend(
        [
            "",
            "## Filter Details",
            "",
            "| Source | Short | Long chars | Long bytes | Control | Replacement | Mojibake | Exact dup | Normalized dup |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in stats:
        lines.append(
            f"| {row.name} | {row.filtered_short} | "
            f"{row.filtered_long} | {row.filtered_bytes} | "
            f"{row.filtered_control} | {row.filtered_replacement} | "
            f"{row.filtered_mojibake} | {row.duplicate_exact} | "
            f"{row.duplicate_normalized} |"
        )
    return "\n".join(lines) + "\n"


def format_leakage_report(
    config: ClaimGradeCorpusConfig,
    stats: list[SourceStats],
    examples: list[str],
) -> str:
    lines = [
        "# v1.7 Claim-Grade Corpus Leakage Report",
        "",
        f"Config: `{config.path.as_posix()}`",
        f"Eval sets: {', '.join(eval_set.name for eval_set in config.eval_sets)}",
        f"N-gram size: `{config.ngram_size}`",
        f"Lowercase normalization: `{config.normalize_lowercase}`",
        f"Strip punctuation: `{config.strip_punctuation}`",
        "",
        "## Summary",
        "",
        "| Source | Exact | Normalized | N-gram |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in stats:
        lines.append(
            f"| {row.name} | {row.exact_leaks} | {row.normalized_leaks} | "
            f"{row.ngram_leaks} |"
        )

    lines.extend(["", "## Example Hits", ""])
    if examples:
        for example in examples:
            lines.append(f"- {example}")
    else:
        lines.append("No leakage examples captured.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Prepare local claim-grade corpus samples and leakage reports.",
    )
    parser.add_argument("config")
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Scan sources and write reports without writing output corpus text.",
    )
    parser.add_argument(
        "--max-scan-lines",
        type=int,
        help="Limit scanned lines per source for quick smoke checks.",
    )
    args = parser.parse_args(argv)

    config = load_claim_grade_corpus_config(args.config)
    stats, examples = prepare_corpus(
        config,
        manifest_only=args.manifest_only,
        max_scan_lines=args.max_scan_lines,
    )

    config.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    config.manifest_out.write_text(
        format_manifest(config, stats, manifest_only=args.manifest_only),
        encoding="utf-8",
    )
    config.leakage_out.parent.mkdir(parents=True, exist_ok=True)
    config.leakage_out.write_text(
        format_leakage_report(config, stats, examples),
        encoding="utf-8",
    )

    print(f"wrote_manifest: {config.manifest_out}")
    print(f"wrote_leakage: {config.leakage_out}")
    if not args.manifest_only:
        print(f"wrote_corpus: {config.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
