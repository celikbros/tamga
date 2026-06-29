from __future__ import annotations

import json

from scripts.run_v3_8_final_corpus_preflight import run_preflight


def make_manifest(tmp_path, *, registry_unchanged: bool = True):
    source = tmp_path / "source.jsonl"
    source.write_text(
        json.dumps({"text": "bir"}) + "\n" + json.dumps({"text": "iki"}) + "\n",
        encoding="utf-8",
    )
    dedup = tmp_path / "dedup.md"
    dedup.write_text("# Dedup\n", encoding="utf-8")
    manifest = {
        "schema_version": "v3.8-final-corpus-manifest-1",
        "corpus": {
            "name": "final",
            "frozen": True,
            "text_path": str(source),
            "format": "jsonl",
            "text_field": "text",
        },
        "dedup": {
            "status": "complete",
            "method": "minhash",
            "report_path": str(dedup),
        },
        "mixture": [
            {
                "name": "tr",
                "language": "tr",
                "domain": "mixed",
                "share": 1.0,
                "source_path": str(source),
            }
        ],
        "normalization": {
            "policy": "identity",
            "already_applied": False,
        },
        "tokenizer_registry": {
            "v3_7_registry_unchanged": registry_unchanged,
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
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_preflight_writes_reports_and_text(tmp_path) -> None:
    manifest_path = make_manifest(tmp_path)
    output_text = tmp_path / "final.txt"
    report_dir = tmp_path / "reports"

    results, summary_path = run_preflight(
        manifest_path=manifest_path,
        base_dir=tmp_path,
        output_text=output_text,
        report_dir=report_dir,
    )

    assert all(not failures for failures, _warnings, _facts, _path in results.values())
    assert output_text.read_text(encoding="utf-8") == "bir\niki\n"
    assert (report_dir / "manifest_validation.md").exists()
    assert (report_dir / "text_materialization.md").exists()
    assert summary_path.exists()
    assert "Status: `PASS`" in summary_path.read_text(encoding="utf-8")


def test_preflight_stops_materialization_after_manifest_failure(tmp_path) -> None:
    manifest_path = make_manifest(tmp_path, registry_unchanged=False)
    output_text = tmp_path / "final.txt"

    results, summary_path = run_preflight(
        manifest_path=manifest_path,
        base_dir=tmp_path,
        output_text=output_text,
        report_dir=tmp_path / "reports",
    )

    manifest_failures = results["manifest"][0]
    materialization_failures = results["materialization"][0]
    assert any("v3_7_registry_unchanged must be true" in item for item in manifest_failures)
    assert materialization_failures == ["skipped because final corpus manifest validation failed"]
    assert not output_text.exists()
    assert "Status: `FAIL`" in summary_path.read_text(encoding="utf-8")
