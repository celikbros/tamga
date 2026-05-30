from __future__ import annotations

from pathlib import Path

from scripts.compare_real_tokenizers import RealBaselineSpec
from scripts.report_fertility import (
    evaluate_fertility,
    format_markdown,
    is_unknown_or_byte_token,
    load_corpus_lines,
    protected_candidates,
)


def test_load_corpus_lines_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "corpus.txt"
    path.write_text("\nGeldim.\n\nREADME.md açıldı.\n", encoding="utf-8")

    lines = load_corpus_lines(path)

    assert [line.index for line in lines] == [2, 4]
    assert [line.text for line in lines] == ["Geldim.", "README.md açıldı."]


def test_protected_candidates_detects_file_and_number() -> None:
    assert protected_candidates("README.md 3.14 yazıldı.") == ["README.md", "3.14"]


def test_protected_candidates_detects_technical_comparators() -> None:
    assert protected_candidates("Install transformers>=4.40.") == [
        "transformers>=4.40",
    ]


def test_unknown_or_byte_proxy() -> None:
    assert is_unknown_or_byte_token("<unk>")
    assert is_unknown_or_byte_token("<0xE2>")
    assert is_unknown_or_byte_token("bad\ufffd")
    assert not is_unknown_or_byte_token("README")


def test_evaluate_fertility_with_builtin_baselines(tmp_path: Path) -> None:
    path = tmp_path / "corpus.txt"
    path.write_text("README.md açıldı.\nGeldim.\n", encoding="utf-8")

    results = evaluate_fertility(
        load_corpus_lines(path),
        [
            RealBaselineSpec("custom_tr_morph", "custom"),
            RealBaselineSpec("unicode_char", "unicode_char"),
        ],
    )
    markdown = format_markdown(results)

    assert results["custom_tr_morph"][0].protected_preserved == 1
    assert results["unicode_char"][0].protected_preserved == 0
    assert "# Natural Corpus Fertility Report" in markdown
    assert "Highest Fertility Lines" in markdown
