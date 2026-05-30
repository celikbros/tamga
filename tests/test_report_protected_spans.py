from __future__ import annotations

from pathlib import Path

from scripts.compare_real_tokenizers import RealBaselineSpec
from scripts.report_protected_spans import (
    evaluate_protected_spans,
    format_markdown,
    is_span_preserved,
)
from scripts.report_stress_public import StressCase, load_stress_cases


def test_is_span_preserved_removes_common_word_start_markers() -> None:
    assert is_span_preserved("README.md", ["▁README.md"])
    assert is_span_preserved("README.md", ["ĠREADME.md"])
    assert is_span_preserved("README.md", ["##README.md"])


def test_is_span_preserved_detects_split_span() -> None:
    assert not is_span_preserved("README.md", ["README", ".md"])


def test_evaluate_protected_spans_with_builtin_baselines(tmp_path: Path) -> None:
    path = tmp_path / "protected.tsv"
    path.write_text(
        'protected_file\tREADME.md dosyasi\t["README.md"]\n',
        encoding="utf-8",
    )

    results = evaluate_protected_spans(
        load_stress_cases(path),
        [
            RealBaselineSpec("custom_tr_morph", "custom"),
            RealBaselineSpec("unicode_char", "unicode_char"),
        ],
    )
    markdown = format_markdown(results)

    assert results["custom_tr_morph"][0].protected_preserved == 1
    assert results["unicode_char"][0].protected_broken == 1
    assert "Protected Span Baseline Report" in markdown


def test_evaluate_protected_spans_handles_cases_without_protected_spans() -> None:
    results = evaluate_protected_spans(
        [StressCase(category="plain", text="Merhaba.", protected_spans=[])],
        [RealBaselineSpec("custom_tr_morph", "custom")],
    )

    assert results["custom_tr_morph"][0].protected_total == 0
