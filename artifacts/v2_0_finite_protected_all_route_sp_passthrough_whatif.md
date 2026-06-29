# v2.0 Finite Protected Wrapper Cost Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Numeric protected SP passthrough: `False`
SP passthrough routes: `apostrophe_surface, arabic_word, cyrillic_word, file_like, greek_word, non_turkish_latin_word, numeric_like, uzbek_apostrophe_word`
Private top-delta examples: `artifacts/private/v2_0_finite_protected_all_route_sp_passthrough_top_delta.jsonl`

This audit decomposes the token-pressure cost of the finite protected
wrapper before any new MorphBPE/constrained-tokenizer work.

## Split Summary

| Split | Lines | Raw bytes | SP tokens/raw byte | Finite tokens/raw byte | Delta tokens/raw byte | Relative delta | Protected bytes share | Protected tokens/protected byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | 1994 | 2843294 | 0.159020 | 0.168202 | 0.009182 | 0.057741 | 0.016455 | 0.376109 |
| test | 1998 | 2781995 | 0.159620 | 0.168813 | 0.009193 | 0.057593 | 0.016956 | 0.373980 |

## Finite Token Components

| Split | Segment SP tokens | Protected piece tokens | Protected SP passthrough tokens | Protected byte tokens | Hard suffix tokens | Apostrophe tokens | EOS tokens | Segment count | Protected pieces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | 447176 | 0 | 17577 | 20 | 6389 | 5093 | 1994 | 354615 | 9545 |
| test | 439088 | 0 | 17605 | 36 | 6122 | 4789 | 1998 | 346922 | 9234 |

## Highest Public Delta Lines

Raw text is omitted from this public report. Full private examples are
written to the JSONL path above.

| Split | Line | Raw bytes | SP tokens | Finite tokens | Delta | Protected pieces | Protected bytes | Routes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| valid | 1920 | 3848 | 795 | 907 | 112 | 56 | 249 | `numeric_like:52, file_like:4` |
| valid | 1335 | 2296 | 420 | 520 | 100 | 31 | 85 | `numeric_like:30, apostrophe_surface:1` |
| valid | 1782 | 3223 | 862 | 946 | 84 | 76 | 275 | `numeric_like:69, file_like:4, apostrophe_surface:3` |
| valid | 1598 | 2080 | 407 | 488 | 81 | 23 | 132 | `numeric_like:22, greek_word:1` |
| valid | 535 | 2632 | 599 | 677 | 78 | 36 | 276 | `numeric_like:30, apostrophe_surface:5, file_like:1` |
| valid | 1345 | 2007 | 416 | 488 | 72 | 30 | 86 | `numeric_like:29, file_like:1` |
| valid | 795 | 2125 | 404 | 473 | 69 | 35 | 104 | `numeric_like:35` |
| valid | 793 | 2086 | 339 | 404 | 65 | 23 | 57 | `numeric_like:23` |
| valid | 1909 | 3516 | 636 | 699 | 63 | 25 | 69 | `numeric_like:19, greek_word:6` |
| valid | 1279 | 1818 | 295 | 358 | 63 | 12 | 53 | `numeric_like:11, file_like:1` |
| test | 1929 | 4180 | 867 | 981 | 114 | 26 | 89 | `numeric_like:22, file_like:2, apostrophe_surface:1, non_turkish_latin_word:1` |
| test | 731 | 2095 | 368 | 474 | 106 | 35 | 81 | `numeric_like:35` |
| test | 1362 | 3198 | 668 | 772 | 104 | 48 | 239 | `numeric_like:44, file_like:2, greek_word:1, apostrophe_surface:1` |
| test | 795 | 3386 | 656 | 756 | 100 | 46 | 124 | `numeric_like:46` |
| test | 1399 | 2150 | 416 | 513 | 97 | 33 | 96 | `numeric_like:33` |
| test | 1907 | 2107 | 433 | 515 | 82 | 45 | 104 | `numeric_like:39, file_like:6` |
| test | 1932 | 1641 | 354 | 427 | 73 | 46 | 191 | `numeric_like:46` |
| test | 674 | 2922 | 589 | 659 | 70 | 53 | 201 | `numeric_like:44, file_like:9` |
| test | 1796 | 4073 | 803 | 871 | 68 | 23 | 186 | `numeric_like:15, file_like:7, apostrophe_surface:1` |
| test | 1876 | 1602 | 297 | 363 | 66 | 15 | 25 | `numeric_like:14, apostrophe_surface:1` |

## Protected Route Cost

| Route | Count | Bytes | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `numeric_like` | 15933 | 54992 | 24251 | 24251 | 0 | 0.440991 | 0.440991 |
| `file_like` | 1636 | 26792 | 6462 | 6462 | 0 | 0.241191 | 0.241191 |
| `apostrophe_surface` | 698 | 7402 | 2819 | 2819 | 0 | 0.380843 | 0.380843 |
| `non_turkish_latin_word` | 381 | 4191 | 1375 | 1362 | 13 | 0.328084 | 0.324982 |
| `greek_word` | 101 | 214 | 130 | 129 | 1 | 0.607477 | 0.602804 |
| `uzbek_apostrophe_word` | 13 | 127 | 47 | 47 | 0 | 0.370079 | 0.370079 |
| `cyrillic_word` | 11 | 152 | 107 | 87 | 20 | 0.703947 | 0.572368 |
| `arabic_word` | 6 | 88 | 47 | 47 | 0 | 0.534091 | 0.534091 |

## Interpretation Gate

If protected bytes are a small share of the corpus but relative token
delta is large, the wrapper needs redesign before MorphBPE work.
If cost is concentrated in a few route kinds, optimize those routes
first.
