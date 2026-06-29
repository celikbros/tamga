from scripts.audit_v2_numeric_protected_encoder_whatif import (
    SplitWhatIf,
    digit_chunk_tokens,
)


def test_digit_chunk_tokens_for_numeric_shapes():
    assert digit_chunk_tokens("2018", chunk_size=2) == 2
    assert digit_chunk_tokens("2018", chunk_size=4) == 1
    assert digit_chunk_tokens("2018-2019", chunk_size=2) == 5
    assert digit_chunk_tokens("2018-2019", chunk_size=4) == 3
    assert digit_chunk_tokens("0.05", chunk_size=2) == 3
    assert digit_chunk_tokens("CO2", chunk_size=2) == 3


def test_split_whatif_replaces_only_numeric_tokens():
    stats = SplitWhatIf(
        split="toy",
        raw_bytes=100,
        current_finite_tokens=20,
        current_numeric_tokens=8,
        numeric_sp_tokens=3,
        numeric_digit2_tokens=5,
        numeric_digit4_tokens=2,
    )

    assert stats.current_tpb == 0.2
    assert stats.sp_numeric_tpb == 0.15
    assert stats.digit2_tpb == 0.17
    assert stats.digit4_tpb == 0.14
