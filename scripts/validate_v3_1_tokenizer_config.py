from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_v2_finite_protected_sp64_intrinsic import load_sp_processor  # noqa: E402


REQUIRED_TOP_LEVEL = {
    "schema_version",
    "status",
    "tokenizer_name",
    "model",
    "id_space",
    "sentencepiece_meta_tokens",
    "special_token_registry",
    "sidecar",
    "training_preprocessing",
}

REQUIRED_SIDECAR_ROUTES = {
    "percent_encoded",
    "azerbaijani_word",
    "url",
    "technical_comparator",
}


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def as_dict(value: Any, failures: list[str], path: str) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    failures.append(f"{path} must be an object")
    return {}


def validate_config(config_path: Path) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    require(isinstance(raw, dict), failures, "root must be an object")
    if not isinstance(raw, dict):
        return failures, warnings

    missing = REQUIRED_TOP_LEVEL - set(raw)
    require(not missing, failures, f"missing top-level keys: {sorted(missing)}")

    model = as_dict(raw.get("model"), failures, "model")
    id_space = as_dict(raw.get("id_space"), failures, "id_space")
    meta = as_dict(raw.get("sentencepiece_meta_tokens"), failures, "sentencepiece_meta_tokens")
    registry = as_dict(raw.get("special_token_registry"), failures, "special_token_registry")
    sidecar = as_dict(raw.get("sidecar"), failures, "sidecar")
    training = as_dict(raw.get("training_preprocessing"), failures, "training_preprocessing")

    sp_model_path = Path(str(model.get("sp_model_path", "")))
    require(sp_model_path.exists(), failures, f"SP model path does not exist: {sp_model_path}")
    processor = load_sp_processor(sp_model_path) if sp_model_path.exists() else None
    if processor is not None:
        piece_size = int(processor.GetPieceSize())
        require(
            int(model.get("sp_vocab_size", -1)) == piece_size,
            failures,
            f"model.sp_vocab_size does not match SP model size: {model.get('sp_vocab_size')} != {piece_size}",
        )
        require(
            int(id_space.get("sp_id_end_exclusive", -1)) == piece_size,
            failures,
            "id_space.sp_id_end_exclusive must equal SP piece size",
        )
        require(
            int(id_space.get("byte_fallback_start", -1)) == piece_size,
            failures,
            "byte_fallback_start must equal SP piece size",
        )
        require(
            int(id_space.get("byte_fallback_size", -1)) == 256,
            failures,
            "byte_fallback_size must be 256",
        )
        require(
            int(id_space.get("byte_fallback_end_exclusive", -1))
            == piece_size + int(id_space.get("byte_fallback_size", 0)),
            failures,
            "byte_fallback_end_exclusive must equal start + size",
        )
        observed = {
            "unk": (int(processor.unk_id()), str(processor.IdToPiece(processor.unk_id()))),
            "bos": (int(processor.bos_id()), str(processor.IdToPiece(processor.bos_id()))),
            "eos": (int(processor.eos_id()), str(processor.IdToPiece(processor.eos_id()))),
            "pad": (int(processor.pad_id()), None),
        }
        for name, (observed_id, observed_piece) in observed.items():
            entry = as_dict(meta.get(name), failures, f"sentencepiece_meta_tokens.{name}")
            require(
                int(entry.get("id", -999)) == observed_id,
                failures,
                f"SP meta id mismatch for {name}: config {entry.get('id')} != model {observed_id}",
            )
            if observed_piece is not None:
                require(
                    entry.get("piece") == observed_piece,
                    failures,
                    f"SP meta piece mismatch for {name}: config {entry.get('piece')} != model {observed_piece}",
                )

    byte_end = int(id_space.get("byte_fallback_end_exclusive", -1))
    effective_vocab_size = int(id_space.get("current_effective_vocab_size", -1))
    require(
        effective_vocab_size >= byte_end,
        failures,
        "current_effective_vocab_size must be >= byte_fallback_end_exclusive",
    )

    control_start = id_space.get("control_token_start")
    control_end = id_space.get("control_token_end_exclusive")
    if control_start is not None or control_end is not None:
        require(
            int(control_start) == byte_end,
            failures,
            "control_token_start must equal byte_fallback_end_exclusive",
        )
        require(
            int(control_end) <= effective_vocab_size,
            failures,
            "control_token_end_exclusive must be <= current_effective_vocab_size",
        )

    assigned_controls = registry.get("assigned", {})
    if assigned_controls:
        require(isinstance(assigned_controls, dict), failures, "special_token_registry.assigned must be an object")
    if isinstance(assigned_controls, dict):
        seen_control_ids: dict[int, str] = {}
        for token, raw_id in assigned_controls.items():
            try:
                token_id = int(raw_id)
            except (TypeError, ValueError):
                failures.append(f"assigned control token {token!r} id must be an integer")
                continue
            require(
                byte_end <= token_id < effective_vocab_size,
                failures,
                f"assigned control token {token!r} id {token_id} must be in control range",
            )
            if token_id in seen_control_ids:
                failures.append(
                    f"assigned control token id collision: {token!r} and {seen_control_ids[token_id]!r} both use {token_id}"
                )
            seen_control_ids[token_id] = str(token)

    aliases = registry.get("aliases", {})
    if aliases:
        require(isinstance(aliases, dict), failures, "special_token_registry.aliases must be an object")
    if isinstance(aliases, dict):
        sp_end = int(id_space.get("sp_id_end_exclusive", -1))
        for alias, raw_id in aliases.items():
            try:
                alias_id = int(raw_id)
            except (TypeError, ValueError):
                failures.append(f"special token alias {alias!r} id must be an integer")
                continue
            require(
                0 <= alias_id < sp_end,
                failures,
                f"special token alias {alias!r} id {alias_id} must point to an SP id",
            )

    route_labels = set(sidecar.get("route_labels", []))
    passthrough_routes = set(sidecar.get("sp_passthrough_routes", []))
    require(
        REQUIRED_SIDECAR_ROUTES <= passthrough_routes,
        failures,
        f"missing required passthrough routes: {sorted(REQUIRED_SIDECAR_ROUTES - passthrough_routes)}",
    )
    require(
        passthrough_routes <= route_labels,
        failures,
        f"passthrough routes not present in route labels: {sorted(passthrough_routes - route_labels)}",
    )
    require(
        sidecar.get("token_boundary_alignment") is False,
        failures,
        "current v3.1 config must explicitly set token_boundary_alignment=false",
    )

    known_conflict = str(registry.get("known_conflict", ""))
    if registry.get("status") != "frozen":
        warnings.append("special_token_registry is not frozen")
    require(
        "pad" in known_conflict.lower() and "unk" in known_conflict.lower(),
        failures,
        "known_conflict must document the <pad> vs <unk> id conflict",
    )
    require(
        training.get("token_dtype") == "uint32_le",
        failures,
        "training_preprocessing.token_dtype must be uint32_le",
    )
    require(
        training.get("loss_mask_dtype") == "uint8",
        failures,
        "training_preprocessing.loss_mask_dtype must be uint8",
    )
    if raw.get("status") != "training_final":
        warnings.append(f"config status is {raw.get('status')!r}, not training_final")
    return failures, warnings


def format_report(config_path: Path, failures: list[str], warnings: list[str]) -> str:
    status = "PASS" if not failures else "FAIL"
    lines = [
        "# v3.1 Tokenizer Config Validation",
        "",
        f"Config: `{config_path.as_posix()}`",
        f"Status: `{status}`",
        "",
        "## Failures",
        "",
    ]
    if failures:
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.append("None.")
    lines.extend(["", "## Warnings", ""])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("None.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Validate v3.1 tokenizer config invariants.")
    parser.add_argument(
        "--config",
        default="configs/tokenizer_config.v3_1.draft.json",
    )
    parser.add_argument("--report-out", default="artifacts/v3_1_tokenizer_config_validation.md")
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    failures, warnings = validate_config(config_path)
    report = format_report(config_path, failures, warnings)
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    print(f"wrote_report: {report_out}")
    if failures or (warnings and args.fail_on_warning):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
