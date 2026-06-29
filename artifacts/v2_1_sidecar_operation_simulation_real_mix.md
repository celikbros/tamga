# v2.1 Passthrough Sidecar Operation Simulation

Input: `artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Max lines per split/file: `all`
Private worst-case samples: `artifacts/private/v2_1_sidecar_operation_simulation_real_mix.samples.jsonl`

This audit simulates a downstream training-mask operation for the
`sp64_protected_passthrough_sidecar` contract. Protected spans are exact
byte ranges in the sidecar, while model tokens may straddle span edges.
The safe token-index policy maps each protected byte span to every
overlapping SP token, conservatively over-masking boundary tokens.

## Split Summary

| Split | Lines | Raw bytes | Protected spans | Protected bytes | Protected bytes/raw byte | Conservative mask bytes | Extra mask bytes | Extra mask bytes/raw byte | Extra/protected byte | Edge-aligned span rate | Crossing span rate | Avg tokens/span | Max extra bytes/span |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `real_mix_60k_sample` | 40388 | 44351801 | 149999 | 682931 | 0.015398 | 859592 | 176661 | 0.003983 | 0.258681 | 0.077861 | 0.922139 | 1.865539 | 9 |

## Route Summary

| Route | Spans | Protected bytes | Summed extra bytes | Extra/protected byte | Edge-aligned span rate | Crossing span rate | Avg tokens/span | Max extra bytes/span | Top surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `numeric_like` | 127588 | 434886 | 160582 | 0.369251 | 0.060672 | 0.939328 | 1.528827 | 9 | `1`:3834, `2`:3097, `3`:2720, `4`:2315, `5`:2268, `19`:1950, `10`:1811, `20`:1706 |
| `file_like` | 10309 | 140560 | 9588 | 0.068213 | 0.113299 | 0.886701 | 3.829178 | 6 | `M.Ö`:482, `0.0px`:192, `M.S`:87, `12.0px`:48, `T.C`:47, `A.Ş`:40, `p0.05`:40, `İ.Ö`:40 |
| `apostrophe_surface` | 7579 | 69792 | 6477 | 0.092804 | 0.155166 | 0.844834 | 3.982979 | 3 | `Kur'an`:366, `Kur'ân`:217, `Me'mûn`:90, `şer'î`:64, `Ma'lûl`:60, `İbnü'l`:57, `bi'l`:50, `Sa'id`:48 |
| `non_turkish_latin_word` | 3228 | 30236 | 2395 | 0.079210 | 0.258055 | 0.741945 | 3.639405 | 1 | `Wahšušana`:112, `Vámbéry`:93, `Ḫaldi`:49, `Aššur`:47, `İštar`:46, `Kaniš`:36, `Gāzî`:30, `Purušhattum`:27 |
| `greek_word` | 606 | 1885 | 279 | 0.148011 | 0.547855 | 0.452145 | 1.495050 | 4 | `α`:125, `μ`:101, `β`:80, `χ`:50, `Δ`:25, `λ`:20, `θ`:19, `σ`:12 |
| `percent_encoded` | 171 | 513 | 278 | 0.541910 | 0.052632 | 0.947368 | 1.046784 | 9 | `%20`:167, `%da`:2, `%EC`:1, `%5C`:1 |
| `arabic_word` | 391 | 3696 | 66 | 0.017857 | 0.930946 | 0.069054 | 4.265985 | 3 | `في`:9, `ر`:8, `التكرار`:6, `ل`:5, `ابن`:5, `قزل`:5, `على`:5, `وتكرار`:5 |
| `uzbek_apostrophe_word` | 69 | 641 | 65 | 0.101404 | 0.057971 | 0.942029 | 3.840580 | 1 | `Muʻtezile`:5, `vukûʻında`:4, `aʻzâ`:4, `taʻyîn`:3, `Şerʻî`:2, `Ebülʻulâ`:2, `şerʻiyye`:2, `Mesʻûd`:2 |
| `azerbaijani_word` | 8 | 98 | 6 | 0.061224 | 0.250000 | 0.750000 | 4.625000 | 1 | `Azərbaycan`:2, `Kızılvəng`:1, `yenilikləri`:1, `ümumtəhsil`:1, `MüassirAzərbaycan`:1, `NizamiCefərov`:1, `Nəzami`:1 |
| `cyrillic_word` | 50 | 624 | 0 | 0.000000 | 1.000000 | 0.000000 | 6.080000 | 0 | `к`:3, `ПО`:3, `и`:2, `Димитар`:1, `Димески`:1, `Македонското`:1, `национално`:1, `ослободително`:1 |

## Gate

Use this audit to decide whether byte-span metadata is operationally
safe enough for training-time masking/redaction workflows.

- `Extra mask bytes/raw byte` estimates the global data lost by
  conservative token over-masking.
- High route-specific `Extra/protected byte` suggests selective
  pre-splitting for that route class before considering global
  pre-splitting.
- This does not test exact constrained decoding/copy. If that becomes a
  base-model requirement, use a pre-split or route-selective aligned
  variant.
