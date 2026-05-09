from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from scripts.evaluate_hidden_eval import (
    evaluate_hidden_rows,
    evaluate_hidden_file,
    render_markdown,
    rows_to_cases,
)
from scripts.prepare_hidden_eval_views import load_hidden_rows

ROOT = Path(__file__).resolve().parents[1]


def test_hidden_eval_markdown_omits_hidden_text():
    rows = [
        (
            "verb_past",
            "Geldim.",
            ["▁Gel", "+di", "+m", "."],
            ["▁Gel", "+di", "+m", "."],
            "",
        ),
        (
            "informal",
            "SECRET hidden sentence.",
            ["▁SECRET", "▁hidden", "▁sentence", "."],
            ["▁SECRET", "▁hidden", "▁sentence", "."],
            "",
        ),
    ]

    path = _write_hidden_rows(rows)
    try:
        report = render_markdown(
            report=evaluate_hidden_file(path),
            title="Test Hidden Eval",
        )
    finally:
        path.unlink(missing_ok=True)

    assert "Test Hidden Eval" in report
    assert "verb_past" in report
    assert "informal" in report
    assert "SECRET hidden sentence" not in report
    assert "▁SECRET" not in report


def test_rows_to_cases_uses_selected_gold_column():
    rows = [
        (
            "softening",
            "Kitabımdan bahsettim.",
            ["▁Kitap", "+ım", "+dan", "."],
            ["▁Kitab", "+ım", "+dan", "."],
            "note",
        )
    ]

    independent = rows_to_cases(rows, which="independent")
    policy = rows_to_cases(rows, which="policy")

    assert independent[0].expected == ["▁Kitap", "+ım", "+dan", "."]
    assert policy[0].expected == ["▁Kitab", "+ım", "+dan", "."]


def test_hidden_eval_report_rejects_empty_rows():
    with pytest.raises(ValueError, match="contains no rows"):
        evaluate_hidden_rows([])


def test_hidden_rows_require_divergence_note_when_golds_differ():
    suffix = uuid4().hex
    path = ROOT / f"artifacts/hidden_note_test_{suffix}.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        'softening\tKitabımdan.\t["▁Kitap","+ım","+dan","."]\t'
        '["▁Kitab","+ım","+dan","."]\t\n',
        encoding="utf-8",
    )

    try:
        with pytest.raises(ValueError, match="divergence_note is required"):
            load_hidden_rows(path)
    finally:
        path.unlink(missing_ok=True)


def _write_hidden_rows(rows: list[tuple[str, str, list[str], list[str], str]]) -> Path:
    suffix = uuid4().hex
    path = ROOT / f"artifacts/hidden_eval_report_test_{suffix}.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "category\ttext\tgold_independent_tokens_json\t"
        "gold_policy_tokens_json\tdivergence_note"
    ]
    for category, text, independent, policy, note in rows:
        lines.append(
            "\t".join(
                [
                    category,
                    text,
                    json.dumps(independent, ensure_ascii=False, separators=(",", ":")),
                    json.dumps(policy, ensure_ascii=False, separators=(",", ":")),
                    note,
                ]
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
