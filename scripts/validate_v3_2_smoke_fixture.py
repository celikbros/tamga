from __future__ import annotations

from array import array
import argparse
import json
import sys
from pathlib import Path
from typing import Any


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_uint32(path: Path) -> array:
    data = array("I")
    with path.open("rb") as handle:
        data.fromfile(handle, path.stat().st_size // 4)
    if data.itemsize != 4:
        raise RuntimeError("array('I') is not uint32 on this platform")
    if sys.byteorder != "little":
        data.byteswap()
    return data


def byte_offsets(text: str) -> list[int]:
    offsets = [0]
    total = 0
    for char in text:
        total += len(char.encode("utf-8"))
        offsets.append(total)
    return offsets


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            rows.append(json.loads(raw_line))
    return rows


def validate_fixture(
    *,
    manifest_path: Path,
    config_path: Path,
) -> tuple[list[str], list[str], dict[str, Any]]:
    failures: list[str] = []
    warnings: list[str] = []
    manifest = read_json(manifest_path)
    config = read_json(config_path)
    summary = manifest.get("summary", {})
    outputs = manifest.get("outputs", {})
    fmt = manifest.get("format", {})
    id_space = config.get("id_space", {})

    lines = int(summary.get("lines", -1))
    token_count = int(summary.get("tokens", -1))
    max_token_id_reported = int(summary.get("max_token_id", -1))
    effective_vocab_size = int(id_space.get("current_effective_vocab_size", -1))
    byte_fallback_end = int(id_space.get("byte_fallback_end_exclusive", -1))

    tokens_path = Path(str(outputs.get("tokens", "")))
    mask_path = Path(str(outputs.get("loss_mask", "")))
    index_path = Path(str(outputs.get("index", "")))
    sidecar_path = Path(str(outputs.get("sidecar", "")))
    input_path = Path(str(manifest.get("input", "")))

    for label, path in [
        ("tokens", tokens_path),
        ("loss_mask", mask_path),
        ("index", index_path),
        ("sidecar", sidecar_path),
        ("input", input_path),
    ]:
        require(path.exists(), failures, f"{label} path does not exist: {path}")

    require(fmt.get("token_dtype") == "uint32_le", failures, "token dtype must be uint32_le")
    require(fmt.get("loss_mask_dtype") == "uint8", failures, "loss mask dtype must be uint8")

    if tokens_path.exists():
        require(tokens_path.stat().st_size == token_count * 4, failures, "tokens.bin size mismatch")
        tokens = read_uint32(tokens_path)
        require(len(tokens) == token_count, failures, "tokens.bin token count mismatch")
        if tokens:
            observed_max = max(tokens)
            require(
                observed_max == max_token_id_reported,
                failures,
                f"manifest max token id mismatch: {max_token_id_reported} != {observed_max}",
            )
            require(
                observed_max < effective_vocab_size,
                failures,
                f"token id {observed_max} exceeds effective vocab size {effective_vocab_size}",
            )
            if observed_max >= byte_fallback_end:
                warnings.append("fixture contains wrapper control token ids")

    if mask_path.exists():
        mask_bytes = mask_path.read_bytes()
        require(len(mask_bytes) == token_count, failures, "loss_mask.bin size mismatch")
        invalid_mask_values = sorted(set(mask_bytes) - {0, 1})
        require(not invalid_mask_values, failures, f"invalid loss mask values: {invalid_mask_values}")

    index_rows = load_jsonl(index_path) if index_path.exists() else []
    sidecar_rows = load_jsonl(sidecar_path) if sidecar_path.exists() else []
    require(len(index_rows) == lines, failures, "index.jsonl line count mismatch")
    require(len(sidecar_rows) == lines, failures, "sidecar.jsonl line count mismatch")

    previous_end = 0
    indexed_tokens = 0
    for row_index, row in enumerate(index_rows, start=1):
        start = int(row.get("token_start", -1))
        end = int(row.get("token_end", -1))
        count = int(row.get("token_count", -1))
        require(start == previous_end, failures, f"index token_start discontinuity at row {row_index}")
        require(end >= start, failures, f"index token_end before token_start at row {row_index}")
        require(end - start == count, failures, f"index token_count mismatch at row {row_index}")
        previous_end = end
        indexed_tokens += count
    require(indexed_tokens == token_count, failures, "index total token count mismatch")

    if input_path.exists() and sidecar_rows:
        input_lines: list[str] = []
        with input_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                if len(input_lines) >= lines:
                    break
                input_lines.append(raw_line.rstrip("\n"))
        require(len(input_lines) == lines, failures, "input line count available for sidecar validation mismatch")
        for row_index, row in enumerate(sidecar_rows, start=1):
            if row_index > len(input_lines):
                break
            text = input_lines[row_index - 1]
            raw = text.encode("utf-8")
            offsets = byte_offsets(text)
            spans = row.get("spans", [])
            require(isinstance(spans, list), failures, f"sidecar spans must be a list at row {row_index}")
            if not isinstance(spans, list):
                continue
            prev_end = 0
            for span_index, span in enumerate(spans, start=1):
                if not isinstance(span, dict):
                    failures.append(f"sidecar span must be object at row {row_index}, span {span_index}")
                    continue
                byte_start = int(span.get("byte_start", -1))
                byte_end = int(span.get("byte_end", -1))
                char_start = int(span.get("char_start", -1))
                char_end = int(span.get("char_end", -1))
                surface = str(span.get("surface", ""))
                require(
                    0 <= byte_start <= byte_end <= len(raw),
                    failures,
                    f"sidecar byte offset out of range at row {row_index}, span {span_index}",
                )
                require(
                    0 <= char_start <= char_end <= len(text),
                    failures,
                    f"sidecar char offset out of range at row {row_index}, span {span_index}",
                )
                if 0 <= char_start <= char_end <= len(text):
                    require(
                        offsets[char_start] == byte_start and offsets[char_end] == byte_end,
                        failures,
                        f"sidecar char/byte offset mismatch at row {row_index}, span {span_index}",
                    )
                    require(
                        text[char_start:char_end] == surface,
                        failures,
                        f"sidecar char surface mismatch at row {row_index}, span {span_index}",
                    )
                if 0 <= byte_start <= byte_end <= len(raw):
                    require(
                        raw[byte_start:byte_end].decode("utf-8") == surface,
                        failures,
                        f"sidecar byte surface mismatch at row {row_index}, span {span_index}",
                    )
                require(
                    byte_start >= prev_end,
                    failures,
                    f"sidecar span order mismatch at row {row_index}, span {span_index}",
                )
                prev_end = byte_end

    facts = {
        "lines": lines,
        "tokens": token_count,
        "tokens_size": tokens_path.stat().st_size if tokens_path.exists() else 0,
        "mask_size": mask_path.stat().st_size if mask_path.exists() else 0,
        "index_rows": len(index_rows),
        "sidecar_rows": len(sidecar_rows),
        "max_token_id": max_token_id_reported,
        "effective_vocab_size": effective_vocab_size,
    }
    return failures, warnings, facts


def format_report(
    *,
    manifest_path: Path,
    config_path: Path,
    failures: list[str],
    warnings: list[str],
    facts: dict[str, Any],
) -> str:
    status = "PASS" if not failures else "FAIL"
    lines = [
        "# v3.2 Smoke Fixture Validation",
        "",
        f"Manifest: `{manifest_path.as_posix()}`",
        f"Config: `{config_path.as_posix()}`",
        f"Status: `{status}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in facts.items():
        lines.append(f"| {key} | {value} |")
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
    parser = argparse.ArgumentParser(description="Validate a v3.2 binary smoke fixture.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--report-out", default="artifacts/v3_2_smoke_fixture_validation.md")
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    config_path = Path(args.config)
    failures, warnings, facts = validate_fixture(
        manifest_path=manifest_path,
        config_path=config_path,
    )
    report = format_report(
        manifest_path=manifest_path,
        config_path=config_path,
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
