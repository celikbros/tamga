from __future__ import annotations

import argparse
import json
import sys

from .tokenizer import TurkishTokenizer


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        prog="tr-tokenizer",
        description="Deterministic Turkish tokenizer prototype.",
    )
    parser.add_argument("text", nargs="*", help="Tokenize edilecek metin")
    parser.add_argument(
        "--lowercase",
        action="store_true",
        help="Turkceye uygun kucuk harfe cevirerek tokenize et",
    )
    args = parser.parse_args(argv)

    text = " ".join(args.text).strip()
    if not text:
        text = sys.stdin.read()

    tokenizer = TurkishTokenizer(lowercase=args.lowercase)
    tokens = tokenizer.encode(text)
    print(json.dumps(tokens, ensure_ascii=False))
    print(tokenizer.decode(tokens))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
