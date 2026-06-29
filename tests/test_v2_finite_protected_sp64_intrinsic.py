from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (
    encode_finite_protected_sp64,
    encode_protected_surface,
)
from tr_tokenizer.tokenizer import WORD_START


class FakeProcessor:
    def __init__(self):
        self._ids_by_surface: dict[str, int] = {}
        self._surface_by_id: dict[int, str] = {}

    def GetPieceSize(self) -> int:
        return 100

    def EncodeAsPieces(self, surface: str) -> list[str]:
        return ["\u2581" + part for part in surface.split(" ")]

    def EncodeAsIds(self, surface: str) -> list[int]:
        if surface not in self._ids_by_surface:
            token_id = 10 + len(self._ids_by_surface)
            self._ids_by_surface[surface] = token_id
            self._surface_by_id[token_id] = surface
        return [self._ids_by_surface[surface]]

    def DecodeIds(self, ids: list[int]) -> str:
        return "".join(self._surface_by_id.get(token_id, "") for token_id in ids)


def test_encode_protected_surface_uses_selected_pieces_then_bytes():
    piece_tokens, byte_tokens = encode_protected_surface("README.ç", ["README", "."])

    assert piece_tokens == 2
    assert byte_tokens == len("ç".encode("utf-8"))


def test_finite_protected_sp64_keeps_logical_span_and_counts_pieces():
    encoded = encode_finite_protected_sp64(
        "README.md'yi aç.",
        processor=FakeProcessor(),
        selected_pieces=["README", ".md"],
    )

    assert f"{WORD_START}README.md" in encoded.logical_tokens
    assert any("'yi" in token for token in encoded.logical_tokens)
    assert encoded.protected_piece_tokens == 2
    assert encoded.protected_byte_tokens == 0
    assert encoded.model_token_count >= len(encoded.logical_tokens)
