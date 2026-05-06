from __future__ import annotations

import re
import unicodedata

_WHITESPACE_RE = re.compile(r"\s+")
_TRANSLATION_TABLE = str.maketrans(
    {
        "’": "'",
        "‘": "'",
        "ʼ": "'",
        "´": "'",
        "`": "'",
        "＇": "'",
        "“": '"',
        "”": '"',
        "„": '"',
        "–": "-",
        "—": "-",
    }
)


def turkish_lower(text: str) -> str:
    """Lowercase text with Turkish dotted/dotless I handling."""
    return text.replace("I", "ı").replace("İ", "i").lower()


def normalize_text(text: str, *, lowercase: bool = False) -> str:
    """Normalize Unicode, apostrophes and whitespace for tokenization."""
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.translate(_TRANSLATION_TABLE)
    normalized = _WHITESPACE_RE.sub(" ", normalized).strip()

    if lowercase:
        normalized = turkish_lower(normalized)

    return normalized
