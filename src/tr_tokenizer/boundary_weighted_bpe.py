from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .baseline_bpe import _attach_word_start_marker, _scan_tokens
from .morphology import split_known_suffixes
from .tokenizer import WORD_START


@dataclass(frozen=True)
class Symbol:
    surface: str
    start: int
    end: int


@dataclass(frozen=True)
class PairStats:
    count: int
    crossing_count: int

    def score(self, boundary_lambda: float) -> float:
        return self.count - boundary_lambda * self.crossing_count


def _source_surface(token: str) -> str:
    if token.startswith(WORD_START) and len(token) > len(WORD_START):
        return token[len(WORD_START) :]
    if token.startswith("+") and len(token) > 1:
        return token[1:]
    return token


def morph_boundaries(token: str) -> tuple[int, ...]:
    parts = split_known_suffixes(token)
    if len(parts) <= 1:
        return ()

    boundaries: list[int] = []
    position = 0
    for part in parts[:-1]:
        position += len(_source_surface(part))
        if 0 < position < len(token):
            boundaries.append(position)
    return tuple(boundaries)


def _initial_symbols(token: str, *, starts_word: bool) -> tuple[Symbol, ...]:
    symbols = [Symbol(char, index, index + 1) for index, char in enumerate(token)]
    if starts_word:
        return (Symbol(WORD_START, 0, 0), *symbols)
    return tuple(symbols)


def _pair_stats(
    vocab: Counter[tuple[Symbol, ...]],
    boundaries_by_symbols: dict[tuple[Symbol, ...], tuple[int, ...]],
) -> dict[tuple[str, str], PairStats]:
    counts: Counter[tuple[str, str]] = Counter()
    crossings: Counter[tuple[str, str]] = Counter()
    for symbols, frequency in vocab.items():
        boundaries = set(boundaries_by_symbols.get(symbols, ()))
        for index in range(len(symbols) - 1):
            left = symbols[index]
            right = symbols[index + 1]
            pair = (left.surface, right.surface)
            counts[pair] += frequency
            if left.end == right.start and left.end in boundaries:
                crossings[pair] += frequency
    return {
        pair: PairStats(count=count, crossing_count=crossings[pair])
        for pair, count in counts.items()
    }


def _merge_symbols(
    symbols: tuple[Symbol, ...],
    pair: tuple[str, str],
) -> tuple[Symbol, ...]:
    merged: list[Symbol] = []
    index = 0
    while index < len(symbols):
        if (
            index < len(symbols) - 1
            and symbols[index].surface == pair[0]
            and symbols[index + 1].surface == pair[1]
        ):
            left = symbols[index]
            right = symbols[index + 1]
            merged.append(
                Symbol(
                    surface=left.surface + right.surface,
                    start=left.start,
                    end=right.end,
                )
            )
            index += 2
            continue
        merged.append(symbols[index])
        index += 1
    return tuple(merged)


def _apply_merges(symbols: tuple[Symbol, ...], merges: list[tuple[str, str]]) -> list[str]:
    current = symbols
    for pair in merges:
        current = _merge_symbols(current, pair)
    return _attach_word_start_marker([symbol.surface for symbol in current])


def train_boundary_weighted_bpe(
    lines: list[str],
    *,
    vocab_size: int,
    boundary_lambda: float,
    min_score: float = 2.0,
    max_lines: int | None = None,
) -> dict[str, Any]:
    vocab: Counter[tuple[Symbol, ...]] = Counter()
    boundaries_by_symbols: dict[tuple[Symbol, ...], tuple[int, ...]] = {}
    base_symbols: set[str] = set()

    selected_lines = lines if max_lines is None else lines[:max_lines]
    for line in selected_lines:
        for token, kind, starts_word in _scan_tokens(line):
            if kind != "word":
                continue
            symbols = _initial_symbols(token, starts_word=starts_word)
            vocab[symbols] += 1
            boundaries_by_symbols[symbols] = morph_boundaries(token)
            base_symbols.update(symbol.surface for symbol in symbols)

    merges: list[tuple[str, str]] = []
    merge_stats: list[dict[str, Any]] = []
    max_merges = max(0, vocab_size - len(base_symbols))

    for _ in range(max_merges):
        stats = _pair_stats(vocab, boundaries_by_symbols)
        if not stats:
            break

        best_pair, best_stats = max(
            stats.items(),
            key=lambda item: (
                item[1].score(boundary_lambda),
                item[1].count,
                -item[1].crossing_count,
                item[0],
            ),
        )
        best_score = best_stats.score(boundary_lambda)
        if best_stats.count < 2 or best_score < min_score:
            break

        merges.append(best_pair)
        merge_stats.append(
            {
                "pair": list(best_pair),
                "count": best_stats.count,
                "crossing_count": best_stats.crossing_count,
                "score": best_score,
            }
        )
        next_vocab: Counter[tuple[Symbol, ...]] = Counter()
        next_boundaries: dict[tuple[Symbol, ...], tuple[int, ...]] = {}
        for symbols, frequency in vocab.items():
            merged = _merge_symbols(symbols, best_pair)
            next_vocab[merged] += frequency
            next_boundaries[merged] = boundaries_by_symbols.get(symbols, ())
        vocab = next_vocab
        boundaries_by_symbols = next_boundaries

    return {
        "version": 1,
        "objective": "boundary_weighted_bpe",
        "vocab_size": vocab_size,
        "boundary_lambda": boundary_lambda,
        "min_score": min_score,
        "trained_lines": len(selected_lines),
        "merges": [list(pair) for pair in merges],
        "merge_stats": merge_stats,
    }


def encode_boundary_weighted_bpe(text: str, model: dict[str, Any]) -> list[str]:
    merges = [tuple(pair) for pair in model.get("merges", [])]
    encoded: list[str] = []
    for token, kind, starts_word in _scan_tokens(text):
        if kind == "word":
            symbols = _initial_symbols(token, starts_word=starts_word)
            encoded.extend(_apply_merges(symbols, merges))
        else:
            encoded.append(token)
    return encoded


def save_boundary_weighted_bpe(model: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")


def load_boundary_weighted_bpe(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
