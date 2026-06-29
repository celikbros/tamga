# v2.4 LLM Consumer Simulation

Input: `artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt`
Sidecar: `artifacts/private/v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl`

This audit simulates three downstream operations over the frozen sidecar:

```text
copy protected bytes by sidecar offsets
redact protected spans in raw text
map protected byte spans to conservative overlapping SP tokens for masking
```

## Summary

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| raw bytes | 44351801 |
| protected spans | 149999 |
| protected bytes/raw byte | 0.015398 |
| copy failures | 0 |
| redaction failures | 0 |
| token-mask failures | 0 |
| total failures | 0 |
| conservative mask bytes | 859592 |
| extra mask bytes | 176661 |
| extra mask bytes/raw byte | 0.003983 |
| extra/protected byte | 0.258681 |
| edge-aligned span rate | 0.077861 |
| crossing span rate | 0.922139 |
| avg tokens/span | 1.865539 |
| max extra bytes/span | 9 |
| status | PASS |

## Route Summary

| Route | Spans | Extra/protected byte | Edge-aligned span rate | Avg tokens/span | Max extra bytes/span | Top surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `apostrophe_surface` | 7579 | 0.092804 | 0.155166 | 3.982979 | 3 | `Kur'an`:366, `Kur'ân`:217, `Me'mûn`:90, `şer'î`:64, `Ma'lûl`:60 |
| `arabic_word` | 391 | 0.017857 | 0.930946 | 4.265985 | 3 | `في`:9, `ر`:8, `التكرار`:6, `ل`:5, `ابن`:5 |
| `azerbaijani_word` | 8 | 0.061224 | 0.250000 | 4.625000 | 1 | `Azərbaycan`:2, `Kızılvəng`:1, `yenilikləri`:1, `ümumtəhsil`:1, `MüassirAzərbaycan`:1 |
| `cyrillic_word` | 50 | 0.000000 | 1.000000 | 6.080000 | 0 | `к`:3, `ПО`:3, `и`:2, `Димитар`:1, `Димески`:1 |
| `file_like` | 10309 | 0.068213 | 0.113299 | 3.829178 | 6 | `M.Ö`:482, `0.0px`:192, `M.S`:87, `12.0px`:48, `T.C`:47 |
| `greek_word` | 606 | 0.148011 | 0.547855 | 1.495050 | 4 | `α`:125, `μ`:101, `β`:80, `χ`:50, `Δ`:25 |
| `non_turkish_latin_word` | 3228 | 0.079210 | 0.258055 | 3.639405 | 1 | `Wahšušana`:112, `Vámbéry`:93, `Ḫaldi`:49, `Aššur`:47, `İštar`:46 |
| `numeric_like` | 127588 | 0.369251 | 0.060672 | 1.528827 | 9 | `1`:3834, `2`:3097, `3`:2720, `4`:2315, `5`:2268 |
| `percent_encoded` | 171 | 0.541910 | 0.052632 | 1.046784 | 9 | `%20`:167, `%da`:2, `%EC`:1, `%5C`:1 |
| `uzbek_apostrophe_word` | 69 | 0.101404 | 0.057971 | 3.840580 | 1 | `Muʻtezile`:5, `vukûʻında`:4, `aʻzâ`:4, `taʻyîn`:3, `Şerʻî`:2 |

## Interpretation

The frozen sidecar supports the simulated LLM consumer operations.
