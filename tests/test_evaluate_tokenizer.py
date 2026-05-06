from pathlib import Path

from scripts.evaluate_tokenizer import EvalCase, evaluate_cases, evaluate_case, load_cases

FIXTURES = Path(__file__).parent / "fixtures"


def test_evaluation_case_exact_match_true():
    case = EvalCase(
        text="Arabalarımızdan indiler.",
        expected=["▁Araba", "+lar", "+ımız", "+dan", "▁in", "+di", "+ler", "."],
    )

    result = evaluate_case(case)

    assert result.exact_match is True


def test_load_cases_supports_two_column_tsv():
    cases = load_cases(FIXTURES / "eval_two_columns.tsv")

    assert cases == [
        EvalCase(text="Geldim.", expected=["▁Gel", "+di", "+m", "."], category="default")
    ]


def test_load_cases_supports_three_column_tsv():
    cases = load_cases(FIXTURES / "eval_three_columns.tsv")

    assert cases == [
        EvalCase(text="Geldim.", expected=["▁Gel", "+di", "+m", "."], category="verb_past")
    ]


def test_evaluation_report_groups_by_category():
    cases = [
        EvalCase(
            category="verb_past",
            text="Geldim.",
            expected=["▁Gel", "+di", "+m", "."],
        ),
        EvalCase(
            category="negative_word",
            text="kadın",
            expected=["▁kadın"],
        ),
    ]

    report = evaluate_cases(cases)

    assert report.by_category["verb_past"].exact_matches == 1
    assert report.by_category["negative_word"].exact_matches == 1
    assert report.by_category["verb_past"].f1 == 1.0
