from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scripts.reference_v3_7_control_wrapper import (
    WrapperSpec,
    decode_control_ids,
    encode_control_text,
    encode_raw_text,
    load_spec,
)


@dataclass(frozen=True)
class FakePiece:
    id: int
    begin: int
    end: int


@dataclass(frozen=True)
class FakeProto:
    pieces: list[FakePiece]


class FakeProcessor:
    def EncodeAsImmutableProto(self, text: str) -> FakeProto:
        return FakeProto([FakePiece(ord(char), index, index + 1) for index, char in enumerate(text)])

    def DecodeIds(self, ids: list[int]) -> str:
        return "".join(chr(token_id) for token_id in ids)

    def unk_id(self) -> int:
        return 0


def test_v3_7_config_control_ids() -> None:
    spec = load_spec(Path("configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json"))
    assert spec.sp_end == 64000
    assert spec.byte_start == 64000
    assert spec.control_start == 64256
    assert spec.effective_vocab_size == 64384
    assert spec.token_to_id["<pad>"] == 64256
    assert spec.token_to_id["<thinking>"] == 64260
    assert spec.token_to_id["<bos>"] == 1
    assert spec.id_to_token[64259] == "<assistant>"


def test_control_text_encode_uses_wrapper_ids() -> None:
    spec = load_spec(Path("configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json"))
    ids = encode_control_text(FakeProcessor(), spec, "<user>A<thinking>")
    assert ids == [64258, ord("A"), 64260]


def test_raw_text_encode_does_not_activate_control_strings() -> None:
    spec = load_spec(Path("configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json"))
    ids = encode_raw_text(FakeProcessor(), spec, "<user>")
    assert ids == [ord("<"), ord("u"), ord("s"), ord("e"), ord("r"), ord(">")]


def test_decode_mixed_control_sp_and_byte_ids() -> None:
    spec = WrapperSpec(
        sp_end=64000,
        byte_start=64000,
        byte_end=64256,
        control_start=64256,
        control_end=64384,
        effective_vocab_size=64384,
        token_to_id={"<user>": 64258, "<assistant>": 64259},
        id_to_token={64258: "<user>", 64259: "<assistant>"},
        sp_model_path=Path("unused.model"),
    )
    ids = [64258, ord("A"), 64000 + ord("!"), 64259]
    assert decode_control_ids(FakeProcessor(), spec, ids) == "<user>A!<assistant>"
