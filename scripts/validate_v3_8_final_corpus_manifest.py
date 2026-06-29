from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "v3.8-final-corpus-manifest-1"
SUPPORTED_CORPUS_FORMATS = {"text", "jsonl"}
SUPPORTED_DEDUP_STATUSES = {"complete", "waived"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def warn(condition: bool, warnings: list[str], message: str) -> None:
    if not condition:
        warnings.append(message)


def resolve_path(value: Any, *, base_dir: Path) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return base_dir / path


def validate_path(
    value: Any,
    *,
    base_dir: Path,
    allow_missing_paths: bool,
    failures: list[str],
    label: str,
) -> Path:
    path = resolve_path(value, base_dir=base_dir)
    if not allow_missing_paths:
        require(path.exists(), failures, f"{label} path does not exist: {path}")
    return path


def validate_manifest(
    *,
    manifest_path: Path,
    base_dir: Path,
    allow_missing_paths: bool = False,
) -> tuple[list[str], list[str], dict[str, Any]]:
    failures: list[str] = []
    warnings: list[str] = []
    manifest = read_json(manifest_path)

    require(
        manifest.get("schema_version") == SCHEMA_VERSION,
        failures,
        f"schema_version must be {SCHEMA_VERSION!r}",
    )

    corpus = manifest.get("corpus")
    require(isinstance(corpus, dict), failures, "corpus must be an object")
    corpus = corpus if isinstance(corpus, dict) else {}
    frozen = corpus.get("frozen")
    require(frozen is True, failures, "corpus.frozen must be true")
    corpus_format = corpus.get("format")
    require(
        corpus_format in SUPPORTED_CORPUS_FORMATS,
        failures,
        f"corpus.format must be one of {sorted(SUPPORTED_CORPUS_FORMATS)}",
    )
    text_path = validate_path(
        corpus.get("text_path", ""),
        base_dir=base_dir,
        allow_missing_paths=allow_missing_paths,
        failures=failures,
        label="corpus.text_path",
    )
    if corpus_format == "jsonl":
        require(bool(corpus.get("text_field")), failures, "corpus.text_field is required for jsonl")

    dedup = manifest.get("dedup")
    require(isinstance(dedup, dict), failures, "dedup must be an object")
    dedup = dedup if isinstance(dedup, dict) else {}
    dedup_status = dedup.get("status")
    require(
        dedup_status in SUPPORTED_DEDUP_STATUSES,
        failures,
        f"dedup.status must be one of {sorted(SUPPORTED_DEDUP_STATUSES)}",
    )
    if dedup_status == "complete":
        require(bool(dedup.get("method")), failures, "dedup.method is required when dedup is complete")
    if dedup.get("report_path"):
        validate_path(
            dedup.get("report_path"),
            base_dir=base_dir,
            allow_missing_paths=allow_missing_paths,
            failures=failures,
            label="dedup.report_path",
        )

    mixture = manifest.get("mixture")
    require(isinstance(mixture, list) and bool(mixture), failures, "mixture must be a non-empty list")
    mixture_rows = mixture if isinstance(mixture, list) else []
    share_total = 0.0
    for index, row in enumerate(mixture_rows, start=1):
        if not isinstance(row, dict):
            failures.append(f"mixture row {index} must be an object")
            continue
        require(bool(row.get("name")), failures, f"mixture row {index} requires name")
        require(bool(row.get("language")), failures, f"mixture row {index} requires language")
        require(bool(row.get("domain")), failures, f"mixture row {index} requires domain")
        if "share" in row:
            try:
                share = float(row.get("share"))
            except (TypeError, ValueError):
                failures.append(f"mixture row {index} share must be numeric")
                share = 0.0
            require(share >= 0.0, failures, f"mixture row {index} share must be non-negative")
            share_total += share
        if row.get("source_path"):
            validate_path(
                row.get("source_path"),
                base_dir=base_dir,
                allow_missing_paths=allow_missing_paths,
                failures=failures,
                label=f"mixture row {index} source_path",
            )
    if any(isinstance(row, dict) and "share" in row for row in mixture_rows):
        warn(abs(share_total - 1.0) <= 0.02, warnings, f"mixture shares sum to {share_total:.6f}, not ~1.0")

    normalization = manifest.get("normalization")
    require(isinstance(normalization, dict), failures, "normalization must be an object")
    normalization = normalization if isinstance(normalization, dict) else {}
    require(bool(normalization.get("policy")), failures, "normalization.policy is required")
    require(
        isinstance(normalization.get("already_applied"), bool),
        failures,
        "normalization.already_applied must be boolean",
    )
    warn(
        normalization.get("policy") == "identity",
        warnings,
        "normalization.policy is not identity; tokenizer retrain settings must be reviewed",
    )

    registry = manifest.get("tokenizer_registry")
    require(isinstance(registry, dict), failures, "tokenizer_registry must be an object")
    registry = registry if isinstance(registry, dict) else {}
    require(
        registry.get("v3_7_registry_unchanged") is True,
        failures,
        "tokenizer_registry.v3_7_registry_unchanged must be true",
    )
    expected_ids = {
        "effective_vocab_size": 64384,
        "sp_vocab_size": 64000,
        "byte_fallback_start": 64000,
        "byte_fallback_end_exclusive": 64256,
        "control_start": 64256,
        "control_end_exclusive": 64384,
        "pad_id": 64256,
        "unk_id": 0,
    }
    for key, expected in expected_ids.items():
        if key in registry:
            require(int(registry[key]) == expected, failures, f"tokenizer_registry.{key} must be {expected}")
        else:
            warnings.append(f"tokenizer_registry.{key} is missing")

    training_sample = manifest.get("training_sample", {})
    require(isinstance(training_sample, dict), failures, "training_sample must be an object if present")
    training_sample = training_sample if isinstance(training_sample, dict) else {}
    use_full = training_sample.get("use_full_corpus")
    require(isinstance(use_full, bool), failures, "training_sample.use_full_corpus must be boolean")
    if use_full is False:
        require(
            training_sample.get("max_bytes") or training_sample.get("max_lines") or training_sample.get("sample_manifest_path"),
            failures,
            "training_sample requires max_bytes, max_lines, or sample_manifest_path when not using full corpus",
        )

    document_boundaries = manifest.get("document_boundaries", {})
    require(
        isinstance(document_boundaries, dict),
        failures,
        "document_boundaries must be an object if present",
    )
    if isinstance(document_boundaries, dict) and "preserve" in document_boundaries:
        require(
            isinstance(document_boundaries.get("preserve"), bool),
            failures,
            "document_boundaries.preserve must be boolean",
        )

    facts: dict[str, Any] = {
        "schema_version": manifest.get("schema_version", ""),
        "corpus_name": corpus.get("name", ""),
        "corpus_text_path": str(text_path),
        "corpus_format": corpus_format,
        "dedup_status": dedup_status,
        "dedup_method": dedup.get("method", ""),
        "mixture_rows": len(mixture_rows),
        "mixture_share_total": round(share_total, 6),
        "normalization_policy": normalization.get("policy", ""),
        "normalization_already_applied": normalization.get("already_applied", ""),
        "registry_unchanged": registry.get("v3_7_registry_unchanged", ""),
        "training_sample_use_full_corpus": training_sample.get("use_full_corpus", ""),
        "allow_missing_paths": allow_missing_paths,
    }
    return failures, warnings, facts


def format_report(
    *,
    manifest_path: Path,
    base_dir: Path,
    failures: list[str],
    warnings: list[str],
    facts: dict[str, Any],
) -> str:
    status = "PASS" if not failures else "FAIL"
    lines = [
        "# v3.8 Final Corpus Manifest Validation",
        "",
        f"Manifest: `{manifest_path}`",
        f"Base dir: `{base_dir}`",
        f"Status: `{status}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    for key, value in facts.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Failures", ""])
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
    parser = argparse.ArgumentParser(description="Validate a v3.8 final corpus manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--base-dir", default=".")
    parser.add_argument(
        "--allow-missing-paths",
        action="store_true",
        help="Permit path placeholders while drafting the manifest.",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v3_8_final_corpus_manifest_validation.md",
    )
    args = parser.parse_args(argv)

    failures, warnings, facts = validate_manifest(
        manifest_path=Path(args.manifest),
        base_dir=Path(args.base_dir),
        allow_missing_paths=args.allow_missing_paths,
    )
    report = format_report(
        manifest_path=Path(args.manifest),
        base_dir=Path(args.base_dir),
        failures=failures,
        warnings=warnings,
        facts=facts,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
