from __future__ import annotations

from pathlib import Path

from scripts.check_tokenizer_roundtrip import (
    RoundtripSpec,
    check_roundtrip,
    format_roundtrip_report,
)


def test_custom_roundtrip_passes_simple_split(tmp_path: Path):
    split_dir = tmp_path / "split"
    split_dir.mkdir()
    for split in ("train", "valid", "test"):
        (split_dir / f"{split}.txt").write_text(
            "Türkiye'den geldim.\nREADME.md'yi aç.\n",
            encoding="utf-8",
        )

    results = check_roundtrip(
        split_dir,
        [RoundtripSpec("custom_tr_morph", "custom")],
        max_failures=5,
    )

    assert all(result.status == "ok" for result in results)
    assert sum(result.failures for result in results) == 0


def test_roundtrip_report_omits_private_failure_text(tmp_path: Path):
    split_dir = tmp_path / "split"
    split_dir.mkdir()
    private_text = "Bu özel satır rapora girmemeli."
    for split in ("train", "valid", "test"):
        (split_dir / f"{split}.txt").write_text(private_text + "\n", encoding="utf-8")

    results = check_roundtrip(
        split_dir,
        [RoundtripSpec("missing_sp", "sentencepiece", "missing.model")],
        max_failures=5,
    )
    report = format_roundtrip_report(
        results,
        split_dir=split_dir,
        sp_config=None,
    )

    assert private_text not in report
    assert "missing sentencepiece model" in report
