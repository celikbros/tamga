from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from scripts.analyze_mismatches import (
    analyze_file,
    find_over_splitting,
    find_under_splitting,
)

ROOT = Path(__file__).resolve().parents[1]


def test_under_splitting_heuristic_detects_collapsed_expected_span():
    findings = find_under_splitting(["▁Yaz", "+ın"], ["▁Yazın"])

    assert findings
    assert "collapsed" in findings[0]


def test_over_splitting_heuristic_detects_extra_actual_span():
    findings = find_over_splitting(["▁kadın"], ["▁kad", "+ın"])

    assert findings
    assert "split as" in findings[0]


def test_analyze_file_writes_mismatch_report_for_small_tsv():
    suffix = uuid4().hex
    input_path = ROOT / f"artifacts/analyze_test_{suffix}.tsv"
    output_path = ROOT / f"artifacts/analyze_test_{suffix}.md"
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text(
        'ambiguity\tYazın.\t["▁Yazın","."]\n',
        encoding="utf-8",
    )

    try:
        analysis = analyze_file(input_path, output_path)
        markdown = output_path.read_text(encoding="utf-8")
    finally:
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)

    assert output_path.exists() is False
    assert analysis.report.results
    assert "Overall Summary" in markdown
    assert "v1.1 Recommendation Table" in markdown
