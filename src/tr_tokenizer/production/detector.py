"""Protected-span route detection for the v3.8 production chain.

Moved verbatim from scripts/materialize_v2_soft_morph_artifacts.py (Faz 2).
``analyze_line`` is the function whose U+2581 sentinel handling caused the
full-corpus crash fixed in docs/v3_8_detector_reconstruct_crash_fix.md; it
now lives in exactly one place.
"""

from __future__ import annotations

from dataclasses import dataclass

from tr_tokenizer import TurkishTokenizer
from tr_tokenizer.pretok import (
    is_apostrophe_surface_token,
    is_arabic_word,
    is_azerbaijani_specific_word,
    is_cyrillic_word,
    is_file_like_token,
    is_greek_word,
    is_non_turkish_latin_word,
    is_numeric_like_token,
    is_percent_encoded_token,
    is_technical_comparator_token,
    is_url_like_token,
    is_uzbek_apostrophe_word,
)
from tr_tokenizer.tokenizer import WORD_START

PROTECTED_KIND_CHECKS = (
    ("url", is_url_like_token),
    ("uzbek_apostrophe_word", is_uzbek_apostrophe_word),
    ("azerbaijani_word", is_azerbaijani_specific_word),
    ("cyrillic_word", is_cyrillic_word),
    ("arabic_word", is_arabic_word),
    ("greek_word", is_greek_word),
    ("non_turkish_latin_word", is_non_turkish_latin_word),
    ("apostrophe_surface", is_apostrophe_surface_token),
    ("file_like", is_file_like_token),
    ("numeric_like", is_numeric_like_token),
    ("percent_encoded", is_percent_encoded_token),
    ("technical_comparator", is_technical_comparator_token),
)


@dataclass(frozen=True)
class Piece:
    token: str
    surface: str
    kind: str
    boundary_before: str


def source_surface(token: str) -> str:
    if token.startswith(WORD_START) and len(token) > len(WORD_START):
        return token[len(WORD_START) :]
    if token.startswith("+") and len(token) > 1:
        return token[1:]
    return token


def protected_kind(surface: str) -> str | None:
    for kind, check in PROTECTED_KIND_CHECKS:
        if check(surface):
            return kind
    return None


def classify_token(token: str, previous_token: str | None) -> Piece:
    surface = source_surface(token)

    if token.isspace():
        return Piece(token=token, surface=surface, kind="whitespace", boundary_before="hard")

    if token == "'":
        return Piece(token=token, surface=surface, kind="apostrophe", boundary_before="hard")

    if token.startswith("+") and len(token) > 1:
        boundary = "hard" if previous_token == "'" else "soft"
        return Piece(token=token, surface=surface, kind="suffix", boundary_before=boundary)

    kind = protected_kind(surface)
    if kind is not None:
        return Piece(
            token=token,
            surface=surface,
            kind=f"protected:{kind}",
            boundary_before="hard",
        )

    if token.startswith(WORD_START) and len(token) > len(WORD_START):
        return Piece(token=token, surface=surface, kind="word_start", boundary_before="hard")

    return Piece(token=token, surface=surface, kind="punct_or_symbol", boundary_before="hard")


def analyze_line(text: str, tokenizer: TurkishTokenizer) -> list[Piece]:
    pieces: list[Piece] = []
    previous: str | None = None
    for token in tokenizer.encode(text):
        piece = classify_token(token, previous)
        pieces.append(piece)
        previous = token
    return pieces
