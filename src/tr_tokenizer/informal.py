from __future__ import annotations

from functools import lru_cache

from .normalizer import turkish_lower

INFORMAL_STEMS: tuple[str, ...] = (
    "napı",
    "gel",
    "gid",
)

INFORMAL_SUFFIXES: tuple[str, ...] = (
    "yorsun",
    "yosun",
    "icem",
    "ıcam",
    "iyom",
    "ıyom",
    "uyom",
    "üyom",
    "cam",
    "cem",
    "yon",
    "yor",
    "sun",
    "sın",
    "sin",
    "sün",
)

_STEMS_BY_LENGTH = tuple(sorted(INFORMAL_STEMS, key=len, reverse=True))
_SUFFIXES_BY_LENGTH = tuple(sorted(INFORMAL_SUFFIXES, key=len, reverse=True))


def split_informal_word(word: str) -> list[str] | None:
    lowered = turkish_lower(word)
    stem = next((item for item in _STEMS_BY_LENGTH if lowered.startswith(item)), None)
    if stem is None:
        return None

    suffix_surface = word[len(stem) :]
    if not suffix_surface:
        return None

    suffixes = _split_informal_suffixes(suffix_surface)
    if suffixes is None:
        return None

    return [word[: len(stem)], *(f"+{suffix}" for suffix in suffixes)]


def _split_informal_suffixes(surface: str) -> list[str] | None:
    lowered = turkish_lower(surface)

    @lru_cache(maxsize=None)
    def parse_from(index: int) -> tuple[str, ...] | None:
        if index == len(surface):
            return ()

        best: tuple[str, ...] | None = None
        for suffix in _SUFFIXES_BY_LENGTH:
            if not lowered.startswith(suffix, index):
                continue

            end = index + len(suffix)
            rest = parse_from(end)
            if rest is None:
                continue

            candidate = (surface[index:end], *rest)
            if best is None or len(candidate) > len(best):
                best = candidate

        return best

    result = parse_from(0)
    if result is None:
        return None
    return list(result)
