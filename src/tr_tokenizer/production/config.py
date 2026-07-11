"""Tokenizer/probe TOML config parsing for the v3.8 production chain.

Moved verbatim from scripts/run_tiny_lm_bpb_probe.py (TokenizerConfig,
ModelConfig, ProbeConfig, load_probe_config and field helpers),
scripts/tokenize_v3_1_corpus_smoke.py (find_tokenizer, normalize_max_lines),
and scripts/evaluate_v2_protected_encoder.py (ProtectedPiece,
load_selected_pieces) plus selected_piece_strings from
scripts/evaluate_v2_finite_protected_sp64_intrinsic.py in Faz 2.

TOML parsing uses the standard-library ``tomllib`` (Python >= 3.11). The
legacy pure-Python fallback parser remains in scripts/report_baseline_matrix.py
for the archived research tooling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TokenizerConfig:
    name: str
    kind: str
    path: Path | None = None
    vocab_path: Path | None = None
    max_vocab_size: int | None = None
    selected_pieces: Path | None = None
    boundary_lambda: float = 0.0
    sp_passthrough_routes: frozenset[str] = field(default_factory=frozenset)
    isolate_sp_passthrough_routes: bool = False
    byte_fallback_crossing_pieces: bool = False
    pre_split_sp_passthrough_routes: bool = False


@dataclass(frozen=True)
class ModelConfig:
    seq_len: int
    batch_size: int
    max_steps: int
    eval_interval: int
    learning_rate: float
    d_model: int
    n_layers: int
    n_heads: int
    ff_mult: int
    dropout: float
    device: str


@dataclass(frozen=True)
class ProbeConfig:
    path: Path
    split_dir: Path
    output_dir: Path
    report_out: Path
    seed: int
    encode_progress: int
    model: ModelConfig
    tokenizers: list[TokenizerConfig]


@dataclass(frozen=True)
class ProtectedPiece:
    piece: str
    count: int
    category: str
    reason: str
    bytes: int
    routes: tuple[str, ...]


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib  # type: ignore[import-not-found]
    except ModuleNotFoundError as error:  # pragma: no cover - py<3.11 only
        raise RuntimeError(
            "tr_tokenizer.production requires Python >= 3.11 for tomllib"
        ) from error
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _string_field(item: dict[str, Any], field: str, *, context: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} requires string field {field!r}")
    return value


def _int_field(item: dict[str, Any], field: str, *, context: str) -> int:
    value = item.get(field)
    if not isinstance(value, int):
        raise ValueError(f"{context} requires integer field {field!r}")
    return value


def _float_field(item: dict[str, Any], field: str, *, context: str) -> float:
    value = item.get(field)
    if not isinstance(value, (float, int)):
        raise ValueError(f"{context} requires numeric field {field!r}")
    return float(value)


def load_probe_config(path: str | Path) -> ProbeConfig:
    config_path = Path(path)
    raw = _load_toml(config_path)
    settings = raw.get("settings", {})
    model_raw = raw.get("model", {})
    if not isinstance(settings, dict):
        raise ValueError("[settings] must be a table")
    if not isinstance(model_raw, dict):
        raise ValueError("[model] must be a table")

    tokenizers: list[TokenizerConfig] = []
    for item in raw.get("tokenizers", []):
        if not isinstance(item, dict) or item.get("enabled", True) is False:
            continue
        name = _string_field(item, "name", context="tokenizer")
        kind = _string_field(item, "kind", context=f"tokenizer {name}")
        if kind not in {
            "custom",
            "sentencepiece",
            "utf8_byte",
            "finite_protected_soft_marker",
            "finite_protected_marker_stripped",
            "finite_protected_marker_stripped_numeric_sp",
            "boundary_biased_unigram_numeric_sp",
        }:
            raise ValueError(f"unsupported tokenizer kind for {name}: {kind}")
        routes_raw = item.get("sp_passthrough_routes", [])
        if isinstance(routes_raw, str):
            sp_passthrough_routes = frozenset(
                route.strip() for route in routes_raw.split(",") if route.strip()
            )
        elif isinstance(routes_raw, list) and all(isinstance(route, str) for route in routes_raw):
            sp_passthrough_routes = frozenset(routes_raw)
        else:
            raise ValueError(
                f"tokenizer {name} sp_passthrough_routes must be a string list or comma string"
            )
        tokenizers.append(
            TokenizerConfig(
                name=name,
                kind=kind,
                path=Path(item["path"]) if isinstance(item.get("path"), str) else None,
                vocab_path=(
                    Path(item["vocab_path"])
                    if isinstance(item.get("vocab_path"), str)
                    else None
                ),
                max_vocab_size=item.get("max_vocab_size")
                if isinstance(item.get("max_vocab_size"), int)
                else None,
                selected_pieces=(
                    Path(item["selected_pieces"])
                    if isinstance(item.get("selected_pieces"), str)
                    else None
                ),
                boundary_lambda=float(item.get("boundary_lambda", 0.0)),
                sp_passthrough_routes=sp_passthrough_routes,
                isolate_sp_passthrough_routes=bool(
                    item.get("isolate_sp_passthrough_routes", False)
                ),
                byte_fallback_crossing_pieces=bool(
                    item.get("byte_fallback_crossing_pieces", False)
                ),
                pre_split_sp_passthrough_routes=bool(
                    item.get("pre_split_sp_passthrough_routes", False)
                ),
            )
        )

    return ProbeConfig(
        path=config_path,
        split_dir=Path(_string_field(settings, "split_dir", context="settings")),
        output_dir=Path(settings.get("output_dir", "artifacts/private/v1_8_tiny_lm_bpb_probe")),
        report_out=Path(settings.get("report_out", "artifacts/v1_8_tiny_lm_bpb_probe.md")),
        seed=_int_field(settings, "seed", context="settings"),
        encode_progress=int(settings.get("encode_progress", 0)),
        model=ModelConfig(
            seq_len=_int_field(model_raw, "seq_len", context="model"),
            batch_size=_int_field(model_raw, "batch_size", context="model"),
            max_steps=_int_field(model_raw, "max_steps", context="model"),
            eval_interval=_int_field(model_raw, "eval_interval", context="model"),
            learning_rate=_float_field(model_raw, "learning_rate", context="model"),
            d_model=_int_field(model_raw, "d_model", context="model"),
            n_layers=_int_field(model_raw, "n_layers", context="model"),
            n_heads=_int_field(model_raw, "n_heads", context="model"),
            ff_mult=_int_field(model_raw, "ff_mult", context="model"),
            dropout=_float_field(model_raw, "dropout", context="model"),
            device=_string_field(model_raw, "device", context="model"),
        ),
        tokenizers=tokenizers,
    )


def find_tokenizer(config_path: Path, name: str) -> TokenizerConfig:
    config = load_probe_config(config_path)
    for tokenizer in config.tokenizers:
        if tokenizer.name == name:
            return tokenizer
    available = ", ".join(tokenizer.name for tokenizer in config.tokenizers)
    raise ValueError(f"tokenizer {name!r} not found. Available: {available}")


def normalize_max_lines(value: int | None) -> int | None:
    if value is not None and value <= 0:
        return None
    return value


def load_selected_pieces(path: str | Path) -> list[ProtectedPiece]:
    pieces: list[ProtectedPiece] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n")
        expected = "piece\tcount\tcategory\treason\tbytes\troutes"
        if header != expected:
            raise ValueError(f"unexpected selected-piece header: {header!r}")
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            piece, count_raw, category, reason, bytes_raw, routes_raw = line.split("\t")
            pieces.append(
                ProtectedPiece(
                    piece=piece,
                    count=int(count_raw),
                    category=category,
                    reason=reason,
                    bytes=int(bytes_raw),
                    routes=tuple(route for route in routes_raw.split(",") if route),
                )
            )
    return pieces


def selected_piece_strings(selected_path: Path) -> list[str]:
    pieces = [piece.piece for piece in load_selected_pieces(selected_path)]
    return sorted((piece for piece in pieces if piece), key=lambda item: (-len(item), item))
