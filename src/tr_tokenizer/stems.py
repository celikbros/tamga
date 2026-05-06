from __future__ import annotations

from .normalizer import turkish_lower

SURFACE_STEMS: tuple[str, ...] = (
    "config_v2.json",
    "readme.md",
    "istanbul",
    "türkiye",
    "oyuncağ",
    "oyuncak",
    "kaybol",
    "bahset",
    "bozul",
    "bileğ",
    "bilek",
    "çocuğ",
    "çocuk",
    "kanad",
    "kanat",
    "araba",
    "ağaç",
    "ağac",
    "ankara",
    "ayşe",
    "beğen",
    "dosya",
    "incit",
    "kedi",
    "kitap",
    "kitab",
    "renk",
    "reng",
    "openai",
    "python",
    "readme",
    "api",
    "ali",
    "alt",
    "aç",
    "gel",
    "git",
    "kırıl",
    "kır",
    "al",
    "in",
    "dur",
    "masa",
    "test",
    "veri",
    "yaz",
)

PROTECTED_WORDS: tuple[str, ...] = (
    "alın",
    "altın",
    "bunu",
    "kadın",
    "yakın",
)

_SURFACE_STEMS_BY_LENGTH = tuple(
    sorted(SURFACE_STEMS, key=len, reverse=True)
)
_PROTECTED_WORD_SET = frozenset(PROTECTED_WORDS)


def is_protected_word(word: str) -> bool:
    return turkish_lower(word) in _PROTECTED_WORD_SET


def find_longest_surface_stem(word: str) -> str | None:
    lowered = turkish_lower(word)

    for stem in _SURFACE_STEMS_BY_LENGTH:
        if lowered.startswith(stem):
            return stem

    return None
