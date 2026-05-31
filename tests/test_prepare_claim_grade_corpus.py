from __future__ import annotations

import json
from pathlib import Path

from scripts.prepare_claim_grade_corpus import (
    load_claim_grade_corpus_config,
    normalize_for_leakage,
    prepare_corpus,
)


def _posix(path: Path) -> str:
    return path.as_posix()


def test_normalize_for_leakage_preserves_case_by_default() -> None:
    assert (
        normalize_for_leakage(
            "Iğdır'ın ışığı!",
            lowercase=False,
            strip_punctuation=True,
        )
        == "Iğdırın ışığı"
    )


def test_prepare_corpus_filters_exact_and_normalized_leaks(tmp_path: Path) -> None:
    eval_path = tmp_path / "eval.tsv"
    eval_path.write_text(
        "default\tGeldim.\t[]\n",
        encoding="utf-8",
    )
    text_source = tmp_path / "source.txt"
    text_source.write_text(
        "Geldim.\nBaşka temiz satır.\n",
        encoding="utf-8",
    )
    jsonl_source = tmp_path / "source.jsonl"
    jsonl_source.write_text(
        json.dumps({"text": "Geldim!"}, ensure_ascii=False)
        + "\n"
        + json.dumps({"text": "Ek temiz satır."}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "out.txt"
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                f'output_path = "{_posix(output_path)}"',
                f'manifest_out = "{_posix(tmp_path / "manifest.md")}"',
                f'leakage_out = "{_posix(tmp_path / "leakage.md")}"',
                "max_output_lines = 10",
                "ngram_size = 2",
                "normalize_lowercase = false",
                "strip_punctuation = true",
                "",
                "[[eval_sets]]",
                'name = "tiny"',
                f'path = "{_posix(eval_path)}"',
                "",
                "[[sources]]",
                'name = "text_source"',
                'format = "text"',
                f'path = "{_posix(text_source)}"',
                "",
                "[[sources]]",
                'name = "jsonl_source"',
                'format = "jsonl"',
                f'path = "{_posix(jsonl_source)}"',
                'text_field = "text"',
            ]
        ),
        encoding="utf-8",
    )

    config = load_claim_grade_corpus_config(config_path)
    stats, examples = prepare_corpus(config)

    assert stats[0].exact_leaks == 1
    assert stats[1].normalized_leaks == 1
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "Başka temiz satır.",
        "Ek temiz satır.",
    ]
    assert examples


def test_prepare_corpus_applies_quality_filters_and_dedupe(tmp_path: Path) -> None:
    eval_path = tmp_path / "eval.tsv"
    eval_path.write_text("default\tLeak yok.\t[]\n", encoding="utf-8")
    source = tmp_path / "source.jsonl"
    clean = "Bu temiz ve yeterince uzun bir Türkçe eğitim satırıdır."
    source.write_text(
        "\n".join(
            json.dumps({"text": text}, ensure_ascii=False)
            for text in [
                "kısa",
                "Bu satır izin verilenden çok daha uzun olduğu için filtrelenmesi gereken ayrıntılı bir satırdır.",
                "Kontrol\u200bkarakterli yeterince uzun bir satır.",
                "Replacement \ufffd karakterli yeterince uzun bir satır.",
                "Mojibake Ä marker içeren yeterince uzun bir satır.",
                clean,
                clean,
                "Bu   temiz ve yeterince uzun bir Türkçe eğitim satırıdır.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "out.txt"
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                f'output_path = "{_posix(output_path)}"',
                f'manifest_out = "{_posix(tmp_path / "manifest.md")}"',
                f'leakage_out = "{_posix(tmp_path / "leakage.md")}"',
                "max_output_lines = 10",
                "ngram_size = 8",
                "normalize_lowercase = false",
                "strip_punctuation = true",
                "min_chars = 20",
                "max_chars = 80",
                "drop_control_chars = true",
                "drop_replacement_char = true",
                "drop_mojibake_suspects = true",
                "dedupe_exact = true",
                "dedupe_normalized = true",
                "",
                "[[eval_sets]]",
                'name = "tiny"',
                f'path = "{_posix(eval_path)}"',
                "",
                "[[sources]]",
                'name = "jsonl_source"',
                'format = "jsonl"',
                f'path = "{_posix(source)}"',
                'text_field = "text"',
            ]
        ),
        encoding="utf-8",
    )

    config = load_claim_grade_corpus_config(config_path)
    stats, examples = prepare_corpus(config)

    assert not examples
    assert stats[0].filtered_short == 1
    assert stats[0].filtered_long == 1
    assert stats[0].filtered_control == 1
    assert stats[0].filtered_replacement == 1
    assert stats[0].filtered_mojibake == 1
    assert stats[0].duplicate_exact == 1
    assert stats[0].duplicate_normalized == 1
    assert output_path.read_text(encoding="utf-8").splitlines() == [clean]
