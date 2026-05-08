from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from scripts.prepare_hidden_eval_views import (
    load_hidden_rows,
    render_standard_eval,
    write_eval_views,
)

ROOT = Path(__file__).resolve().parents[1]


def test_load_hidden_rows_accepts_header_and_two_gold_columns():
    suffix = uuid4().hex
    path = ROOT / f"artifacts/hidden_view_test_{suffix}.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "category\ttext\tgold_independent_tokens_json\t"
        "gold_policy_tokens_json\tdivergence_note\n"
        'softening\tKitabımdan bahsettim.\t["▁Kitap","+ım","+dan","."]\t'
        '["▁Kitab","+ım","+dan","."]\tnote\n',
        encoding="utf-8",
    )

    try:
        rows = load_hidden_rows(path)
    finally:
        path.unlink(missing_ok=True)

    assert rows == [
        (
            "softening",
            "Kitabımdan bahsettim.",
            ["▁Kitap", "+ım", "+dan", "."],
            ["▁Kitab", "+ım", "+dan", "."],
            "note",
        )
    ]


def test_render_standard_eval_can_emit_policy_or_independent_view():
    rows = [
        (
            "softening",
            "Kitabımdan bahsettim.",
            ["▁Kitap", "+ım", "+dan", "."],
            ["▁Kitab", "+ım", "+dan", "."],
            "note",
        )
    ]

    independent = render_standard_eval(rows, which="independent")
    policy = render_standard_eval(rows, which="policy")

    assert 'softening\tKitabımdan bahsettim.\t["▁Kitap","+ım","+dan","."]' in independent
    assert 'softening\tKitabımdan bahsettim.\t["▁Kitab","+ım","+dan","."]' in policy


def test_write_eval_views_writes_two_standard_tsv_files():
    suffix = uuid4().hex
    input_path = ROOT / f"artifacts/hidden_view_test_{suffix}.tsv"
    out_dir = ROOT / f"artifacts/hidden_view_out_{suffix}"
    input_path.write_text(
        'negative_word\tKadın yakın.\t["▁Kadın","▁yakın","."]\t'
        '["▁Kadın","▁yakın","."]\t\n',
        encoding="utf-8",
    )

    try:
        independent_path, policy_path = write_eval_views(input_path, out_dir=out_dir)
        independent = independent_path.read_text(encoding="utf-8")
        policy = policy_path.read_text(encoding="utf-8")
    finally:
        input_path.unlink(missing_ok=True)
        for path in out_dir.glob("*"):
            path.unlink(missing_ok=True)
        out_dir.rmdir()

    assert independent_path.name.endswith("_independent.tsv")
    assert policy_path.name.endswith("_policy.tsv")
    assert independent == policy
