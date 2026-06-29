# v2.0 Finite Protected Wrapper Cost Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Private top-delta examples: `artifacts/private/v2_0_finite_protected_wrapper_cost_top_delta.jsonl`

This audit decomposes the token-pressure cost of the finite protected
wrapper before any new MorphBPE/constrained-tokenizer work.

## Split Summary

| Split | Lines | Raw bytes | SP tokens/raw byte | Finite tokens/raw byte | Delta tokens/raw byte | Relative delta | Protected bytes share | Protected tokens/protected byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 0.154680 | 0.178591 | 0.023910 | 0.154580 | 0.026123 | 0.853723 |
| valid | 1994 | 2843294 | 0.159020 | 0.182112 | 0.023092 | 0.145213 | 0.026063 | 0.857041 |
| test | 1998 | 2781995 | 0.159620 | 0.183362 | 0.023742 | 0.148738 | 0.026718 | 0.865772 |

## Finite Token Components

| Split | Segment SP tokens | Protected piece tokens | Protected byte tokens | Hard suffix tokens | Apostrophe tokens | EOS tokens | Segment count | Protected pieces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 3470059 | 507327 | 1597 | 44819 | 35612 | 16000 | 2827589 | 96132 |
| valid | 441787 | 63317 | 194 | 5815 | 4692 | 1994 | 351287 | 12027 |
| test | 433797 | 64103 | 249 | 5559 | 4406 | 1998 | 343627 | 11678 |

## Highest Public Delta Lines

Raw text is omitted from this public report. Full private examples are
written to the JSONL path above.

| Split | Line | Raw bytes | SP tokens | Finite tokens | Delta | Protected pieces | Protected bytes | Routes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| train | 6653 | 2753 | 540 | 1343 | 803 | 114 | 1245 | `non_turkish_latin_word:102, numeric_like:10, file_like:2` |
| train | 6657 | 2050 | 392 | 1089 | 697 | 95 | 1049 | `non_turkish_latin_word:86, numeric_like:8, apostrophe_surface:1` |
| train | 6673 | 1391 | 238 | 794 | 556 | 61 | 864 | `non_turkish_latin_word:61` |
| train | 6671 | 1507 | 262 | 760 | 498 | 62 | 732 | `non_turkish_latin_word:57, numeric_like:4, file_like:1` |
| train | 6656 | 1493 | 309 | 774 | 465 | 64 | 753 | `non_turkish_latin_word:59, numeric_like:5` |
| train | 6672 | 1414 | 251 | 597 | 346 | 48 | 519 | `non_turkish_latin_word:38, numeric_like:10` |
| train | 6658 | 1287 | 230 | 547 | 317 | 35 | 476 | `non_turkish_latin_word:34, numeric_like:1` |
| train | 4752 | 2139 | 449 | 764 | 315 | 68 | 490 | `non_turkish_latin_word:58, numeric_like:6, apostrophe_surface:4` |
| train | 7970 | 1727 | 344 | 656 | 312 | 52 | 519 | `non_turkish_latin_word:52` |
| train | 14390 | 4045 | 1073 | 1371 | 298 | 77 | 377 | `numeric_like:72, file_like:5` |
| valid | 818 | 1520 | 306 | 800 | 494 | 66 | 804 | `non_turkish_latin_word:64, numeric_like:2` |
| valid | 1944 | 3642 | 668 | 1007 | 339 | 43 | 469 | `non_turkish_latin_word:32, numeric_like:7, apostrophe_surface:2, file_like:2` |
| valid | 815 | 1029 | 239 | 508 | 269 | 41 | 460 | `non_turkish_latin_word:41` |
| valid | 535 | 2632 | 599 | 862 | 263 | 37 | 292 | `numeric_like:30, apostrophe_surface:6, file_like:1` |
| valid | 1920 | 3848 | 795 | 1055 | 260 | 59 | 332 | `numeric_like:52, file_like:7` |
| valid | 594 | 2320 | 454 | 692 | 238 | 44 | 324 | `non_turkish_latin_word:37, numeric_like:6, file_like:1` |
| valid | 1782 | 3223 | 862 | 1085 | 223 | 79 | 340 | `numeric_like:69, file_like:7, apostrophe_surface:3` |
| valid | 457 | 1590 | 375 | 585 | 210 | 43 | 397 | `non_turkish_latin_word:43` |
| valid | 1953 | 1922 | 315 | 496 | 181 | 25 | 278 | `non_turkish_latin_word:19, file_like:4, numeric_like:2` |
| valid | 475 | 1848 | 397 | 577 | 180 | 47 | 321 | `non_turkish_latin_word:32, numeric_like:13, apostrophe_surface:2` |
| test | 865 | 1592 | 354 | 764 | 410 | 65 | 706 | `non_turkish_latin_word:60, numeric_like:5` |
| test | 1029 | 1510 | 319 | 580 | 261 | 43 | 452 | `non_turkish_latin_word:42, numeric_like:1` |
| test | 1362 | 3198 | 668 | 908 | 240 | 51 | 299 | `numeric_like:44, file_like:5, greek_word:1, apostrophe_surface:1` |
| test | 1798 | 3230 | 688 | 919 | 231 | 30 | 309 | `numeric_like:18, file_like:12` |
| test | 28 | 4041 | 600 | 830 | 230 | 24 | 236 | `non_turkish_latin_word:18, numeric_like:4, apostrophe_surface:1, file_like:1` |
| test | 628 | 1663 | 334 | 563 | 229 | 42 | 401 | `non_turkish_latin_word:39, numeric_like:3` |
| test | 1799 | 4092 | 820 | 1028 | 208 | 26 | 248 | `numeric_like:15, file_like:11` |
| test | 1927 | 3905 | 728 | 933 | 205 | 38 | 259 | `numeric_like:28, file_like:8, non_turkish_latin_word:1, apostrophe_surface:1` |
| test | 1900 | 1146 | 253 | 456 | 203 | 28 | 379 | `non_turkish_latin_word:28` |
| test | 1859 | 2769 | 499 | 702 | 203 | 47 | 306 | `numeric_like:40, file_like:5, apostrophe_surface:2` |

## Protected Route Cost

| Route | Count | Bytes | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `numeric_like` | 81022 | 279160 | 260245 | 122438 | 137807 | 0.932243 | 0.438594 |
| `non_turkish_latin_word` | 18984 | 162953 | 133982 | 39321 | 94661 | 0.822213 | 0.241303 |
| `file_like` | 12256 | 218498 | 165506 | 44926 | 120580 | 0.757471 | 0.205613 |
| `apostrophe_surface` | 6833 | 80798 | 74811 | 23608 | 51203 | 0.925902 | 0.292185 |
| `greek_word` | 580 | 1292 | 839 | 793 | 46 | 0.649381 | 0.613777 |
| `arabic_word` | 106 | 1236 | 801 | 614 | 187 | 0.648058 | 0.496764 |
| `cyrillic_word` | 24 | 338 | 338 | 190 | 148 | 1.000000 | 0.562130 |
| `uzbek_apostrophe_word` | 24 | 184 | 171 | 81 | 90 | 0.929348 | 0.440217 |
| `azerbaijani_word` | 8 | 98 | 94 | 37 | 57 | 0.959184 | 0.377551 |

## Interpretation Gate

If protected bytes are a small share of the corpus but relative token
delta is large, the wrapper needs redesign before MorphBPE work.
If cost is concentrated in a few route kinds, optimize those routes
first.
