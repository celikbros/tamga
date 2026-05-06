from __future__ import annotations

from dataclasses import dataclass
import re

from .morphology import split_apostrophe_suffix, split_known_suffixes
from .pretok import TURKISH_LETTERS, is_file_like_token, pre_tokenize

WORD_START = "▁"
_WORD_RE = re.compile(rf"^[{TURKISH_LETTERS}]+$")
_NO_SPACE_BEFORE = set(".,!?;:%)]}»”")
_NO_SPACE_AFTER = set("([{«“")


def _is_word(token: str) -> bool:
    return bool(_WORD_RE.match(token))


def _should_attach_left(token: str) -> bool:
    return token.startswith("+") or token == "'" or token in _NO_SPACE_BEFORE


def _mark_word_start(pieces: list[str]) -> list[str]:
    if not pieces:
        return pieces
    if pieces[0].startswith("+"):
        return pieces
    return [f"{WORD_START}{pieces[0]}", *pieces[1:]]


@dataclass(frozen=True)
class TurkishTokenizer:
    """Small deterministic tokenizer close to Turkish morphology."""

    lowercase: bool = False
    split_suffixes: bool = True

    def encode(self, text: str) -> list[str]:
        tokens = pre_tokenize(text, lowercase=self.lowercase)
        encoded: list[str] = []

        for index, token in enumerate(tokens):
            next_token = tokens[index + 1] if index + 1 < len(tokens) else None

            if token.startswith("+"):
                encoded.extend(split_apostrophe_suffix(token[1:]))
            elif token == "'":
                encoded.append(token)
            elif _is_word(token):
                if next_token == "'":
                    pieces = [token]
                else:
                    pieces = split_known_suffixes(token) if self.split_suffixes else [token]
                encoded.extend(_mark_word_start(pieces))
            elif is_file_like_token(token):
                encoded.extend(_mark_word_start([token]))
            else:
                encoded.append(token)

        return encoded

    def decode(self, tokens: list[str] | tuple[str, ...]) -> str:
        return decode(tokens)


def encode(text: str, *, lowercase: bool = False, split_suffixes: bool = True) -> list[str]:
    return TurkishTokenizer(
        lowercase=lowercase,
        split_suffixes=split_suffixes,
    ).encode(text)


def decode(tokens: list[str] | tuple[str, ...]) -> str:
    text = ""

    for token in tokens:
        if not token:
            continue

        if token.startswith(WORD_START):
            word = token[len(WORD_START) :]
            if not text or text.endswith((" ", "'")) or text[-1] in _NO_SPACE_AFTER:
                text += word
            else:
                text += f" {word}"
        elif token.startswith("+"):
            text = text.rstrip() + token[1:]
        elif token == "'":
            text = text.rstrip() + "'"
        elif _should_attach_left(token):
            text = text.rstrip() + token
        elif not text or text.endswith((" ", "'")) or text[-1] in _NO_SPACE_AFTER:
            text += token
        else:
            text += f" {token}"

    return text
