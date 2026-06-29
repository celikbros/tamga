from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_CANDIDATES = [
    Path("configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json"),
    Path("configs/tokenizer_v3_0/tokenizer_config.json"),
]


@dataclass(frozen=True)
class WrapperSpec:
    sp_end: int
    byte_start: int
    byte_end: int
    control_start: int
    control_end: int
    effective_vocab_size: int
    token_to_id: dict[str, int]
    id_to_token: dict[int, str]
    sp_model_path: Path


def load_spec(config_path: Path) -> WrapperSpec:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    id_space = config["id_space"]
    registry = config["special_token_registry"]
    aliases = registry.get("aliases", {})
    assigned = registry.get("assigned", {})
    token_to_id = {str(token): int(token_id) for token, token_id in aliases.items()}
    token_to_id.update({str(token): int(token_id) for token, token_id in assigned.items()})
    id_to_token = {token_id: token for token, token_id in token_to_id.items()}
    model_path = Path(config["model"]["sp_model_path"])
    return WrapperSpec(
        sp_end=int(id_space["sp_id_end_exclusive"]),
        byte_start=int(id_space["byte_fallback_start"]),
        byte_end=int(id_space["byte_fallback_end_exclusive"]),
        control_start=int(id_space["control_token_start"]),
        control_end=int(id_space["control_token_end_exclusive"]),
        effective_vocab_size=int(id_space["current_effective_vocab_size"]),
        token_to_id=token_to_id,
        id_to_token=id_to_token,
        sp_model_path=model_path,
    )


def load_processor(model_path: Path) -> Any:
    try:
        import sentencepiece as spm
    except ImportError as exc:  # pragma: no cover - depends on optional env
        raise RuntimeError("sentencepiece is required for the reference wrapper") from exc
    processor = spm.SentencePieceProcessor()
    if not processor.Load(str(model_path)):
        raise RuntimeError(f"failed to load SentencePiece model: {model_path}")
    return processor


def char_to_byte_offsets(text: str) -> list[int]:
    offsets = [0]
    total = 0
    for char in text:
        total += len(char.encode("utf-8"))
        offsets.append(total)
    return offsets


def encode_raw_text(processor: Any, spec: WrapperSpec, text: str) -> list[int]:
    """Encode ordinary user text. This does not interpret control-token strings."""
    proto = processor.EncodeAsImmutableProto(text)
    piece_ids = [int(piece.id) for piece in proto.pieces if int(piece.begin) != int(piece.end)]
    decoded = processor.DecodeIds(piece_ids)
    if decoded == text:
        return piece_ids

    unknown_id = int(processor.unk_id()) if hasattr(processor, "unk_id") else 0
    ids: list[int] = []
    for piece in proto.pieces:
        piece_id = int(piece.id)
        begin = int(piece.begin)
        end = int(piece.end)
        if begin == end:
            continue
        if piece_id != unknown_id:
            ids.append(piece_id)
            continue
        for raw_byte in text[begin:end].encode("utf-8"):
            ids.append(spec.byte_start + raw_byte)
    return ids


def _control_pattern(tokens: list[str]) -> re.Pattern[str] | None:
    if not tokens:
        return None
    alternatives = sorted((re.escape(token) for token in tokens), key=len, reverse=True)
    return re.compile("(" + "|".join(alternatives) + ")")


def encode_control_text(processor: Any, spec: WrapperSpec, text: str) -> list[int]:
    """Encode trusted template text where configured control tokens are active."""
    pattern = _control_pattern(list(spec.token_to_id))
    if pattern is None:
        return encode_raw_text(processor, spec, text)

    ids: list[int] = []
    position = 0
    for match in pattern.finditer(text):
        if match.start() > position:
            ids.extend(encode_raw_text(processor, spec, text[position : match.start()]))
        ids.append(spec.token_to_id[match.group(0)])
        position = match.end()
    if position < len(text):
        ids.extend(encode_raw_text(processor, spec, text[position:]))
    return ids


def _flush_sp(processor: Any, buffer: list[int], output: list[str]) -> None:
    if buffer:
        output.append(processor.DecodeIds(buffer))
        buffer.clear()


def _flush_bytes(buffer: bytearray, output: list[str]) -> None:
    if buffer:
        output.append(bytes(buffer).decode("utf-8"))
        buffer.clear()


def decode_control_ids(processor: Any, spec: WrapperSpec, ids: list[int]) -> str:
    output: list[str] = []
    sp_buffer: list[int] = []
    byte_buffer = bytearray()
    for token_id in ids:
        token_id = int(token_id)
        if token_id in spec.id_to_token:
            _flush_sp(processor, sp_buffer, output)
            _flush_bytes(byte_buffer, output)
            output.append(spec.id_to_token[token_id])
        elif 0 <= token_id < spec.sp_end:
            _flush_bytes(byte_buffer, output)
            sp_buffer.append(token_id)
        elif spec.byte_start <= token_id < spec.byte_end:
            _flush_sp(processor, sp_buffer, output)
            byte_buffer.append(token_id - spec.byte_start)
        else:
            raise ValueError(f"token id outside v3.7 effective vocab: {token_id}")
    _flush_sp(processor, sp_buffer, output)
    _flush_bytes(byte_buffer, output)
    return "".join(output)


def parse_ids(value: str) -> list[int]:
    return [int(part) for part in re.split(r"[\s,]+", value.strip()) if part]


def default_config_path() -> str:
    for path in DEFAULT_CONFIG_CANDIDATES:
        if path.exists():
            return str(path)
    return str(DEFAULT_CONFIG_CANDIDATES[0])


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Reference v3.7 control-token wrapper.")
    parser.add_argument(
        "--config",
        default=default_config_path(),
    )
    parser.add_argument("--text", help="Trusted template text to encode.")
    parser.add_argument("--raw-text", help="Raw user text to encode without control-token recognition.")
    parser.add_argument("--ids", help="Comma/space-separated ids to decode.")
    parser.add_argument("--roundtrip", action="store_true", help="Decode encoded --text or --raw-text.")
    args = parser.parse_args(argv)

    spec = load_spec(Path(args.config))
    processor = load_processor(spec.sp_model_path)

    if args.text is not None:
        ids = encode_control_text(processor, spec, args.text)
        print(json.dumps({"ids": ids}, ensure_ascii=False))
        if args.roundtrip:
            print(json.dumps({"decoded": decode_control_ids(processor, spec, ids)}, ensure_ascii=False))
    if args.raw_text is not None:
        ids = encode_raw_text(processor, spec, args.raw_text)
        print(json.dumps({"ids": ids}, ensure_ascii=False))
        if args.roundtrip:
            print(json.dumps({"decoded": decode_control_ids(processor, spec, ids)}, ensure_ascii=False))
    if args.ids is not None:
        print(json.dumps({"decoded": decode_control_ids(processor, spec, parse_ids(args.ids))}, ensure_ascii=False))
    if args.text is None and args.raw_text is None and args.ids is None:
        parser.error("provide --text, --raw-text, or --ids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
