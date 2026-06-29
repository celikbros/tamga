# v1.8 Tokenizer Roundtrip Report

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SentencePiece config: `configs/v1_8_train_only_sentencepiece_sweep.toml`

This report checks whether each tokenizer can exactly reconstruct each
input line after encode/decode. It does not include private corpus text.

## Summary

| Tokenizer | Split | Status | Lines | Failures | Failure rate | Avg tokens/line | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | train | ok | 16000 | 16000 | 1.000000 | 242.5737 |  |
| custom_tr_morph | valid | ok | 1994 | 1994 | 1.000000 | 242.6088 |  |
| custom_tr_morph | test | ok | 1998 | 1997 | 0.999499 | 236.3589 |  |
| sp_bpe_16000_train_only | train | ok | 16000 | 0 | 0.000000 | 265.3126 |  |
| sp_bpe_16000_train_only | valid | ok | 1994 | 0 | 0.000000 | 265.9413 |  |
| sp_bpe_16000_train_only | test | ok | 1998 | 0 | 0.000000 | 260.7788 |  |
| sp_unigram_16000_train_only | train | ok | 16000 | 0 | 0.000000 | 261.8523 |  |
| sp_unigram_16000_train_only | valid | ok | 1994 | 0 | 0.000000 | 263.3726 |  |
| sp_unigram_16000_train_only | test | ok | 1998 | 0 | 0.000000 | 258.2277 |  |
| sp_bpe_32000_train_only | train | ok | 16000 | 0 | 0.000000 | 237.5674 |  |
| sp_bpe_32000_train_only | valid | ok | 1994 | 0 | 0.000000 | 239.6540 |  |
| sp_bpe_32000_train_only | test | ok | 1998 | 0 | 0.000000 | 234.9014 |  |
| sp_unigram_32000_train_only | train | ok | 16000 | 0 | 0.000000 | 236.6234 |  |
| sp_unigram_32000_train_only | valid | ok | 1994 | 0 | 0.000000 | 240.4443 |  |
| sp_unigram_32000_train_only | test | ok | 1998 | 0 | 0.000000 | 235.5325 |  |
| sp_bpe_64000_train_only | train | ok | 16000 | 0 | 0.000000 | 217.7748 |  |
| sp_bpe_64000_train_only | valid | ok | 1994 | 0 | 0.000000 | 222.2578 |  |
| sp_bpe_64000_train_only | test | ok | 1998 | 0 | 0.000000 | 217.6446 |  |
| sp_unigram_64000_train_only | train | ok | 16000 | 0 | 0.000000 | 219.6113 |  |
| sp_unigram_64000_train_only | valid | ok | 1994 | 0 | 0.000000 | 225.7513 |  |
| sp_unigram_64000_train_only | test | ok | 1998 | 0 | 0.000000 | 221.2538 |  |

## Failure Details

Rows, source line indexes, hashes, and lengths are reported instead of
private text snippets.

### custom_tr_morph / train

| Row | Source line | Input hash | Input bytes | Decoded bytes | Tokens |
| ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 1 | 6a0e8b53dd10 | 746 | 745 | 121 |
| 2 | 2 | 69aaf0a73040 | 94 | 93 | 16 |
| 3 | 3 | 3fac51efcdc1 | 580 | 579 | 109 |
| 4 | 4 | 55fc0db47e6e | 104 | 103 | 13 |
| 5 | 6 | 5922f200efc4 | 126 | 125 | 24 |
| 6 | 8 | 57819bb09b71 | 2999 | 2998 | 434 |
| 7 | 9 | d353239708b3 | 3006 | 3023 | 505 |
| 8 | 10 | 1f4f6b5cd5be | 2564 | 2574 | 406 |
| 9 | 12 | b9bc17e5c89a | 4157 | 4153 | 657 |
| 10 | 13 | 0b93d286ca53 | 2981 | 2987 | 432 |

### custom_tr_morph / valid

| Row | Source line | Input hash | Input bytes | Decoded bytes | Tokens |
| ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 5 | ce285d1fdadf | 2639 | 2646 | 416 |
| 2 | 7 | d918c9a03281 | 1870 | 1871 | 271 |
| 3 | 11 | 12957fb7d407 | 2963 | 2966 | 448 |
| 4 | 15 | c9692ccbbdda | 3015 | 3013 | 440 |
| 5 | 34 | 6f64b56d9d1f | 3068 | 3069 | 507 |
| 6 | 59 | 4eb438ce9d35 | 3932 | 3942 | 638 |
| 7 | 61 | 0621123181a2 | 2811 | 2810 | 452 |
| 8 | 73 | 0c5c0a407591 | 3075 | 3061 | 500 |
| 9 | 95 | 805634c4d5b9 | 1121 | 1116 | 204 |
| 10 | 106 | 8f571f60af89 | 2438 | 2429 | 425 |

### custom_tr_morph / test

| Row | Source line | Input hash | Input bytes | Decoded bytes | Tokens |
| ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 26 | 957b0000a41b | 471 | 470 | 71 |
| 2 | 29 | 386007b0251a | 2268 | 2267 | 370 |
| 3 | 52 | c558154d9da2 | 2710 | 2719 | 496 |
| 4 | 77 | 90266a8220d6 | 1391 | 1390 | 230 |
| 5 | 82 | adcb9b3d0e69 | 3217 | 3198 | 533 |
| 6 | 90 | f85c9eafacd0 | 1895 | 1894 | 341 |
| 7 | 98 | de711f4b0ff1 | 1409 | 1408 | 233 |
| 8 | 103 | 4e8a54ef9f34 | 2995 | 2997 | 518 |
| 9 | 112 | 53a075d496a6 | 687 | 688 | 103 |
| 10 | 118 | 3109bd01799f | 3106 | 3109 | 470 |
