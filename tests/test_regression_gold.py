from __future__ import annotations

from pathlib import Path

from scripts.evaluate_tokenizer import evaluate_cases, load_cases

ROOT = Path(__file__).resolve().parents[1]


def test_gold_expanded_exact_match_is_frozen():
    cases = load_cases(ROOT / "data/eval/tr_gold_expanded.tsv")
    report = evaluate_cases(cases)

    assert len(cases) == 50
    assert report.exact_matches == 50


def test_challenge_eval_loads_and_runs_without_exact_match_contract():
    cases = load_cases(ROOT / "data/eval/tr_challenge.tsv")
    report = evaluate_cases(cases)
    categories = {case.category for case in cases}

    assert len(cases) >= 100
    assert {
        "suffix_chain",
        "proper_name",
        "softening",
        "negative_word",
        "verb_past",
        "verb_future",
        "question",
        "informal",
        "code_mixed",
        "ambiguity",
        "numbers_dates",
        "punctuation",
    }.issubset(categories)
    assert len(report.results) == len(cases)
