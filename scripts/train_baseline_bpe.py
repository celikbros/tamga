from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer.baseline_bpe import save_bpe, train_bpe  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Train a toy pure-Python BPE baseline.")
    parser.add_argument("corpus_path", help="UTF-8 training corpus path")
    parser.add_argument("output_path", help="JSON model output path")
    parser.add_argument("--vocab-size", type=int, default=200)
    args = parser.parse_args(argv)

    corpus_path = Path(args.corpus_path)
    lines = corpus_path.read_text(encoding="utf-8").splitlines()
    model = train_bpe(lines, vocab_size=args.vocab_size)
    save_bpe(model, args.output_path)

    print(f"trained_lines: {len(lines)}")
    print(f"vocab_size:    {args.vocab_size}")
    print(f"merges:        {len(model['merges'])}")
    print(f"saved:         {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
