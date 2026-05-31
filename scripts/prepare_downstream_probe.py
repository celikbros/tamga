from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_real_tokenizers import RealBaselineSpec, encode_with_spec  # noqa: E402
from scripts.compare_tokenizers import count_words  # noqa: E402
from scripts.report_baseline_matrix import _load_toml  # noqa: E402


@dataclass(frozen=True)
class ProbeTokenizerSpec:
    name: str
    kind: str
    value: str = ""


@dataclass(frozen=True)
class ProbeConfig:
    path: Path
    corpus_path: Path
    output_dir: Path
    report_out: Path
    max_lines: int | None
    seed: int
    train_parts: int
    valid_parts: int
    test_parts: int
    write_tokenized: bool
    allow_download: bool
    tokenizers: list[ProbeTokenizerSpec]


@dataclass(frozen=True)
class CorpusSample:
    index: int
    text: str

    @property
    def byte_len(self) -> int:
        return len(self.text.encode("utf-8"))

    @property
    def char_len(self) -> int:
        return len(self.text)

    @property
    def word_count(self) -> int:
        return count_words(self.text)


@dataclass(frozen=True)
class SplitSamples:
    name: str
    samples: list[CorpusSample]

    @property
    def line_count(self) -> int:
        return len(self.samples)

    @property
    def byte_count(self) -> int:
        return sum(sample.byte_len for sample in self.samples)

    @property
    def char_count(self) -> int:
        return sum(sample.char_len for sample in self.samples)

    @property
    def word_count(self) -> int:
        return sum(sample.word_count for sample in self.samples)


@dataclass(frozen=True)
class ProbeTokenizerStats:
    tokenizer: str
    split: str
    status: str
    lines: int
    bytes: int
    words: int
    tokens: int
    max_tokens_line: int
    reason: str = ""

    @property
    def avg_tokens_line(self) -> float:
        return self.tokens / self.lines if self.lines else 0.0

    @property
    def avg_tokens_word(self) -> float:
        return self.tokens / self.words if self.words else 0.0

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.bytes if self.bytes else 0.0

    @property
    def bytes_per_token(self) -> float:
        return self.bytes / self.tokens if self.tokens else 0.0


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


def _optional_positive_int(
    settings: dict[str, Any],
    field: str,
    default: int | None,
) -> int | None:
    value = settings.get(field, default)
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"[settings] field {field!r} must be an integer")
    return value if value > 0 else None


def _default_tokenizers() -> list[ProbeTokenizerSpec]:
    return [
        ProbeTokenizerSpec(name="custom_tr_morph", kind="custom"),
        ProbeTokenizerSpec(name="unicode_char", kind="unicode_char"),
    ]


def load_probe_config(path: str | Path) -> ProbeConfig:
    config_path = Path(path)
    raw = _load_toml(config_path)
    settings = raw.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("[settings] must be a table")

    tokenizers: list[ProbeTokenizerSpec] = []
    valid_kinds = {
        "custom",
        "unicode_char",
        "toy_bpe",
        "hf",
        "sentencepiece",
        "tokenizers_json",
    }
    for item in raw.get("tokenizers", []):
        if not isinstance(item, dict) or item.get("enabled", True) is False:
            continue
        name = _string_field(item, "name", context="tokenizer")
        kind = _string_field(item, "kind", context=f"tokenizer {name}")
        if kind not in valid_kinds:
            raise ValueError(f"unknown tokenizer kind for {name}: {kind}")
        value = ""
        if kind in {"toy_bpe", "sentencepiece", "tokenizers_json"}:
            value = _string_field(item, "path", context=f"tokenizer {name}")
        elif kind == "hf":
            value = _string_field(item, "model", context=f"tokenizer {name}")
        tokenizers.append(ProbeTokenizerSpec(name=name, kind=kind, value=value))

    train_parts = _int_setting(settings, "train_parts", 8)
    valid_parts = _int_setting(settings, "valid_parts", 1)
    test_parts = _int_setting(settings, "test_parts", 1)
    if train_parts < 0 or valid_parts < 0 or test_parts < 0:
        raise ValueError("split parts must be non-negative")
    if train_parts + valid_parts + test_parts <= 0:
        raise ValueError("at least one split part must be positive")

    return ProbeConfig(
        path=config_path,
        corpus_path=Path(_string_field(settings, "corpus_path", context="settings")),
        output_dir=Path(
            settings.get("output_dir", "artifacts/private/v1_7_downstream_probe")
        ),
        report_out=Path(
            settings.get("report_out", "artifacts/v1_7_downstream_probe_prep.md")
        ),
        max_lines=_optional_positive_int(settings, "max_lines", None),
        seed=_int_setting(settings, "seed", 20260531),
        train_parts=train_parts,
        valid_parts=valid_parts,
        test_parts=test_parts,
        write_tokenized=bool(settings.get("write_tokenized", True)),
        allow_download=bool(settings.get("allow_download", False)),
        tokenizers=tokenizers or _default_tokenizers(),
    )


def load_corpus_samples(path: str | Path, *, max_lines: int | None = None) -> list[CorpusSample]:
    samples: list[CorpusSample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for index, raw_line in enumerate(handle, start=1):
            text = raw_line.strip()
            if not text:
                continue
            samples.append(CorpusSample(index=index, text=text))
            if max_lines is not None and len(samples) >= max_lines:
                break
    return samples


def split_samples(config: ProbeConfig, samples: list[CorpusSample]) -> list[SplitSamples]:
    if not samples:
        raise ValueError("corpus has no usable non-empty lines")

    shuffled = list(samples)
    random.Random(config.seed).shuffle(shuffled)
    total_parts = config.train_parts + config.valid_parts + config.test_parts
    train_count = len(shuffled) * config.train_parts // total_parts
    valid_count = len(shuffled) * config.valid_parts // total_parts
    splits = [
        SplitSamples("train", sorted(shuffled[:train_count], key=lambda sample: sample.index)),
        SplitSamples(
            "valid",
            sorted(
                shuffled[train_count : train_count + valid_count],
                key=lambda sample: sample.index,
            ),
        ),
        SplitSamples(
            "test",
            sorted(shuffled[train_count + valid_count :], key=lambda sample: sample.index),
        ),
    ]
    return [split for split in splits if split.samples]


def _safe_name(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return safe or "tokenizer"


def _real_spec(spec: ProbeTokenizerSpec) -> RealBaselineSpec:
    return RealBaselineSpec(name=spec.name, kind=spec.kind, value=spec.value)


def prepare_probe_outputs(
    config: ProbeConfig,
    *,
    max_lines_override: int | None = None,
    write_tokenized_override: bool | None = None,
) -> tuple[list[SplitSamples], list[ProbeTokenizerStats]]:
    samples = load_corpus_samples(
        config.corpus_path,
        max_lines=max_lines_override if max_lines_override is not None else config.max_lines,
    )
    splits = split_samples(config, samples)
    write_tokenized = (
        config.write_tokenized
        if write_tokenized_override is None
        else write_tokenized_override
    )
    local_files_only = not config.allow_download
    stats: list[ProbeTokenizerStats] = []

    if write_tokenized:
        config.output_dir.mkdir(parents=True, exist_ok=True)

    for tokenizer in config.tokenizers:
        real_spec = _real_spec(tokenizer)
        skipped: tuple[str, str] | None = None
        for split in splits:
            split_tokens = 0
            max_tokens_line = 0
            status = "ok"
            reason = ""
            writer = None
            if write_tokenized:
                target = config.output_dir / _safe_name(tokenizer.name) / f"{split.name}.jsonl"
                target.parent.mkdir(parents=True, exist_ok=True)
                writer = target.open("w", encoding="utf-8")

            try:
                for sample in split.samples:
                    if skipped is None:
                        encoding = encode_with_spec(
                            real_spec,
                            sample.text,
                            local_files_only=local_files_only,
                        )
                        if encoding.status != "ok":
                            skipped = (encoding.status, encoding.reason)
                    if skipped is not None:
                        status, reason = skipped
                        continue

                    token_count = len(encoding.tokens)
                    split_tokens += token_count
                    max_tokens_line = max(max_tokens_line, token_count)
                    if writer is not None:
                        writer.write(
                            json.dumps(
                                {
                                    "line_index": sample.index,
                                    "byte_len": sample.byte_len,
                                    "tokens": encoding.tokens,
                                },
                                ensure_ascii=False,
                            )
                            + "\n"
                        )
            finally:
                if writer is not None:
                    writer.close()

            stats.append(
                ProbeTokenizerStats(
                    tokenizer=tokenizer.name,
                    split=split.name,
                    status=status,
                    lines=split.line_count,
                    bytes=split.byte_count,
                    words=split.word_count,
                    tokens=split_tokens,
                    max_tokens_line=max_tokens_line,
                    reason=reason,
                )
            )

    return splits, stats


def _format_bytes(size: int) -> str:
    if size >= 1024**2:
        return f"{size / 1024**2:.2f} MiB"
    if size >= 1024:
        return f"{size / 1024:.2f} KiB"
    return f"{size} B"


def format_report(
    config: ProbeConfig,
    splits: list[SplitSamples],
    stats: list[ProbeTokenizerStats],
    *,
    wrote_tokenized: bool,
) -> str:
    lines = [
        "# v1.7 Downstream Probe Prep Report",
        "",
        f"Config: `{config.path.as_posix()}`",
        f"Corpus: `{config.corpus_path.as_posix()}`",
        f"Seed: `{config.seed}`",
        f"Split parts: `{config.train_parts}:{config.valid_parts}:{config.test_parts}`",
        f"Tokenized output dir: `{config.output_dir.as_posix()}`",
        f"Tokenized outputs written: `{wrote_tokenized}`",
        "",
        "This report prepares tokenizer inputs for a later LM probe. It does not",
        "train a model and does not report bits-per-byte yet.",
        "",
        "Public reports must not include raw corpus text or tokenized private lines.",
        "",
        "## Split Summary",
        "",
        "| Split | Lines | Bytes | Chars | Words |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for split in splits:
        lines.append(
            f"| {split.name} | {split.line_count} | {_format_bytes(split.byte_count)} | "
            f"{split.char_count} | {split.word_count} |"
        )

    lines.extend(
        [
            "",
            "## Tokenizer Prep Summary",
            "",
            "| Tokenizer | Split | Status | Lines | Bytes | Words | Tokens | Avg tokens/line | Avg tokens/word | Tokens/byte | Bytes/token | Max tokens/line | Notes |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in stats:
        lines.append(
            f"| {row.tokenizer} | {row.split} | {row.status} | {row.lines} | "
            f"{_format_bytes(row.bytes)} | {row.words} | {row.tokens} | "
            f"{row.avg_tokens_line:.4f} | {row.avg_tokens_word:.4f} | "
            f"{row.tokens_per_byte:.6f} | {row.bytes_per_token:.4f} | "
            f"{row.max_tokens_line} | {row.reason} |"
        )

    lines.extend(
        [
            "",
            "## Handoff Notes",
            "",
            "- Use the same raw split for every tokenizer run.",
            "- Compare LM runs with byte-normalized validation/test loss.",
            "- Token-level perplexity is not comparable across tokenizers by itself.",
            "- The JSONL token files are private artifacts because tokens can reconstruct private corpus text.",
            "- This prep step should be repeated after the final claim-grade corpus policy is fixed.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Prepare deterministic tokenizer inputs for a downstream LM probe.",
    )
    parser.add_argument("config")
    parser.add_argument("--max-lines", type=int, help="Override config max_lines.")
    parser.add_argument(
        "--no-write-tokenized",
        action="store_true",
        help="Write only the aggregate report, not private token JSONL files.",
    )
    args = parser.parse_args(argv)

    config = load_probe_config(args.config)
    splits, stats = prepare_probe_outputs(
        config,
        max_lines_override=args.max_lines,
        write_tokenized_override=False if args.no_write_tokenized else None,
    )
    report = format_report(
        config,
        splits,
        stats,
        wrote_tokenized=not args.no_write_tokenized and config.write_tokenized,
    )
    config.report_out.parent.mkdir(parents=True, exist_ok=True)
    config.report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {config.report_out}")
    if not args.no_write_tokenized and config.write_tokenized:
        print(f"wrote_tokenized_dir: {config.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
