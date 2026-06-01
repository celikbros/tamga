from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def train_sentencepiece(
    input_path: str | Path,
    output_prefix: str | Path,
    *,
    vocab_size: int,
    model_type: str,
    max_sentence_length: int | None = None,
) -> tuple[Path, Path]:
    if importlib.util.find_spec("sentencepiece") is None:
        raise RuntimeError(
            "sentencepiece is not installed. Install the optional baselines extra."
        )

    import sentencepiece as spm  # type: ignore[import-not-found]

    prefix = Path(output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    train_kwargs = {
        "input": str(input_path),
        "model_prefix": str(prefix),
        "vocab_size": vocab_size,
        "model_type": model_type,
        "character_coverage": 1.0,
        "hard_vocab_limit": False,
        "normalization_rule_name": "identity",
        "remove_extra_whitespaces": False,
        "split_by_whitespace": True,
        "train_extremely_large_corpus": False,
    }
    if max_sentence_length is not None:
        train_kwargs["max_sentence_length"] = max_sentence_length

    spm.SentencePieceTrainer.train(**train_kwargs)

    return prefix.with_suffix(".model"), prefix.with_suffix(".vocab")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Train small local SentencePiece baselines for comparison.",
    )
    parser.add_argument("input_path")
    parser.add_argument("output_prefix")
    parser.add_argument("--vocab-size", type=int, default=1000)
    parser.add_argument(
        "--model-type",
        choices=("bpe", "unigram"),
        default="bpe",
    )
    args = parser.parse_args(argv)

    model_path, vocab_path = train_sentencepiece(
        args.input_path,
        args.output_prefix,
        vocab_size=args.vocab_size,
        model_type=args.model_type,
    )
    print(f"wrote_model: {model_path}")
    print(f"wrote_vocab: {vocab_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
