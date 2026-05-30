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


def test_pre_tokenize_keeps_non_turkish_apostrophe_words_intact():
    assert pre_tokenize("Don't split John's book.") == [
        "Don't",
        "split",
        "John's",
        "book",
        ".",
    ]
    assert pre_tokenize("L'amico visits d'Istanbul.") == [
        "L'amico",
        "visits",
        "d'Istanbul",
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


def test_pre_tokenize_keeps_technical_comparator_spans_intact():
    assert pre_tokenize("Install transformers>=4.40 and tokenizers>=0.19.") == [
        "Install",
        "transformers>=4.40",
        "and",
        "tokenizers>=0.19",
        ".",
    ]
    assert pre_tokenize("Use lib<=2.0 pkg==1.2 tool~=3.1 bad!=0.9.") == [
        "Use",
        "lib<=2.0",
        "pkg==1.2",
        "tool~=3.1",
        "bad!=0.9",
        ".",
    ]


def test_pre_tokenize_does_not_make_plain_comparators_sticky():
    assert pre_tokenize("A >= B and x>y.") == [
        "A",
        ">",
        "=",
        "B",
        "and",
        "x",
        ">",
        "y",
        ".",
    ]


def test_pre_tokenize_v11_keeps_guarded_number_and_file_forms():
    assert pre_tokenize("README.md'yi 3.14 34-ABC-1907.") == [
        "README.md",
        "'",
        "+yi",
        "3.14",
        "34-ABC-1907",
        ".",
    ]
    assert pre_tokenize("%25'lik 12:30'da 2024/05/01") == [
        "%",
        "25",
        "'",
        "+lik",
        "12:30",
        "'",
        "+da",
        "2024/05/01",
    ]


def test_pre_tokenize_keeps_urls_intact_and_splits_sentence_punctuation():
    assert pre_tokenize("https://example.com/tr/sayfa.") == [
        "https://example.com/tr/sayfa",
        ".",
    ]
    assert pre_tokenize("Bak: https://example.com/a/b?x=1#c") == [
        "Bak",
        ":",
        "https://example.com/a/b?x=1#c",
    ]


def test_pre_tokenize_keeps_uzbek_apostrophe_words_intact():
    assert pre_tokenize("Oʻzbekistonning poytaxti Toshkent.") == [
        "Oʻzbekistonning",
        "poytaxti",
        "Toshkent",
        ".",
    ]
    assert pre_tokenize("Oʻzbekcha: gʻisht, sanʼat, maʼno.") == [
        "Oʻzbekcha",
        ":",
        "gʻisht",
        ",",
        "sanʼat",
        ",",
        "maʼno",
        ".",
    ]


def test_pre_tokenize_keeps_azerbaijani_specific_words_intact():
    assert pre_tokenize("Mənim adım Əli, Bakıda yaşayıram.") == [
        "Mənim",
        "adım",
        "Əli",
        ",",
        "Bakıda",
        "yaşayıram",
        ".",
    ]
    assert pre_tokenize("Xəbər: qız məktəbə gedir.") == [
        "Xəbər",
        ":",
        "qız",
        "məktəbə",
        "gedir",
        ".",
    ]


def test_pre_tokenize_keeps_cyrillic_words_intact():
    assert pre_tokenize("Қазақстан Республикасы — Алматы қаласы.") == [
        "Қазақстан",
        "Республикасы",
        "—",
        "Алматы",
        "қаласы",
        ".",
    ]
    assert pre_tokenize("Кыргызча: тоо, суу, өң, үн, жаңы күн.") == [
        "Кыргызча",
        ":",
        "тоо",
        ",",
        "суу",
        ",",
        "өң",
        ",",
        "үн",
        ",",
        "жаңы",
        "күн",
        ".",
    ]


def test_pre_tokenize_keeps_arabic_and_greek_words_intact():
    arabic = "\u0645\u0631\u062d\u0628\u0627 \u0628\u0627\u0644\u0639\u0627\u0644\u0645."
    greek = (
        "\u0391\u03b8\u03ae\u03bd\u03b1 "
        "\u03b5\u03af\u03bd\u03b1\u03b9 "
        "\u03cc\u03bc\u03bf\u03c1\u03c6\u03b7 "
        "\u03c0\u03cc\u03bb\u03b7."
    )

    assert pre_tokenize(arabic) == [
        "\u0645\u0631\u062d\u0628\u0627",
        "\u0628\u0627\u0644\u0639\u0627\u0644\u0645",
        ".",
    ]
    assert pre_tokenize(greek) == [
        "\u0391\u03b8\u03ae\u03bd\u03b1",
        "\u03b5\u03af\u03bd\u03b1\u03b9",
        "\u03cc\u03bc\u03bf\u03c1\u03c6\u03b7",
        "\u03c0\u03cc\u03bb\u03b7",
        ".",
    ]


def test_pre_tokenize_keeps_arabic_punctuation_separate():
    assert pre_tokenize(
        "\u0645\u0631\u062d\u0628\u0627\u060c \u0628\u0627\u0644\u0639\u0627\u0644\u0645\u061f"
    ) == [
        "\u0645\u0631\u062d\u0628\u0627",
        "\u060c",
        "\u0628\u0627\u0644\u0639\u0627\u0644\u0645",
        "\u061f",
    ]
