from pathlib import Path

from scripts.report_stress_public import (
    StressCase,
    evaluate_stress_cases,
    is_span_preserved,
    load_stress_cases,
    render_markdown,
)
from tr_tokenizer.tokenizer import WORD_START


def test_is_span_preserved_ignores_word_start_marker():
    assert is_span_preserved("README.md", [f"{WORD_START}README.md", "'", "+yi"])


def test_is_span_preserved_detects_broken_span():
    assert not is_span_preserved("README.md", ["â–README", ".", "md"])


def test_load_stress_cases(tmp_path: Path):
    path = tmp_path / "stress.tsv"
    path.write_text(
        'protected_file\tREADME.md dosyasi\t["README.md"]\n',
        encoding="utf-8",
    )

    assert load_stress_cases(path) == [
        StressCase(
            category="protected_file",
            text="README.md dosyasi",
            protected_spans=["README.md"],
        )
    ]


def test_evaluate_stress_cases_reports_protected_span():
    report = evaluate_stress_cases(
        [
            StressCase(
                category="protected_file",
                text="README.md dosyasi",
                protected_spans=["README.md"],
            )
        ]
    )

    assert report.total_examples == 1
    assert report.protected_total == 1
    assert report.protected_preserved == 1


def test_render_markdown_includes_summary():
    report = evaluate_stress_cases(
        [
            StressCase(
                category="protected_file",
                text="README.md dosyasi",
                protected_spans=["README.md"],
            )
        ]
    )

    markdown = render_markdown(report)

    assert "## SUMMARY" in markdown
    assert "protected_spans_preserved" in markdown
    assert "## SAMPLE TOKENIZATIONS" in markdown
