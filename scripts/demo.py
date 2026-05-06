from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tr_tokenizer import TurkishTokenizer  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    text = " ".join(sys.argv[1:]) or "Türkiye'den kedilerden geldim."
    tokenizer = TurkishTokenizer()
    tokens = tokenizer.encode(text)

    print(json.dumps(tokens, ensure_ascii=False))
    print(tokenizer.decode(tokens))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
