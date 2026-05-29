from tr_tokenizer import TurkishTokenizer, decode, encode
from tr_tokenizer.tokenizer import WORD_START


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


def test_encode_v11_low_risk_pretokenizer_targets():
    cases = {
        "2025'ten sonra değişti.": [
            "▁2025",
            "'",
            "+ten",
            "▁sonra",
            "▁değiş",
            "+ti",
            ".",
        ],
        "3.14 değerini yazdım.": [
            "▁3.14",
            "▁değer",
            "+i",
            "+ni",
            "▁yaz",
            "+dı",
            "+m",
            ".",
        ],
        "34-ABC-1907 plakası vardı.": [
            "▁34-ABC-1907",
            "▁plaka",
            "+sı",
            "▁var",
            "+dı",
            ".",
        ],
        "%25'lik artış oldu.": [
            "%",
            "▁25",
            "'",
            "+lik",
            "▁artış",
            "▁ol",
            "+du",
            ".",
        ],
        "README.md'yi açtın mı?": [
            "▁README.md",
            "'",
            "+yi",
            "▁aç",
            "+tı",
            "+n",
            "▁mı",
            "?",
        ],
        "Ali, Ayşe'ye baktı.": [
            "▁Ali",
            ",",
            "▁Ayşe",
            "'",
            "+ye",
            "▁bak",
            "+tı",
            ".",
        ],
        "“Merhaba,” dedi.": [
            "“",
            "▁Merhaba",
            ",",
            "”",
            "▁de",
            "+di",
            ".",
        ],
        "Evet; ama sonra döndü.": [
            "▁Evet",
            ";",
            "▁ama",
            "▁sonra",
            "▁dön",
            "+dü",
            ".",
        ],
    }

    for text, expected_tokens in cases.items():
        assert encode(text) == expected_tokens


def test_encode_v11_high_risk_categories_stay_stable():
    cases = {
        "Kadın yakın altın kedi.": [
            "▁Kadın",
            "▁yakın",
            "▁altın",
            "▁kedi",
            ".",
        ],
        "Yazın tatile gittik.": [
            "▁Yaz",
            "+ın",
            "▁tatile",
            "▁git",
            "+ti",
            "+k",
            ".",
        ],
        "Yazarım ama göndermem.": [
            "▁Yazar",
            "+ım",
            "▁ama",
            "▁göndermem",
            ".",
        ],
        "Gül dalında açtı.": [
            "▁Gül",
            "▁dalın",
            "+da",
            "▁aç",
            "+tı",
            ".",
        ],
        "Yüz kişi geldi.": [
            "▁Yüz",
            "▁kişi",
            "▁gel",
            "+di",
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


def test_encode_v13_keeps_urls_as_protected_spans():
    assert encode("See https://example.com/tr/page now.") == [
        f"{WORD_START}See",
        f"{WORD_START}https://example.com/tr/page",
        f"{WORD_START}now",
        ".",
    ]
    assert decode(encode("https://example.com/2024-05-19 dosya.py")) == (
        "https://example.com/2024-05-19 dosya.py"
    )


def test_decode_v13_preserves_smart_double_quote_spacing():
    assert decode(encode("“Merhaba,” dedi.")) == "“Merhaba,” dedi."


def test_decode_v13_preserves_code_call_spacing():
    text = "def kullanici_adi(ad): return ad.strip() # Türkçe örnek"
    assert decode(encode(text)) == text


def test_decode_v13_keeps_plain_parentheses_spacing():
    assert decode([f"{WORD_START}Bunu", "(", f"{WORD_START}test", ")"]) == "Bunu (test)"


def test_encode_v13_keeps_uzbek_apostrophe_words_intact():
    assert encode("Oʻzbekistonning poytaxti Toshkent.") == [
        f"{WORD_START}Oʻzbekistonning",
        f"{WORD_START}poytaxti",
        f"{WORD_START}Toshkent",
        ".",
    ]
    assert decode(encode("Oʻzbekcha: gʻisht, sanʼat, maʼno.")) == (
        "Oʻzbekcha: gʻisht, sanʼat, maʼno."
    )


def test_encode_v13_keeps_azerbaijani_specific_words_intact():
    assert encode("Mənim adım Əli, Bakıda yaşayıram.") == [
        f"{WORD_START}Mənim",
        f"{WORD_START}ad",
        "+ım",
        f"{WORD_START}Əli",
        ",",
        f"{WORD_START}Bak",
        "+ı",
        "+da",
        f"{WORD_START}yaşayıram",
        ".",
    ]
    assert decode(encode("Xəbər: qız məktəbə gedir, dağ yolu uzundur.")) == (
        "Xəbər: qız məktəbə gedir, dağ yolu uzundur."
    )


def test_encode_v13_keeps_cyrillic_words_intact():
    assert encode("Қазақстан Республикасы — Алматы қаласы.") == [
        f"{WORD_START}Қазақстан",
        f"{WORD_START}Республикасы",
        "—",
        f"{WORD_START}Алматы",
        f"{WORD_START}қаласы",
        ".",
    ]
    assert decode(encode("Кыргызча: тоо, суу, өң, үн, жаңы күн.")) == (
        "Кыргызча: тоо, суу, өң, үн, жаңы күн."
    )


def test_encode_v14_protects_exact_low_risk_words():
    assert encode("Peki... sonra ne oldu?") == [
        f"{WORD_START}Peki",
        ".",
        ".",
        ".",
        f"{WORD_START}sonra",
        f"{WORD_START}ne",
        f"{WORD_START}ol",
        "+du",
        "?",
    ]
    assert encode("(Ankara'dan) yeni döndüm.") == [
        "(",
        f"{WORD_START}Ankara",
        "'",
        "+dan",
        ")",
        f"{WORD_START}yeni",
        f"{WORD_START}dön",
        "+dü",
        "+m",
        ".",
    ]


def test_encode_v14_protection_regressions_stay_stable():
    cases = {
        "Kadın yakın altın kedi.": [
            f"{WORD_START}Kadın",
            f"{WORD_START}yakın",
            f"{WORD_START}altın",
            f"{WORD_START}kedi",
            ".",
        ],
        "Yazın tatile gittik.": [
            f"{WORD_START}Yaz",
            "+ın",
            f"{WORD_START}tatile",
            f"{WORD_START}git",
            "+ti",
            "+k",
            ".",
        ],
        "Yazarım ama göndermem.": [
            f"{WORD_START}Yazar",
            "+ım",
            f"{WORD_START}ama",
            f"{WORD_START}göndermem",
            ".",
        ],
        "Arabalarımızdakilerdenmişsiniz.": [
            f"{WORD_START}Araba",
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
        "OpenAIlaştırılamayanlardanmış.": [
            f"{WORD_START}OpenAI",
            "+laştır",
            "+ıl",
            "+ama",
            "+yan",
            "+lar",
            "+dan",
            "+mış",
            ".",
        ],
        "Don't split John's book.": [
            f"{WORD_START}Don",
            "'",
            "+t",
            f"{WORD_START}split",
            f"{WORD_START}John",
            "'",
            "+s",
            f"{WORD_START}book",
            ".",
        ],
        "Oʻzbekcha: gʻisht, sanʼat, maʼno.": [
            f"{WORD_START}Oʻzbekcha",
            ":",
            f"{WORD_START}gʻisht",
            ",",
            f"{WORD_START}sanʼat",
            ",",
            f"{WORD_START}maʼno",
            ".",
        ],
    }

    for text, expected_tokens in cases.items():
        assert encode(text) == expected_tokens
