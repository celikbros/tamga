from __future__ import annotations

from collections import Counter
import json
import re
from pathlib import Path
from typing import Any

from .normalizer import normalize_text
from .pretok import TURKISH_LETTERS

_WORD_RE = re.compile(rf"[0-9{TURKISH_LETTERS}_]+")


def _scan_tokens(text: str) -> list[tuple[str, str, bool]]:
    normalized = normalize_text(text)
    tokens: list[tuple[str, str, bool]] = []

    for match in re.finditer(rf"[0-9{TURKISH_LETTERS}_]+|\S", normalized):
        token = match.group(0)
        is_word = bool(_WORD_RE.fullmatch(token))
        starts_word = match.start() == 0 or normalized[match.start() - 1].isspace()
        kind = "word" if is_word else "punct"
        tokens.append((token, kind, starts_word))

    return tokens


def _initial_symbols(token: str, *, starts_word: bool) -> tuple[str, ...]:
    symbols = tuple(token)
    if starts_word:
        return ("▁", *symbols)
    return symbols


def _pair_counts(vocab: Counter[tuple[str, ...]]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for symbols, frequency in vocab.items():
        for index in range(len(symbols) - 1):
            counts[(symbols[index], symbols[index + 1])] += frequency
    return counts


def _merge_symbols(
    symbols: tuple[str, ...],
    pair: tuple[str, str],
) -> tuple[str, ...]:
    merged: list[str] = []
    index = 0

    while index < len(symbols):
        if (
            index < len(symbols) - 1
            and symbols[index] == pair[0]
            and symbols[index + 1] == pair[1]
        ):
            merged.append(symbols[index] + symbols[index + 1])
            index += 2
        else:
            merged.append(symbols[index])
            index += 1

    return tuple(merged)


def _apply_merges(symbols: tuple[str, ...], merges: list[tuple[str, str]]) -> list[str]:
    current = symbols
    for pair in merges:
        current = _merge_symbols(current, pair)
    return _attach_word_start_marker(list(current))


def _attach_word_start_marker(symbols: list[str]) -> list[str]:
    if len(symbols) >= 2 and symbols[0] == "▁":
        return [f"▁{symbols[1]}", *symbols[2:]]
    return symbols


def train_bpe(lines: list[str], vocab_size: int) -> dict[str, Any]:
    vocab: Counter[tuple[str, ...]] = Counter()
    base_symbols: set[str] = set()

    for line in lines:
        for token, kind, starts_word in _scan_tokens(line):
            if kind != "word":
                continue
            symbols = _initial_symbols(token, starts_word=starts_word)
            vocab[symbols] += 1
            base_symbols.update(symbols)

    merges: list[tuple[str, str]] = []
    max_merges = max(0, vocab_size - len(base_symbols))

    for _ in range(max_merges):
        counts = _pair_counts(vocab)
        if not counts:
            break

        best_pair, best_count = max(
            counts.items(),
            key=lambda item: (item[1], item[0]),
        )
        if best_count < 2:
            break

        merges.append(best_pair)
        vocab = Counter(
            {
                _merge_symbols(symbols, best_pair): frequency
                for symbols, frequency in vocab.items()
            }
        )

    return {
        "version": 1,
        "vocab_size": vocab_size,
        "merges": [list(pair) for pair in merges],
    }


def encode_bpe(text: str, model: dict[str, Any]) -> list[str]:
    merges = [tuple(pair) for pair in model.get("merges", [])]
    encoded: list[str] = []

    for token, kind, starts_word in _scan_tokens(text):
        if kind == "word":
            symbols = _initial_symbols(token, starts_word=starts_word)
            encoded.extend(_apply_merges(symbols, merges))
        else:
            encoded.append(token)

    return encoded


def save_bpe(model: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(model, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_bpe(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
