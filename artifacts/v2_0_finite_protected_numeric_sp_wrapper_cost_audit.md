# v2.0 Finite Protected Wrapper Cost Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Numeric protected SP passthrough: `True`
Private top-delta examples: `artifacts/private/v2_0_finite_protected_numeric_sp_wrapper_cost_top_delta.jsonl`

This audit decomposes the token-pressure cost of the finite protected
wrapper before any new MorphBPE/constrained-tokenizer work.

## Split Summary

| Split | Lines | Raw bytes | SP tokens/raw byte | Finite tokens/raw byte | Delta tokens/raw byte | Relative delta | Protected bytes share | Protected tokens/protected byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | 1994 | 2843294 | 0.159020 | 0.171903 | 0.012883 | 0.081014 | 0.016455 | 0.601022 |
| test | 1998 | 2781995 | 0.159620 | 0.172734 | 0.013113 | 0.082153 | 0.016956 | 0.605181 |

## Finite Token Components

| Split | Segment SP tokens | Protected piece tokens | Protected SP passthrough tokens | Protected byte tokens | Hard suffix tokens | Apostrophe tokens | EOS tokens | Segment count | Protected pieces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | 447176 | 15636 | 12284 | 200 | 6389 | 5093 | 1994 | 354615 | 9545 |
| test | 439088 | 16331 | 11967 | 249 | 6122 | 4789 | 1998 | 346922 | 9234 |

## Highest Public Delta Lines

Raw text is omitted from this public report. Full private examples are
written to the JSONL path above.

| Split | Line | Raw bytes | SP tokens | Finite tokens | Delta | Protected pieces | Protected bytes | Routes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| valid | 818 | 1520 | 306 | 790 | 484 | 66 | 804 | `non_turkish_latin_word:64, numeric_like:2` |
| valid | 815 | 1029 | 239 | 508 | 269 | 41 | 460 | `non_turkish_latin_word:41` |
| valid | 535 | 2632 | 599 | 765 | 166 | 36 | 276 | `numeric_like:30, apostrophe_surface:5, file_like:1` |
| valid | 1510 | 1774 | 328 | 481 | 153 | 29 | 275 | `non_turkish_latin_word:19, numeric_like:10` |
| valid | 1920 | 3848 | 795 | 938 | 143 | 56 | 249 | `numeric_like:52, file_like:4` |
| valid | 1782 | 3223 | 862 | 984 | 122 | 76 | 275 | `numeric_like:69, file_like:4, apostrophe_surface:3` |
| valid | 82 | 1299 | 254 | 374 | 120 | 15 | 178 | `file_like:11, numeric_like:4` |
| valid | 1898 | 3136 | 620 | 734 | 114 | 31 | 161 | `numeric_like:20, file_like:11` |
| valid | 1787 | 3611 | 740 | 852 | 112 | 14 | 164 | `numeric_like:6, file_like:5, apostrophe_surface:3` |
| valid | 1789 | 3991 | 882 | 988 | 106 | 34 | 211 | `numeric_like:28, file_like:5, apostrophe_surface:1` |
| test | 865 | 1592 | 354 | 741 | 387 | 64 | 700 | `non_turkish_latin_word:59, numeric_like:5` |
| test | 1900 | 1146 | 253 | 456 | 203 | 28 | 379 | `non_turkish_latin_word:28` |
| test | 1799 | 4092 | 820 | 993 | 173 | 25 | 234 | `numeric_like:15, file_like:10` |
| test | 545 | 3194 | 543 | 697 | 154 | 13 | 213 | `apostrophe_surface:5, file_like:4, numeric_like:3, non_turkish_latin_word:1` |
| test | 1796 | 4073 | 803 | 954 | 151 | 23 | 186 | `numeric_like:15, file_like:7, apostrophe_surface:1` |
| test | 1362 | 3198 | 668 | 812 | 144 | 48 | 239 | `numeric_like:44, file_like:2, greek_word:1, apostrophe_surface:1` |
| test | 1064 | 2749 | 582 | 720 | 138 | 23 | 241 | `file_like:17, numeric_like:6` |
| test | 1029 | 1510 | 319 | 456 | 137 | 22 | 235 | `non_turkish_latin_word:21, numeric_like:1` |
| test | 34 | 2819 | 493 | 626 | 133 | 13 | 163 | `apostrophe_surface:7, numeric_like:6` |
| test | 1929 | 4180 | 867 | 990 | 123 | 26 | 89 | `numeric_like:22, file_like:2, apostrophe_surface:1, non_turkish_latin_word:1` |

## Protected Route Cost

| Route | Count | Bytes | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `numeric_like` | 15933 | 54992 | 24251 | 24251 | 0 | 0.440991 | 0.440991 |
| `file_like` | 1636 | 26792 | 21574 | 6462 | 15112 | 0.805240 | 0.241191 |
| `apostrophe_surface` | 698 | 7402 | 6774 | 2819 | 3955 | 0.915158 | 0.380843 |
| `non_turkish_latin_word` | 381 | 4191 | 3611 | 1362 | 2249 | 0.861608 | 0.324982 |
| `greek_word` | 101 | 214 | 131 | 129 | 2 | 0.612150 | 0.602804 |
| `uzbek_apostrophe_word` | 13 | 127 | 112 | 47 | 65 | 0.881890 | 0.370079 |
| `cyrillic_word` | 11 | 152 | 152 | 87 | 65 | 1.000000 | 0.572368 |
| `arabic_word` | 6 | 88 | 62 | 47 | 15 | 0.704545 | 0.534091 |

## Interpretation Gate

If protected bytes are a small share of the corpus but relative token
delta is large, the wrapper needs redesign before MorphBPE work.
If cost is concentrated in a few route kinds, optimize those routes
first.
