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
| `train` | 16000 | 22819852 | 76373 | 372934 | 0.016343 | 0.742125 | n/a | n/a | n/a | n/a | n/a |
| `valid` | 1994 | 2843294 | 9552 | 46802 | 0.016460 | 0.757272 | n/a | n/a | n/a | n/a | n/a |
| `test` | 1998 | 2781995 | 9237 | 47166 | 0.016954 | 0.736236 | n/a | n/a | n/a | n/a | n/a |
| `all` | 19992 | 28445141 | 95162 | 466902 | 0.016414 | 0.743047 | n/a | n/a | n/a | n/a | n/a |

## Route Summary

| Route | Occurrences | Bytes | Bytes/raw byte | Line share | Unique surfaces | Top surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `numeric_like` | 80938 | 278878 | 0.009804 | 0.665316 | 16574 | `1`:2494, `2`:1929, `3`:1768, `4`:1488, `19`:1448, `5`:1447, `10`:1182, `6`:1107 |
| `file_like` | 8005 | 128789 | 0.004528 | 0.208033 | 6434 | `0.0px`:192, `p0.05`:76, `M.Ö`:49, `12.0px`:48, `T.C`:40, `A.Ş`:33, `p.p1`:24, `14.0px`:24 |
| `apostrophe_surface` | 3662 | 37990 | 0.001336 | 0.092537 | 2188 | `Kur'an`:318, `Kur'ân`:178, `Cronbach's`:30, `İbnü'l`:28, `patient's`:24, `Mu'tezile`:21, `KUR'AN`:18, `şer'î`:16 |
| `non_turkish_latin_word` | 1644 | 17499 | 0.000615 | 0.015256 | 1121 | `É`:12, `Poincaré`:12, `þiddet`:11, `olduðu`:10, `öðrencilerin`:9, `öðretmen`:8, `adaylarýnýn`:8, `Cézanne`:8 |
| `greek_word` | 580 | 1292 | 0.000045 | 0.012755 | 43 | `α`:157, `μ`:95, `β`:76, `Δ`:59, `χ`:46, `λ`:20, `θ`:19, `η`:12 |
| `arabic_word` | 106 | 1236 | 0.000043 | 0.000700 | 91 | `ى`:4, `و`:3, `كاد`:3, `وُ`:3, `ن`:2, `ل`:2, `إ`:2, `أبَداً`:2 |
| `percent_encoded` | 163 | 489 | 0.000017 | 0.006403 | 5 | `%20`:158, `%da`:2, `%EC`:1, `%5C`:1, `%de`:1 |
| `cyrillic_word` | 24 | 338 | 0.000012 | 0.000350 | 22 | `к`:3, `Петербург`:1, `Петербургские`:1, `дневники`:1, `Новый`:1, `историзм`:1, `Керченская`:1, `Катастрофа`:1 |
| `uzbek_apostrophe_word` | 32 | 293 | 0.000010 | 0.000550 | 19 | `Muʻtezile`:5, `İʻcâz`:4, `Muʻcizât`:4, `Şerʻî`:2, `Ebülʻulâ`:2, `Mesʻûd`:2, `Mefʻûlün`:1, `iʻrâb`:1 |
| `azerbaijani_word` | 8 | 98 | 0.000003 | 0.000150 | 7 | `Azərbaycan`:2, `Kızılvəng`:1, `yenilikləri`:1, `ümumtəhsil`:1, `MüassirAzərbaycan`:1, `NizamiCefərov`:1, `Nəzami`:1 |

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
