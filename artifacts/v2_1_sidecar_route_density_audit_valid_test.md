# v2.1 Sidecar Protected Route Density Audit

Input: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Max lines per split/file: `all`
Include EOS in token pressure: `False`
Token pressure mode: `False`

This audit estimates whether the selected passthrough sidecar baseline
is exposed to a different protected-span density than the v1.8 pilot.
It also reports the local pre-split token tax on the same text.

## Split Summary

| Split | Lines | Raw bytes | Protected spans | Protected bytes | Protected bytes/raw byte | Protected line share | SP tokens/raw byte | Passthrough tokens/raw byte | Pre-split tokens/raw byte | Pre-split tax tokens/raw byte | Pre-split tax relative |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `valid` | 1994 | 2843294 | 9552 | 46802 | 0.016460 | 0.757272 | n/a | n/a | n/a | n/a | n/a |
| `test` | 1998 | 2781995 | 9237 | 47166 | 0.016954 | 0.736236 | n/a | n/a | n/a | n/a | n/a |
| `all` | 3992 | 5625289 | 18789 | 93968 | 0.016705 | 0.746743 | n/a | n/a | n/a | n/a | n/a |

## Route Summary

| Route | Occurrences | Bytes | Bytes/raw byte | Line share | Unique surfaces | Top surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `numeric_like` | 15914 | 54914 | 0.009762 | 0.667084 | 4714 | `1`:491, `2`:360, `3`:351, `4`:302, `19`:299, `5`:258, `10`:214, `20`:198 |
| `file_like` | 1636 | 26792 | 0.004763 | 0.217435 | 1424 | `0.0px`:24, `M.Ö`:15, `T.C`:10, `p0.05`:10, `A.Ş`:7, `3.molar`:7, `s.a.v`:6, `12.0px`:6 |
| `apostrophe_surface` | 698 | 7403 | 0.001316 | 0.088928 | 496 | `Kur'an`:61, `Kur'ân`:21, `İbnü'l`:10, `Babü'l`:8, `cüz'î`:7, `ma'rûf`:7, `fi'l`:6, `İbnü'n`:6 |
| `non_turkish_latin_word` | 381 | 4191 | 0.000745 | 0.014780 | 309 | `Poincaré`:9, `þiddet`:6, `dikē`:4, `István`:4, `Cordobés`:3, `oluĢturduğu`:3, `eðitsel`:3, `programlarý`:3 |
| `greek_word` | 101 | 214 | 0.000038 | 0.011774 | 13 | `α`:37, `μ`:16, `χ`:10, `β`:10, `Δ`:8, `θ`:8, `Ψ`:5, `ϵ`:2 |
| `cyrillic_word` | 11 | 152 | 0.000027 | 0.000752 | 11 | `Ф`:1, `Ѐ`:1, `Димитар`:1, `Димески`:1, `Македонското`:1, `национално`:1, `ослободително`:1, `движење`:1 |
| `uzbek_apostrophe_word` | 13 | 127 | 0.000023 | 0.001002 | 8 | `Muʻtezile`:4, `Ebülʻulâ`:2, `Mesʻûd`:2, `Şerʻî`:1, `şerʻiyye`:1, `MUʻCİZÂT`:1, `Muʻcizât`:1, `Eşʻıyâ`:1 |
| `arabic_word` | 6 | 88 | 0.000016 | 0.000501 | 5 | `قَرْن`:2, `لِمَنْ`:1, `أَرَادَ`:1, `قَرْنَ`:1, `فِيبُيُوتِكُنَّ`:1 |
| `percent_encoded` | 29 | 87 | 0.000015 | 0.006012 | 2 | `%20`:28, `%de`:1 |

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
