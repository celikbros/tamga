from scripts.tokenize_v3_1_corpus_smoke import normalize_max_lines


def test_normalize_max_lines_keeps_positive_limit() -> None:
    assert normalize_max_lines(100) == 100


def test_normalize_max_lines_treats_zero_as_all_lines() -> None:
    assert normalize_max_lines(0) is None


def test_normalize_max_lines_treats_negative_as_all_lines() -> None:
    assert normalize_max_lines(-1) is None


def test_normalize_max_lines_keeps_none_as_all_lines() -> None:
    assert normalize_max_lines(None) is None
