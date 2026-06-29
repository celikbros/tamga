# v2.0 Finite Protected Wrapper Cost Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Private top-delta examples: `artifacts/private/v2_0_finite_protected_wrapper_cost_top_delta_after_file_glue_pass.jsonl`

This audit decomposes the token-pressure cost of the finite protected
wrapper before any new MorphBPE/constrained-tokenizer work.

## Split Summary

| Split | Lines | Raw bytes | SP tokens/raw byte | Finite tokens/raw byte | Delta tokens/raw byte | Relative delta | Protected bytes share | Protected tokens/protected byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 0.154680 | 0.172871 | 0.018191 | 0.117603 | 0.016340 | 0.888044 |
| valid | 1994 | 2843294 | 0.159020 | 0.176643 | 0.017622 | 0.110817 | 0.016455 | 0.889029 |
| test | 1998 | 2781995 | 0.159620 | 0.177726 | 0.018105 | 0.113428 | 0.016956 | 0.899599 |

## Finite Token Components

| Split | Segment SP tokens | Protected piece tokens | Protected byte tokens | Hard suffix tokens | Apostrophe tokens | EOS tokens | Segment count | Protected pieces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 3509481 | 329531 | 1601 | 49525 | 38756 | 16000 | 2854463 | 76328 |
| valid | 447176 | 41395 | 200 | 6389 | 5093 | 1994 | 354615 | 9545 |
| test | 439088 | 42186 | 249 | 6122 | 4789 | 1998 | 346922 | 9234 |

## Highest Public Delta Lines

Raw text is omitted from this public report. Full private examples are
written to the JSONL path above.

| Split | Line | Raw bytes | SP tokens | Finite tokens | Delta | Protected pieces | Protected bytes | Routes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| train | 6653 | 2753 | 540 | 1343 | 803 | 114 | 1245 | `non_turkish_latin_word:102, numeric_like:10, file_like:2` |
| train | 6657 | 2050 | 392 | 1073 | 681 | 94 | 1019 | `non_turkish_latin_word:86, numeric_like:8` |
| train | 6673 | 1391 | 238 | 794 | 556 | 61 | 864 | `non_turkish_latin_word:61` |
| train | 6671 | 1507 | 262 | 760 | 498 | 62 | 732 | `non_turkish_latin_word:57, numeric_like:4, file_like:1` |
| train | 6656 | 1493 | 309 | 774 | 465 | 64 | 753 | `non_turkish_latin_word:59, numeric_like:5` |
| train | 6672 | 1414 | 251 | 597 | 346 | 48 | 519 | `non_turkish_latin_word:38, numeric_like:10` |
| train | 6658 | 1287 | 230 | 547 | 317 | 35 | 476 | `non_turkish_latin_word:34, numeric_like:1` |
| train | 14390 | 4045 | 1073 | 1371 | 298 | 77 | 377 | `numeric_like:72, file_like:5` |
| train | 6654 | 1122 | 236 | 519 | 283 | 42 | 469 | `non_turkish_latin_word:38, numeric_like:3, file_like:1` |
| train | 15398 | 4139 | 926 | 1172 | 246 | 72 | 252 | `numeric_like:62, greek_word:8, file_like:2` |
| valid | 818 | 1520 | 306 | 800 | 494 | 66 | 804 | `non_turkish_latin_word:64, numeric_like:2` |
| valid | 815 | 1029 | 239 | 508 | 269 | 41 | 460 | `non_turkish_latin_word:41` |
| valid | 535 | 2632 | 599 | 852 | 253 | 36 | 276 | `numeric_like:30, apostrophe_surface:5, file_like:1` |
| valid | 1920 | 3848 | 795 | 1009 | 214 | 56 | 249 | `numeric_like:52, file_like:4` |
| valid | 1782 | 3223 | 862 | 1047 | 185 | 76 | 275 | `numeric_like:69, file_like:4, apostrophe_surface:3` |
| valid | 1510 | 1774 | 328 | 495 | 167 | 29 | 275 | `non_turkish_latin_word:19, numeric_like:10` |
| valid | 1789 | 3991 | 882 | 1044 | 162 | 34 | 211 | `numeric_like:28, file_like:5, apostrophe_surface:1` |
| valid | 1290 | 2247 | 382 | 527 | 145 | 36 | 181 | `numeric_like:33, file_like:2, greek_word:1` |
| valid | 1787 | 3611 | 740 | 883 | 143 | 14 | 164 | `numeric_like:6, file_like:5, apostrophe_surface:3` |
| valid | 1335 | 2296 | 420 | 560 | 140 | 31 | 85 | `numeric_like:30, apostrophe_surface:1` |
| test | 865 | 1592 | 354 | 760 | 406 | 64 | 700 | `non_turkish_latin_word:59, numeric_like:5` |
| test | 1362 | 3198 | 668 | 879 | 211 | 48 | 239 | `numeric_like:44, file_like:2, greek_word:1, apostrophe_surface:1` |
| test | 1900 | 1146 | 253 | 456 | 203 | 28 | 379 | `non_turkish_latin_word:28` |
| test | 1799 | 4092 | 820 | 1020 | 200 | 25 | 234 | `numeric_like:15, file_like:10` |
| test | 1859 | 2769 | 499 | 694 | 195 | 46 | 292 | `numeric_like:40, file_like:5, apostrophe_surface:1` |
| test | 1932 | 1641 | 354 | 543 | 189 | 46 | 191 | `numeric_like:46` |
| test | 1796 | 4073 | 803 | 975 | 172 | 23 | 186 | `numeric_like:15, file_like:7, apostrophe_surface:1` |
| test | 545 | 3194 | 543 | 712 | 169 | 13 | 213 | `apostrophe_surface:5, file_like:4, numeric_like:3, non_turkish_latin_word:1` |
| test | 1534 | 1445 | 358 | 518 | 160 | 56 | 224 | `numeric_like:55, file_like:1` |
| test | 1360 | 3052 | 514 | 667 | 153 | 20 | 188 | `numeric_like:15, file_like:4, apostrophe_surface:1` |

## Protected Route Cost

| Route | Count | Bytes | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `numeric_like` | 81045 | 279296 | 260370 | 122485 | 137885 | 0.932237 | 0.438549 |
| `file_like` | 8006 | 128795 | 102538 | 30495 | 72043 | 0.796133 | 0.236772 |
| `apostrophe_surface` | 3662 | 37989 | 34938 | 14276 | 20662 | 0.919687 | 0.375793 |
| `non_turkish_latin_word` | 1644 | 17499 | 14991 | 5199 | 9792 | 0.856678 | 0.297103 |
| `greek_word` | 580 | 1292 | 839 | 793 | 46 | 0.649381 | 0.613777 |
| `arabic_word` | 106 | 1236 | 801 | 614 | 187 | 0.648058 | 0.496764 |
| `uzbek_apostrophe_word` | 32 | 293 | 253 | 108 | 145 | 0.863481 | 0.368601 |
| `cyrillic_word` | 24 | 338 | 338 | 190 | 148 | 1.000000 | 0.562130 |
| `azerbaijani_word` | 8 | 98 | 94 | 37 | 57 | 0.959184 | 0.377551 |

## Interpretation Gate

If protected bytes are a small share of the corpus but relative token
delta is large, the wrapper needs redesign before MorphBPE work.
If cost is concentrated in a few route kinds, optimize those routes
first.
