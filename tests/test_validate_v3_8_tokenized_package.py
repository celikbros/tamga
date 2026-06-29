from __future__ import annotations

import json

from scripts.validate_v3_8_tokenized_package import sha256_file, validate_package


def write_package(tmp_path, *, corrupt_token_checksum: bool = False):
    out_dir = tmp_path / "fixture"
    out_dir.mkdir()
    manifest_path = out_dir / "manifest.json"
    checksums_path = out_dir / "checksums.json"

    payloads = {
        "tokens.bin": b"\x01\x00\x00\x00\x02\x00\x00\x00",
        "loss_mask.bin": b"\x01\x00",
        "index.jsonl": b'{"line":1,"token_start":0,"token_end":2,"token_count":2}\n',
        "sidecar.jsonl": b'{"line":1,"spans":[]}\n',
    }
    for file_name, payload in payloads.items():
        (out_dir / file_name).write_bytes(payload)

    data_digests = {
        file_name: sha256_file(out_dir / file_name)
        for file_name in payloads
    }
    manifest_digests = dict(data_digests)
    if corrupt_token_checksum:
        manifest_digests["tokens.bin"] = "0" * 64

    manifest = {
        "schema_version": "v3-production-tokenized-corpus-1",
        "outputs": {
            "tokens": str(out_dir / "tokens.bin"),
            "loss_mask": str(out_dir / "loss_mask.bin"),
            "index": str(out_dir / "index.jsonl"),
            "sidecar": str(out_dir / "sidecar.jsonl"),
            "checksums": str(checksums_path),
        },
        "summary": {"tokens": 2},
        "checksums": manifest_digests,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    ledger_digests = dict(data_digests)
    ledger_digests["manifest.json"] = sha256_file(manifest_path)
    checksums_path.write_text(
        json.dumps({"algorithm": "sha256", "files": ledger_digests}),
        encoding="utf-8",
    )
    return manifest_path


def test_validate_package_accepts_matching_checksums(tmp_path) -> None:
    manifest_path = write_package(tmp_path)

    failures, warnings, facts = validate_package(
        manifest_path=manifest_path,
        base_dir=tmp_path,
    )

    assert failures == []
    assert warnings == []
    assert facts["files_checked"] == 5


def test_validate_package_rejects_manifest_checksum_mismatch(tmp_path) -> None:
    manifest_path = write_package(tmp_path, corrupt_token_checksum=True)

    failures, _warnings, _facts = validate_package(
        manifest_path=manifest_path,
        base_dir=tmp_path,
    )

    assert any("manifest checksum mismatch for tokens.bin" in item for item in failures)
