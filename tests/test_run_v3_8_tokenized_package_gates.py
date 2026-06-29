from __future__ import annotations

from array import array
import json

from scripts.run_v3_8_tokenized_package_gates import run_gates
from scripts.validate_v3_8_tokenized_package import sha256_file


def write_uint32(path, values: list[int]) -> None:
    data = array("I", values)
    if data.itemsize != 4:
        raise RuntimeError("array('I') is not uint32 on this platform")
    data.tofile(path.open("wb"))


def make_fixture(tmp_path):
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()
    input_path = tmp_path / "input.txt"
    input_path.write_text("Merhaba\n", encoding="utf-8")

    tokens = [1, 10, 11, 12, 2]
    mask = bytes([1, 1, 1, 1, 1])
    write_uint32(fixture_dir / "tokens.bin", tokens)
    (fixture_dir / "loss_mask.bin").write_bytes(mask)
    (fixture_dir / "index.jsonl").write_text(
        '{"line":1,"byte_start":0,"byte_end":7,"token_start":0,"token_end":5,"token_count":5}\n',
        encoding="utf-8",
    )
    (fixture_dir / "sidecar.jsonl").write_text(
        '{"line":1,"spans":[]}\n',
        encoding="utf-8",
    )

    data_digests = {
        "tokens.bin": sha256_file(fixture_dir / "tokens.bin"),
        "loss_mask.bin": sha256_file(fixture_dir / "loss_mask.bin"),
        "index.jsonl": sha256_file(fixture_dir / "index.jsonl"),
        "sidecar.jsonl": sha256_file(fixture_dir / "sidecar.jsonl"),
    }
    manifest_path = fixture_dir / "manifest.json"
    checksums_path = fixture_dir / "checksums.json"
    manifest = {
        "schema_version": "v3-production-tokenized-corpus-1",
        "input": str(input_path),
        "outputs": {
            "tokens": str(fixture_dir / "tokens.bin"),
            "loss_mask": str(fixture_dir / "loss_mask.bin"),
            "index": str(fixture_dir / "index.jsonl"),
            "sidecar": str(fixture_dir / "sidecar.jsonl"),
            "checksums": str(checksums_path),
        },
        "format": {
            "token_dtype": "uint32_le",
            "loss_mask_dtype": "uint8",
            "append_eos": True,
        },
        "summary": {
            "lines": 1,
            "raw_bytes": 7,
            "tokens": len(tokens),
            "max_token_id": max(tokens),
        },
        "checksums": data_digests,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    ledger_digests = dict(data_digests)
    ledger_digests["manifest.json"] = sha256_file(manifest_path)
    checksums_path.write_text(
        json.dumps({"algorithm": "sha256", "files": ledger_digests}),
        encoding="utf-8",
    )

    config_path = tmp_path / "tokenizer_config.json"
    config_path.write_text(
        json.dumps(
            {
                "id_space": {
                    "sp_id_end_exclusive": 64000,
                    "byte_fallback_start": 64000,
                    "byte_fallback_end_exclusive": 64256,
                    "control_token_start": 64256,
                    "control_token_end_exclusive": 64384,
                    "current_effective_vocab_size": 64384,
                },
                "special_token_registry": {
                    "assigned": {
                        "<pad>": 64256,
                        "<system>": 64257,
                        "<user>": 64258,
                        "<assistant>": 64259,
                        "<tool_call>": 64264,
                        "<tool_result>": 64265,
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
    return manifest_path, config_path


def test_run_gates_writes_summary_and_reports(tmp_path) -> None:
    manifest_path, config_path = make_fixture(tmp_path)
    report_dir = tmp_path / "reports"

    results, summary_path = run_gates(
        manifest_path=manifest_path,
        config_path=config_path,
        base_dir=tmp_path,
        report_dir=report_dir,
        batch_size=1,
        seq_len=2,
    )

    assert all(not failures for failures, _warnings, _facts, _path in results.values())
    assert (report_dir / "checksum_validation.md").exists()
    assert (report_dir / "fixture_validation.md").exists()
    assert (report_dir / "dataloader_simulation.md").exists()
    assert summary_path.exists()
    summary = summary_path.read_text(encoding="utf-8")
    assert "Status: `PASS`" in summary
    assert "Dataloader batch limit: `4096`" in summary
