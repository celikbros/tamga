# v2.1 Sidecar Protected Route Density Audit

Input: `artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Max lines per split/file: `all`
Include EOS in token pressure: `False`
Token pressure mode: `True`

This audit estimates whether the selected passthrough sidecar baseline
is exposed to a different protected-span density than the v1.8 pilot.
It also reports the local pre-split token tax on the same text.

## Split Summary

| Split | Lines | Raw bytes | Protected spans | Protected bytes | Protected bytes/raw byte | Protected line share | SP tokens/raw byte | Passthrough tokens/raw byte | Pre-split tokens/raw byte | Pre-split tax tokens/raw byte | Pre-split tax relative |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `real_mix_60k_sample` | 40388 | 44351801 | 149999 | 682931 | 0.015398 | 0.680053 | 0.167769 | 0.167822 | 0.173911 | 0.006088 | 0.036279 |

## Route Summary

| Route | Occurrences | Bytes | Bytes/raw byte | Line share | Unique surfaces | Top surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `numeric_like` | 127588 | 434886 | 0.009805 | 0.615034 | 21045 | `1`:3834, `2`:3097, `3`:2720, `4`:2315, `5`:2268, `19`:1950, `10`:1811, `20`:1706 |
| `file_like` | 10309 | 140560 | 0.003169 | 0.128578 | 7118 | `M.Ö`:482, `0.0px`:192, `M.S`:87, `12.0px`:48, `T.C`:47, `A.Ş`:40, `p0.05`:40, `İ.Ö`:40 |
| `apostrophe_surface` | 7579 | 69792 | 0.001574 | 0.094954 | 3784 | `Kur'an`:366, `Kur'ân`:217, `Me'mûn`:90, `şer'î`:64, `Ma'lûl`:60, `İbnü'l`:57, `bi'l`:50, `Sa'id`:48 |
| `non_turkish_latin_word` | 3228 | 30236 | 0.000682 | 0.017654 | 1733 | `Wahšušana`:112, `Vámbéry`:93, `Ḫaldi`:49, `Aššur`:47, `İštar`:46, `Kaniš`:36, `Gāzî`:30, `Purušhattum`:27 |
| `arabic_word` | 391 | 3696 | 0.000083 | 0.001089 | 285 | `في`:9, `ر`:8, `التكرار`:6, `ل`:5, `ابن`:5, `قزل`:5, `على`:5, `وتكرار`:5 |
| `greek_word` | 606 | 1885 | 0.000043 | 0.006264 | 85 | `α`:125, `μ`:101, `β`:80, `χ`:50, `Δ`:25, `λ`:20, `θ`:19, `σ`:12 |
| `uzbek_apostrophe_word` | 69 | 641 | 0.000014 | 0.000619 | 47 | `Muʻtezile`:5, `vukûʻında`:4, `aʻzâ`:4, `taʻyîn`:3, `Şerʻî`:2, `Ebülʻulâ`:2, `şerʻiyye`:2, `Mesʻûd`:2 |
| `cyrillic_word` | 50 | 624 | 0.000014 | 0.000421 | 45 | `к`:3, `ПО`:3, `и`:2, `Димитар`:1, `Димески`:1, `Македонското`:1, `национално`:1, `ослободително`:1 |
| `percent_encoded` | 171 | 513 | 0.000012 | 0.003318 | 4 | `%20`:167, `%da`:2, `%EC`:1, `%5C`:1 |
| `azerbaijani_word` | 8 | 98 | 0.000002 | 0.000074 | 7 | `Azərbaycan`:2, `Kızılvəng`:1, `yenilikləri`:1, `ümumtəhsil`:1, `MüassirAzərbaycan`:1, `NizamiCefərov`:1, `Nəzami`:1 |

## Gate

Use this report before any future global pre-split decision.

- If protected bytes/raw byte is much higher than the v1.8 pilot, the
  global pre-split tax is likely understated by previous results.
- If only a few routes dominate, prefer selective pre-split by route
  class over global pre-split.
- Run with `--with-token-pressure` only for small samples or when
  the extra encoding cost is acceptable.
- `sp64_protected_passthrough_sidecar` remains the default v2.1
  baseline unless token-boundary alignment is a committed requirement.
