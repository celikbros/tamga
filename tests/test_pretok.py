from tr_tokenizer.pretok import pre_tokenize


def test_pre_tokenize_splits_words_apostrophe_suffixes_and_punctuation():
    text = "Türkiye'den, Ankara'ya."

    assert pre_tokenize(text) == [
        "Türkiye",
        "'",
        "+den",
        ",",
        "Ankara",
        "'",
        "+ya",
        ".",
    ]


def test_pre_tokenize_keeps_numbers_and_punctuation():
    assert pre_tokenize("3'ün 12,5!") == ["3", "'", "+ün", "12,5", "!"]


def test_pre_tokenize_keeps_file_like_tokens_intact():
    assert pre_tokenize("README.md config_v2.json.") == [
        "README.md",
        "config_v2.json",
        ".",
    ]
