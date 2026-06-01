from __future__ import annotations

from pathlib import Path

from scripts.check_probe_split_overlap import (
    check_split_overlap,
    format_overlap_report,
    load_split_records,
    rows_to_exclude_for_eval,
    write_filtered_split,
)


def test_check_split_overlap_detects_normalized_exact_duplicate(tmp_path: Path):
    split_dir = tmp_path / "raw_split"
    split_dir.mkdir()
    (split_dir / "train.txt").write_text("İSTANBUL'a geldim.\n", encoding="utf-8")
    (split_dir / "valid.txt").write_text("istanbul'a geldim.\n", encoding="utf-8")
    (split_dir / "test.txt").write_text("Bambaşka bir satır.\n", encoding="utf-8")

    reports = check_split_overlap(
        split_dir,
        ngram_size=8,
        min_near_words=8,
        near_threshold=0.8,
    )

    train_valid = reports[0]
    assert train_valid.raw_exact_pairs == 0
    assert train_valid.normalized_exact_pairs == 1


def test_check_split_overlap_detects_near_duplicate(tmp_path: Path):
    split_dir = tmp_path / "raw_split"
    split_dir.mkdir()
    (split_dir / "train.txt").write_text(
        "Bugün Ankara yolunda uzun ve temiz bir deneme cümlesi yazdım çünkü "
        "bu satır tekrar kontrolü içindir.\n",
        encoding="utf-8",
    )
    (split_dir / "valid.txt").write_text(
        "Dün Ankara yolunda uzun ve temiz bir deneme cümlesi yazdım çünkü "
        "bu satır tekrar kontrolü içindir.\n",
        encoding="utf-8",
    )
    (split_dir / "test.txt").write_text("Alakasız kısa satır.\n", encoding="utf-8")

    reports = check_split_overlap(
        split_dir,
        ngram_size=8,
        min_near_words=8,
        near_threshold=0.8,
    )

    assert len(reports[0].near_pairs) == 1
    assert reports[0].near_pairs[0].containment >= 0.8


def test_format_overlap_report_omits_private_text(tmp_path: Path):
    split_dir = tmp_path / "raw_split"
    split_dir.mkdir()
    private_text = "Bu özel corpus satırı raporda görünmemeli."
    (split_dir / "train.txt").write_text(private_text + "\n", encoding="utf-8")
    (split_dir / "valid.txt").write_text(private_text + "\n", encoding="utf-8")
    (split_dir / "test.txt").write_text("Başka satır.\n", encoding="utf-8")

    reports = check_split_overlap(
        split_dir,
        ngram_size=8,
        min_near_words=8,
        near_threshold=0.8,
    )
    report_text = format_overlap_report(
        reports,
        split_dir=split_dir,
        ngram_size=8,
        min_near_words=8,
        near_threshold=0.8,
        max_details=20,
    )

    assert private_text not in report_text
    assert "Exact overlap pairs" in report_text


def test_load_split_records_reads_manifest_source_indexes(tmp_path: Path):
    split_path = tmp_path / "train.txt"
    manifest_path = tmp_path / "train.manifest.jsonl"
    split_path.write_text("Bir satır.\n", encoding="utf-8")
    manifest_path.write_text('{"source_line_index": 42}\n', encoding="utf-8")

    records = load_split_records(
        split_path,
        split="train",
        ngram_size=8,
        min_near_words=8,
    )

    assert records[0].source_line_index == 42


def test_write_filtered_split_removes_train_to_eval_overlap_rows(tmp_path: Path):
    split_dir = tmp_path / "raw_split"
    split_dir.mkdir()
    (split_dir / "train.txt").write_text(
        "Bugün Ankara yolunda uzun ve temiz bir deneme cümlesi yazdım çünkü "
        "bu satır tekrar kontrolü içindir.\n",
        encoding="utf-8",
    )
    (split_dir / "valid.txt").write_text(
        "Dün Ankara yolunda uzun ve temiz bir deneme cümlesi yazdım çünkü "
        "bu satır tekrar kontrolü içindir.\n"
        "Bu satır temiz kalmalı.\n",
        encoding="utf-8",
    )
    (split_dir / "test.txt").write_text("Alakasız kısa satır.\n", encoding="utf-8")

    reports = check_split_overlap(
        split_dir,
        ngram_size=8,
        min_near_words=8,
        near_threshold=0.8,
    )
    assert rows_to_exclude_for_eval(reports) == {"valid": {1}}

    filtered_dir = tmp_path / "filtered_split"
    stats = write_filtered_split(split_dir, filtered_dir, reports)

    assert stats["train"] == {"kept": 1, "removed": 0}
    assert stats["valid"] == {"kept": 1, "removed": 1}
    assert stats["test"] == {"kept": 1, "removed": 0}
    assert filtered_dir.joinpath("valid.txt").read_text(encoding="utf-8") == (
        "Bu satır temiz kalmalı.\n"
    )
