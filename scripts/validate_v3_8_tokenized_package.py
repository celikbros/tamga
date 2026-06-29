from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


DATA_FILES = {
    "tokens": "tokens.bin",
    "loss_mask": "loss_mask.bin",
    "index": "index.jsonl",
    "sidecar": "sidecar.jsonl",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_output_path(raw_path: str, *, base_dir: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return base_dir / path


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def validate_package(
    *,
    manifest_path: Path,
    base_dir: Path,
) -> tuple[list[str], list[str], dict[str, Any]]:
    failures: list[str] = []
    warnings: list[str] = []
    facts: dict[str, Any] = {}

    manifest = read_json(manifest_path)
    outputs = manifest.get("outputs", {})
    manifest_checksums = manifest.get("checksums", {})

    require(isinstance(outputs, dict), failures, "manifest outputs must be an object")
    require(
        isinstance(manifest_checksums, dict),
        failures,
        "manifest checksums must be an object",
    )
    require(
        manifest.get("schema_version") == "v3-production-tokenized-corpus-1",
        failures,
        "unexpected manifest schema_version",
    )

    checksums_raw = str(outputs.get("checksums", ""))
    checksums_path = resolve_output_path(checksums_raw, base_dir=base_dir)
    require(checksums_path.exists(), failures, f"checksums path does not exist: {checksums_path}")

    ledger: dict[str, Any] = {}
    if checksums_path.exists():
        ledger = read_json(checksums_path)
        require(ledger.get("algorithm") == "sha256", failures, "checksums algorithm must be sha256")
        require(isinstance(ledger.get("files"), dict), failures, "checksums files must be an object")
    ledger_files = ledger.get("files", {}) if isinstance(ledger.get("files"), dict) else {}

    computed: dict[str, str] = {}
    sizes: dict[str, int] = {}
    for output_key, file_name in DATA_FILES.items():
        raw = str(outputs.get(output_key, ""))
        path = resolve_output_path(raw, base_dir=base_dir)
        require(path.exists(), failures, f"{output_key} path does not exist: {path}")
        if not path.exists():
            continue
        digest = sha256_file(path)
        computed[file_name] = digest
        sizes[file_name] = path.stat().st_size

        manifest_digest = manifest_checksums.get(file_name)
        ledger_digest = ledger_files.get(file_name)
        require(
            manifest_digest == digest,
            failures,
            f"manifest checksum mismatch for {file_name}: {manifest_digest} != {digest}",
        )
        require(
            ledger_digest == digest,
            failures,
            f"checksums.json mismatch for {file_name}: {ledger_digest} != {digest}",
        )
        if manifest_digest != ledger_digest:
            failures.append(
                f"manifest/checksums.json disagree for {file_name}: "
                f"{manifest_digest} != {ledger_digest}"
            )

    manifest_digest = sha256_file(manifest_path)
    computed["manifest.json"] = manifest_digest
    sizes["manifest.json"] = manifest_path.stat().st_size
    ledger_manifest_digest = ledger_files.get("manifest.json")
    require(
        ledger_manifest_digest == manifest_digest,
        failures,
        f"checksums.json mismatch for manifest.json: {ledger_manifest_digest} != {manifest_digest}",
    )

    facts = {
        "schema_version": manifest.get("schema_version", ""),
        "base_dir": str(base_dir),
        "manifest": str(manifest_path),
        "checksums": str(checksums_path),
        "files_checked": len(computed),
        "computed_checksums": computed,
        "file_sizes": sizes,
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
        "# v3.8 Tokenized Corpus Package Checksum Validation",
        "",
        f"Manifest: `{manifest_path}`",
        f"Base dir: `{base_dir}`",
        f"Status: `{status}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| schema_version | `{facts.get('schema_version', '')}` |",
        f"| files checked | {facts.get('files_checked', 0)} |",
    ]
    sizes = facts.get("file_sizes", {})
    if isinstance(sizes, dict):
        for file_name, size in sizes.items():
            lines.append(f"| {file_name} bytes | {size} |")

    lines.extend(["", "## Checksums", "", "| File | SHA-256 |", "| --- | --- |"])
    computed = facts.get("computed_checksums", {})
    if isinstance(computed, dict):
        for file_name, digest in computed.items():
            lines.append(f"| `{file_name}` | `{digest}` |")

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
    parser = argparse.ArgumentParser(
        description="Validate v3.8 tokenized corpus package checksums."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument(
        "--base-dir",
        default=".",
        help="Base directory for relative output paths recorded in manifest.json.",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v3_8_tokenized_package_checksum_validation.md",
    )
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    base_dir = Path(args.base_dir)
    failures, warnings, facts = validate_package(
        manifest_path=manifest_path,
        base_dir=base_dir,
    )
    report = format_report(
        manifest_path=manifest_path,
        base_dir=base_dir,
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
