# v1.7 Downstream Probe Prep Report

Config: `configs/v1_7_downstream_probe_celik_gold_clean_pilot.toml`
Corpus: `data/train/claim_grade/celik_gold_clean_pilot.txt`
Seed: `20260601`
Split parts: `8:1:1`
Tokenized output dir: `artifacts/private/v1_7_downstream_probe/celik_gold_clean_pilot_20k`
Tokenized outputs written: `True`

This report prepares tokenizer inputs for a later LM probe. It does not
train a model and does not report bits-per-byte yet.

Public reports must not include raw corpus text or tokenized private lines.

## Split Summary

| Split | Lines | Bytes | Chars | Words |
| --- | ---: | ---: | ---: | ---: |
| train | 16000 | 21.76 MiB | 20840097 | 2603245 |
| valid | 2000 | 2.72 MiB | 2600563 | 324562 |
| test | 2000 | 2.65 MiB | 2540544 | 316529 |

## Tokenizer Prep Summary

| Tokenizer | Split | Status | Lines | Bytes | Words | Tokens | Avg tokens/line | Avg tokens/word | Tokens/byte | Bytes/token | Max tokens/line | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | train | ok | 16000 | 21.76 MiB | 2603245 | 3881180 | 242.5737 | 1.4909 | 0.170079 | 5.8796 | 978 |  |
| custom_tr_morph | valid | ok | 2000 | 2.72 MiB | 324562 | 484606 | 242.3030 | 1.4931 | 0.170166 | 5.8766 | 754 |  |
| custom_tr_morph | test | ok | 2000 | 2.65 MiB | 316529 | 472433 | 236.2165 | 1.4925 | 0.169754 | 5.8909 | 823 |  |
| unicode_char | train | ok | 16000 | 21.76 MiB | 2603245 | 18345926 | 1146.6204 | 7.0473 | 0.803946 | 1.2439 | 3552 |  |
| unicode_char | valid | ok | 2000 | 2.72 MiB | 324562 | 2289471 | 1144.7355 | 7.0540 | 0.803931 | 1.2439 | 3253 |  |
| unicode_char | test | ok | 2000 | 2.65 MiB | 316529 | 2237503 | 1118.7515 | 7.0689 | 0.803977 | 1.2438 | 3513 |  |
| sp_bpe_8000_celik_gold_clean | train | ok | 16000 | 21.76 MiB | 2603245 | 5034317 | 314.6448 | 1.9339 | 0.220611 | 4.5329 | 1541 |  |
| sp_bpe_8000_celik_gold_clean | valid | ok | 2000 | 2.72 MiB | 324562 | 625508 | 312.7540 | 1.9272 | 0.219642 | 4.5529 | 1327 |  |
| sp_bpe_8000_celik_gold_clean | test | ok | 2000 | 2.65 MiB | 316529 | 614297 | 307.1485 | 1.9407 | 0.220729 | 4.5305 | 1442 |  |
| sp_unigram_8000_celik_gold_clean | train | ok | 16000 | 21.76 MiB | 2603245 | 4907142 | 306.6964 | 1.8850 | 0.215038 | 4.6503 | 1562 |  |
| sp_unigram_8000_celik_gold_clean | valid | ok | 2000 | 2.72 MiB | 324562 | 609895 | 304.9475 | 1.8791 | 0.214160 | 4.6694 | 1312 |  |
| sp_unigram_8000_celik_gold_clean | test | ok | 2000 | 2.65 MiB | 316529 | 598958 | 299.4790 | 1.8923 | 0.215217 | 4.6465 | 1378 |  |
| sp_bpe_16000_celik_gold_clean | train | ok | 16000 | 21.76 MiB | 2603245 | 4378546 | 273.6591 | 1.6820 | 0.191874 | 5.2117 | 1338 |  |
| sp_bpe_16000_celik_gold_clean | valid | ok | 2000 | 2.72 MiB | 324562 | 544450 | 272.2250 | 1.6775 | 0.191180 | 5.2307 | 1114 |  |
| sp_bpe_16000_celik_gold_clean | test | ok | 2000 | 2.65 MiB | 316529 | 534416 | 267.2080 | 1.6884 | 0.192026 | 5.2076 | 1194 |  |
| sp_unigram_16000_celik_gold_clean | train | ok | 16000 | 21.76 MiB | 2603245 | 4299596 | 268.7247 | 1.6516 | 0.188415 | 5.3074 | 1334 |  |
| sp_unigram_16000_celik_gold_clean | valid | ok | 2000 | 2.72 MiB | 324562 | 534355 | 267.1775 | 1.6464 | 0.187635 | 5.3295 | 1123 |  |
| sp_unigram_16000_celik_gold_clean | test | ok | 2000 | 2.65 MiB | 316529 | 524873 | 262.4365 | 1.6582 | 0.188597 | 5.3023 | 1178 |  |
| sp_bpe_32000_celik_gold_clean | train | ok | 16000 | 21.76 MiB | 2603245 | 3916504 | 244.7815 | 1.5045 | 0.171627 | 5.8266 | 1185 |  |
| sp_bpe_32000_celik_gold_clean | valid | ok | 2000 | 2.72 MiB | 324562 | 487311 | 243.6555 | 1.5014 | 0.171116 | 5.8440 | 988 |  |
| sp_bpe_32000_celik_gold_clean | test | ok | 2000 | 2.65 MiB | 316529 | 478245 | 239.1225 | 1.5109 | 0.171842 | 5.8193 | 1041 |  |
| sp_unigram_32000_celik_gold_clean | train | ok | 16000 | 21.76 MiB | 2603245 | 3871013 | 241.9383 | 1.4870 | 0.169634 | 5.8951 | 1206 |  |
| sp_unigram_32000_celik_gold_clean | valid | ok | 2000 | 2.72 MiB | 324562 | 481771 | 240.8855 | 1.4844 | 0.169170 | 5.9112 | 997 |  |
| sp_unigram_32000_celik_gold_clean | test | ok | 2000 | 2.65 MiB | 316529 | 472959 | 236.4795 | 1.4942 | 0.169943 | 5.8843 | 1039 |  |
| sp_bpe_64000_celik_gold_clean | train | ok | 16000 | 21.76 MiB | 2603245 | 3590921 | 224.4326 | 1.3794 | 0.157360 | 6.3549 | 1110 |  |
| sp_bpe_64000_celik_gold_clean | valid | ok | 2000 | 2.72 MiB | 324562 | 447102 | 223.5510 | 1.3776 | 0.156997 | 6.3696 | 896 |  |
| sp_bpe_64000_celik_gold_clean | test | ok | 2000 | 2.65 MiB | 316529 | 438623 | 219.3115 | 1.3857 | 0.157606 | 6.3450 | 936 |  |
| sp_unigram_64000_celik_gold_clean | train | ok | 16000 | 21.76 MiB | 2603245 | 3571529 | 223.2206 | 1.3720 | 0.156510 | 6.3894 | 1129 |  |
| sp_unigram_64000_celik_gold_clean | valid | ok | 2000 | 2.72 MiB | 324562 | 444744 | 222.3720 | 1.3703 | 0.156169 | 6.4033 | 898 |  |
| sp_unigram_64000_celik_gold_clean | test | ok | 2000 | 2.65 MiB | 316529 | 436004 | 218.0020 | 1.3775 | 0.156664 | 6.3831 | 927 |  |

## Handoff Notes

- Use the same raw split for every tokenizer run.
- Compare LM runs with byte-normalized validation/test loss.
- Token-level perplexity is not comparable across tokenizers by itself.
- The JSONL token files are private artifacts because tokens can reconstruct private corpus text.
- This prep step should be repeated after the final claim-grade corpus policy is fixed.
