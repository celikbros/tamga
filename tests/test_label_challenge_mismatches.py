from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from scripts.evaluate_tokenizer import CaseResult
from scripts.label_challenge_mismatches import (
    classify_result,
    label_file,
    render_labeled_tsv,
)

ROOT = Path(__file__).resolve().parents[1]


def test_classify_result_marks_exact_match():
    result = CaseResult(
        category="verb_past",
        text="Geldim.",
        expected=["▁Gel", "+di", "+m", "."],
        actual=["▁Gel", "+di", "+m", "."],
    )

    label, reason, next_step = classify_result(result)

    assert label == "exact_match"
    assert "match" in reason
    assert next_step


def test_classify_result_marks_ambiguity_as_needing_context():
    result = CaseResult(
        category="ambiguity",
        text="Yazın tatile gittik.",
        expected=["▁Yazın", "▁tatil", "+e", "▁git", "+ti", "+k", "."],
        actual=["▁Yaz", "+ın", "▁tatile", "▁git", "+ti", "+k", "."],
    )

    label, reason, next_step = classify_result(result)

    assert label == "needs_context"
    assert "context" in reason
    assert "broad rule" in next_step


def test_label_file_writes_labeled_tsv_for_small_input():
    suffix = uuid4().hex
    input_path = ROOT / f"artifacts/label_test_{suffix}.tsv"
    output_path = ROOT / f"artifacts/label_test_{suffix}.labeled.tsv"
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text(
        'ambiguity\tYazın.\t["▁Yazın","."]\n',
        encoding="utf-8",
    )

    try:
        labeled = label_file(input_path, output_path)
        output = output_path.read_text(encoding="utf-8")
    finally:
        input_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)

    assert labeled
    assert output.startswith("label\tcategory\ttext")
    assert "needs_context" in output


def test_render_labeled_tsv_has_stable_header():
    result = CaseResult(
        category="default",
        text="Geldim.",
        expected=["▁Gel", "+di", "+m", "."],
        actual=["▁Gel", "+di", "+m", "."],
    )
    label, reason, next_step = classify_result(result)
    output = render_labeled_tsv(
        [
            type(
                "Labeled",
                (),
                {
                    "label": label,
                    "category": result.category,
                    "text": result.text,
                    "expected": result.expected,
                    "actual": result.actual,
                    "reason": reason,
                    "next_step": next_step,
                },
            )()
        ]
    )

    assert output.splitlines()[0] == (
        "label\tcategory\ttext\texpected_tokens_json\tactual_tokens_json"
        "\treason\tnext_step"
    )
