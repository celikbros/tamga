from __future__ import annotations

from scripts.check_eval_leakage import find_exact_leakage
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
