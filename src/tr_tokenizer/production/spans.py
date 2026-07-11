"""Protected-span geometry and loss-mask helpers for the v3.8 chain.

Moved verbatim from scripts/audit_v2_1_sidecar_operation_simulation.py
(Span, char_to_byte_offsets, protected_spans) and
scripts/tokenize_v3_1_corpus_smoke.py (EncodedTokenSpan, span_to_json,
token_mask_for_line) in Faz 2.
"""

from __future__ import annotations

from dataclasses import dataclass

from tr_tokenizer import TurkishTokenizer
from tr_tokenizer.production.detector import analyze_line


@dataclass(frozen=True)
class Span:
    route: str
    surface: str
    char_start: int
    char_end: int
    byte_start: int
    byte_end: int

    @property
    def byte_len(self) -> int:
        return self.byte_end - self.byte_start


@dataclass(frozen=True)
class EncodedTokenSpan:
    token_id: int
    byte_start: int
    byte_end: int


def char_to_byte_offsets(text: str) -> list[int]:
    offsets = [0]
    total = 0
    for char in text:
        total += len(char.encode("utf-8"))
        offsets.append(total)
    return offsets


def protected_spans(text: str, tokenizer: TurkishTokenizer) -> list[Span]:
    byte_offsets = char_to_byte_offsets(text)
    spans: list[Span] = []
    char_offset = 0
    for piece in analyze_line(text, tokenizer):
        start = char_offset
        end = start + len(piece.surface)
        if piece.kind.startswith("protected:"):
            spans.append(
                Span(
                    route=piece.kind.removeprefix("protected:"),
                    surface=piece.surface,
                    char_start=start,
                    char_end=end,
                    byte_start=byte_offsets[start],
                    byte_end=byte_offsets[end],
                )
            )
        char_offset = end
    if char_offset != len(text):
        raise ValueError("analyze_line surfaces did not reconstruct input")
    return spans


def span_to_json(span: Span) -> dict[str, object]:
    return {
        "route": span.route,
        "byte_start": span.byte_start,
        "byte_end": span.byte_end,
        "char_start": span.char_start,
        "char_end": span.char_end,
        "surface": span.surface,
    }


def token_mask_for_line(*, token_spans: list[EncodedTokenSpan], spans: list[Span]) -> bytearray:
    mask = bytearray([1] * len(token_spans))
    for span in spans:
        for index, token in enumerate(token_spans):
            if token.byte_start < span.byte_end and span.byte_start < token.byte_end:
                mask[index] = 0
    return mask
