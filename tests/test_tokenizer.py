from tr_tokenizer import TurkishTokenizer, decode, encode


def test_encode_splits_apostrophe_and_known_suffixes():
    tokenizer = TurkishTokenizer()

    assert tokenizer.encode("Türkiye'den kedilerden geldim.") == [
        "▁Türkiye",
        "'",
        "+den",
        "▁kedi",
        "+ler",
        "+den",
        "▁gel",
        "+di",
        "+m",
        ".",
    ]


def test_decode_round_trip_normalized_text():
    text = "Türkiye’den   kedilerden geldim."
    tokens = encode(text)

    assert decode(tokens) == "Türkiye'den kedilerden geldim."


def test_encode_requested_v02_examples():
    cases = {
        "Arabalarımızdan indiler.": [
            "▁Araba",
            "+lar",
            "+ımız",
            "+dan",
            "▁in",
            "+di",
            "+ler",
            ".",
        ],
        "Gelemeyecekmişsiniz.": [
            "▁Gel",
            "+eme",
            "+yecek",
            "+miş",
            "+siniz",
            ".",
        ],
        "Türkiye'den İstanbul'a gittim.": [
            "▁Türkiye",
            "'",
            "+den",
            "▁İstanbul",
            "'",
            "+a",
            "▁git",
            "+ti",
            "+m",
            ".",
        ],
        "Kitaplarımdan birini aldın mı?": [
            "▁Kitap",
            "+lar",
            "+ım",
            "+dan",
            "▁biri",
            "+ni",
            "▁al",
            "+dı",
            "+n",
            "▁mı",
            "?",
        ],
        "Arabalarımızdakilerdenmişsiniz.": [
            "▁Araba",
            "+lar",
            "+ımız",
            "+da",
            "+ki",
            "+ler",
            "+den",
            "+miş",
            "+siniz",
            ".",
        ],
        "Ağacın altında durdum.": [
            "▁Ağac",
            "+ın",
            "▁alt",
            "+ın",
            "+da",
            "▁dur",
            "+du",
            "+m",
            ".",
        ],
        "Rengini beğendim.": [
            "▁Reng",
            "+i",
            "+ni",
            "▁beğen",
            "+di",
            "+m",
            ".",
        ],
    }

    for text, expected_tokens in cases.items():
        assert encode(text) == expected_tokens


def test_decode_requested_v02_examples():
    texts = [
        "Arabalarımızdan indiler.",
        "Gelemeyecekmişsiniz.",
        "Türkiye'den İstanbul'a gittim.",
        "Kitaplarımdan birini aldın mı?",
        "Arabalarımızdakilerdenmişsiniz.",
        "Ağacın altında durdum.",
        "Rengini beğendim.",
    ]

    for text in texts:
        assert decode(encode(text)) == text


def test_encode_does_not_split_ambiguous_short_suffix_words():
    assert encode("kadın yakın altın kedi") == [
        "▁kadın",
        "▁yakın",
        "▁altın",
        "▁kedi",
    ]


def test_encode_v06_proper_name_softening_and_code_mixed_examples():
    cases = {
        "Ali'nin kitabı kayboldu.": [
            "▁Ali",
            "'",
            "+nin",
            "▁kitab",
            "+ı",
            "▁kaybol",
            "+du",
            ".",
        ],
        "Ayşe'nin arabası bozuldu.": [
            "▁Ayşe",
            "'",
            "+nin",
            "▁araba",
            "+sı",
            "▁bozul",
            "+du",
            ".",
        ],
        "API'den veri aldım.": [
            "▁API",
            "'",
            "+den",
            "▁veri",
            "▁al",
            "+dı",
            "+m",
            ".",
        ],
        "Python'da test yazdım.": [
            "▁Python",
            "'",
            "+da",
            "▁test",
            "▁yaz",
            "+dı",
            "+m",
            ".",
        ],
        "README.md dosyasını açtım.": [
            "▁README.md",
            "▁dosya",
            "+sı",
            "+nı",
            "▁aç",
            "+tı",
            "+m",
            ".",
        ],
        "config_v2.json dosyasını açtım.": [
            "▁config_v2.json",
            "▁dosya",
            "+sı",
            "+nı",
            "▁aç",
            "+tı",
            "+m",
            ".",
        ],
        "OpenAIlaştırılamayanlardanmış.": [
            "▁OpenAI",
            "+laştır",
            "+ıl",
            "+ama",
            "+yan",
            "+lar",
            "+dan",
            "+mış",
            ".",
        ],
    }

    for text, expected_tokens in cases.items():
        assert encode(text) == expected_tokens


def test_encode_v06_does_not_touch_informal_or_negative_guards():
    assert encode("Kadın yakın altın kedi.") == [
        "▁Kadın",
        "▁yakın",
        "▁altın",
        "▁kedi",
        ".",
    ]
    assert encode("Naber?") == ["▁Naber", "?"]


def test_encode_v07_informal_surface_forms():
    cases = {
        "Napıyorsun?": ["▁Napı", "+yor", "+sun", "?"],
        "Gelicem birazdan.": ["▁Gel", "+icem", "▁biraz", "+dan", "."],
        "Gidiyom ben.": ["▁Gid", "+iyom", "▁ben", "."],
        "Geliyom musun?": ["▁Gel", "+iyom", "▁mu", "+sun", "?"],
        "Naber?": ["▁Naber", "?"],
    }

    for text, expected_tokens in cases.items():
        assert encode(text) == expected_tokens


def test_encode_v07_regressions_stay_stable():
    cases = {
        "Kadın yakın altın kedi.": [
            "▁Kadın",
            "▁yakın",
            "▁altın",
            "▁kedi",
            ".",
        ],
        "OpenAIlaştırılamayanlardanmış.": [
            "▁OpenAI",
            "+laştır",
            "+ıl",
            "+ama",
            "+yan",
            "+lar",
            "+dan",
            "+mış",
            ".",
        ],
        "Ali'nin kitabı kayboldu.": [
            "▁Ali",
            "'",
            "+nin",
            "▁kitab",
            "+ı",
            "▁kaybol",
            "+du",
            ".",
        ],
        "Arabalarımızdakilerdenmişsiniz.": [
            "▁Araba",
            "+lar",
            "+ımız",
            "+da",
            "+ki",
            "+ler",
            "+den",
            "+miş",
            "+siniz",
            ".",
        ],
        "Geldim.": ["▁Gel", "+di", "+m", "."],
        "Alacak mısınız?": ["▁Al", "+acak", "▁mı", "+sınız", "?"],
    }

    for text, expected_tokens in cases.items():
        assert encode(text) == expected_tokens
