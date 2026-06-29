from scripts.audit_v2_morph_vocab_coverage import (
    MorphPolicyEntry,
    coverage_for_entry,
    strip_word_start,
    summarize,
)


class FakeProcessor:
    def __init__(self, pieces):
        self.pieces = list(pieces)

    def GetPieceSize(self):
        return len(self.pieces)

    def IdToPiece(self, index):
        return self.pieces[index]

    def EncodeAsPieces(self, surface):
        if surface == "lar":
            return ["lar"]
        return list(surface)


def _entry(surface: str, count: int = 10) -> MorphPolicyEntry:
    return MorphPolicyEntry(
        token=f"+{surface}",
        surface=surface,
        total_count=count,
        recommendation="uds_or_seed_candidate",
        action="seed_bias",
        reason="test",
        soft_share=1.0,
        hard_share=0.0,
        exact_collision_rate=0.0,
    )


def test_strip_word_start():
    assert strip_word_start("\u2581kitap") == "kitap"
    assert strip_word_start("lar") == "lar"


def test_coverage_for_entry_detects_vocab_and_single_piece():
    processor = FakeProcessor(["<unk>", "\u2581lar", "lar", "l", "a", "r"])
    coverage = coverage_for_entry(
        model_name="toy",
        entry=_entry("lar"),
        processor=processor,
        vocab=set(processor.pieces),
    )

    assert coverage.exact_piece
    assert coverage.word_start_piece
    assert coverage.has_vocab_surface
    assert coverage.standalone_single_piece


def test_summary_weights_by_occurrences():
    processor = FakeProcessor(["<unk>", "lar", "d", "a"])
    rows = [
        coverage_for_entry(
            model_name="toy",
            entry=_entry("lar", 100),
            processor=processor,
            vocab=set(processor.pieces),
        ),
        coverage_for_entry(
            model_name="toy",
            entry=_entry("da", 50),
            processor=processor,
            vocab=set(processor.pieces),
        ),
    ]

    summary = summarize("toy", rows)

    assert summary.occurrences == 150
    assert summary.exact_piece_occurrences == 100
    assert summary.single_piece_occurrence_share == 100 / 150
