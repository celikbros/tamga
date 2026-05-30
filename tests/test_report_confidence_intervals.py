from __future__ import annotations

import json
from pathlib import Path

from scripts.compare_real_tokenizers import RealBaselineSpec, evaluate_real_baselines
from scripts.evaluate_tokenizer import load_cases
from scripts.report_confidence_intervals import (
    bootstrap_report,
    format_markdown,
    interval,
    percentile,
)


def test_percentile_interpolates() -> None:
    assert percentile([0.0, 10.0], 0.25) == 2.5


def test_interval_reports_observed_point_value() -> None:
    result = interval([0.0, 1.0], point=0.75)

    assert result.point == 0.75
    assert result.lower == 0.025
    assert result.upper == 0.975


def test_bootstrap_report_with_builtin_baselines(tmp_path: Path) -> None:
    tsv = tmp_path / "eval.tsv"
    tsv.write_text(
        "verb_past\tGeldim.\t"
        + json.dumps(["\u2581Gel", "+di", "+m", "."], ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )

    model_results = evaluate_real_baselines(
        load_cases(tsv),
        [
            RealBaselineSpec("custom_tr_morph", "custom"),
            RealBaselineSpec("unicode_char", "unicode_char"),
        ],
    )
    rows = bootstrap_report(model_results, samples=20, seed=3)
    markdown = format_markdown(rows, samples=20)

    assert rows[0].model_name == "custom_tr_morph"
    assert rows[0].status == "ok"
    assert rows[0].exact_match_rate.point == 1.0
    assert rows[0].boundary_f1.point == 1.0
    assert rows[1].model_name == "unicode_char"
    assert "# Metric Confidence Intervals" in markdown
    assert "custom_tr_morph" in markdown
