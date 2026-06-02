from pathlib import Path

from scripts.analyze_v2_seed_vocab import (
    coverage_rows,
    format_report,
    load_seed_vocab,
    token_category,
)


def test_seed_vocab_analysis_coverage_and_categories(tmp_path: Path):
    seed_path = tmp_path / "seed.tsv"
    seed_path.write_text(
        "token\tcount\n"
        "▁test\t10\n"
        "+ler\t5\n"
        ".\t3\n"
        "\"\t2\n"
        "abc\t1\n",
        encoding="utf-8",
    )

    entries = load_seed_vocab(seed_path)
    rows = coverage_rows(entries, (1, 2, 5))

    assert [row.covered_count for row in rows] == [10, 15, 21]
    assert token_category("▁test") == "word_start"
    assert token_category("+ler") == "suffix"
    assert token_category(".") == "punct_or_symbol"
    assert token_category("abc") == "other"

    report = format_report(
        seed_path=seed_path,
        entries=entries,
        caps=(1, 2, 4),
        reference_cap=2,
    )

    assert "Coverage By Vocabulary Cap" in report
    assert "Category Summary" in report
