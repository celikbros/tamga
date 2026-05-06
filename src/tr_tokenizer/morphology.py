from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re

from .informal import split_informal_word
from .normalizer import turkish_lower
from .stems import find_longest_surface_stem, is_protected_word


@dataclass(frozen=True)
class SuffixRule:
    surface: str
    tag: str


SUFFIX_RULES: tuple[SuffixRule, ...] = (
    SuffixRule("lar", "PL"),
    SuffixRule("ler", "PL"),
    SuffixRule("ımız", "POSS_1PL"),
    SuffixRule("imiz", "POSS_1PL"),
    SuffixRule("umuz", "POSS_1PL"),
    SuffixRule("ümüz", "POSS_1PL"),
    SuffixRule("dan", "ABL"),
    SuffixRule("den", "ABL"),
    SuffixRule("tan", "ABL"),
    SuffixRule("ten", "ABL"),
    SuffixRule("nın", "GEN"),
    SuffixRule("nin", "GEN"),
    SuffixRule("nun", "GEN"),
    SuffixRule("nün", "GEN"),
    SuffixRule("da", "LOC"),
    SuffixRule("de", "LOC"),
    SuffixRule("ta", "LOC"),
    SuffixRule("te", "LOC"),
    SuffixRule("ki", "REL"),
    SuffixRule("laştır", "DERIV"),
    SuffixRule("leştir", "DERIV"),
    SuffixRule("laş", "DERIV"),
    SuffixRule("leş", "DERIV"),
    SuffixRule("abil", "DERIV"),
    SuffixRule("ebil", "DERIV"),
    SuffixRule("yan", "DERIV"),
    SuffixRule("yen", "DERIV"),
    SuffixRule("ıl", "DERIV"),
    SuffixRule("il", "DERIV"),
    SuffixRule("ul", "DERIV"),
    SuffixRule("ül", "DERIV"),
    SuffixRule("ın", "LEXICON_ONLY"),
    SuffixRule("in", "LEXICON_ONLY"),
    SuffixRule("un", "LEXICON_ONLY"),
    SuffixRule("ün", "LEXICON_ONLY"),
    SuffixRule("sı", "LEXICON_ONLY"),
    SuffixRule("si", "LEXICON_ONLY"),
    SuffixRule("su", "LEXICON_ONLY"),
    SuffixRule("sü", "LEXICON_ONLY"),
    SuffixRule("ı", "LEXICON_ONLY"),
    SuffixRule("i", "LEXICON_ONLY"),
    SuffixRule("u", "LEXICON_ONLY"),
    SuffixRule("ü", "LEXICON_ONLY"),
    SuffixRule("a", "LEXICON_ONLY"),
    SuffixRule("e", "LEXICON_ONLY"),
    SuffixRule("ya", "LEXICON_ONLY"),
    SuffixRule("ye", "LEXICON_ONLY"),
    SuffixRule("nı", "ACC"),
    SuffixRule("ni", "ACC"),
    SuffixRule("nu", "ACC"),
    SuffixRule("nü", "ACC"),
    SuffixRule("dı", "PST"),
    SuffixRule("di", "PST"),
    SuffixRule("du", "PST"),
    SuffixRule("dü", "PST"),
    SuffixRule("tı", "PST"),
    SuffixRule("ti", "PST"),
    SuffixRule("tu", "PST"),
    SuffixRule("tü", "PST"),
    SuffixRule("acak", "FUT"),
    SuffixRule("ecek", "FUT"),
    SuffixRule("yacak", "FUT"),
    SuffixRule("yecek", "FUT"),
    SuffixRule("ama", "NEG"),
    SuffixRule("eme", "NEG"),
    SuffixRule("mış", "EVID"),
    SuffixRule("miş", "EVID"),
    SuffixRule("muş", "EVID"),
    SuffixRule("müş", "EVID"),
    SuffixRule("sınız", "P2PL"),
    SuffixRule("siniz", "P2PL"),
    SuffixRule("sunuz", "P2PL"),
    SuffixRule("sünüz", "P2PL"),
    SuffixRule("dir", "COP"),
    SuffixRule("dır", "COP"),
    SuffixRule("dur", "COP"),
    SuffixRule("dür", "COP"),
    SuffixRule("tir", "COP"),
    SuffixRule("tır", "COP"),
    SuffixRule("tur", "COP"),
    SuffixRule("tür", "COP"),
    SuffixRule("ım", "P1SG"),
    SuffixRule("im", "P1SG"),
    SuffixRule("um", "P1SG"),
    SuffixRule("üm", "P1SG"),
    SuffixRule("sın", "P2SG"),
    SuffixRule("sin", "P2SG"),
    SuffixRule("sun", "P2SG"),
    SuffixRule("sün", "P2SG"),
    SuffixRule("ız", "P1PL"),
    SuffixRule("iz", "P1PL"),
    SuffixRule("uz", "P1PL"),
    SuffixRule("üz", "P1PL"),
    SuffixRule("lık", "NMLZ"),
    SuffixRule("lik", "NMLZ"),
    SuffixRule("luk", "NMLZ"),
    SuffixRule("lük", "NMLZ"),
)

_GENERAL_EXCLUDED_TAGS = {"PST", "LEXICON_ONLY", "DERIV", "GEN"}
_NOMINAL_SPLIT_RULES = tuple(
    sorted(
        (rule for rule in SUFFIX_RULES if rule.tag not in _GENERAL_EXCLUDED_TAGS),
        key=lambda rule: len(rule.surface),
        reverse=True,
    )
)
_LEXICON_SUFFIX_RULES = tuple(
    sorted(SUFFIX_RULES, key=lambda rule: len(rule.surface), reverse=True)
)
_LEXICON_TIE_PRIORITY = {
    "ı": 0,
    "i": 0,
    "u": 0,
    "ü": 0,
    "nı": 0,
    "ni": 0,
    "nu": 0,
    "nü": 0,
    "ın": 1,
    "in": 1,
    "un": 1,
    "ün": 1,
    "sın": 2,
    "sin": 2,
    "sun": 2,
    "sün": 2,
}
_APOSTROPHE_SUFFIX_SURFACES = tuple(
    sorted(
        {
            *(rule.surface for rule in SUFFIX_RULES),
            "yı",
            "yi",
            "yu",
            "yü",
            "lı",
            "li",
            "lu",
            "lü",
            "ıncı",
            "inci",
            "uncu",
            "üncü",
        },
        key=len,
        reverse=True,
    )
)
_ASCII_UPPER_RE = re.compile(r"[A-Z]")
_PAST_BASES = ("dı", "di", "du", "dü", "tı", "ti", "tu", "tü")
_PAST_PERSONS = (
    "m",
    "n",
    "k",
    "nız",
    "niz",
    "nuz",
    "nüz",
    "lar",
    "ler",
)
_PAST_ENDINGS = tuple(
    sorted(
        (
            (f"{base}{person}", base, person)
            for base in _PAST_BASES
            for person in _PAST_PERSONS
        ),
        key=lambda item: len(item[0]),
        reverse=True,
    )
)


def suffix_inventory() -> tuple[SuffixRule, ...]:
    """Return the current deterministic suffix inventory."""
    return SUFFIX_RULES


def split_past_tense(word: str, *, min_stem_length: int = 2) -> list[str] | None:
    """Split simple Turkish past tense forms such as geldim/gittiler."""
    lowered = turkish_lower(word)

    for ending, past, person in _PAST_ENDINGS:
        if not lowered.endswith(ending):
            continue

        stem = word[: -len(ending)]
        if len(stem) < min_stem_length:
            continue

        return [stem, f"+{past}", f"+{person}"]

    return None


def split_suffix_chain_by_inventory(surface: str) -> list[str] | None:
    """Split an entire suffix chain using the inventory, or return None."""
    lowered = turkish_lower(surface)

    @lru_cache(maxsize=None)
    def parse_from(index: int) -> tuple[str, ...] | None:
        if index == len(surface):
            return ()

        best: tuple[str, ...] | None = None
        best_score: tuple[int, int] | None = None

        for rule in _LEXICON_SUFFIX_RULES:
            if not lowered.startswith(rule.surface, index):
                continue

            end = index + len(rule.surface)
            rest = parse_from(end)
            if rest is None:
                continue

            suffix = surface[index:end]
            candidate = (suffix, *rest)
            score = (
                len(candidate),
                sum(
                    _LEXICON_TIE_PRIORITY.get(turkish_lower(part), 0)
                    for part in candidate
                ),
            )
            if best_score is None or score < best_score:
                best = candidate
                best_score = score

        return best

    result = parse_from(0)
    if result is None:
        return None
    return list(result)


def split_apostrophe_suffix_chain(surface: str) -> list[str] | None:
    """Split suffixes in the guarded apostrophe-only flow."""
    lowered = turkish_lower(surface)

    @lru_cache(maxsize=None)
    def parse_from(index: int) -> tuple[str, ...] | None:
        if index == len(surface):
            return ()

        for suffix_surface in _APOSTROPHE_SUFFIX_SURFACES:
            if not lowered.startswith(suffix_surface, index):
                continue

            end = index + len(suffix_surface)
            rest = parse_from(end)
            if rest is not None:
                return (surface[index:end], *rest)

        return None

    result = parse_from(0)
    if result is None:
        return None
    return list(result)


def split_apostrophe_suffix(surface: str) -> list[str]:
    suffixes = split_apostrophe_suffix_chain(surface)
    if suffixes is None:
        return [f"+{surface}"]
    return [f"+{suffix}" for suffix in suffixes]


def _has_internal_ascii_uppercase(text: str) -> bool:
    return any(_ASCII_UPPER_RE.match(char) for char in text[1:])


def split_mixed_case_suffix_chain(word: str) -> list[str] | None:
    """Split code-mixed words such as OpenAIlaştırılamayanlardanmış."""
    if not _has_internal_ascii_uppercase(word):
        return None

    for index in range(len(word) - 1, 1, -1):
        stem = word[:index]
        if not stem.isascii() or not stem.replace("_", "").replace(".", "").isalnum():
            continue
        if not _has_internal_ascii_uppercase(stem):
            continue

        suffixes = split_suffix_chain_by_inventory(word[index:])
        if suffixes is not None:
            return [stem, *(f"+{suffix}" for suffix in suffixes)]

    return None


def split_by_surface_lexicon(word: str) -> list[str] | None:
    """Split only when a known surface stem explains the full suffix chain."""
    if is_protected_word(word):
        return None

    stem = find_longest_surface_stem(word)
    if stem is None:
        return None

    stem_surface = word[: len(stem)]
    suffix_surface = word[len(stem) :]
    if not suffix_surface:
        return [stem_surface]

    suffixes = split_suffix_chain_by_inventory(suffix_surface)
    if suffixes is None:
        return None

    return [stem_surface, *(f"+{suffix}" for suffix in suffixes)]


def split_known_suffixes(
    word: str,
    *,
    max_splits: int = 8,
    min_stem_length: int = 2,
) -> list[str]:
    """Greedily split known Turkish-like suffixes from a word's end."""
    if len(word) <= min_stem_length:
        return [word]

    if is_protected_word(word):
        return [word]

    informal_parts = split_informal_word(word)
    if informal_parts is not None:
        return informal_parts

    mixed_parts = split_mixed_case_suffix_chain(word)
    if mixed_parts is not None:
        return mixed_parts

    lexicon_parts = split_by_surface_lexicon(word)
    if lexicon_parts is not None:
        return lexicon_parts

    past_parts = split_past_tense(word, min_stem_length=min_stem_length)
    if past_parts is not None:
        return past_parts

    stem = word
    suffixes: list[str] = []

    for _ in range(max_splits):
        lowered = turkish_lower(stem)
        match = next(
            (
                rule
                for rule in _NOMINAL_SPLIT_RULES
                if lowered.endswith(rule.surface)
                and len(stem) - len(rule.surface) >= min_stem_length
            ),
            None,
        )
        if match is None:
            break

        suffix = stem[-len(match.surface) :]
        stem = stem[: -len(match.surface)]
        suffixes.append(f"+{suffix}")

    if not suffixes:
        return [word]

    return [stem, *reversed(suffixes)]
