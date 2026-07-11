"""SentencePiece processor helpers for the v3.8 production chain.

Moved verbatim from scripts/evaluate_v2_finite_protected_sp64_intrinsic.py
(ensure_sentencepiece, load_sp_processor) and scripts/run_tiny_lm_bpb_probe.py
(_processor_piece_size, _processor_eos_id, _processor_decode_ids) in Faz 2.

sentencepiece is imported lazily so that importing this module (and the
package) works without the optional ``production`` extra installed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def ensure_sentencepiece():
    if importlib.util.find_spec("sentencepiece") is None:
        raise RuntimeError("sentencepiece is not installed")
    import sentencepiece as spm  # type: ignore[import-not-found]

    return spm


def load_sp_processor(model_path: Path):
    spm = ensure_sentencepiece()
    processor = spm.SentencePieceProcessor()
    processor.Load(str(model_path))
    return processor


def _processor_piece_size(processor) -> int:
    if hasattr(processor, "GetPieceSize"):
        return int(processor.GetPieceSize())
    return int(processor.PieceSize())


def _processor_eos_id(processor) -> int:
    return int(processor.eos_id()) if hasattr(processor, "eos_id") else -1


def _processor_decode_ids(processor, ids: list[int]) -> str | None:
    if not ids:
        return ""
    if hasattr(processor, "DecodeIds"):
        return str(processor.DecodeIds(ids))
    if hasattr(processor, "decode"):
        return str(processor.decode(ids))
    return None
