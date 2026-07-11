from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, replace
import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.report_baseline_matrix import _load_toml  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    load_sp_processor,
    selected_piece_strings,
)
from scripts.sweep_v2_boundary_biased_unigram import (  # noqa: E402
    BoundaryBiasedVocab,
    viterbi_segment,
)
from scripts.materialize_v2_raw_soft_marker_candidate_views import SOFT_MARKER  # noqa: E402
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402

PAD_ID = 0
UNK_ID = 1
EOS_ID = 2
BYTE_OFFSET = 3
BYTE_VOCAB_SIZE = 256


# Moved to the production package (Faz 2); re-exported here so the archived
# research tooling and historical commands keep working unchanged.
from tr_tokenizer.production.config import (  # noqa: E402,F401
    ModelConfig,
    ProbeConfig,
    TokenizerConfig,
    load_probe_config,
)


@dataclass(frozen=True)
class SplitText:
    name: str
    lines: list[str]

    @property
    def bytes(self) -> int:
        return sum(len(line.encode("utf-8")) for line in self.lines)


@dataclass
class EncodedSplit:
    name: str
    ids: list[int]
    bytes: int
    lines: int
    oov_tokens: int = 0

    @property
    def tokens(self) -> int:
        return len(self.ids)

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.bytes if self.bytes else 0.0

    @property
    def oov_rate(self) -> float:
        return self.oov_tokens / self.tokens if self.tokens else 0.0


@dataclass
class EncodedTokenizer:
    config: TokenizerConfig
    vocab_size: int
    status: str
    reason: str = ""
    splits: dict[str, EncodedSplit] = field(default_factory=dict)


@dataclass
class TrainMetrics:
    tokenizer: str
    status: str
    vocab_size: int
    total_params: int = 0
    embedding_params: int = 0
    non_embedding_params: int = 0
    steps: int = 0
    tokens_seen: int = 0
    approx_bytes_seen: float = 0.0
    best_valid_bpb: float | None = None
    final_valid_bpb: float | None = None
    test_bpb: float | None = None
    final_valid_bits_per_token: float | None = None
    test_bits_per_token: float | None = None
    final_valid_target_tokens: int = 0
    test_target_tokens: int = 0
    final_valid_evaluated_bytes: float = 0.0
    test_evaluated_bytes: float = 0.0
    reason: str = ""


@dataclass(frozen=True)
class EvalLossStats:
    bpb: float
    bits_per_token: float
    target_tokens: int
    evaluated_bytes: float
    evaluated_fraction: float
    nll_bits: float


def load_split_texts(split_dir: str | Path) -> dict[str, SplitText]:
    root = Path(split_dir)
    splits: dict[str, SplitText] = {}
    for name in ("train", "valid", "test"):
        path = root / f"{name}.txt"
        if not path.exists():
            raise FileNotFoundError(path)
        splits[name] = SplitText(
            name=name,
            lines=[line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines()],
        )
    return splits


def build_custom_vocab(lines: list[str], *, max_vocab_size: int | None) -> dict[str, int]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    counts: Counter[str] = Counter()
    for line in lines:
        counts.update(tokenizer.encode(line))

    vocab = {"<pad>": PAD_ID, "<unk>": UNK_ID, "<eos>": EOS_ID}
    for byte in range(BYTE_VOCAB_SIZE):
        vocab[f"<byte_{byte:02x}>"] = BYTE_OFFSET + byte

    reserved = len(vocab)
    if max_vocab_size is not None and max_vocab_size < reserved:
        raise ValueError(
            f"custom max_vocab_size={max_vocab_size} is too small; "
            f"needs at least {reserved} for specials plus byte fallback"
        )

    limit = max_vocab_size - reserved if max_vocab_size is not None else None
    for token, _count in counts.most_common(limit):
        if token not in vocab:
            vocab[token] = len(vocab)
    return vocab


def encode_custom_split(lines: list[str], vocab: dict[str, int], byte_count: int, split: str) -> EncodedSplit:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    ids: list[int] = []
    fallback_source_tokens = 0
    for line in lines:
        for token in tokenizer.encode(line):
            token_id = vocab.get(token)
            if token_id is None:
                fallback_source_tokens += 1
                ids.extend(BYTE_OFFSET + byte for byte in token.encode("utf-8"))
            else:
                ids.append(token_id)
        ids.append(EOS_ID)
    return EncodedSplit(
        split,
        ids,
        byte_count,
        len(lines),
        oov_tokens=fallback_source_tokens,
    )


def encode_utf8_byte_split(lines: list[str], byte_count: int, split: str) -> EncodedSplit:
    ids: list[int] = []
    for line in lines:
        ids.extend(line.encode("utf-8"))
        ids.append(256)
    return EncodedSplit(split, ids, byte_count, len(lines))


def encode_sentencepiece_split(
    model_path: Path,
    lines: list[str],
    byte_count: int,
    split: str,
    *,
    tokenizer_name: str = "",
    progress: int = 0,
) -> EncodedSplit:
    import sentencepiece as spm  # type: ignore[import-not-found]

    processor = spm.SentencePieceProcessor(model_file=str(model_path))
    eos = processor.eos_id()
    ids: list[int] = []
    for line_number, line in enumerate(lines, start=1):
        ids.extend(int(piece_id) for piece_id in processor.encode(line, out_type=int))
        if eos >= 0:
            ids.append(int(eos))
        if progress > 0 and line_number % progress == 0:
            print(
                f"encoding {tokenizer_name or model_path.stem} split={split}: "
                f"{line_number:,} lines tokens={len(ids):,}",
                flush=True,
            )
    return EncodedSplit(split, ids, byte_count, len(lines))


# Moved to the production package (Faz 2); re-exported for compatibility.
from tr_tokenizer.production.sp import (  # noqa: E402,F401
    _processor_decode_ids,
    _processor_eos_id,
    _processor_piece_size,
)


def _processor_encode_ids(processor, surface: str) -> list[int]:
    if not surface:
        return []
    if hasattr(processor, "EncodeAsIds"):
        return [int(item) for item in processor.EncodeAsIds(surface)]
    return [int(item) for item in processor.encode(surface, out_type=int)]


def _processor_encode_ids_lossless_or_byte_fallback(
    processor,
    surface: str,
    *,
    byte_offset: int,
) -> tuple[list[int], int]:
    ids = _processor_encode_ids(processor, surface)
    decoded = _processor_decode_ids(processor, ids)
    if decoded is None or decoded == surface:
        return ids, 0
    if not hasattr(processor, "EncodeAsImmutableProto"):
        output: list[int] = []
        byte_fallback_tokens = 0
        for char in surface:
            char_ids = _processor_encode_ids(processor, char)
            if _processor_decode_ids(processor, char_ids) == char:
                output.extend(char_ids)
                continue
            byte_fallback_tokens += _append_utf8_bytes(
                output,
                char,
                byte_offset=byte_offset,
            )
        return output, byte_fallback_tokens
    return _processor_encode_ids_with_boundary_byte_fallback(
        processor,
        surface,
        boundaries=set(),
        byte_offset=byte_offset,
    )


def encode_protected_surface_ids(
    surface: str,
    *,
    selected_pieces: list[str],
    piece_to_id: dict[str, int],
    byte_offset: int,
) -> tuple[list[int], int]:
    ids: list[int] = []
    byte_fallback_tokens = 0
    position = 0
    while position < len(surface):
        match = ""
        for piece in selected_pieces:
            if surface.startswith(piece, position):
                match = piece
                break
        if match:
            ids.append(piece_to_id[match])
            position += len(match)
            continue

        encoded = surface[position].encode("utf-8")
        ids.extend(byte_offset + byte for byte in encoded)
        byte_fallback_tokens += len(encoded)
        position += 1
    return ids, byte_fallback_tokens


def _processor_encode_ids_with_boundary_byte_fallback(
    processor,
    surface: str,
    *,
    boundaries: set[int],
    byte_offset: int,
) -> tuple[list[int], int]:
    if not surface:
        return [], 0
    proto = processor.EncodeAsImmutableProto(surface)
    output: list[int] = []
    byte_fallback_tokens = 0
    unknown_id = int(processor.unk_id()) if hasattr(processor, "unk_id") else 0
    for piece in proto.pieces:
        begin = int(piece.begin)
        end = int(piece.end)
        crosses_boundary = any(begin < boundary < end for boundary in boundaries)
        is_unknown = int(piece.id) == unknown_id
        if not crosses_boundary and not is_unknown:
            output.append(int(piece.id))
            continue
        encoded = surface[begin:end].encode("utf-8")
        output.extend(byte_offset + byte for byte in encoded)
        byte_fallback_tokens += len(encoded)
    return output, byte_fallback_tokens


def _processor_piece_to_id_safe(processor, piece: str) -> int:
    if hasattr(processor, "PieceToId"):
        return int(processor.PieceToId(piece))
    if hasattr(processor, "piece_to_id"):
        return int(processor.piece_to_id(piece))
    return -1


def _processor_id_to_piece(processor, piece_id: int) -> str:
    if hasattr(processor, "IdToPiece"):
        return str(processor.IdToPiece(piece_id))
    return str(processor.id_to_piece(piece_id))


def _append_utf8_bytes(output: list[int], surface: str, *, byte_offset: int) -> int:
    encoded = surface.encode("utf-8")
    output.extend(byte_offset + byte for byte in encoded)
    return len(encoded)


def _processor_encode_presplit_segment_ids(
    processor,
    surface: str,
    *,
    starts_at_line_start: bool,
    byte_offset: int,
) -> tuple[list[int], int]:
    if not surface:
        return [], 0
    proto = processor.EncodeAsImmutableProto(surface)
    output: list[int] = []
    byte_fallback_tokens = 0
    unknown_id = int(processor.unk_id()) if hasattr(processor, "unk_id") else 0

    for index, piece in enumerate(proto.pieces):
        piece_id = int(piece.id)
        begin = int(piece.begin)
        end = int(piece.end)
        raw_surface = surface[begin:end]
        if not raw_surface and piece_id == _processor_eos_id(processor):
            continue
        if piece_id == unknown_id:
            byte_fallback_tokens += _append_utf8_bytes(
                output,
                raw_surface,
                byte_offset=byte_offset,
            )
            continue

        sp_piece = _processor_id_to_piece(processor, piece_id)
        dummy_prefix = (
            index == 0
            and not starts_at_line_start
            and not raw_surface.startswith((" ", "\t", "\r", "\n"))
            and sp_piece.startswith("▁")
        )
        if not dummy_prefix:
            output.append(piece_id)
            continue

        stripped_piece = sp_piece[1:]
        if not stripped_piece:
            continue
        stripped_id = _processor_piece_to_id_safe(processor, stripped_piece)
        if stripped_id >= 0 and _processor_id_to_piece(processor, stripped_id) == stripped_piece:
            output.append(stripped_id)
            continue

        byte_fallback_tokens += _append_utf8_bytes(
            output,
            raw_surface,
            byte_offset=byte_offset,
        )

    return output, byte_fallback_tokens


def encode_finite_protected_soft_marker_line_ids(
    text: str,
    *,
    processor,
    selected_pieces: list[str],
    protected_piece_offset: int,
    insert_soft_markers: bool = True,
    numeric_sp_passthrough: bool = False,
    sp_passthrough_routes: frozenset[str] | set[str] | None = None,
    isolate_sp_passthrough_routes: bool = False,
    byte_fallback_crossing_pieces: bool = False,
    pre_split_sp_passthrough_routes: bool = False,
) -> tuple[list[int], int]:
    piece_to_id = {
        piece: protected_piece_offset + index
        for index, piece in enumerate(selected_pieces)
    }
    byte_offset = protected_piece_offset + len(selected_pieces)
    pieces = analyze_line(text, TurkishTokenizer(preserve_whitespace=True))
    ids: list[int] = []
    protected_byte_tokens = 0
    segment = ""
    passthrough_routes = set(sp_passthrough_routes or set())
    if numeric_sp_passthrough:
        passthrough_routes.add("numeric_like")

    if not insert_soft_markers:
        if pre_split_sp_passthrough_routes:
            segment_start = 0
            offset = 0

            def flush_presplit() -> None:
                nonlocal segment, protected_byte_tokens, segment_start
                if not segment:
                    return
                segment_ids, byte_tokens = _processor_encode_presplit_segment_ids(
                    processor,
                    segment,
                    starts_at_line_start=segment_start == 0,
                    byte_offset=byte_offset,
                )
                ids.extend(segment_ids)
                protected_byte_tokens += byte_tokens
                segment = ""

            for piece in pieces:
                piece_start = offset
                piece_end = piece_start + len(piece.surface)
                if piece.kind.startswith("protected:"):
                    route = piece.kind.removeprefix("protected:")
                    if route in passthrough_routes:
                        flush_presplit()
                        segment_ids, byte_tokens = _processor_encode_presplit_segment_ids(
                            processor,
                            piece.surface,
                            starts_at_line_start=piece_start == 0,
                            byte_offset=byte_offset,
                        )
                        ids.extend(segment_ids)
                        protected_byte_tokens += byte_tokens
                        offset = piece_end
                        segment_start = offset
                        continue
                    flush_presplit()
                    protected_ids, byte_tokens = encode_protected_surface_ids(
                        piece.surface,
                        selected_pieces=selected_pieces,
                        piece_to_id=piece_to_id,
                        byte_offset=byte_offset,
                    )
                    ids.extend(protected_ids)
                    protected_byte_tokens += byte_tokens
                    offset = piece_end
                    segment_start = offset
                    continue

                if not segment:
                    segment_start = piece_start
                segment += piece.surface
                offset = piece_end

            flush_presplit()
            return ids, protected_byte_tokens

        if byte_fallback_crossing_pieces:
            segment_boundaries: set[int] = set()

            def flush_edge_safe() -> None:
                nonlocal segment, protected_byte_tokens, segment_boundaries
                if not segment:
                    return
                segment_ids, byte_tokens = _processor_encode_ids_with_boundary_byte_fallback(
                    processor,
                    segment,
                    boundaries=segment_boundaries,
                    byte_offset=byte_offset,
                )
                ids.extend(segment_ids)
                protected_byte_tokens += byte_tokens
                segment = ""
                segment_boundaries = set()

            for piece in pieces:
                if piece.kind.startswith("protected:"):
                    route = piece.kind.removeprefix("protected:")
                    if route in passthrough_routes:
                        start = len(segment)
                        segment += piece.surface
                        segment_boundaries.add(start)
                        segment_boundaries.add(len(segment))
                        continue
                    flush_edge_safe()
                    protected_ids, byte_tokens = encode_protected_surface_ids(
                        piece.surface,
                        selected_pieces=selected_pieces,
                        piece_to_id=piece_to_id,
                        byte_offset=byte_offset,
                    )
                    ids.extend(protected_ids)
                    protected_byte_tokens += byte_tokens
                    continue

                segment += piece.surface

            flush_edge_safe()
            return ids, protected_byte_tokens

        # Runtime protected wrappers must not reset SentencePiece at every
        # morphology/punctuation boundary. Doing so creates internal dummy-prefix
        # pieces that decode as fake spaces. Keep normal text as raw chunks and
        # split only around finite protected spans.
        def flush_route_only() -> None:
            nonlocal segment, protected_byte_tokens
            if segment:
                segment_ids, byte_tokens = _processor_encode_ids_lossless_or_byte_fallback(
                    processor,
                    segment,
                    byte_offset=byte_offset,
                )
                ids.extend(segment_ids)
                protected_byte_tokens += byte_tokens
                segment = ""

        for piece in pieces:
            if piece.kind.startswith("protected:"):
                route = piece.kind.removeprefix("protected:")
                if route in passthrough_routes:
                    if isolate_sp_passthrough_routes:
                        flush_route_only()
                        segment_ids, byte_tokens = _processor_encode_ids_lossless_or_byte_fallback(
                            processor,
                            piece.surface,
                            byte_offset=byte_offset,
                        )
                        ids.extend(segment_ids)
                        protected_byte_tokens += byte_tokens
                    else:
                        segment += piece.surface
                    continue
                flush_route_only()
                protected_ids, byte_tokens = encode_protected_surface_ids(
                    piece.surface,
                    selected_pieces=selected_pieces,
                    piece_to_id=piece_to_id,
                    byte_offset=byte_offset,
                )
                ids.extend(protected_ids)
                protected_byte_tokens += byte_tokens
                continue

            segment += piece.surface

        flush_route_only()
        return ids, protected_byte_tokens

    def flush() -> None:
        nonlocal segment
        if segment:
            ids.extend(_processor_encode_ids(processor, segment))
            segment = ""

    for piece in pieces:
        if piece.kind == "whitespace":
            flush()
            continue

        if piece.kind.startswith("protected:"):
            flush()
            route = piece.kind.removeprefix("protected:")
            if route in passthrough_routes:
                ids.extend(_processor_encode_ids(processor, piece.surface))
                continue
            protected_ids, byte_tokens = encode_protected_surface_ids(
                piece.surface,
                selected_pieces=selected_pieces,
                piece_to_id=piece_to_id,
                byte_offset=byte_offset,
            )
            ids.extend(protected_ids)
            protected_byte_tokens += byte_tokens
            continue

        if piece.kind == "apostrophe":
            flush()
            ids.extend(_processor_encode_ids(processor, piece.surface))
            continue

        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            ids.extend(_processor_encode_ids(processor, piece.surface))
            continue

        if piece.boundary_before == "soft":
            segment += (SOFT_MARKER if insert_soft_markers else "") + piece.surface
            continue

        if piece.boundary_before == "hard":
            flush()
            segment = piece.surface
            continue

        segment += piece.surface

    flush()
    return ids, protected_byte_tokens


def encode_finite_protected_soft_marker_split(
    *,
    model_path: Path,
    selected_pieces_path: Path | None,
    lines: list[str],
    byte_count: int,
    split: str,
    insert_soft_markers: bool = True,
    numeric_sp_passthrough: bool = False,
    sp_passthrough_routes: frozenset[str] | set[str] | None = None,
    isolate_sp_passthrough_routes: bool = False,
    byte_fallback_crossing_pieces: bool = False,
    pre_split_sp_passthrough_routes: bool = False,
    tokenizer_name: str = "",
    progress: int = 0,
) -> tuple[int, EncodedSplit]:
    processor = load_sp_processor(model_path)
    selected = selected_piece_strings(selected_pieces_path) if selected_pieces_path else []
    piece_size = _processor_piece_size(processor)
    eos = _processor_eos_id(processor)
    ids: list[int] = []
    protected_byte_tokens = 0
    for line_number, line in enumerate(lines, start=1):
        line_ids, byte_tokens = encode_finite_protected_soft_marker_line_ids(
            line,
            processor=processor,
            selected_pieces=selected,
            protected_piece_offset=piece_size,
            insert_soft_markers=insert_soft_markers,
            numeric_sp_passthrough=numeric_sp_passthrough,
            sp_passthrough_routes=sp_passthrough_routes,
            isolate_sp_passthrough_routes=isolate_sp_passthrough_routes,
            byte_fallback_crossing_pieces=byte_fallback_crossing_pieces,
            pre_split_sp_passthrough_routes=pre_split_sp_passthrough_routes,
        )
        ids.extend(line_ids)
        protected_byte_tokens += byte_tokens
        if eos >= 0:
            ids.append(eos)
        if progress > 0 and line_number % progress == 0:
            print(
                f"encoding {tokenizer_name or model_path.stem} split={split}: "
                f"{line_number:,} lines tokens={len(ids):,} "
                f"protected_byte_tokens={protected_byte_tokens:,}",
                flush=True,
            )
    vocab_size = piece_size + len(selected) + BYTE_VOCAB_SIZE
    return (
        vocab_size,
        EncodedSplit(split, ids, byte_count, len(lines), oov_tokens=protected_byte_tokens),
    )


def _processor_piece_to_id(processor, piece: str) -> int:
    if hasattr(processor, "PieceToId"):
        return int(processor.PieceToId(piece))
    return int(processor.piece_to_id(piece))


def _append_boundary_biased_segment_ids(
    ids: list[int],
    *,
    surface: str,
    soft_boundaries: tuple[int, ...],
    vocab: BoundaryBiasedVocab,
    processor,
    boundary_lambda: float,
) -> None:
    if not surface:
        return
    result = viterbi_segment(
        surface,
        boundaries=soft_boundaries,
        vocab=vocab,
        boundary_lambda=boundary_lambda,
    )
    for sp_piece, piece_surface in zip(result.sp_pieces, result.surfaces):
        piece_id = _processor_piece_to_id(processor, sp_piece)
        if piece_id >= 0:
            ids.append(piece_id)
        else:
            ids.extend(_processor_encode_ids(processor, piece_surface))


def encode_boundary_biased_unigram_line_ids(
    text: str,
    *,
    processor,
    boundary_vocab: BoundaryBiasedVocab,
    selected_pieces: list[str],
    protected_piece_offset: int,
    boundary_lambda: float,
    numeric_sp_passthrough: bool = True,
) -> tuple[list[int], int]:
    piece_to_id = {
        piece: protected_piece_offset + index
        for index, piece in enumerate(selected_pieces)
    }
    byte_offset = protected_piece_offset + len(selected_pieces)
    pieces = analyze_line(text, TurkishTokenizer(preserve_whitespace=True))
    ids: list[int] = []
    protected_byte_tokens = 0
    segment = ""
    segment_boundaries: list[int] = []

    def flush() -> None:
        nonlocal segment, segment_boundaries
        if segment:
            _append_boundary_biased_segment_ids(
                ids,
                surface=segment,
                soft_boundaries=tuple(segment_boundaries),
                vocab=boundary_vocab,
                processor=processor,
                boundary_lambda=boundary_lambda,
            )
            segment = ""
            segment_boundaries = []

    for piece in pieces:
        if piece.kind == "whitespace":
            flush()
            continue

        if piece.kind.startswith("protected:"):
            flush()
            if numeric_sp_passthrough and piece.kind == "protected:numeric_like":
                ids.extend(_processor_encode_ids(processor, piece.surface))
                continue
            protected_ids, byte_tokens = encode_protected_surface_ids(
                piece.surface,
                selected_pieces=selected_pieces,
                piece_to_id=piece_to_id,
                byte_offset=byte_offset,
            )
            ids.extend(protected_ids)
            protected_byte_tokens += byte_tokens
            continue

        if piece.kind == "apostrophe":
            flush()
            ids.extend(_processor_encode_ids(processor, piece.surface))
            continue

        if piece.kind == "suffix" and piece.boundary_before == "hard":
            flush()
            ids.extend(_processor_encode_ids(processor, piece.surface))
            continue

        if piece.boundary_before == "soft":
            segment_boundaries.append(len(segment))
            segment += piece.surface
            continue

        if piece.boundary_before == "hard":
            flush()
            segment = piece.surface
            segment_boundaries = []
            continue

        segment += piece.surface

    flush()
    return ids, protected_byte_tokens


def encode_boundary_biased_unigram_split(
    *,
    model_path: Path,
    vocab_path: Path,
    selected_pieces_path: Path,
    lines: list[str],
    byte_count: int,
    split: str,
    boundary_lambda: float,
    tokenizer_name: str = "",
    progress: int = 0,
) -> tuple[int, EncodedSplit]:
    processor = load_sp_processor(model_path)
    boundary_vocab = BoundaryBiasedVocab.from_vocab_file(vocab_path)
    selected = selected_piece_strings(selected_pieces_path)
    piece_size = _processor_piece_size(processor)
    eos = _processor_eos_id(processor)
    ids: list[int] = []
    protected_byte_tokens = 0
    for line_number, line in enumerate(lines, start=1):
        line_ids, byte_tokens = encode_boundary_biased_unigram_line_ids(
            line,
            processor=processor,
            boundary_vocab=boundary_vocab,
            selected_pieces=selected,
            protected_piece_offset=piece_size,
            boundary_lambda=boundary_lambda,
            numeric_sp_passthrough=True,
        )
        ids.extend(line_ids)
        protected_byte_tokens += byte_tokens
        if eos >= 0:
            ids.append(eos)
        if progress > 0 and line_number % progress == 0:
            print(
                f"encoding {tokenizer_name or model_path.stem} split={split}: "
                f"{line_number:,} lines tokens={len(ids):,} "
                f"protected_byte_tokens={protected_byte_tokens:,}",
                flush=True,
            )
    vocab_size = piece_size + len(selected) + BYTE_VOCAB_SIZE
    return (
        vocab_size,
        EncodedSplit(split, ids, byte_count, len(lines), oov_tokens=protected_byte_tokens),
    )


def encode_tokenizer(
    config: TokenizerConfig,
    splits: dict[str, SplitText],
    *,
    encode_progress: int = 0,
) -> EncodedTokenizer:
    try:
        if config.kind == "custom":
            vocab = build_custom_vocab(
                splits["train"].lines,
                max_vocab_size=config.max_vocab_size,
            )
            encoded = {
                name: encode_custom_split(split.lines, vocab, split.bytes, name)
                for name, split in splits.items()
            }
            return EncodedTokenizer(config, len(vocab), "ok", splits=encoded)
        if config.kind == "utf8_byte":
            encoded = {
                name: encode_utf8_byte_split(split.lines, split.bytes, name)
                for name, split in splits.items()
            }
            return EncodedTokenizer(config, 257, "ok", splits=encoded)
        if config.kind == "sentencepiece":
            if config.path is None or not config.path.exists():
                return EncodedTokenizer(config, 0, "skipped", reason=f"missing model: {config.path}")
            import sentencepiece as spm  # type: ignore[import-not-found]

            processor = spm.SentencePieceProcessor(model_file=str(config.path))
            encoded = {
                name: encode_sentencepiece_split(
                    config.path,
                    split.lines,
                    split.bytes,
                    name,
                    tokenizer_name=config.name,
                    progress=encode_progress,
                )
                for name, split in splits.items()
            }
            return EncodedTokenizer(config, int(processor.GetPieceSize()), "ok", splits=encoded)
        if config.kind == "boundary_biased_unigram_numeric_sp":
            if config.path is None or not config.path.exists():
                return EncodedTokenizer(config, 0, "skipped", reason=f"missing model: {config.path}")
            vocab_path = config.vocab_path or config.path.with_suffix(".vocab")
            if not vocab_path.exists():
                return EncodedTokenizer(config, 0, "skipped", reason=f"missing vocab: {vocab_path}")
            if config.selected_pieces is None or not config.selected_pieces.exists():
                return EncodedTokenizer(
                    config,
                    0,
                    "skipped",
                    reason=f"missing selected pieces: {config.selected_pieces}",
                )
            encoded = {}
            vocab_size = 0
            for name, split in splits.items():
                vocab_size, encoded[name] = encode_boundary_biased_unigram_split(
                    model_path=config.path,
                    vocab_path=vocab_path,
                    selected_pieces_path=config.selected_pieces,
                    lines=split.lines,
                    byte_count=split.bytes,
                    split=name,
                    boundary_lambda=config.boundary_lambda,
                    tokenizer_name=config.name,
                    progress=encode_progress,
                )
            return EncodedTokenizer(config, vocab_size, "ok", splits=encoded)
        if config.kind in {
            "finite_protected_soft_marker",
            "finite_protected_marker_stripped",
            "finite_protected_marker_stripped_numeric_sp",
        }:
            if config.path is None or not config.path.exists():
                return EncodedTokenizer(config, 0, "skipped", reason=f"missing model: {config.path}")
            if config.selected_pieces is not None and not config.selected_pieces.exists():
                return EncodedTokenizer(
                    config,
                    0,
                    "skipped",
                    reason=f"missing selected pieces: {config.selected_pieces}",
                )
            encoded: dict[str, EncodedSplit] = {}
            vocab_size = 0
            for name, split in splits.items():
                vocab_size, encoded[name] = encode_finite_protected_soft_marker_split(
                    model_path=config.path,
                    selected_pieces_path=config.selected_pieces,
                    lines=split.lines,
                    byte_count=split.bytes,
                    split=name,
                    insert_soft_markers=config.kind == "finite_protected_soft_marker",
                    numeric_sp_passthrough=(
                        config.kind == "finite_protected_marker_stripped_numeric_sp"
                    ),
                    sp_passthrough_routes=config.sp_passthrough_routes,
                    isolate_sp_passthrough_routes=config.isolate_sp_passthrough_routes,
                    byte_fallback_crossing_pieces=config.byte_fallback_crossing_pieces,
                    pre_split_sp_passthrough_routes=config.pre_split_sp_passthrough_routes,
                    tokenizer_name=config.name,
                    progress=encode_progress,
                )
            return EncodedTokenizer(config, vocab_size, "ok", splits=encoded)
    except Exception as exc:
        return EncodedTokenizer(config, 0, "skipped", reason=str(exc))
    raise ValueError(f"unsupported tokenizer kind: {config.kind}")


def encode_all(config: ProbeConfig) -> list[EncodedTokenizer]:
    splits = load_split_texts(config.split_dir)
    encoded: list[EncodedTokenizer] = []
    for tokenizer in config.tokenizers:
        print(f"Encoding tokenizer={tokenizer.name} kind={tokenizer.kind}", flush=True)
        result = encode_tokenizer(
            tokenizer,
            splits,
            encode_progress=config.encode_progress,
        )
        encoded.append(result)
        if result.status == "ok":
            train = result.splits["train"]
            valid = result.splits["valid"]
            test = result.splits["test"]
            print(
                f"Encoded tokenizer={tokenizer.name} vocab={result.vocab_size} "
                f"train_tokens={train.tokens} valid_tokens={valid.tokens} "
                f"test_tokens={test.tokens} "
                f"valid_fallback_source_tokens={valid.oov_tokens} "
                f"test_fallback_source_tokens={test.oov_tokens}",
                flush=True,
            )
        else:
            print(
                f"Skipped tokenizer={tokenizer.name} reason={result.reason}",
                flush=True,
            )
    return encoded


def _require_torch():
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as functional
    except Exception as exc:  # pragma: no cover - depends on optional dependency.
        raise RuntimeError("PyTorch is required to run training") from exc
    return torch, nn, functional


def _device(torch, requested: str):
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def build_model(vocab_size: int, model_config: ModelConfig):
    torch, nn, _functional = _require_torch()

    class TinyTransformerLM(nn.Module):
        def __init__(self):
            super().__init__()
            self.token_emb = nn.Embedding(vocab_size, model_config.d_model)
            self.pos_emb = nn.Embedding(model_config.seq_len, model_config.d_model)
            layer = nn.TransformerEncoderLayer(
                d_model=model_config.d_model,
                nhead=model_config.n_heads,
                dim_feedforward=model_config.d_model * model_config.ff_mult,
                dropout=model_config.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.blocks = nn.TransformerEncoder(layer, num_layers=model_config.n_layers)
            self.norm = nn.LayerNorm(model_config.d_model)
            self.lm_head = nn.Linear(model_config.d_model, vocab_size, bias=False)
            self.lm_head.weight = self.token_emb.weight

        def forward(self, input_ids):
            batch, seq_len = input_ids.shape
            positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
            hidden = self.token_emb(input_ids) + self.pos_emb(positions)
            mask = torch.triu(
                torch.ones(seq_len, seq_len, dtype=torch.bool, device=input_ids.device),
                diagonal=1,
            )
            hidden = self.blocks(hidden, mask=mask)
            return self.lm_head(self.norm(hidden))

    return TinyTransformerLM()


def model_param_counts(model) -> tuple[int, int, int]:
    total = sum(parameter.numel() for parameter in model.parameters())
    embedding = model.token_emb.weight.numel() + model.pos_emb.weight.numel()
    return total, embedding, total - embedding


def sample_batch(torch, ids: list[int], *, seq_len: int, batch_size: int, rng: random.Random, device):
    if len(ids) <= seq_len + 1:
        raise ValueError("encoded train split is too short for configured seq_len")
    starts = [rng.randrange(0, len(ids) - seq_len - 1) for _ in range(batch_size)]
    inputs = [ids[start : start + seq_len] for start in starts]
    targets = [ids[start + 1 : start + seq_len + 1] for start in starts]
    return (
        torch.tensor(inputs, dtype=torch.long, device=device),
        torch.tensor(targets, dtype=torch.long, device=device),
    )


def evaluate_loss_stats(model, encoded: EncodedSplit, *, model_config: ModelConfig, device) -> EvalLossStats:
    torch, _nn, functional = _require_torch()
    model.eval()
    total_nll = 0.0
    total_targets = 0
    ids = encoded.ids
    with torch.no_grad():
        for start in range(0, max(0, len(ids) - model_config.seq_len - 1), model_config.seq_len):
            chunk = ids[start : start + model_config.seq_len + 1]
            if len(chunk) < model_config.seq_len + 1:
                continue
            inputs = torch.tensor([chunk[:-1]], dtype=torch.long, device=device)
            targets = torch.tensor([chunk[1:]], dtype=torch.long, device=device)
            logits = model(inputs)
            loss = functional.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                targets.reshape(-1),
                reduction="sum",
            )
            total_nll += float(loss.item())
            total_targets += int(targets.numel())
    if total_targets == 0 or encoded.bytes == 0:
        return EvalLossStats(
            bpb=float("nan"),
            bits_per_token=float("nan"),
            target_tokens=total_targets,
            evaluated_bytes=0.0,
            evaluated_fraction=0.0,
            nll_bits=float("nan"),
        )
    evaluated_fraction = total_targets / max(1, len(ids) - 1)
    evaluated_bytes = encoded.bytes * evaluated_fraction
    nll_bits = total_nll / math.log(2)
    return EvalLossStats(
        bpb=nll_bits / evaluated_bytes,
        bits_per_token=nll_bits / total_targets,
        target_tokens=total_targets,
        evaluated_bytes=evaluated_bytes,
        evaluated_fraction=evaluated_fraction,
        nll_bits=nll_bits,
    )


def evaluate_bpb(model, encoded: EncodedSplit, *, model_config: ModelConfig, device) -> float:
    return evaluate_loss_stats(model, encoded, model_config=model_config, device=device).bpb


def train_one(
    encoded: EncodedTokenizer,
    config: ProbeConfig,
    *,
    output_dir: Path,
) -> TrainMetrics:
    if encoded.status != "ok":
        return TrainMetrics(
            tokenizer=encoded.config.name,
            status=encoded.status,
            vocab_size=encoded.vocab_size,
            reason=encoded.reason,
        )

    torch, _nn, functional = _require_torch()
    torch.manual_seed(config.seed)
    rng = random.Random(config.seed)
    device = _device(torch, config.model.device)
    model = build_model(encoded.vocab_size, config.model).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.model.learning_rate)
    total_params, embedding_params, non_embedding_params = model_param_counts(model)

    train_ids = encoded.splits["train"].ids
    train_tokens_per_byte = encoded.splits["train"].tokens_per_byte
    metrics_path = output_dir / encoded.config.name / "metrics.jsonl"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    best_valid: float | None = None
    final_valid: float | None = None
    tokens_seen = 0

    with metrics_path.open("w", encoding="utf-8") as metrics_file:
        for step in range(1, config.model.max_steps + 1):
            model.train()
            inputs, targets = sample_batch(
                torch,
                train_ids,
                seq_len=config.model.seq_len,
                batch_size=config.model.batch_size,
                rng=rng,
                device=device,
            )
            logits = model(inputs)
            loss = functional.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                targets.reshape(-1),
            )
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            tokens_seen += int(targets.numel())

            if step == 1 or step % config.model.eval_interval == 0 or step == config.model.max_steps:
                valid_stats = evaluate_loss_stats(
                    model,
                    encoded.splits["valid"],
                    model_config=config.model,
                    device=device,
                )
                final_valid = valid_stats.bpb
                best_valid = valid_stats.bpb if best_valid is None else min(best_valid, valid_stats.bpb)
                approx_bytes = tokens_seen / train_tokens_per_byte if train_tokens_per_byte else 0.0
                row = {
                    "step": step,
                    "train_loss_nats_per_token": float(loss.item()),
                    "valid_bpb": valid_stats.bpb,
                    "valid_bits_per_token": valid_stats.bits_per_token,
                    "valid_target_tokens": valid_stats.target_tokens,
                    "valid_evaluated_bytes": valid_stats.evaluated_bytes,
                    "valid_evaluated_fraction": valid_stats.evaluated_fraction,
                    "tokens_seen": tokens_seen,
                    "approx_bytes_seen": approx_bytes,
                }
                metrics_file.write(json.dumps(row, ensure_ascii=False) + "\n")
                metrics_file.flush()
                print(
                    f"{encoded.config.name}: step={step} "
                    f"tokens_seen={tokens_seen} approx_bytes_seen={approx_bytes:.0f} "
                    f"valid_bpb={valid_stats.bpb:.6f}",
                    flush=True,
                )

    valid_final_stats = evaluate_loss_stats(
        model,
        encoded.splits["valid"],
        model_config=config.model,
        device=device,
    )
    test_stats = evaluate_loss_stats(model, encoded.splits["test"], model_config=config.model, device=device)
    return TrainMetrics(
        tokenizer=encoded.config.name,
        status="ok",
        vocab_size=encoded.vocab_size,
        total_params=total_params,
        embedding_params=embedding_params,
        non_embedding_params=non_embedding_params,
        steps=config.model.max_steps,
        tokens_seen=tokens_seen,
        approx_bytes_seen=tokens_seen / train_tokens_per_byte if train_tokens_per_byte else 0.0,
        best_valid_bpb=best_valid,
        final_valid_bpb=final_valid,
        test_bpb=test_stats.bpb,
        final_valid_bits_per_token=valid_final_stats.bits_per_token,
        test_bits_per_token=test_stats.bits_per_token,
        final_valid_target_tokens=valid_final_stats.target_tokens,
        test_target_tokens=test_stats.target_tokens,
        final_valid_evaluated_bytes=valid_final_stats.evaluated_bytes,
        test_evaluated_bytes=test_stats.evaluated_bytes,
    )


def _fmt_float(value: float | None, digits: int = 6) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def format_report(
    config: ProbeConfig,
    encoded_tokenizers: list[EncodedTokenizer],
    train_metrics: list[TrainMetrics],
    *,
    dry_run: bool,
) -> str:
    lines = [
        "# Tiny LM Bits-Per-Byte Probe",
        "",
        f"Config: `{config.path.as_posix()}`",
        f"Split dir: `{config.split_dir.as_posix()}`",
        f"Dry run: `{dry_run}`",
        "",
        "This is an early screening probe, not final LLM tokenizer evidence.",
        "",
        "## Model Config",
        "",
        "| Setting | Value |",
        "| --- | ---: |",
        f"| seq_len | {config.model.seq_len} |",
        f"| batch_size | {config.model.batch_size} |",
        f"| max_steps | {config.model.max_steps} |",
        f"| eval_interval | {config.model.eval_interval} |",
        f"| d_model | {config.model.d_model} |",
        f"| n_layers | {config.model.n_layers} |",
        f"| n_heads | {config.model.n_heads} |",
        "",
        "## Encoding Summary",
        "",
        "| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for encoded in encoded_tokenizers:
        if encoded.status != "ok":
            lines.append(
                f"| {encoded.config.name} | {encoded.status} | {encoded.vocab_size} |  | 0 | 0 | 0 | 0.000000 | 0 | 0.000000 | {encoded.reason} |"
            )
            continue
        for split_name in ("train", "valid", "test"):
            split = encoded.splits[split_name]
            lines.append(
                f"| {encoded.config.name} | {encoded.status} | {encoded.vocab_size} | "
                f"{split_name} | {split.lines} | {split.bytes} | {split.tokens} | "
                f"{split.tokens_per_byte:.6f} | {split.oov_tokens} | "
                f"{split.oov_rate:.6f} | {encoded.reason} |"
            )

    lines.extend(
        [
            "",
            "## Training Results",
            "",
            "| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    if dry_run:
        lines.append("| dry_run | skipped | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  | no training run |")
    else:
        for row in train_metrics:
            lines.append(
                f"| {row.tokenizer} | {row.status} | {row.vocab_size} | "
                f"{row.total_params} | {row.embedding_params} | {row.non_embedding_params} | "
                f"{row.steps} | {row.tokens_seen} | {row.approx_bytes_seen:.0f} | "
                f"{_fmt_float(row.best_valid_bpb)} | {_fmt_float(row.final_valid_bpb)} | "
                f"{_fmt_float(row.test_bpb)} | {row.reason} |"
            )

    if not dry_run and train_metrics:
        lines.extend(
            [
                "",
                "## Loss Accounting",
                "",
                "This table reports the same eval pass used for BPB, converted back",
                "to bits/token. Values above `log2(vocab)` indicate an early or",
                "pathological optimization regime and should not be read as",
                "converged LM quality.",
                "",
                "| Tokenizer | log2(vocab) | Valid bits/token | Test bits/token | Valid target tokens | Test target tokens | Valid evaluated bytes | Test evaluated bytes |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in train_metrics:
            uniform = math.log2(row.vocab_size) if row.vocab_size > 0 else float("nan")
            lines.append(
                f"| {row.tokenizer} | {_fmt_float(uniform, 4)} | "
                f"{_fmt_float(row.final_valid_bits_per_token, 4)} | "
                f"{_fmt_float(row.test_bits_per_token, 4)} | "
                f"{row.final_valid_target_tokens} | {row.test_target_tokens} | "
                f"{row.final_valid_evaluated_bytes:.0f} | {row.test_evaluated_bytes:.0f} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- Compare only byte-normalized validation/test loss, not token perplexity.",
            "- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.",
            "- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.",
            "- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.",
            "- This script does not make the tokenizer LLM-ready.",
            "- A negative result should be read with the protocol caveats for the active experiment.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_encoded_artifacts(config: ProbeConfig, encoded_tokenizers: list[EncodedTokenizer]) -> None:
    target = config.output_dir / "encoded_stats.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for encoded in encoded_tokenizers:
            item = {
                "tokenizer": encoded.config.name,
                "status": encoded.status,
                "reason": encoded.reason,
                "vocab_size": encoded.vocab_size,
                "splits": {
                    name: {
                        "lines": split.lines,
                        "bytes": split.bytes,
                        "tokens": split.tokens,
                        "tokens_per_byte": split.tokens_per_byte,
                        "oov_tokens": split.oov_tokens,
                        "oov_rate": split.oov_rate,
                    }
                    for name, split in encoded.splits.items()
                },
            }
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run or dry-run the v1.8 tiny LM BPB probe.")
    parser.add_argument("config")
    parser.add_argument("--dry-run", action="store_true", help="Only encode splits and write the report.")
    parser.add_argument(
        "--tokenizer",
        action="append",
        default=[],
        help="Restrict to one or more tokenizer names.",
    )
    parser.add_argument("--max-steps", type=int, help="Override configured max_steps.")
    parser.add_argument("--eval-interval", type=int, help="Override configured eval_interval.")
    parser.add_argument("--encode-progress", type=int, help="Print encode progress every N lines.")
    parser.add_argument("--report-out", help="Override configured public report path.")
    parser.add_argument("--output-dir", help="Override configured private output directory.")
    args = parser.parse_args(argv)

    config = load_probe_config(args.config)
    if args.max_steps is not None:
        if args.max_steps <= 0:
            raise ValueError("--max-steps must be positive")
        config = replace(
            config,
            model=replace(config.model, max_steps=args.max_steps),
        )
    if args.eval_interval is not None:
        if args.eval_interval <= 0:
            raise ValueError("--eval-interval must be positive")
        config = replace(
            config,
            model=replace(config.model, eval_interval=args.eval_interval),
        )
    if args.encode_progress is not None:
        if args.encode_progress < 0:
            raise ValueError("--encode-progress must be non-negative")
        config = replace(config, encode_progress=args.encode_progress)
    if args.report_out:
        config = replace(config, report_out=Path(args.report_out))
    if args.output_dir:
        config = replace(config, output_dir=Path(args.output_dir))
    if args.tokenizer:
        selected = set(args.tokenizer)
        config = ProbeConfig(
            path=config.path,
            split_dir=config.split_dir,
            output_dir=config.output_dir,
            report_out=config.report_out,
            seed=config.seed,
            encode_progress=config.encode_progress,
            model=config.model,
            tokenizers=[tokenizer for tokenizer in config.tokenizers if tokenizer.name in selected],
        )
        unknown = selected - {tokenizer.name for tokenizer in config.tokenizers}
        if unknown:
            raise ValueError(f"unknown tokenizer name(s): {', '.join(sorted(unknown))}")

    print(
        f"Starting tiny LM BPB probe: dry_run={args.dry_run} "
        f"tokenizers={len(config.tokenizers)} split_dir={config.split_dir}",
        flush=True,
    )
    encoded_tokenizers = encode_all(config)
    write_encoded_artifacts(config, encoded_tokenizers)

    train_metrics: list[TrainMetrics] = []
    if not args.dry_run:
        for encoded in encoded_tokenizers:
            print(f"Training tokenizer={encoded.config.name}", flush=True)
            train_metrics.append(train_one(encoded, config, output_dir=config.output_dir))

    report = format_report(
        config,
        encoded_tokenizers,
        train_metrics,
        dry_run=args.dry_run,
    )
    config.report_out.parent.mkdir(parents=True, exist_ok=True)
    config.report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {config.report_out}")
    print(f"wrote_private_stats: {config.output_dir / 'encoded_stats.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
