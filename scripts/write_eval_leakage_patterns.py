from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.check_eval_leakage import normalize_for_leakage, word_shingles  # noqa: E402
from scripts.evaluate_tokenizer import load_cases  # noqa: E402


def flexible_word_pattern(words: tuple[str, ...]) -> str:
    escaped = [re.escape(word) for word in words]
    return r"\b" + r"\W+".join(escaped) + r"\b"


def collect_patterns(
    eval_paths: list[Path],
    *,
    ngram_size: int,
    min_words: int,
) -> list[str]:
    patterns: set[str] = set()
    for path in eval_paths:
        for case in load_cases(path):
            words = tuple(normalize_for_leakage(case.text).split())
            if len(words) < min_words:
                continue
            shingles = word_shingles(words, ngram_size=ngram_size)
            if not shingles:
                shingles = {words}
            for shingle in shingles:
                patterns.add(flexible_word_pattern(shingle))
    return sorted(patterns)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write flexible regex patterns for fast eval leakage scans."
    )
    parser.add_argument("--eval", action="append", required=True, dest="eval_paths")
    parser.add_argument("--out", required=True)
    parser.add_argument("--ngram", type=int, default=8)
    parser.add_argument("--min-words", type=int, default=3)
    args = parser.parse_args(argv)

    patterns = collect_patterns(
        [Path(path) for path in args.eval_paths],
        ngram_size=args.ngram,
        min_words=args.min_words,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(patterns) + "\n", encoding="utf-8")
    print(f"wrote_patterns: {out}")
    print(f"patterns: {len(patterns)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
