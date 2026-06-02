from __future__ import annotations

from dataclasses import dataclass
import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.report_baseline_matrix import _load_toml  # noqa: E402


@dataclass(frozen=True)
class CandidateSPConfig:
    path: Path
    candidate_name: str
    train_view: Path
    valid_view: Path
    test_view: Path
    model_prefix: Path
    model_type: str
    vocab_size: int
    report_out: Path
    normalization_rule_name: str
    character_coverage: float
    hard_vocab_limit: bool
    split_by_whitespace: bool
    remove_extra_whitespaces: bool
    train_extremely_large_corpus: bool
    max_sentence_length: int

    @property
    def model_path(self) -> Path:
        return self.model_prefix.with_suffix(".model")

    @property
    def vocab_path(self) -> Path:
        return self.model_prefix.with_suffix(".vocab")


@dataclass(frozen=True)
class ViewStats:
    split: str
    lines: int
    raw_bytes: int
    view_bytes: int
    sp_tokens: int

    @property
    def sp_tokens_per_view_byte(self) -> float:
        return self.sp_tokens / self.view_bytes if self.view_bytes else 0.0

    @property
    def sp_tokens_per_raw_byte(self) -> float:
        return self.sp_tokens / self.raw_bytes if self.raw_bytes else 0.0

    @property
    def view_bytes_per_raw_byte(self) -> float:
        return self.view_bytes / self.raw_bytes if self.raw_bytes else 0.0


def _string_field(settings: dict[str, Any], field: str) -> str:
    value = settings.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"[settings] requires string field {field!r}")
    return value


def load_config(path: str | Path) -> CandidateSPConfig:
    config_path = Path(path)
    raw = _load_toml(config_path)
    settings = raw.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("[settings] must be a table")
    return CandidateSPConfig(
        path=config_path,
        candidate_name=_string_field(settings, "candidate_name"),
        train_view=Path(_string_field(settings, "train_view")),
        valid_view=Path(_string_field(settings, "valid_view")),
        test_view=Path(_string_field(settings, "test_view")),
        model_prefix=Path(_string_field(settings, "model_prefix")),
        model_type=_string_field(settings, "model_type"),
        vocab_size=int(settings.get("vocab_size", 64000)),
        report_out=Path(_string_field(settings, "report_out")),
        normalization_rule_name=str(settings.get("normalization_rule_name", "identity")),
        character_coverage=float(settings.get("character_coverage", 1.0)),
        hard_vocab_limit=bool(settings.get("hard_vocab_limit", False)),
        split_by_whitespace=bool(settings.get("split_by_whitespace", True)),
        remove_extra_whitespaces=bool(settings.get("remove_extra_whitespaces", False)),
        train_extremely_large_corpus=bool(settings.get("train_extremely_large_corpus", False)),
        max_sentence_length=int(settings.get("max_sentence_length", 16384)),
    )


def ensure_sentencepiece():
    if importlib.util.find_spec("sentencepiece") is None:
        raise RuntimeError("sentencepiece is not installed")
    import sentencepiece as spm  # type: ignore[import-not-found]

    return spm


def train_model(config: CandidateSPConfig, *, force: bool) -> None:
    spm = ensure_sentencepiece()
    if config.model_path.exists() and not force:
        print(f"model_exists: {config.model_path}")
        return
    config.model_prefix.parent.mkdir(parents=True, exist_ok=True)
    print(
        "Training SentencePiece candidate: "
        f"input={config.train_view} model_type={config.model_type} vocab_size={config.vocab_size}"
    )
    spm.SentencePieceTrainer.train(
        input=str(config.train_view),
        model_prefix=str(config.model_prefix),
        vocab_size=config.vocab_size,
        model_type=config.model_type,
        normalization_rule_name=config.normalization_rule_name,
        character_coverage=config.character_coverage,
        hard_vocab_limit=config.hard_vocab_limit,
        split_by_whitespace=config.split_by_whitespace,
        remove_extra_whitespaces=config.remove_extra_whitespaces,
        train_extremely_large_corpus=config.train_extremely_large_corpus,
        max_sentence_length=config.max_sentence_length,
    )
    print(f"wrote_model: {config.model_path}")
    print(f"wrote_vocab: {config.vocab_path}")


def count_view(
    *,
    processor,
    split: str,
    view_path: Path,
    raw_bytes: int | None,
) -> ViewStats:
    lines = 0
    view_bytes = 0
    sp_tokens = 0
    with view_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            text = raw_line.rstrip("\n")
            lines += 1
            view_bytes += len(text.encode("utf-8"))
            sp_tokens += len(processor.EncodeAsIds(text))
    return ViewStats(
        split=split,
        lines=lines,
        raw_bytes=raw_bytes if raw_bytes is not None else view_bytes,
        view_bytes=view_bytes,
        sp_tokens=sp_tokens,
    )


def raw_bytes_from_candidate_jsonl(path: Path) -> int | None:
    jsonl = path.with_suffix(".jsonl")
    if not jsonl.exists():
        return None
    import json

    total = 0
    with jsonl.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            item = json.loads(raw_line)
            total += len(item["text"].encode("utf-8"))
    return total


def evaluate_model(config: CandidateSPConfig) -> list[ViewStats]:
    spm = ensure_sentencepiece()
    processor = spm.SentencePieceProcessor()
    processor.Load(str(config.model_path))
    print(f"Loaded model: {config.model_path}")
    rows = []
    for split, view_path in (
        ("train", config.train_view),
        ("valid", config.valid_view),
        ("test", config.test_view),
    ):
        print(f"Evaluating split={split} view={view_path}")
        row = count_view(
            processor=processor,
            split=split,
            view_path=view_path,
            raw_bytes=raw_bytes_from_candidate_jsonl(view_path),
        )
        print(
            f"Evaluated split={split} lines={row.lines} sp_tokens={row.sp_tokens} "
            f"tokens/raw_byte={row.sp_tokens_per_raw_byte:.6f}"
        )
        rows.append(row)
    return rows


def format_report(config: CandidateSPConfig, rows: list[ViewStats]) -> str:
    lines = [
        "# v2.0 Candidate SentencePiece Probe",
        "",
        f"Candidate: `{config.candidate_name}`",
        f"Config: `{config.path.as_posix()}`",
        f"Model: `{config.model_path.as_posix()}`",
        "",
        "This is an intrinsic learned-tokenizer probe, not an LLM result.",
        "SentencePiece trains on the serialized train view. Candidate metadata,",
        "when present, is diagnostic and is not enforced as SentencePiece",
        "user-defined symbols in this first probe.",
        "",
        "## Model Settings",
        "",
        "| Setting | Value |",
        "| --- | ---: |",
        f"| model_type | {config.model_type} |",
        f"| vocab_size | {config.vocab_size} |",
        f"| split_by_whitespace | {config.split_by_whitespace} |",
        f"| remove_extra_whitespaces | {config.remove_extra_whitespaces} |",
        f"| max_sentence_length | {config.max_sentence_length} |",
        "",
        "## Token Pressure",
        "",
        "| Split | Lines | Raw bytes | View bytes | View/raw bytes | SP tokens | SP tokens/view byte | SP tokens/raw byte |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.split} | {row.lines} | {row.raw_bytes} | {row.view_bytes} | "
            f"{row.view_bytes_per_raw_byte:.6f} | {row.sp_tokens} | "
            f"{row.sp_tokens_per_view_byte:.6f} | {row.sp_tokens_per_raw_byte:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "Compare valid/test `SP tokens/raw byte` against:",
            "",
            "```text",
            "SP64 baseline valid/test: ~0.1566 / ~0.1570 tokens/raw byte",
            "custom lossless+64k byte fallback valid/test: ~0.4162 / ~0.4194 tokens/raw byte",
            "candidate hard segment floor valid/test: ~0.1307 / ~0.1306 segments/raw byte",
            "```",
            "",
            "The candidate is worth intrinsic evaluation only if it is much closer",
            "to SP64 than to pure custom lossless pressure.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Train/evaluate v2.0 candidate SentencePiece prototype.")
    parser.add_argument("config")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-train", action="store_true")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    if not args.no_train:
        train_model(config, force=args.force)
    rows = evaluate_model(config)
    report = format_report(config, rows)
    config.report_out.parent.mkdir(parents=True, exist_ok=True)
    config.report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {config.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
