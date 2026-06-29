from scripts.sweep_v2_boundary_biased_unigram import (
    BoundaryBiasedVocab,
    VocabEntry,
    crossed_boundary_count,
    viterbi_segment,
)


def _toy_vocab() -> BoundaryBiasedVocab:
    return BoundaryBiasedVocab(
        entries_by_surface={
            "ab": VocabEntry(piece="ab", surface="ab", score=-1.0, word_start=False),
            "a": VocabEntry(piece="a", surface="a", score=-0.7, word_start=False),
            "b": VocabEntry(piece="b", surface="b", score=-0.7, word_start=False),
        },
        start_entries_by_surface={},
        max_entry_len=2,
        max_start_entry_len=0,
    )


def test_crossed_boundary_count_counts_strict_internal_boundaries():
    boundaries = (1, 3)

    assert crossed_boundary_count(0, 1, boundaries) == 0
    assert crossed_boundary_count(0, 2, boundaries) == 1
    assert crossed_boundary_count(1, 3, boundaries) == 0
    assert crossed_boundary_count(0, 4, boundaries) == 2


def test_viterbi_prefers_merge_until_boundary_penalty_is_high():
    vocab = _toy_vocab()

    no_penalty = viterbi_segment(
        "ab",
        boundaries=(1,),
        vocab=vocab,
        boundary_lambda=0.0,
    )
    high_penalty = viterbi_segment(
        "ab",
        boundaries=(1,),
        vocab=vocab,
        boundary_lambda=1.0,
    )

    assert no_penalty.surfaces == ("ab",)
    assert high_penalty.surfaces == ("a", "b")
