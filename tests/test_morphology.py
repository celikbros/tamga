from tr_tokenizer.morphology import (
    split_by_surface_lexicon,
    split_known_suffixes,
    split_past_tense,
    split_suffix_chain_by_inventory,
    suffix_inventory,
)
from tr_tokenizer.informal import split_informal_word


def test_suffix_inventory_is_available():
    surfaces = {rule.surface for rule in suffix_inventory()}

    assert {
        "lar",
        "ler",
        "dan",
        "den",
        "im",
        "di",
        "miş",
        "siniz",
        "ın",
        "i",
        "ni",
    }.issubset(surfaces)


def test_split_known_suffixes_greedily_from_right():
    assert split_known_suffixes("kedilerden") == ["kedi", "+ler", "+den"]
    assert split_known_suffixes("kitaplar") == ["kitap", "+lar"]
    assert split_known_suffixes("Arabalarımızdakilerdenmişsiniz") == [
        "Araba",
        "+lar",
        "+ımız",
        "+da",
        "+ki",
        "+ler",
        "+den",
        "+miş",
        "+siniz",
    ]
    assert split_known_suffixes("Ağacın") == ["Ağac", "+ın"]
    assert split_known_suffixes("Rengini") == ["Reng", "+i", "+ni"]


def test_split_suffix_chain_by_inventory_prefers_safe_surface_chain():
    assert split_suffix_chain_by_inventory("ini") == ["i", "ni"]
    assert split_suffix_chain_by_inventory("ımızdan") == ["ımız", "dan"]
    assert split_suffix_chain_by_inventory("dakilerden") == ["da", "ki", "ler", "den"]
    assert split_suffix_chain_by_inventory("sını") == ["sı", "nı"]


def test_split_by_surface_lexicon_keeps_ambiguous_words_intact():
    assert split_by_surface_lexicon("altında") == ["alt", "+ın", "+da"]
    assert split_by_surface_lexicon("altın") is None
    assert split_known_suffixes("kadın") == ["kadın"]
    assert split_known_suffixes("yakın") == ["yakın"]
    assert split_known_suffixes("altın") == ["altın"]
    assert split_known_suffixes("kedi") == ["kedi"]


def test_split_known_suffixes_keeps_past_out_of_nominal_greedy_split():
    assert split_known_suffixes("kedi") == ["kedi"]


def test_split_past_tense_forms():
    assert split_past_tense("geldim") == ["gel", "+di", "+m"]
    assert split_past_tense("gittim") == ["git", "+ti", "+m"]
    assert split_past_tense("aldım") == ["al", "+dı", "+m"]
    assert split_past_tense("geldiler") == ["gel", "+di", "+ler"]


def test_split_known_suffixes_keeps_short_words_intact():
    assert split_known_suffixes("az") == ["az"]


def test_split_known_suffixes_handles_mixed_case_derivation():
    assert split_known_suffixes("OpenAIlaştırılamayanlardanmış") == [
        "OpenAI",
        "+laştır",
        "+ıl",
        "+ama",
        "+yan",
        "+lar",
        "+dan",
        "+mış",
    ]


def test_split_informal_word_preserves_surface_forms():
    assert split_informal_word("Napıyorsun") == ["Napı", "+yor", "+sun"]
    assert split_informal_word("Gelicem") == ["Gel", "+icem"]
    assert split_informal_word("Gidiyom") == ["Gid", "+iyom"]
    assert split_informal_word("Naber") is None
