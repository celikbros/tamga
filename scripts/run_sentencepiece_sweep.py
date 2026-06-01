from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_real_tokenizers import (  # noqa: E402
    RealBaselineSpec,
    format_markdown,
    format_report,
    run_report,
)
from scripts.evaluate_tokenizer import load_cases  # noqa: E402
from scripts.report_baseline_matrix import _load_toml  # noqa: E402
from scripts.train_sentencepiece_baselines import train_sentencepiece  # noqa: E402


@dataclass(frozen=True)
class SentencePieceSweepModel:
    name: str
    model_type: str
    vocab_size: int
    model_prefix: Path

    @property
    def model_path(self) -> Path:
        return self.model_prefix.with_suffix(".model")


@dataclass(frozen=True)
class SentencePieceEvalSet:
    name: str
    path: Path
    markdown_out: Path


@dataclass(frozen=True)
class SentencePieceSweepConfig:
    path: Path
    corpus: Path
    corpus_label: str
    claim_grade: bool
    allow_train: bool
    max_sentence_length: int | None
    models: list[SentencePieceSweepModel]
    eval_sets: list[SentencePieceEvalSet]


def _string_field(item: dict[str, Any], field: str, *, context: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} requires string field {field!r}")
    return value


def _int_field(item: dict[str, Any], field: str, *, context: str) -> int:
    value = item.get(field)
    if not isinstance(value, int):
        raise ValueError(f"{context} requires integer field {field!r}")
    return value


def _optional_positive_int_setting(settings: dict[str, Any], field: str) -> int | None:
    value = settings.get(field)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"[settings] field {field!r} must be a positive integer")
    return value


def load_sentencepiece_sweep_config(path: str | Path) -> SentencePieceSweepConfig:
    config_path = Path(path)
    raw = _load_toml(config_path)
    settings = raw.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("[settings] must be a table")

    corpus = Path(_string_field(settings, "corpus", context="settings"))
    corpus_label = str(settings.get("corpus_label", corpus.as_posix()))
    claim_grade = bool(settings.get("claim_grade", False))
    allow_train = bool(settings.get("allow_train", True))
    max_sentence_length = _optional_positive_int_setting(settings, "max_sentence_length")

    models: list[SentencePieceSweepModel] = []
    for item in raw.get("models", []):
        if not isinstance(item, dict) or item.get("enabled", True) is False:
            continue
        name = _string_field(item, "name", context="model")
        model_type = _string_field(item, "model_type", context=f"model {name}")
        if model_type not in {"bpe", "unigram"}:
            raise ValueError(f"model {name} has unsupported model_type: {model_type}")
        models.append(
            SentencePieceSweepModel(
                name=name,
                model_type=model_type,
                vocab_size=_int_field(item, "vocab_size", context=f"model {name}"),
                model_prefix=Path(
                    _string_field(item, "model_prefix", context=f"model {name}")
                ),
            )
        )

    eval_sets: list[SentencePieceEvalSet] = []
    for item in raw.get("eval_sets", []):
        if not isinstance(item, dict):
            raise ValueError("[[eval_sets]] entries must be tables")
        name = _string_field(item, "name", context="eval_set")
        eval_sets.append(
            SentencePieceEvalSet(
                name=name,
                path=Path(_string_field(item, "path", context=f"eval_set {name}")),
                markdown_out=Path(
                    item.get(
                        "markdown_out",
                        f"artifacts/v1_7_sentencepiece_sweep_{name}.md",
                    )
                ),
            )
        )

    return SentencePieceSweepConfig(
        path=config_path,
        corpus=corpus,
        corpus_label=corpus_label,
        claim_grade=claim_grade,
        allow_train=allow_train,
        max_sentence_length=max_sentence_length,
        models=models,
        eval_sets=eval_sets,
    )


def train_enabled_models(
    config: SentencePieceSweepConfig,
    *,
    model_names: set[str] | None = None,
    force: bool = False,
) -> list[SentencePieceSweepModel]:
    selected = [
        model
        for model in config.models
        if model_names is None or model.name in model_names
    ]
    if model_names is not None:
        known = {model.name for model in config.models}
        unknown = model_names - known
        if unknown:
            raise ValueError(f"unknown model filter(s): {', '.join(sorted(unknown))}")

    for model in selected:
        if model.model_path.exists() and not force:
            print(f"model_exists: {model.model_path}")
            continue
        if not config.allow_train:
            raise ValueError(f"model missing and training disabled: {model.model_path}")
        model_path, vocab_path = train_sentencepiece(
            config.corpus,
            model.model_prefix,
            vocab_size=model.vocab_size,
            model_type=model.model_type,
            max_sentence_length=config.max_sentence_length,
        )
        print(f"wrote_model: {model_path}")
        print(f"wrote_vocab: {vocab_path}")

    return selected


def _sweep_markdown(
    eval_set: SentencePieceEvalSet,
    config: SentencePieceSweepConfig,
    summary_markdown: str,
) -> str:
    body_lines = summary_markdown.splitlines()
    if body_lines and body_lines[0].startswith("# "):
        body_lines = body_lines[2:]

    claim_status = "claim-grade" if config.claim_grade else "demo-only"
    lines = [
        f"# v1.7 SentencePiece Sweep: {eval_set.name}",
        "",
        f"Dataset: `{eval_set.path.as_posix()}`",
        f"Corpus: `{config.corpus.as_posix()}`",
        f"Corpus label: `{config.corpus_label}`",
        f"Status: `{claim_status}`",
        f"Max sentence length: `{config.max_sentence_length or 'sentencepiece_default'}`",
        "",
        "This report is a reproducibility and wiring check unless the corpus is",
        "explicitly marked claim-grade. It must not be used as hidden-eval or",
        "downstream LLM-quality evidence.",
        "",
    ]
    lines.extend(body_lines)
    return "\n".join(lines).rstrip() + "\n"


def run_sentencepiece_sweep(
    config: SentencePieceSweepConfig,
    *,
    dataset_names: set[str] | None = None,
    model_names: set[str] | None = None,
    train: bool = True,
    force: bool = False,
) -> list[Path]:
    if dataset_names is not None:
        known = {eval_set.name for eval_set in config.eval_sets}
        unknown = dataset_names - known
        if unknown:
            raise ValueError(f"unknown dataset filter(s): {', '.join(sorted(unknown))}")

    selected = config.models
    if model_names is not None:
        selected = [model for model in config.models if model.name in model_names]

    if train:
        selected = train_enabled_models(config, model_names=model_names, force=force)

    specs = [RealBaselineSpec("custom_tr_morph", "custom")]
    specs.extend(
        RealBaselineSpec(model.name, "sentencepiece", str(model.model_path))
        for model in selected
    )

    written: list[Path] = []
    for eval_set in config.eval_sets:
        if dataset_names is not None and eval_set.name not in dataset_names:
            continue

        summary_rows, category_table = run_report(load_cases(eval_set.path), specs)
        print(f"DATASET {eval_set.name}")
        print(format_report(summary_rows, category_table))
        print("")

        eval_set.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        eval_set.markdown_out.write_text(
            _sweep_markdown(
                eval_set,
                config,
                format_markdown(summary_rows, category_table),
            ),
            encoding="utf-8",
        )
        written.append(eval_set.markdown_out)
        print(f"wrote_markdown: {eval_set.markdown_out}")

    return written


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Train and evaluate the v1.7 SentencePiece sweep config.",
    )
    parser.add_argument("config", help="SentencePiece sweep TOML config path.")
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        help="Run only a named eval set from the config. Can be repeated.",
    )
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        help="Run only a named model from the config. Can be repeated.",
    )
    parser.add_argument(
        "--no-train",
        action="store_true",
        help="Evaluate existing model files without training.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Retrain even when model files already exist.",
    )
    args = parser.parse_args(argv)

    run_sentencepiece_sweep(
        load_sentencepiece_sweep_config(args.config),
        dataset_names=set(args.dataset) if args.dataset else None,
        model_names=set(args.model) if args.model else None,
        train=not args.no_train,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
