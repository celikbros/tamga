"""v3.8 production tokenization chain (extracted from scripts/, Faz 2).

This package is the single source of truth for the code that produced the
frozen v3.8 tokenized package:

- ``detector``: protected-span route detection (``analyze_line``) on top of the
  deterministic ``TurkishTokenizer`` pretokenizer.
- ``spans``: byte/char span types, ``protected_spans``, and loss-mask helpers.
- ``sp``: SentencePiece processor loading and id helpers (sentencepiece is
  imported lazily; install the ``production`` extra).
- ``config``: TOML probe/tokenizer config parsing (``load_probe_config``,
  ``find_tokenizer``) and selected-piece loading.

Behavioral contract: this code was moved verbatim from the research scripts
and is gated by bit-identical output checks against the pre-move chain
(docs/handover_iyilestirme_yol_haritasi.md, Faz 2). Do not change behavior
here without re-running those gates; the v3.8 id contract is frozen.

The original script locations re-export these names for backward
compatibility, so historical commands and imports keep working.
"""

from tr_tokenizer.production.config import (
    ModelConfig,
    ProbeConfig,
    ProtectedPiece,
    TokenizerConfig,
    find_tokenizer,
    load_probe_config,
    load_selected_pieces,
    normalize_max_lines,
    selected_piece_strings,
)
from tr_tokenizer.production.detector import (
    PROTECTED_KIND_CHECKS,
    Piece,
    analyze_line,
    classify_token,
    protected_kind,
    source_surface,
)
from tr_tokenizer.production.sp import (
    _processor_decode_ids,
    _processor_eos_id,
    _processor_piece_size,
    ensure_sentencepiece,
    load_sp_processor,
)
from tr_tokenizer.production.spans import (
    EncodedTokenSpan,
    Span,
    char_to_byte_offsets,
    protected_spans,
    span_to_json,
    token_mask_for_line,
)

__all__ = [
    "PROTECTED_KIND_CHECKS",
    "EncodedTokenSpan",
    "ModelConfig",
    "Piece",
    "ProbeConfig",
    "ProtectedPiece",
    "Span",
    "TokenizerConfig",
    "_processor_decode_ids",
    "_processor_eos_id",
    "_processor_piece_size",
    "analyze_line",
    "char_to_byte_offsets",
    "classify_token",
    "ensure_sentencepiece",
    "find_tokenizer",
    "load_probe_config",
    "load_selected_pieces",
    "load_sp_processor",
    "normalize_max_lines",
    "protected_kind",
    "protected_spans",
    "selected_piece_strings",
    "source_surface",
    "span_to_json",
    "token_mask_for_line",
]
