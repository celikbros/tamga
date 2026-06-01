from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_eval_leakage import (
    build_indexes,
    build_byte_prefilter,
    find_exact_leakage,
    load_eval_set,
    make_leakage_case,
    normalize_for_leakage,
    scan_corpus_text,
    summarize_cases,
    word_shingles,
)
from scripts.compare_bpe_sweep import format_sweep_markdown, format_sweep_report, run_sweep
from scripts.evaluate_tokenizer import EvalCase
from scripts.materialize_probe_split import materialize_probe_split
from scripts.prepare_downstream_probe import load_probe_config
from tr_tokenizer.baseline_bpe import train_bpe


def test_find_exact_leakage_detects_matching_eval_text():
    leaks = find_exact_leakage(
        train_lines=["Geldim.", "Başka bir cümle."],
        eval_texts=["Geldim.", "Gittim."],
    )

    assert leaks == ["Geldim."]


def test_find_exact_leakage_reports_empty_when_clean():
    assert find_exact_leakage(["Dün geldim."], ["Geldim."]) == []


def test_normalize_for_leakage_uses_turkish_aware_lowercase():
    assert normalize_for_leakage("İSTANBUL IĞDIR'da!") == "istanbul ığdır da"


def test_word_shingles_uses_short_sentence_fallback():
    assert word_shingles(("geldim", "bugün"), ngram_size=8) == {
        ("geldim", "bugün")
    }


def test_scan_corpus_text_detects_normalized_full_hit():
    case = make_leakage_case(
        set_name="gold",
        row=1,
        text="İstanbul'a geldim.",
        category="proper_name",
        ngram_size=8,
    )
    assert case is not None
    indexes = build_indexes([case])

    scan_corpus_text(
        "Dün istanbul'a geldim ve döndüm.",
        raw_prefix_index=indexes[0],
        full_first_index=indexes[1],
        shingle_first_index=indexes[2],
    )

    summary = summarize_cases([case])
    assert summary["gold"]["raw_exact"] == 0
    assert summary["gold"]["normalized_full"] == 1
    assert summary["gold"]["clean"] == 0


def test_load_eval_set_rejects_category_column_text_col(tmp_path: Path):
    path = tmp_path / "eval.tsv"
    path.write_text(
        'suffix_chain\tGeldim.\t["▁Gel","+di","+m","."]\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="category column"):
        load_eval_set(path, set_name="gold", ngram_size=8, text_col=0)


def test_load_eval_set_can_skip_short_items(tmp_path: Path):
    path = tmp_path / "eval.tsv"
    path.write_text(
        "\n".join(
            [
                'verb_past\tGeldim.\t["▁Gel","+di","+m","."]',
                'verb_past\tDün eve geldim.\t["▁Dün","▁ev","+e","▁gel","+di","+m","."]',
            ]
        ),
        encoding="utf-8",
    )

    cases = load_eval_set(path, set_name="gold", ngram_size=8, min_case_words=3)

    assert [case.text for case in cases] == ["Dün eve geldim."]


def test_build_byte_prefilter_matches_utf8_markers():
    case = make_leakage_case(
        set_name="gold",
        row=1,
        text="Türkiye'den geldim.",
        category="proper_name",
        ngram_size=8,
    )
    assert case is not None

    prefilter = build_byte_prefilter([case], min_word_length=6)

    assert any(marker in "Bugün Türkiye'den haber geldi.".encode("utf-8") for marker in prefilter)


def test_materialize_probe_split_writes_text_and_manifest(tmp_path: Path):
    corpus = tmp_path / "pilot.txt"
    corpus.write_text(
        "\n".join(f"satir {index}" for index in range(1, 11)) + "\n",
        encoding="utf-8",
    )
    config_path = tmp_path / "split.toml"
    output_dir = tmp_path / "raw_split"
    report_out = tmp_path / "split_report.md"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                f'corpus_path = "{corpus.as_posix()}"',
                f'output_dir = "{output_dir.as_posix()}"',
                f'report_out = "{report_out.as_posix()}"',
                "max_lines = 10",
                "seed = 123",
                "train_parts = 8",
                "valid_parts = 1",
                "test_parts = 1",
                "write_tokenized = false",
                "allow_download = false",
            ]
        ),
        encoding="utf-8",
    )

    config = load_probe_config(config_path)
    splits, written = materialize_probe_split(config)

    assert [split.name for split in splits] == ["train", "valid", "test"]
    assert [split.line_count for split in splits] == [8, 1, 1]
    assert written["train"].read_text(encoding="utf-8").count("\n") == 8
    assert written["valid"].read_text(encoding="utf-8").count("\n") == 1
    assert written["test"].read_text(encoding="utf-8").count("\n") == 1
    assert written["manifest"].exists()
    assert written["train_manifest"].exists()


def test_compare_bpe_sweep_with_two_models_outputs_summary():
    cases = [
        EvalCase(
            category="verb_past",
            text="Geldim.",
            expected=["▁Gel", "+di", "+m", "."],
        ),
        EvalCase(
            category="informal",
            text="Gidiyom ben.",
            expected=["▁Gid", "+iyom", "▁ben", "."],
        ),
    ]
    model_small = train_bpe(["Dün geldim.", "Gidiyorum ben."], vocab_size=30)
    model_large = train_bpe(["Dün geldim.", "Gidiyorum ben."], vocab_size=60)

    summary_rows, category_table = run_sweep(
        cases,
        [("bpe_30", model_small), ("bpe_60", model_large)],
    )
    report = format_sweep_report(summary_rows, category_table)

    assert "SUMMARY" in report
    assert "CATEGORY SUMMARY" in report
    assert "custom" in report
    assert "bpe_30" in report
    assert "bpe_60" in report
    assert "verb_past" in report

    markdown = format_sweep_markdown(summary_rows, category_table)
    assert "| Model |" in markdown
    assert "Token count tek basina kalite degildir." in markdown
