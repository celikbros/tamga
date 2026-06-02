from scripts.compare_tokenizers import boundary_score
from scripts.evaluate_v2_raw_hard_candidate_intrinsic import (
    ModelCaseResult,
    encode_raw_hard_sentencepiece,
    format_eval_table,
    raw_hard_segments,
)
from tr_tokenizer.tokenizer import WORD_START


class FakeProcessor:
    def EncodeAsPieces(self, text: str) -> list[str]:
        return ["▁" + text]


def test_raw_hard_segments_keep_original_space_state():
    segments = raw_hard_segments("README.md'den geldim")

    assert [(segment.surface, segment.starts_after_space) for segment in segments[:4]] == [
        ("README.md", True),
        ("'", False),
        ("den", False),
        ("geldim", True),
    ]


def test_encode_raw_hard_sentencepiece_does_not_insert_space_at_internal_hard_boundaries():
    tokens = encode_raw_hard_sentencepiece("README.md'den geldim", FakeProcessor())

    assert tokens[:4] == [f"{WORD_START}README.md", "'", "den", f"{WORD_START}geldim"]


def test_internal_hard_boundary_tokens_score_against_apostrophe_gold():
    tokens = encode_raw_hard_sentencepiece("README.md'den", FakeProcessor())
    gold = [f"{WORD_START}README.md", "'", "+den"]

    assert boundary_score(tokens, gold).f1 == 1.0


def test_format_eval_table_renders_model_rows():
    result = ModelCaseResult(
        model_name="candidate",
        category="demo",
        text="kitaplar",
        expected=[f"{WORD_START}kitap", "+lar"],
        tokens=[f"{WORD_START}kitaplar"],
        status="ok",
        reason="",
        boundary=boundary_score([f"{WORD_START}kitaplar"], [f"{WORD_START}kitap", "+lar"]),
    )

    table = "\n".join(format_eval_table("Demo", {"candidate": [result]}))

    assert "## Demo" in table
    assert "candidate" in table
    assert "Boundary F1" in table
