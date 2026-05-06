from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_tokenizer import load_cases  # noqa: E402


def find_exact_leakage(train_lines: list[str], eval_texts: list[str]) -> list[str]:
    train_set = {line.strip() for line in train_lines if line.strip()}
    return sorted({text for text in eval_texts if text in train_set})


def check_files(train_path: str | Path, eval_path: str | Path) -> list[str]:
    train_lines = Path(train_path).read_text(encoding="utf-8").splitlines()
    eval_texts = [case.text for case in load_cases(eval_path)]
    return find_exact_leakage(train_lines, eval_texts)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Check exact eval-text leakage.")
    parser.add_argument("train_path")
    parser.add_argument("eval_path")
    args = parser.parse_args(argv)

    leaks = check_files(args.train_path, args.eval_path)
    if not leaks:
        print("no exact leakage found")
        return 0

    print("exact leakage found")
    for text in leaks:
        print(text)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
