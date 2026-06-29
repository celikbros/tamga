from scripts.audit_v2_1_sidecar_operation_simulation import Span
from scripts.audit_v2_4_llm_consumer_simulation import (
    ConsumerStats,
    audit_consumer_line,
    redact_by_sidecar,
)


class FakeProcessor:
    def EncodeAsImmutableProto(self, surface: str):
        class Piece:
            def __init__(self, begin: int, end: int, piece: str):
                self.begin = begin
                self.end = end
                self.piece = piece

        class Proto:
            pieces = [Piece(0, 9, "README.md"), Piece(9, len(surface), " rest")]

        return Proto()


def test_redact_by_sidecar_replaces_protected_span() -> None:
    span = Span(
        route="file_like",
        surface="README.md",
        char_start=0,
        char_end=9,
        byte_start=0,
        byte_end=9,
    )

    assert redact_by_sidecar("README.md hazir", [span]) == "<PROTECTED:file_like> hazir"


def test_consumer_line_accepts_copy_redact_and_token_mask() -> None:
    span = Span(
        route="file_like",
        surface="README.md",
        char_start=0,
        char_end=9,
        byte_start=0,
        byte_end=9,
    )
    stats = ConsumerStats()

    samples = audit_consumer_line(
        text="README.md hazir",
        spans=[span],
        processor=FakeProcessor(),
        stats=stats,
    )

    assert samples == []
    assert stats.failures == 0
    assert stats.spans == 1
    assert stats.edge_aligned_spans == 1


def test_consumer_line_rejects_wrong_surface() -> None:
    span = Span(
        route="file_like",
        surface="WRONG",
        char_start=0,
        char_end=9,
        byte_start=0,
        byte_end=9,
    )
    stats = ConsumerStats()

    samples = audit_consumer_line(
        text="README.md hazir",
        spans=[span],
        processor=FakeProcessor(),
        stats=stats,
    )

    assert stats.copy_failures == 1
    assert samples[0]["reason"] == "copy_failure"
