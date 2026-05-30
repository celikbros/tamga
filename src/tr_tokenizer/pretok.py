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
_VERSION = rf"\d+(?:[._-]?[0-9{TURKISH_LETTERS}]+)*(?:[-+][0-9{TURKISH_LETTERS}._-]+)?"
_TECHNICAL_COMPARATOR = (
    rf"[{TURKISH_LETTERS}][0-9{TURKISH_LETTERS}_.-]*"
    rf"(?:>=|<=|==|~=|!=){_VERSION}"
)
_URL = r"https?://[^\s<>()\"']+"
_UZBEK_APOSTROPHES = "\u02bb\u02bc"
_UZBEK_APOSTROPHE_WORD = (
    rf"[{TURKISH_LETTERS}]+(?:[{_UZBEK_APOSTROPHES}][{TURKISH_LETTERS}]+)+"
)
_AZERBAIJANI_SPECIFIC_LETTERS = "\u018f\u0259"
_AZERBAIJANI_WORD_CHARS = rf"{TURKISH_LETTERS}{_AZERBAIJANI_SPECIFIC_LETTERS}"
_AZERBAIJANI_SPECIFIC_WORD = (
    rf"(?=[{_AZERBAIJANI_WORD_CHARS}]*[{_AZERBAIJANI_SPECIFIC_LETTERS}])"
    rf"[{_AZERBAIJANI_WORD_CHARS}]+"
)
_CYRILLIC_WORD = r"[\u0400-\u04FF]+"
_APOSTROPHE_FORM = rf"(?:{_FILE_LIKE}|{_NUMERIC_LIKE}|{_WORD})'(?:{_WORD})"
_TOKEN_RE = re.compile(
    rf"{_URL}|{_UZBEK_APOSTROPHE_WORD}|{_AZERBAIJANI_SPECIFIC_WORD}|"
    rf"{_APOSTROPHE_FORM}|{_TECHNICAL_COMPARATOR}|{_FILE_LIKE}|"
    rf"{_NUMERIC_LIKE}|{_CYRILLIC_WORD}|{_WORD}|\S"
)
_WORD_RE = re.compile(rf"^{_WORD}$")
_UZBEK_APOSTROPHE_WORD_RE = re.compile(rf"^{_UZBEK_APOSTROPHE_WORD}$")
_AZERBAIJANI_SPECIFIC_WORD_RE = re.compile(rf"^{_AZERBAIJANI_SPECIFIC_WORD}$")
_CYRILLIC_WORD_RE = re.compile(rf"^{_CYRILLIC_WORD}$")
_FILE_LIKE_RE = re.compile(rf"^{_FILE_LIKE}$")
_NUMERIC_LIKE_RE = re.compile(rf"^{_NUMERIC_LIKE}$")
_TECHNICAL_COMPARATOR_RE = re.compile(rf"^{_TECHNICAL_COMPARATOR}$")
_URL_RE = re.compile(rf"^{_URL}$")
_URL_TRAILING_PUNCTUATION = ".,!?;:"


def is_url_like_token(token: str) -> bool:
    return bool(_URL_RE.match(token))


def is_uzbek_apostrophe_word(token: str) -> bool:
    return bool(_UZBEK_APOSTROPHE_WORD_RE.match(token))


def is_azerbaijani_specific_word(token: str) -> bool:
    return bool(_AZERBAIJANI_SPECIFIC_WORD_RE.match(token))


def is_cyrillic_word(token: str) -> bool:
    return bool(_CYRILLIC_WORD_RE.match(token))


def is_file_like_token(token: str) -> bool:
    return bool(_FILE_LIKE_RE.match(token))


def is_numeric_like_token(token: str) -> bool:
    return bool(_NUMERIC_LIKE_RE.match(token))


def is_technical_comparator_token(token: str) -> bool:
    return bool(_TECHNICAL_COMPARATOR_RE.match(token))


def split_url_token(token: str) -> list[str]:
    """Keep URLs intact while leaving sentence punctuation outside."""
    if not is_url_like_token(token):
        return [token]

    trailing: list[str] = []
    while token and token[-1] in _URL_TRAILING_PUNCTUATION:
        trailing.append(token[-1])
        token = token[:-1]

    if not token:
        return list(reversed(trailing))

    return [token, *reversed(trailing)]


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
        token = match.group(0)
        if is_url_like_token(token):
            tokens.extend(split_url_token(token))
        else:
            tokens.extend(split_apostrophe_token(token))

    return tokens
