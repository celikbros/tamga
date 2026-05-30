from pathlib import Path

from scripts.report_coverage import (
    TextCase,
    classify_token,
    evaluate_coverage,
    load_text_cases,
    render_markdown,
)
from tr_tokenizer.tokenizer import WORD_START


def test_classify_token_kinds():
    assert classify_token("+lar") == "suffix"
    assert classify_token("'") == "apostrophe"
    assert classify_token(f"{WORD_START}https://example.com/a") == "protected_url"
    assert classify_token(f"{WORD_START}README.md") == "protected_file"
    assert classify_token(f"{WORD_START}3.14") == "protected_number"
    assert classify_token(f"{WORD_START}transformers>=4.40") == "protected_technical"
    assert classify_token(f"{WORD_START}Gel") == "word"
    assert classify_token(".") == "punctuation_symbol"
    assert classify_token("ə") == "other"


def test_load_text_cases_supports_two_column_eval_tsv(tmp_path: Path):
    path = tmp_path / "eval.tsv"
    path.write_text('Geldim.\t["x"]\n', encoding="utf-8")

    assert load_text_cases(path) == [TextCase(category="default", text="Geldim.")]


def test_load_text_cases_supports_three_column_tsv(tmp_path: Path):
    path = tmp_path / "stress.tsv"
    path.write_text('protected_url\tSee https://example.com\t[]\n', encoding="utf-8")

    assert load_text_cases(path) == [
        TextCase(category="protected_url", text="See https://example.com")
    ]


def test_evaluate_coverage_counts_token_kinds():
    report = evaluate_coverage(
        [TextCase(category="protected_url", text="See https://example.com.")]
    )

    assert report.total_examples == 1
    assert report.counts["protected_url"] == 1
    assert report.counts["punctuation_symbol"] == 1


def test_render_markdown_includes_coverage_sections():
    report = evaluate_coverage(
        [TextCase(category="protected_url", text="See https://example.com.")]
    )

    markdown = render_markdown(report)

    assert "## TOKEN KIND COUNTS" in markdown
    assert "## CATEGORY SUMMARY" in markdown
    assert "protected_url" in markdown
