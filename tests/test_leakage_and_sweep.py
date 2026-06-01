from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_eval_leakage import (
    build_indexes,
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
