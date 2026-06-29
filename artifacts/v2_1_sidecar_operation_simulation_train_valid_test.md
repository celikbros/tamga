# v2.1 Passthrough Sidecar Operation Simulation

Input: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Max lines per split/file: `all`
Private worst-case samples: `artifacts/private/v2_1_sidecar_operation_simulation_train_valid_test.samples.jsonl`

This audit simulates a downstream training-mask operation for the
`sp64_protected_passthrough_sidecar` contract. Protected spans are exact
byte ranges in the sidecar, while model tokens may straddle span edges.
The safe token-index policy maps each protected byte span to every
overlapping SP token, conservatively over-masking boundary tokens.

## Split Summary

| Split | Lines | Raw bytes | Protected spans | Protected bytes | Protected bytes/raw byte | Conservative mask bytes | Extra mask bytes | Extra mask bytes/raw byte | Extra/protected byte | Edge-aligned span rate | Crossing span rate | Avg tokens/span | Max extra bytes/span |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `train` | 16000 | 22819852 | 76373 | 372934 | 0.016343 | 466929 | 93995 | 0.004119 | 0.252042 | 0.073246 | 0.926754 | 1.819884 | 9 |
| `valid` | 1994 | 2843294 | 9552 | 46802 | 0.016460 | 58445 | 11643 | 0.004095 | 0.248771 | 0.074958 | 0.925042 | 1.861704 | 7 |
| `test` | 1998 | 2781995 | 9237 | 47166 | 0.016954 | 58161 | 10995 | 0.003952 | 0.233113 | 0.078380 | 0.921620 | 1.933636 | 8 |
| `all` | 19992 | 28445141 | 95162 | 466902 | 0.016414 | 583535 | 116633 | 0.004100 | 0.249802 | 0.073916 | 0.926084 | 1.835123 | 9 |

## Route Summary

| Route | Spans | Protected bytes | Summed extra bytes | Extra/protected byte | Edge-aligned span rate | Crossing span rate | Avg tokens/span | Max extra bytes/span | Top surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `numeric_like` | 80938 | 278878 | 106852 | 0.383150 | 0.064914 | 0.935086 | 1.524846 | 9 | `1`:2494, `2`:1929, `3`:1768, `4`:1488, `19`:1448, `5`:1447, `10`:1182, `6`:1107 |
| `file_like` | 8005 | 128789 | 7790 | 0.060487 | 0.067958 | 0.932042 | 3.791131 | 6 | `0.0px`:192, `p0.05`:76, `M.Ö`:49, `12.0px`:48, `T.C`:40, `A.Ş`:33, `p.p1`:24, `14.0px`:24 |
| `apostrophe_surface` | 3662 | 37990 | 3201 | 0.084259 | 0.147187 | 0.852813 | 3.875751 | 3 | `Kur'an`:318, `Kur'ân`:178, `Cronbach's`:30, `İbnü'l`:28, `patient's`:24, `Mu'tezile`:21, `KUR'AN`:18, `şer'î`:16 |
| `non_turkish_latin_word` | 1644 | 17499 | 1368 | 0.078176 | 0.167883 | 0.832117 | 3.068127 | 1 | `É`:12, `Poincaré`:12, `þiddet`:11, `olduðu`:10, `öðrencilerin`:9, `öðretmen`:8, `adaylarýnýn`:8, `Cézanne`:8 |
| `greek_word` | 580 | 1292 | 286 | 0.221362 | 0.512069 | 0.487931 | 1.110345 | 4 | `α`:157, `μ`:95, `β`:76, `Δ`:59, `χ`:46, `λ`:20, `θ`:19, `η`:12 |
| `percent_encoded` | 163 | 489 | 262 | 0.535787 | 0.055215 | 0.944785 | 1.061350 | 9 | `%20`:158, `%da`:2, `%EC`:1, `%5C`:1, `%de`:1 |
| `arabic_word` | 106 | 1236 | 64 | 0.051780 | 0.754717 | 0.245283 | 4.745283 | 3 | `ى`:4, `و`:3, `كاد`:3, `وُ`:3, `ن`:2, `ل`:2, `إ`:2, `أبَداً`:2 |
| `uzbek_apostrophe_word` | 32 | 293 | 23 | 0.078498 | 0.281250 | 0.718750 | 3.375000 | 1 | `Muʻtezile`:5, `İʻcâz`:4, `Muʻcizât`:4, `Şerʻî`:2, `Ebülʻulâ`:2, `Mesʻûd`:2, `Mefʻûlün`:1, `iʻrâb`:1 |
| `azerbaijani_word` | 8 | 98 | 6 | 0.061224 | 0.250000 | 0.750000 | 4.625000 | 1 | `Azərbaycan`:2, `Kızılvəng`:1, `yenilikləri`:1, `ümumtəhsil`:1, `MüassirAzərbaycan`:1, `NizamiCefərov`:1, `Nəzami`:1 |
| `cyrillic_word` | 24 | 338 | 0 | 0.000000 | 1.000000 | 0.000000 | 6.916667 | 0 | `к`:3, `Петербург`:1, `Петербургские`:1, `дневники`:1, `Новый`:1, `историзм`:1, `Керченская`:1, `Катастрофа`:1 |

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
