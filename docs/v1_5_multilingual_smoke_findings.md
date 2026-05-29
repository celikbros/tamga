# v1.5 Multilingual Smoke Findings

Date: 2026-05-30

Tokenizer behavior: not changed

## Purpose

This smoke set asks a narrow question:

```text
When non-Turkish text appears, does the Turkish-centered tokenizer avoid
damaging it?
```

This is not a multilingual morphology benchmark. It is a do-no-harm test for
future v2.0 routing and fallback design.

## Dataset

```text
data/eval/multilingual_smoke.tsv
```

Languages/scripts covered:

- Azerbaijani Latin
- Uzbek Latin apostrophe/tutuq forms
- Kazakh Cyrillic
- Kyrgyz Cyrillic
- Tatar Cyrillic
- French
- German
- Spanish
- Italian
- Arabic
- Russian
- Greek
- mixed Turkish/English/Cyrillic

## Summary

```text
custom_tr_morph exact_match: 8/20
custom_tr_morph boundary_f1: 0.6775
custom_tr_morph avg_tokens/word: 2.8493
```

All-baseline report:

```text
artifacts/v1_5_real_tokenizer_report_multilingual_smoke.md
```

## Baseline Table

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.8493 | 0.6775 | 8/20 |
| mistral | 4.8767 | 0.4835 | 0/20 |
| sp_bpe | 4.9041 | 0.4902 | 0/20 |
| sp_unigram | 4.9726 | 0.4848 | 0/20 |
| qwen | 4.1781 | 0.2079 | 0/20 |
| llama | 4.1644 | 0.2134 | 0/20 |
| toy_bpe_1000 | 6.6164 | 0.3368 | 0/20 |
| unicode_char | 7.6986 | 0.3601 | 0/20 |

## Category Findings

| Category | custom_tr_morph F1 | Main observation |
| --- | ---: | --- |
| kazakh_cyrillic | 1.0000 | Cyrillic Turkic words pass through as surface spans. |
| kyrgyz_cyrillic | 1.0000 | Cyrillic Turkic words pass through as surface spans. |
| russian | 1.0000 | Russian Cyrillic passes through as surface spans. |
| tatar_cyrillic | 1.0000 | Tatar Cyrillic passes through as surface spans. |
| uzbek_latin | 1.0000 | Uzbek apostrophe-like lexical spans are preserved. |
| azerbaijani | 0.8571 | Turkish morphology leaks into Azerbaijani words such as `adım`, `Bakıda`, `gedir`, `uzundur`. |
| french | 0.5385 | French apostrophe forms are split by Turkish apostrophe logic. |
| italian | 0.6154 | Italian apostrophe forms are split by Turkish apostrophe logic. |
| german | 0.5600 | Non-Turkish Latin letters like `ß` are split from words. |
| spanish | 0.2222 | Non-Turkish Latin diacritics like `ñ`, `ó`, `á` are split from words. |
| arabic | 0.1765 | Arabic script currently falls to character-level behavior. |
| greek | 0.2500 | Greek script currently falls to character-level behavior. |
| multilingual_mixed | 0.6250 | Hyphenated English-like compounds are split. |

## Important Mismatches

### Azerbaijani Leakage

```text
Mənim adım Əli, Bakıda yaşayıram.
expected: ▁Mənim ▁adım ▁Əli , ▁Bakıda ▁yaşayıram .
actual:   ▁Mənim ▁ad +ım ▁Əli , ▁Bak +ı +da ▁yaşayıram .
```

This confirms the routing risk: Turkish suffix rules can fire on Azerbaijani
Latin words.

### French / Italian Apostrophe

```text
Je viens d'Istanbul aujourd'hui.
actual: ▁Je ▁viens ▁d ' +Istanbul ▁aujourd ' +hui .

L'amico va all'università oggi.
actual: ▁L ' +amico ▁va ▁all ' +universit à ▁oggi .
```

These should not route through Turkish apostrophe splitting.

### Non-Turkish Latin Diacritics

```text
Straße -> ▁Stra ß ▁e
niño   -> ▁ni ñ ▁o
Bogotá -> ▁Bogot á
```

The current word scanner is Turkish-letter-centered, so Latin letters outside
the Turkish alphabet break surface spans.

### Arabic / Greek Character-Level Fallback

```text
مرحبا بالعالم. -> character sequence
Αθήνα είναι όμορφη πόλη. -> character sequence
```

This is not destructive for roundtrip, but it is inefficient and not ideal for a
future multilingual tokenizer.

## What Looks Good

- Uzbek apostrophe-like lexical forms are preserved:
  `Oʻzbekiston`, `gʻisht`, `sanʼat`, `maʼno`.
- Cyrillic Turkic and Russian words generally pass through as whole surface
  spans.
- The tokenizer does not attempt to transliterate or normalize non-Turkish
  scripts.

## Recommended Follow-Up

Do not implement full multilingual morphology in v1.x.

Low-risk v1.x do-no-harm candidates:

1. Add a generic non-Turkish Latin word guard for letters outside Turkish
   alphabet, so `Straße`, `niño`, `Bogotá`, `università` pass through as surface
   spans.
2. Add a non-Turkish apostrophe guard for French/Italian/English forms, while
   preserving Turkish apostrophe suffix splitting.
3. Strengthen Azerbaijani routing: if a word contains Azerbaijani-specific
   letters such as `ə/Ə`, `q`, or `x`, avoid Turkish suffix splitting for the
   whole span or sentence-level local context.
4. Add script-span fallback for Arabic and Greek so words stay as word-level
   spans rather than character-level spans.

These are routing/pretokenizer safeguards, not new morphology rules.

## v2.0 Implication

The multilingual path should be:

```text
script/language-aware routing
+ cross-language protection
+ high-precision Turkish morphology
+ Turkic-aware layer only when cues are strong
+ MorphBPE/Unigram fallback
+ byte fallback
```

The most important rule remains:

```text
Unknown or non-Turkish text should fall back safely instead of being forced
through Turkish morphology.
```
