from __future__ import annotations

import re

from .normalizer import normalize_text

TURKISH_LETTERS = "A-Za-zÇĞİÖŞÜçğıöşü"

_FILE_CHARS = rf"0-9{TURKISH_LETTERS}"
_FILE_LIKE = (
    rf"(?=[{_FILE_CHARS}_.]*[{TURKISH_LETTERS}])"
    rf"[{_FILE_CHARS}]+(?:[_.][{_FILE_CHARS}]+)+"
)
_WORD = rf"[{TURKISH_LETTERS}]+"
_NUMBER = r"\d+(?:[.,]\d+)*"
_TIME = r"\d{1,2}:\d{2}(?::\d{2})?"
_SLASH_NUMBER = r"\d+(?:/\d+)+"
_HYPHEN_CODE = rf"\d+(?:-[0-9{TURKISH_LETTERS}]+)+"
_ALNUM_NUMBER = rf"(?:\d+[{TURKISH_LETTERS}]+|[{TURKISH_LETTERS}]+\d+)[0-9{TURKISH_LETTERS}]*"
_NUMERIC_LIKE = rf"(?:{_SLASH_NUMBER}|{_TIME}|{_HYPHEN_CODE}|{_ALNUM_NUMBER}|{_NUMBER})"
_APOSTROPHE_FORM = rf"(?:{_FILE_LIKE}|{_NUMERIC_LIKE}|{_WORD})'(?:{_WORD})"
_TOKEN_RE = re.compile(
    rf"{_APOSTROPHE_FORM}|{_FILE_LIKE}|{_NUMERIC_LIKE}|{_WORD}|\S"
)
_WORD_RE = re.compile(rf"^{_WORD}$")
_FILE_LIKE_RE = re.compile(rf"^{_FILE_LIKE}$")
_NUMERIC_LIKE_RE = re.compile(rf"^{_NUMERIC_LIKE}$")


def is_file_like_token(token: str) -> bool:
    return bool(_FILE_LIKE_RE.match(token))


def is_numeric_like_token(token: str) -> bool:
    return bool(_NUMERIC_LIKE_RE.match(token))


def split_apostrophe_token(token: str) -> list[str]:
    """Split Turkish apostrophe forms as stem, apostrophe, +suffix."""
    if "'" not in token:
        return [token]

    stem, suffix = token.split("'", 1)
    if stem and suffix and _WORD_RE.match(suffix):
        return [stem, "'", f"+{suffix}"]

    return [token]


def pre_tokenize(text: str, *, lowercase: bool = False) -> list[str]:
    """Split text into deterministic word, apostrophe and punctuation tokens."""
    normalized = normalize_text(text, lowercase=lowercase)
    tokens: list[str] = []

    for match in _TOKEN_RE.finditer(normalized):
        tokens.extend(split_apostrophe_token(match.group(0)))

    return tokens
