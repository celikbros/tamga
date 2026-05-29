from __future__ import annotations

import json
from pathlib import Path

from scripts.compare_real_tokenizers import (
    RealBaselineSpec,
    canonicalize_external_tokens,
    format_report,
    run_report,
)
from scripts.evaluate_tokenizer import load_cases


def test_canonicalize_external_tokens_handles_common_markers() -> None:
    assert canonicalize_external_tokens(["ĠGel", "dim", "##ler", "."]) == [
        "▁Gel",
        "dim",
        "ler",
        ".",
    ]


def test_run_report_with_builtin_baselines(tmp_path: Path) -> None:
    tsv = tmp_path / "eval.tsv"
    tsv.write_text(
        "verb_past\tGeldim.\t"
        + json.dumps(["▁Gel", "+di", "+m", "."], ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )

    rows, category_table = run_report(
        load_cases(tsv),
        [
            RealBaselineSpec("custom_tr_morph", "custom"),
            RealBaselineSpec("unicode_char", "unicode_char"),
        ],
    )

    report = format_report(rows, category_table)
    assert "SUMMARY" in report
    assert "custom_tr_morph\tok" in report
    assert "unicode_char\tok" in report
    assert rows[0].exact_match == "1/1"
    assert "verb_past" in category_table
