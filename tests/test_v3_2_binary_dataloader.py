from __future__ import annotations

from array import array
import json

from scripts.simulate_v3_2_binary_dataloader import simulate


def write_uint32(path, values: list[int]) -> None:
    data = array("I", values)
    if data.itemsize != 4:
        raise RuntimeError("array('I') is not uint32 on this platform")
    data.tofile(path.open("wb"))


def test_binary_dataloader_simulation_accepts_shifted_mask_fixture(tmp_path) -> None:
    tokens_path = tmp_path / "tokens.bin"
    mask_path = tmp_path / "loss_mask.bin"
    manifest_path = tmp_path / "manifest.json"
    config_path = tmp_path / "config.json"

    tokens = [1, 10, 11, 12, 2, 13, 14, 15, 16, 17, 18]
    mask = bytes([1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1])
    write_uint32(tokens_path, tokens)
    mask_path.write_bytes(mask)
    manifest_path.write_text(
        json.dumps(
            {
                "outputs": {
                    "tokens": str(tokens_path),
                    "loss_mask": str(mask_path),
                },
                "format": {
                    "token_dtype": "uint32_le",
                    "loss_mask_dtype": "uint8",
                    "eos_id": 2,
                },
                "summary": {
                    "tokens": len(tokens),
                },
            }
        ),
        encoding="utf-8",
    )
    config_path.write_text(
        json.dumps(
            {
                "id_space": {
                    "sp_id_end_exclusive": 32,
                    "byte_fallback_start": 32,
                    "byte_fallback_end_exclusive": 288,
                    "control_token_start": 288,
                    "control_token_end_exclusive": 320,
                    "current_effective_vocab_size": 320,
                },
                "special_token_registry": {
                    "assigned": {
                        "<pad>": 288,
                        "<system>": 289,
                        "<user>": 290,
                        "<assistant>": 291,
                        "<tool_call>": 292,
                        "<tool_result>": 293,
                    },
                    "aliases": {
                        "<bos>": 1,
                        "<eos>": 2,
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    facts, failures, warnings = simulate(
        manifest_path=manifest_path,
        config_path=config_path,
        batch_size=1,
        seq_len=4,
    )

    assert failures == []
    assert warnings == []
    assert facts["full_batches"] == 2
    # Target-position masks use mask[1:] for shifted labels.
    assert facts["train_label_positions"] == 6
    assert facts["masked_label_positions"] == 2
    assert facts["tail_padded_tokens"] == 2


def test_binary_dataloader_simulation_rejects_out_of_range_token(tmp_path) -> None:
    tokens_path = tmp_path / "tokens.bin"
    mask_path = tmp_path / "loss_mask.bin"
    manifest_path = tmp_path / "manifest.json"
    config_path = tmp_path / "config.json"

    write_uint32(tokens_path, [1, 999])
    mask_path.write_bytes(bytes([1, 1]))
    manifest_path.write_text(
        json.dumps(
            {
                "outputs": {
                    "tokens": str(tokens_path),
                    "loss_mask": str(mask_path),
                },
                "format": {
                    "token_dtype": "uint32_le",
                    "loss_mask_dtype": "uint8",
                },
                "summary": {
                    "tokens": 2,
                },
            }
        ),
        encoding="utf-8",
    )
    config_path.write_text(
        json.dumps(
            {
                "id_space": {
                    "sp_id_end_exclusive": 32,
                    "byte_fallback_start": 32,
                    "byte_fallback_end_exclusive": 288,
                    "control_token_start": 288,
                    "control_token_end_exclusive": 320,
                    "current_effective_vocab_size": 320,
                },
                "special_token_registry": {
                    "assigned": {"<pad>": 288},
                    "aliases": {"<bos>": 1, "<eos>": 2},
                },
            }
        ),
        encoding="utf-8",
    )

    _facts, failures, _warnings = simulate(
        manifest_path=manifest_path,
        config_path=config_path,
        batch_size=1,
        seq_len=4,
    )

    assert any("exceeds effective vocab" in failure for failure in failures)


def test_binary_dataloader_simulation_evenly_samples_limited_batches(tmp_path) -> None:
    tokens_path = tmp_path / "tokens.bin"
    mask_path = tmp_path / "loss_mask.bin"
    manifest_path = tmp_path / "manifest.json"
    config_path = tmp_path / "config.json"

    tokens = [1] + [10 + (index % 10) for index in range(39)]
    write_uint32(tokens_path, tokens)
    mask_path.write_bytes(bytes([1] * len(tokens)))
    manifest_path.write_text(
        json.dumps(
            {
                "outputs": {
                    "tokens": str(tokens_path),
                    "loss_mask": str(mask_path),
                },
                "format": {
                    "token_dtype": "uint32_le",
                    "loss_mask_dtype": "uint8",
                },
                "summary": {
                    "tokens": len(tokens),
                    "max_token_id": max(tokens),
                },
            }
        ),
        encoding="utf-8",
    )
    config_path.write_text(
        json.dumps(
            {
                "id_space": {
                    "sp_id_end_exclusive": 32,
                    "byte_fallback_start": 32,
                    "byte_fallback_end_exclusive": 288,
                    "control_token_start": 288,
                    "control_token_end_exclusive": 320,
                    "current_effective_vocab_size": 320,
                },
                "special_token_registry": {
                    "assigned": {"<pad>": 288},
                    "aliases": {"<bos>": 1, "<eos>": 2},
                },
            }
        ),
        encoding="utf-8",
    )

    facts, failures, warnings = simulate(
        manifest_path=manifest_path,
        config_path=config_path,
        batch_size=1,
        seq_len=4,
        max_batches=3,
    )

    assert failures == []
    assert warnings == []
    assert facts["full_batches"] == 9
    assert facts["sampled_batches"] == 3
    assert facts["sampled_windows"] == 3
    assert facts["sampling_mode"] == "evenly_spaced"
