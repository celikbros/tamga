from __future__ import annotations

import json

from scripts.validate_v3_8_final_corpus_manifest import validate_manifest


def make_manifest(tmp_path, *, overrides: dict | None = None):
    corpus_path = tmp_path / "final.txt"
    corpus_path.write_text("Merhaba\n", encoding="utf-8")
    dedup_report = tmp_path / "dedup.md"
    dedup_report.write_text("# Dedup\n", encoding="utf-8")

    manifest = {
        "schema_version": "v3.8-final-corpus-manifest-1",
        "corpus": {
            "name": "celik_tr_primary_pretrain_final_v1_0_20260620",
            "frozen": True,
            "text_path": str(corpus_path),
            "format": "text",
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
                "domain": "mixed_clean",
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
        "document_boundaries": {
            "preserve": False,
        },
    }
    if overrides:
        for key, value in overrides.items():
            manifest[key] = value

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def test_valid_final_corpus_manifest_passes(tmp_path) -> None:
    manifest_path = make_manifest(tmp_path)

    failures, warnings, facts = validate_manifest(
        manifest_path=manifest_path,
        base_dir=tmp_path,
    )

    assert failures == []
    assert warnings == []
    assert facts["registry_unchanged"] is True


def test_registry_change_fails(tmp_path) -> None:
    manifest_path = make_manifest(
        tmp_path,
        overrides={
            "tokenizer_registry": {
                "v3_7_registry_unchanged": False,
                "pad_id": 0,
            }
        },
    )

    failures, _warnings, _facts = validate_manifest(
        manifest_path=manifest_path,
        base_dir=tmp_path,
    )

    assert any("v3_7_registry_unchanged must be true" in item for item in failures)
    assert any("pad_id must be 64256" in item for item in failures)


def test_complete_dedup_requires_method(tmp_path) -> None:
    manifest_path = make_manifest(
        tmp_path,
        overrides={
            "dedup": {
                "status": "complete",
            }
        },
    )

    failures, _warnings, _facts = validate_manifest(
        manifest_path=manifest_path,
        base_dir=tmp_path,
    )

    assert any("dedup.method is required" in item for item in failures)


def test_missing_paths_allowed_for_draft_template(tmp_path) -> None:
    manifest_path = make_manifest(
        tmp_path,
        overrides={
            "corpus": {
                "name": "draft",
                "frozen": True,
                "text_path": "missing.txt",
                "format": "text",
            },
            "mixture": [
                {
                    "name": "draft",
                    "language": "tr",
                    "domain": "mixed",
                    "share": 1.0,
                    "source_path": "missing.txt",
                }
            ],
        },
    )

    failures, _warnings, _facts = validate_manifest(
        manifest_path=manifest_path,
        base_dir=tmp_path,
        allow_missing_paths=True,
    )

    assert failures == []
