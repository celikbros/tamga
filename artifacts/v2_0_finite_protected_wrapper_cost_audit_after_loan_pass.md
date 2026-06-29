# v2.0 Finite Protected Wrapper Cost Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Private top-delta examples: `artifacts/private/v2_0_finite_protected_wrapper_cost_top_delta_after_loan_pass.jsonl`

This audit decomposes the token-pressure cost of the finite protected
wrapper before any new MorphBPE/constrained-tokenizer work.

## Split Summary

| Split | Lines | Raw bytes | SP tokens/raw byte | Finite tokens/raw byte | Delta tokens/raw byte | Relative delta | Protected bytes share | Protected tokens/protected byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 0.154680 | 0.175683 | 0.021003 | 0.135780 | 0.021273 | 0.862228 |
| valid | 1994 | 2843294 | 0.159020 | 0.179405 | 0.020384 | 0.128188 | 0.021292 | 0.865508 |
| test | 1998 | 2781995 | 0.159620 | 0.180564 | 0.020944 | 0.131211 | 0.021851 | 0.874944 |

## Finite Token Components

| Split | Segment SP tokens | Protected piece tokens | Protected byte tokens | Hard suffix tokens | Apostrophe tokens | EOS tokens | Segment count | Protected pieces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 3494057 | 416972 | 1601 | 44816 | 35610 | 16000 | 2840772 | 82880 |
| valid | 445205 | 52197 | 200 | 5813 | 4692 | 1994 | 352943 | 10354 |
| test | 437179 | 52938 | 249 | 5559 | 4406 | 1998 | 345263 | 10032 |

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
| train | 14390 | 4045 | 1073 | 1371 | 298 | 77 | 377 | `numeric_like:72, file_like:5` |
| train | 6654 | 1122 | 236 | 519 | 283 | 42 | 469 | `non_turkish_latin_word:38, numeric_like:3, file_like:1` |
| train | 14309 | 3804 | 841 | 1119 | 278 | 92 | 528 | `numeric_like:84, file_like:8` |
| valid | 818 | 1520 | 306 | 800 | 494 | 66 | 804 | `non_turkish_latin_word:64, numeric_like:2` |
| valid | 815 | 1029 | 239 | 508 | 269 | 41 | 460 | `non_turkish_latin_word:41` |
| valid | 535 | 2632 | 599 | 862 | 263 | 37 | 292 | `numeric_like:30, apostrophe_surface:6, file_like:1` |
| valid | 1920 | 3848 | 795 | 1055 | 260 | 59 | 332 | `numeric_like:52, file_like:7` |
| valid | 1782 | 3223 | 862 | 1085 | 223 | 79 | 340 | `numeric_like:69, file_like:7, apostrophe_surface:3` |
| valid | 639 | 2474 | 481 | 656 | 175 | 28 | 236 | `numeric_like:23, file_like:5` |
| valid | 1242 | 2201 | 302 | 475 | 173 | 11 | 243 | `apostrophe_surface:6, file_like:5` |
| valid | 1510 | 1774 | 328 | 495 | 167 | 29 | 275 | `non_turkish_latin_word:19, numeric_like:10` |
| valid | 1787 | 3611 | 740 | 904 | 164 | 16 | 207 | `numeric_like:6, file_like:6, apostrophe_surface:4` |
| valid | 1789 | 3991 | 882 | 1044 | 162 | 34 | 211 | `numeric_like:28, file_like:5, apostrophe_surface:1` |
| test | 865 | 1592 | 354 | 760 | 406 | 64 | 700 | `non_turkish_latin_word:59, numeric_like:5` |
| test | 1362 | 3198 | 668 | 908 | 240 | 51 | 299 | `numeric_like:44, file_like:5, greek_word:1, apostrophe_surface:1` |
| test | 1798 | 3230 | 688 | 919 | 231 | 30 | 309 | `numeric_like:18, file_like:12` |
| test | 1799 | 4092 | 820 | 1028 | 208 | 26 | 248 | `numeric_like:15, file_like:11` |
| test | 1900 | 1146 | 253 | 456 | 203 | 28 | 379 | `non_turkish_latin_word:28` |
| test | 1859 | 2769 | 499 | 702 | 203 | 47 | 306 | `numeric_like:40, file_like:5, apostrophe_surface:2` |
| test | 1796 | 4073 | 803 | 1000 | 197 | 26 | 235 | `numeric_like:15, file_like:10, apostrophe_surface:1` |
| test | 1927 | 3905 | 728 | 922 | 194 | 37 | 246 | `numeric_like:28, file_like:8, apostrophe_surface:1` |
| test | 1932 | 1641 | 354 | 543 | 189 | 46 | 191 | `numeric_like:46` |
| test | 1929 | 4180 | 867 | 1055 | 188 | 29 | 153 | `numeric_like:22, file_like:5, apostrophe_surface:1, non_turkish_latin_word:1` |

## Protected Route Cost

| Route | Count | Bytes | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `numeric_like` | 81021 | 279179 | 260261 | 122442 | 137819 | 0.932237 | 0.438579 |
| `file_like` | 12264 | 218882 | 165789 | 44989 | 120800 | 0.757436 | 0.205540 |
| `apostrophe_surface` | 7587 | 87943 | 80768 | 26713 | 54055 | 0.918413 | 0.303754 |
| `non_turkish_latin_word` | 1644 | 17522 | 15014 | 5209 | 9805 | 0.856866 | 0.297283 |
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
