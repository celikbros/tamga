# v1.8 Canary Diagnostics

Input: `data/eval/v1_8_canary.tsv`

This is a small public/synthetic diagnostic set. It is not a hidden eval,
not a downstream LM-loss result, and not a final tokenizer selection.

## Summary

| Model | Status | Lines | Words | Bytes | Tokens | Avg tokens/word | Tokens/byte | Bytes/token | Roundtrip failures | Protected broken | Unknown/byte tokens | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph_lossless | ok | 23 | 131 | 1055 | 290 | 2.2137 | 0.274882 | 3.6379 | 0 | 0/7 | 0 |  |
| sp_bpe_32000_train_only | ok | 23 | 131 | 1055 | 463 | 3.5344 | 0.438863 | 2.2786 | 0 | 7/7 | 0 |  |
| sp_unigram_32000_train_only | ok | 23 | 131 | 1055 | 478 | 3.6489 | 0.453081 | 2.2071 | 0 | 7/7 | 0 |  |
| sp_bpe_64000_train_only | ok | 23 | 131 | 1055 | 442 | 3.3740 | 0.418957 | 2.3869 | 0 | 7/7 | 0 |  |
| sp_unigram_64000_train_only | ok | 23 | 131 | 1055 | 455 | 3.4733 | 0.431280 | 2.3187 | 0 | 7/7 | 0 |  |
| hybrid_morph_pretok_bpe_64000_train_only | ok | 23 | 131 | 1055 | 455 | 3.4733 | 0.431280 | 2.3187 | 0 | 7/7 | 0 |  |
| hybrid_morph_pretok_unigram_64000_train_only | ok | 23 | 131 | 1055 | 468 | 3.5725 | 0.443602 | 2.2543 | 0 | 7/7 | 0 |  |
| unicode_char | ok | 23 | 131 | 1055 | 782 | 5.9695 | 0.741232 | 1.3491 | 23 | 7/7 | 0 |  |

## Category Diagnostics

### custom_tr_morph_lossless

| Category | Lines | Avg tokens/word | Roundtrip failures |
| --- | ---: | ---: | ---: |
| arabic | 1 | 2.0000 | 0 |
| ascii_folded | 2 | 2.2000 | 0 |
| azerbaijani | 2 | 2.6667 | 0 |
| code_mixed | 2 | 2.4000 | 0 |
| emoji_symbol | 1 | 3.6667 | 0 |
| english | 2 | 1.7143 | 0 |
| greek | 1 | 2.0000 | 0 |
| kazakh_cyrillic | 1 | 2.2000 | 0 |
| kyrgyz_cyrillic | 1 | 2.7143 | 0 |
| russian | 1 | 2.6667 | 0 |
| tatar_cyrillic | 1 | 2.8571 | 0 |
| technical | 2 | 0.9000 | 0 |
| turkish_clean | 2 | 3.2727 | 0 |
| turkish_noisy | 2 | 2.1818 | 0 |
| uzbek_latin | 2 | 2.4286 | 0 |

### sp_bpe_32000_train_only

| Category | Lines | Avg tokens/word | Roundtrip failures |
| --- | ---: | ---: | ---: |
| arabic | 1 | 7.5000 | 0 |
| ascii_folded | 2 | 2.8000 | 0 |
| azerbaijani | 2 | 3.2500 | 0 |
| code_mixed | 2 | 2.8000 | 0 |
| emoji_symbol | 1 | 3.0000 | 0 |
| english | 2 | 2.5714 | 0 |
| greek | 1 | 6.2500 | 0 |
| kazakh_cyrillic | 1 | 8.2000 | 0 |
| kyrgyz_cyrillic | 1 | 5.2857 | 0 |
| russian | 1 | 7.0000 | 0 |
| tatar_cyrillic | 1 | 6.0000 | 0 |
| technical | 2 | 2.1500 | 0 |
| turkish_clean | 2 | 2.5455 | 0 |
| turkish_noisy | 2 | 2.0000 | 0 |
| uzbek_latin | 2 | 5.0000 | 0 |

### sp_unigram_32000_train_only

| Category | Lines | Avg tokens/word | Roundtrip failures |
| --- | ---: | ---: | ---: |
| arabic | 1 | 7.5000 | 0 |
| ascii_folded | 2 | 2.8000 | 0 |
| azerbaijani | 2 | 3.3333 | 0 |
| code_mixed | 2 | 2.9333 | 0 |
| emoji_symbol | 1 | 2.6667 | 0 |
| english | 2 | 3.0000 | 0 |
| greek | 1 | 6.2500 | 0 |
| kazakh_cyrillic | 1 | 8.2000 | 0 |
| kyrgyz_cyrillic | 1 | 5.2857 | 0 |
| russian | 1 | 7.3333 | 0 |
| tatar_cyrillic | 1 | 6.0000 | 0 |
| technical | 2 | 2.3000 | 0 |
| turkish_clean | 2 | 2.7273 | 0 |
| turkish_noisy | 2 | 1.9091 | 0 |
| uzbek_latin | 2 | 5.2857 | 0 |

### sp_bpe_64000_train_only

| Category | Lines | Avg tokens/word | Roundtrip failures |
| --- | ---: | ---: | ---: |
| arabic | 1 | 6.5000 | 0 |
| ascii_folded | 2 | 2.7000 | 0 |
| azerbaijani | 2 | 3.1667 | 0 |
| code_mixed | 2 | 2.4667 | 0 |
| emoji_symbol | 1 | 2.6667 | 0 |
| english | 2 | 2.4286 | 0 |
| greek | 1 | 6.2500 | 0 |
| kazakh_cyrillic | 1 | 8.2000 | 0 |
| kyrgyz_cyrillic | 1 | 5.2857 | 0 |
| russian | 1 | 7.0000 | 0 |
| tatar_cyrillic | 1 | 6.0000 | 0 |
| technical | 2 | 1.9500 | 0 |
| turkish_clean | 2 | 2.3636 | 0 |
| turkish_noisy | 2 | 1.8182 | 0 |
| uzbek_latin | 2 | 4.8571 | 0 |

### sp_unigram_64000_train_only

| Category | Lines | Avg tokens/word | Roundtrip failures |
| --- | ---: | ---: | ---: |
| arabic | 1 | 6.5000 | 0 |
| ascii_folded | 2 | 2.7000 | 0 |
| azerbaijani | 2 | 3.1667 | 0 |
| code_mixed | 2 | 2.6000 | 0 |
| emoji_symbol | 1 | 2.6667 | 0 |
| english | 2 | 2.5000 | 0 |
| greek | 1 | 6.2500 | 0 |
| kazakh_cyrillic | 1 | 8.2000 | 0 |
| kyrgyz_cyrillic | 1 | 5.2857 | 0 |
| russian | 1 | 7.0000 | 0 |
| tatar_cyrillic | 1 | 6.0000 | 0 |
| technical | 2 | 2.3000 | 0 |
| turkish_clean | 2 | 2.4545 | 0 |
| turkish_noisy | 2 | 1.7273 | 0 |
| uzbek_latin | 2 | 5.2857 | 0 |

### hybrid_morph_pretok_bpe_64000_train_only

| Category | Lines | Avg tokens/word | Roundtrip failures |
| --- | ---: | ---: | ---: |
| arabic | 1 | 7.0000 | 0 |
| ascii_folded | 2 | 2.4000 | 0 |
| azerbaijani | 2 | 3.3333 | 0 |
| code_mixed | 2 | 2.8667 | 0 |
| emoji_symbol | 1 | 3.0000 | 0 |
| english | 2 | 2.3571 | 0 |
| greek | 1 | 6.0000 | 0 |
| kazakh_cyrillic | 1 | 8.2000 | 0 |
| kyrgyz_cyrillic | 1 | 5.2857 | 0 |
| russian | 1 | 7.0000 | 0 |
| tatar_cyrillic | 1 | 6.0000 | 0 |
| technical | 2 | 2.1500 | 0 |
| turkish_clean | 2 | 2.5455 | 0 |
| turkish_noisy | 2 | 2.0000 | 0 |
| uzbek_latin | 2 | 4.8571 | 0 |

### hybrid_morph_pretok_unigram_64000_train_only

| Category | Lines | Avg tokens/word | Roundtrip failures |
| --- | ---: | ---: | ---: |
| arabic | 1 | 6.5000 | 0 |
| ascii_folded | 2 | 2.8000 | 0 |
| azerbaijani | 2 | 3.5833 | 0 |
| code_mixed | 2 | 2.9333 | 0 |
| emoji_symbol | 1 | 3.0000 | 0 |
| english | 2 | 2.5000 | 0 |
| greek | 1 | 6.2500 | 0 |
| kazakh_cyrillic | 1 | 8.2000 | 0 |
| kyrgyz_cyrillic | 1 | 5.2857 | 0 |
| russian | 1 | 7.0000 | 0 |
| tatar_cyrillic | 1 | 6.0000 | 0 |
| technical | 2 | 2.0500 | 0 |
| turkish_clean | 2 | 2.6364 | 0 |
| turkish_noisy | 2 | 2.1818 | 0 |
| uzbek_latin | 2 | 5.1429 | 0 |

### unicode_char

| Category | Lines | Avg tokens/word | Roundtrip failures |
| --- | ---: | ---: | ---: |
| arabic | 1 | 6.5000 | 1 |
| ascii_folded | 2 | 6.4000 | 2 |
| azerbaijani | 2 | 5.5000 | 2 |
| code_mixed | 2 | 6.2667 | 2 |
| emoji_symbol | 1 | 7.6667 | 1 |
| english | 2 | 5.7857 | 2 |
| greek | 1 | 5.2500 | 1 |
| kazakh_cyrillic | 1 | 7.4000 | 1 |
| kyrgyz_cyrillic | 1 | 4.4286 | 1 |
| russian | 1 | 6.6667 | 1 |
| tatar_cyrillic | 1 | 5.1429 | 1 |
| technical | 2 | 4.3500 | 2 |
| turkish_clean | 2 | 8.0909 | 2 |
| turkish_noisy | 2 | 5.2727 | 2 |
| uzbek_latin | 2 | 8.8571 | 2 |

## Highest Fertility Lines

### custom_tr_morph_lossless

- row 2 `turkish_clean`: 4.0000 tokens/word, 16 tokens - `Kitaplarımdan birkaçını İstanbul'a götürdüm.`
- row 23 `emoji_symbol`: 3.6667 tokens/word, 11 tokens - `Merhaba 👩‍💻 test ediyoruz.`
- row 1 `turkish_clean`: 2.8571 tokens/word, 20 tokens - `Türkiye'de 2026'da yeni bir tokenizer denemesi yaptık.`
- row 19 `tatar_cyrillic`: 2.8571 tokens/word, 20 tokens - `Татарча: әни, җил, күңел, өч, үрдәк, һава.`
- row 13 `azerbaijani`: 2.8000 tokens/word, 14 tokens - `Mənim adım Əli, Bakıda yaşayıram.`

### sp_bpe_32000_train_only

- row 17 `kazakh_cyrillic`: 8.2000 tokens/word, 41 tokens - `Қазақстанда тұрамын, Алматы қаласы әдемі.`
- row 20 `arabic`: 7.5000 tokens/word, 15 tokens - `مرحبا بالعالم.`
- row 21 `russian`: 7.0000 tokens/word, 21 tokens - `Москва — большой город.`
- row 22 `greek`: 6.2500 tokens/word, 25 tokens - `Αθήνα είναι όμορφη πόλη.`
- row 19 `tatar_cyrillic`: 6.0000 tokens/word, 42 tokens - `Татарча: әни, җил, күңел, өч, үрдәк, һава.`

### sp_unigram_32000_train_only

- row 17 `kazakh_cyrillic`: 8.2000 tokens/word, 41 tokens - `Қазақстанда тұрамын, Алматы қаласы әдемі.`
- row 20 `arabic`: 7.5000 tokens/word, 15 tokens - `مرحبا بالعالم.`
- row 21 `russian`: 7.3333 tokens/word, 22 tokens - `Москва — большой город.`
- row 22 `greek`: 6.2500 tokens/word, 25 tokens - `Αθήνα είναι όμορφη πόλη.`
- row 19 `tatar_cyrillic`: 6.0000 tokens/word, 42 tokens - `Татарча: әни, җил, күңел, өч, үрдәк, һава.`

### sp_bpe_64000_train_only

- row 17 `kazakh_cyrillic`: 8.2000 tokens/word, 41 tokens - `Қазақстанда тұрамын, Алматы қаласы әдемі.`
- row 21 `russian`: 7.0000 tokens/word, 21 tokens - `Москва — большой город.`
- row 20 `arabic`: 6.5000 tokens/word, 13 tokens - `مرحبا بالعالم.`
- row 22 `greek`: 6.2500 tokens/word, 25 tokens - `Αθήνα είναι όμορφη πόλη.`
- row 19 `tatar_cyrillic`: 6.0000 tokens/word, 42 tokens - `Татарча: әни, җил, күңел, өч, үрдәк, һава.`

### sp_unigram_64000_train_only

- row 17 `kazakh_cyrillic`: 8.2000 tokens/word, 41 tokens - `Қазақстанда тұрамын, Алматы қаласы әдемі.`
- row 21 `russian`: 7.0000 tokens/word, 21 tokens - `Москва — большой город.`
- row 20 `arabic`: 6.5000 tokens/word, 13 tokens - `مرحبا بالعالم.`
- row 22 `greek`: 6.2500 tokens/word, 25 tokens - `Αθήνα είναι όμορφη πόλη.`
- row 19 `tatar_cyrillic`: 6.0000 tokens/word, 42 tokens - `Татарча: әни, җил, күңел, өч, үрдәк, һава.`

### hybrid_morph_pretok_bpe_64000_train_only

- row 17 `kazakh_cyrillic`: 8.2000 tokens/word, 41 tokens - `Қазақстанда тұрамын, Алматы қаласы әдемі.`
- row 21 `russian`: 7.0000 tokens/word, 21 tokens - `Москва — большой город.`
- row 20 `arabic`: 7.0000 tokens/word, 14 tokens - `مرحبا بالعالم.`
- row 19 `tatar_cyrillic`: 6.0000 tokens/word, 42 tokens - `Татарча: әни, җил, күңел, өч, үрдәк, һава.`
- row 22 `greek`: 6.0000 tokens/word, 24 tokens - `Αθήνα είναι όμορφη πόλη.`

### hybrid_morph_pretok_unigram_64000_train_only

- row 17 `kazakh_cyrillic`: 8.2000 tokens/word, 41 tokens - `Қазақстанда тұрамын, Алматы қаласы әдемі.`
- row 21 `russian`: 7.0000 tokens/word, 21 tokens - `Москва — большой город.`
- row 20 `arabic`: 6.5000 tokens/word, 13 tokens - `مرحبا بالعالم.`
- row 22 `greek`: 6.2500 tokens/word, 25 tokens - `Αθήνα είναι όμορφη πόλη.`
- row 19 `tatar_cyrillic`: 6.0000 tokens/word, 42 tokens - `Татарча: әни, җил, күңел, өч, үрдәк, һава.`

### unicode_char

- row 15 `uzbek_latin`: 10.6667 tokens/word, 32 tokens - `Oʻzbekistonning poytaxti Toshkent.`
- row 2 `turkish_clean`: 10.2500 tokens/word, 41 tokens - `Kitaplarımdan birkaçını İstanbul'a götürdüm.`
- row 5 `ascii_folded`: 7.8000 tokens/word, 39 tokens - `Turkiye'de Istanbul isigi farkli gorunuyor.`
- row 23 `emoji_symbol`: 7.6667 tokens/word, 23 tokens - `Merhaba 👩‍💻 test ediyoruz.`
- row 16 `uzbek_latin`: 7.5000 tokens/word, 30 tokens - `Oʻzbekcha: gʻisht, sanʼat, maʼno.`

## Notes

- The custom tokenizer is evaluated in lossless whitespace-preserving mode here.
- Protected candidates are auto-detected URL/file-like/numeric-like/comparator spans.
- Unknown/byte token count is a coarse diagnostic for explicit fallback markers.
- Canary failures should block overconfident claims, not automatically kill the project.
