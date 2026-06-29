from __future__ import annotations

import argparse
from array import array
import json
from pathlib import Path
import sys
from typing import Any, BinaryIO


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_uint32_slice(handle: BinaryIO, *, start: int, count: int) -> list[int]:
    handle.seek(start * 4)
    raw = handle.read(count * 4)
    if len(raw) != count * 4:
        raise ValueError(
            f"short uint32 read: start={start} count={count} bytes={len(raw)}"
        )
    data = array("I")
    data.frombytes(raw)
    if data.itemsize != 4:
        raise RuntimeError("array('I') is not uint32 on this platform")
    if sys.byteorder != "little":
        data.byteswap()
    return list(data)


def read_byte_slice(handle: BinaryIO, *, start: int, count: int) -> list[int]:
    handle.seek(start)
    raw = handle.read(count)
    if len(raw) != count:
        raise ValueError(
            f"short byte read: start={start} count={count} bytes={len(raw)}"
        )
    return list(raw)


def select_batch_indices(full_batches: int, max_batches: int | None) -> list[int]:
    if full_batches <= 0:
        return []
    if max_batches is None or max_batches >= full_batches:
        return list(range(full_batches))
    if max_batches == 1:
        return [0]
    return [
        round(index * (full_batches - 1) / (max_batches - 1))
        for index in range(max_batches)
    ]


def require(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def count_range(values: list[int], start: int, end: int) -> int:
    return sum(1 for value in values if start <= value < end)


def format_report(
    *,
    manifest_path: Path,
    config_path: Path,
    batch_size: int,
    seq_len: int,
    max_batches: int | None,
    facts: dict[str, Any],
    failures: list[str],
    warnings: list[str],
) -> str:
    status = "PASS" if not failures else "FAIL"
    lines = [
        "# v3.2 Binary Dataloader Simulation",
        "",
        f"Manifest: `{manifest_path.as_posix()}`",
        f"Config: `{config_path.as_posix()}`",
        f"Batch shape: `batch_size={batch_size}`, `seq_len={seq_len}`",
        f"Batch limit: `{max_batches if max_batches is not None else 'all'}`",
        f"Status: `{status}`",
        "",
        "This tokenizer-side simulation checks whether the binary fixture can be",
        "turned into causal-LM input ids, shifted labels, and target-position loss",
        "masks without relying on the future LLM engine.",
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
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The binary token stream is internally consistent for packed causal-LM "
                "batching and target-position masking."
                if not failures
                else "The binary token stream failed at least one dataloader simulation gate."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def simulate(
    *,
    manifest_path: Path,
    config_path: Path,
    batch_size: int,
    seq_len: int,
    max_batches: int | None = None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    manifest = read_json(manifest_path)
    config = read_json(config_path)
    outputs = manifest.get("outputs", {})
    summary = manifest.get("summary", {})
    fmt = manifest.get("format", {})
    id_space = config.get("id_space", {})
    registry = config.get("special_token_registry", {})

    tokens_path = Path(str(outputs.get("tokens", "")))
    mask_path = Path(str(outputs.get("loss_mask", "")))
    require(tokens_path.exists(), failures, f"tokens path does not exist: {tokens_path}")
    require(mask_path.exists(), failures, f"loss mask path does not exist: {mask_path}")
    require(fmt.get("token_dtype") == "uint32_le", failures, "manifest token_dtype must be uint32_le")
    require(fmt.get("loss_mask_dtype") == "uint8", failures, "manifest loss_mask_dtype must be uint8")

    token_count = int(summary.get("tokens", -1))
    token_file_count = tokens_path.stat().st_size // 4 if tokens_path.exists() else 0
    mask_file_count = mask_path.stat().st_size if mask_path.exists() else 0
    if tokens_path.exists():
        require(
            tokens_path.stat().st_size % 4 == 0,
            failures,
            "tokens file size must be divisible by 4",
        )
    require(token_file_count == token_count, failures, "manifest token count mismatch")
    require(
        mask_file_count == token_file_count,
        failures,
        "loss mask length must equal token length",
    )

    effective_vocab = int(id_space.get("current_effective_vocab_size", -1))
    sp_end = int(id_space.get("sp_id_end_exclusive", -1))
    byte_start = int(id_space.get("byte_fallback_start", -1))
    byte_end = int(id_space.get("byte_fallback_end_exclusive", -1))
    control_start = int(id_space.get("control_token_start", byte_end))
    control_end = int(id_space.get("control_token_end_exclusive", effective_vocab))
    assigned = registry.get("assigned", {})
    aliases = registry.get("aliases", {})
    pad_id = int(assigned.get("<pad>", -1)) if isinstance(assigned, dict) else -1
    bos_id = int(aliases.get("<bos>", 1)) if isinstance(aliases, dict) else 1
    eos_id = int(aliases.get("<eos>", int(fmt.get("eos_id", 2)))) if isinstance(aliases, dict) else 2

    manifest_max_token = int(summary.get("max_token_id", -1))
    if manifest_max_token >= 0:
        require(
            manifest_max_token < effective_vocab,
            failures,
            "manifest max token id exceeds effective vocab size",
        )
    require(0 <= pad_id < effective_vocab, failures, "pad id must be inside effective vocab")
    require(control_start <= pad_id < control_end, failures, "pad id must be in control-token range")
    require(0 <= bos_id < sp_end, failures, "bos alias must point to SP range")
    require(0 <= eos_id < sp_end, failures, "eos alias must point to SP range")

    windows = max(0, (token_file_count - 1) // seq_len)
    full_batches = windows // batch_size
    selected_batches = select_batch_indices(full_batches, max_batches)
    used_windows = len(selected_batches) * batch_size
    train_label_positions = 0
    masked_label_positions = 0
    label_invalid_ids = 0
    sampled_min_token = effective_vocab
    sampled_max_token = -1
    sampled_sp_tokens = 0
    sampled_byte_tokens = 0
    sampled_control_tokens = 0
    sampled_token_positions = 0
    invalid_mask_values: set[int] = set()

    if tokens_path.exists() and mask_path.exists():
        with tokens_path.open("rb") as token_handle, mask_path.open("rb") as mask_handle:
            batch_token_count = batch_size * seq_len
            for batch_index in selected_batches:
                start = batch_index * batch_token_count
                batch_tokens = read_uint32_slice(
                    token_handle,
                    start=start,
                    count=batch_token_count + 1,
                )
                batch_mask = read_byte_slice(
                    mask_handle,
                    start=start,
                    count=batch_token_count + 1,
                )
                invalid_mask_values.update(set(batch_mask) - {0, 1})
                sampled_values = batch_tokens[:-1]
                sampled_token_positions += len(sampled_values)
                if batch_tokens:
                    sampled_min_token = min(sampled_min_token, min(batch_tokens))
                    sampled_max_token = max(sampled_max_token, max(batch_tokens))
                sampled_sp_tokens += count_range(sampled_values, 0, sp_end)
                sampled_byte_tokens += count_range(sampled_values, byte_start, byte_end)
                sampled_control_tokens += count_range(
                    sampled_values, control_start, control_end
                )

                for batch_window in range(batch_size):
                    offset = batch_window * seq_len
                    input_ids = batch_tokens[offset : offset + seq_len]
                    labels = batch_tokens[offset + 1 : offset + seq_len + 1]
                    label_mask = batch_mask[offset + 1 : offset + seq_len + 1]
                    require(
                        len(input_ids) == seq_len,
                        failures,
                        f"short input window at batch {batch_index}:{batch_window}",
                    )
                    require(
                        len(labels) == seq_len,
                        failures,
                        f"short label window at batch {batch_index}:{batch_window}",
                    )
                    require(
                        len(label_mask) == seq_len,
                        failures,
                        f"short label mask window at batch {batch_index}:{batch_window}",
                    )
                    train_label_positions += sum(label_mask)
                    masked_label_positions += seq_len - sum(label_mask)
                    label_invalid_ids += sum(
                        1 for value in labels if value < 0 or value >= effective_vocab
                    )

    require(
        not invalid_mask_values,
        failures,
        f"invalid sampled mask values: {sorted(invalid_mask_values)}",
    )
    fully_consumed_tokens = full_batches * batch_size * seq_len
    tail_tokens = token_file_count - fully_consumed_tokens
    tail_padded = 0
    tail_train_labels = 0
    if tail_tokens > 1 and pad_id >= 0 and tokens_path.exists() and mask_path.exists():
        with tokens_path.open("rb") as token_handle, mask_path.open("rb") as mask_handle:
            tail_values = read_uint32_slice(
                token_handle,
                start=fully_consumed_tokens,
                count=tail_tokens,
            )
            tail_masks = read_byte_slice(
                mask_handle,
                start=fully_consumed_tokens,
                count=tail_tokens,
            )
        invalid_mask_values.update(set(tail_masks) - {0, 1})
        require(
            not invalid_mask_values,
            failures,
            f"invalid sampled mask values: {sorted(invalid_mask_values)}",
        )
        sampled_token_positions += len(tail_values)
        if tail_values:
            sampled_min_token = min(sampled_min_token, min(tail_values))
            sampled_max_token = max(sampled_max_token, max(tail_values))
        sampled_sp_tokens += count_range(tail_values, 0, sp_end)
        sampled_byte_tokens += count_range(tail_values, byte_start, byte_end)
        sampled_control_tokens += count_range(tail_values, control_start, control_end)
        label_invalid_ids += sum(
            1 for value in tail_values if value < 0 or value >= effective_vocab
        )

        tail_input = tail_values[:-1][:seq_len]
        tail_labels = tail_values[1:][:seq_len]
        tail_mask = tail_masks[1:][:seq_len]
        pad_needed = seq_len - len(tail_input)
        if pad_needed > 0:
            tail_input = tail_input + [pad_id] * pad_needed
            tail_labels = tail_labels + [pad_id] * pad_needed
            tail_mask = tail_mask + [0] * pad_needed
            tail_padded = pad_needed
        require(len(tail_input) == seq_len, failures, "padded tail input length mismatch")
        require(len(tail_labels) == seq_len, failures, "padded tail label length mismatch")
        require(len(tail_mask) == seq_len, failures, "padded tail mask length mismatch")
        require(all(value in {0, 1} for value in tail_mask), failures, "padded tail mask invalid")
        tail_train_labels = sum(tail_mask)

    if sampled_max_token >= 0:
        require(sampled_min_token >= 0, failures, "negative sampled token id found")
        require(
            sampled_max_token < effective_vocab,
            failures,
            "sampled token id exceeds effective vocab size",
        )

    control_sequence = []
    if isinstance(assigned, dict):
        for token in ["<system>", "<user>", "<assistant>", "<tool_call>", "<tool_result>"]:
            if token in assigned:
                control_sequence.append(int(assigned[token]))
    require(
        all(control_start <= token_id < control_end for token_id in control_sequence),
        failures,
        "control token sequence contains id outside control range",
    )

    if full_batches == 0:
        warnings.append("fixture does not contain a full batch at the requested shape")
    if sampled_control_tokens > 0:
        warnings.append("sampled fixture positions contain wrapper control token ids")
    if label_invalid_ids:
        failures.append(f"labels contain ids outside effective vocab: {label_invalid_ids}")

    facts = {
        "tokens": token_file_count,
        "mask_bytes": mask_file_count,
        "seq_len": seq_len,
        "batch_size": batch_size,
        "windows": windows,
        "full_batches": full_batches,
        "sampling_mode": "full" if len(selected_batches) == full_batches else "evenly_spaced",
        "max_batches": max_batches if max_batches is not None else "all",
        "sampled_batches": len(selected_batches),
        "sampled_windows": used_windows,
        "used_windows": used_windows,
        "sampled_token_positions": sampled_token_positions,
        "train_label_positions": train_label_positions,
        "masked_label_positions": masked_label_positions,
        "tail_tokens": tail_tokens,
        "tail_padded_tokens": tail_padded,
        "tail_train_labels": tail_train_labels,
        "sampled_sp_tokens": sampled_sp_tokens,
        "sampled_byte_fallback_tokens": sampled_byte_tokens,
        "sampled_control_tokens": sampled_control_tokens,
        "sampled_max_token_id": sampled_max_token,
        "manifest_max_token_id": manifest_max_token,
        # Backward-compatible aliases. In sampled mode these cover sampled positions.
        "sp_tokens": sampled_sp_tokens,
        "byte_fallback_tokens": sampled_byte_tokens,
        "control_tokens_in_fixture": sampled_control_tokens,
        "max_token_id": sampled_max_token,
        "effective_vocab_size": effective_vocab,
        "pad_id": pad_id,
        "bos_id": bos_id,
        "eos_id": eos_id,
        "control_sequence_len": len(control_sequence),
    }
    return facts, failures, warnings


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Simulate packed causal-LM dataloader batches.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seq-len", type=int, default=128)
    parser.add_argument(
        "--max-batches",
        type=int,
        default=0,
        help="Evenly sample at most this many full batches; 0 scans all batches.",
    )
    parser.add_argument("--report-out", default="artifacts/v3_2_binary_dataloader_simulation.md")
    args = parser.parse_args(argv)

    if args.batch_size <= 0 or args.seq_len <= 0 or args.max_batches < 0:
        raise ValueError(
            "--batch-size and --seq-len must be positive; --max-batches cannot be negative"
        )
    manifest_path = Path(args.manifest)
    config_path = Path(args.config)
    facts, failures, warnings = simulate(
        manifest_path=manifest_path,
        config_path=config_path,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        max_batches=args.max_batches or None,
    )
    report = format_report(
        manifest_path=manifest_path,
        config_path=config_path,
        batch_size=args.batch_size,
        seq_len=args.seq_len,
        max_batches=args.max_batches or None,
        facts=facts,
        failures=failures,
        warnings=warnings,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
