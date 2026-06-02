from pathlib import Path

from scripts.audit_v1_8_token_accounting import audit_token_accounting, format_report


def _write_split(root: Path) -> None:
    root.mkdir()
    for split in ("train", "valid", "test"):
        (root / f"{split}.txt").write_text(
            "Türkiye'de test yaptık.\nREADME.md dosyası hazır.\n",
            encoding="utf-8",
        )


def test_token_accounting_audit_reports_custom_modes(tmp_path: Path):
    split_dir = tmp_path / "split"
    _write_split(split_dir)

    rows = audit_token_accounting(
        split_dir=split_dir,
        sp_model=None,
        custom_vocab_size=300,
        max_lines=None,
    )
    modes = {row.mode for row in rows}

    assert "custom_standard_no_whitespace" in modes
    assert "custom_lossless_open_vocab" in modes
    assert "custom_lossless_300_byte_fallback" in modes
    assert {row.split for row in rows} == {"train", "valid", "test"}
    assert all(row.tokens > 0 for row in rows)

    report = format_report(
        split_dir=split_dir,
        sp_model=None,
        custom_vocab_size=300,
        max_lines=None,
        rows=rows,
    )

    assert "v1.8 Token Accounting Audit" in report
    assert "custom_lossless_open_vocab" in report
    assert "Decision Rule" in report
