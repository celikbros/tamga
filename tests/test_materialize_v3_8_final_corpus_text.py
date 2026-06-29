from __future__ import annotations

import json

from scripts.materialize_v3_8_final_corpus_text import materialize_from_manifest


def write_manifest(tmp_path, *, corpus_path, corpus_format="text", text_field="text"):
    dedup_report = tmp_path / "dedup.md"
    dedup_report.write_text("# Dedup\n", encoding="utf-8")
    manifest = {
        "schema_version": "v3.8-final-corpus-manifest-1",
        "corpus": {
            "name": "final",
            "frozen": True,
            "text_path": str(corpus_path),
            "format": corpus_format,
            "text_field": text_field,
        },
        "dedup": {
            "status": "complete",
            "method": "minhash",
            "report_path": str(dedup_report),
        },
        "mixture": [
            {
                "name": "turkish_primary",
                "language": "tr",
                "domain": "mixed",
                "share": 1.0,
                "source_path": str(corpus_path),
            }
        ],
        "normalization": {
            "policy": "identity",
            "already_applied": False,
        },
        "tokenizer_registry": {
            "v3_7_registry_unchanged": True,
            "effective_vocab_size": 64384,
            "sp_vocab_size": 64000,
            "byte_fallback_start": 64000,
            "byte_fallback_end_exclusive": 64256,
            "control_start": 64256,
            "control_end_exclusive": 64384,
            "pad_id": 64256,
            "unk_id": 0,
        },
        "training_sample": {
            "use_full_corpus": True,
        },
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def test_materialize_text_manifest_writes_lf_view(tmp_path) -> None:
    source = tmp_path / "source.txt"
    source.write_bytes("bir\r\niki\n".encode("utf-8"))
    manifest_path = write_manifest(tmp_path, corpus_path=source)
    output = tmp_path / "out.txt"

    stats, failures, warnings = materialize_from_manifest(
        manifest_path=manifest_path,
        base_dir=tmp_path,
        output_path=output,
    )

    assert failures == []
    assert warnings == []
    assert stats is not None
    assert stats.scanned_lines == 2
    assert output.read_text(encoding="utf-8") == "bir\niki\n"


def test_materialize_text_manifest_allows_existing_output_path(tmp_path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("bir\niki\n", encoding="utf-8", newline="\n")
    manifest_path = write_manifest(tmp_path, corpus_path=source)

    stats, failures, warnings = materialize_from_manifest(
        manifest_path=manifest_path,
        base_dir=tmp_path,
        output_path=source,
    )

    assert failures == []
    assert warnings == []
    assert stats is not None
    assert stats.source_path == source
    assert stats.output_path == source
    assert stats.scanned_lines == 2
    assert stats.output_bytes == source.stat().st_size


def test_materialize_jsonl_manifest_extracts_text_field(tmp_path) -> None:
    source = tmp_path / "source.jsonl"
    source.write_text(
        "\n".join(
            [
                json.dumps({"text": "bir"}),
                json.dumps({"text": "iki\nsatir"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    manifest_path = write_manifest(tmp_path, corpus_path=source, corpus_format="jsonl")
    output = tmp_path / "out.txt"

    stats, failures, warnings = materialize_from_manifest(
        manifest_path=manifest_path,
        base_dir=tmp_path,
        output_path=output,
    )

    assert failures == []
    assert warnings == []
    assert stats is not None
    assert stats.corpus_format == "jsonl"
    assert stats.written_lines == 2
    assert output.read_text(encoding="utf-8") == "bir\niki satir\n"


def test_materialize_jsonl_manifest_fails_on_missing_text(tmp_path) -> None:
    source = tmp_path / "source.jsonl"
    source.write_text(json.dumps({"body": "missing"}) + "\n", encoding="utf-8")
    manifest_path = write_manifest(tmp_path, corpus_path=source, corpus_format="jsonl")
    output = tmp_path / "out.txt"

    stats, failures, _warnings = materialize_from_manifest(
        manifest_path=manifest_path,
        base_dir=tmp_path,
        output_path=output,
    )

    assert stats is not None
    assert any("missing text field" in item for item in failures)
    assert not output.exists()
