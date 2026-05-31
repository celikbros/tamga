# v1.7 Downstream Probe Prep Report

Config: `configs/v1_7_downstream_probe_celik_gold_pilot.toml`
Corpus: `data/train/claim_grade/celik_gold_filtered_pilot.txt`
Seed: `20260531`
Split parts: `8:1:1`
Tokenized output dir: `artifacts/private/v1_7_downstream_probe/celik_gold_filtered_pilot_20k`
Tokenized outputs written: `True`

This report prepares tokenizer inputs for a later LM probe. It does not
train a model and does not report bits-per-byte yet.

Public reports must not include raw corpus text or tokenized private lines.

## Split Summary

| Split | Lines | Bytes | Chars | Words |
| --- | ---: | ---: | ---: | ---: |
| train | 16000 | 21.68 MiB | 20763268 | 2592338 |
| valid | 2000 | 2.73 MiB | 2609199 | 325698 |
| test | 2000 | 2.71 MiB | 2599154 | 324637 |

## Tokenizer Prep Summary

| Tokenizer | Split | Status | Lines | Bytes | Words | Tokens | Avg tokens/line | Avg tokens/word | Tokens/byte | Bytes/token | Max tokens/line | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | train | ok | 16000 | 21.68 MiB | 2592338 | 3865181 | 241.5738 | 1.4910 | 0.170001 | 5.8823 | 978 |  |
| custom_tr_morph | valid | ok | 2000 | 2.73 MiB | 325698 | 486006 | 243.0030 | 1.4922 | 0.170041 | 5.8809 | 783 |  |
| custom_tr_morph | test | ok | 2000 | 2.71 MiB | 324637 | 484847 | 242.4235 | 1.4935 | 0.170326 | 5.8711 | 752 |  |
| unicode_char | train | ok | 16000 | 21.68 MiB | 2592338 | 18279139 | 1142.4462 | 7.0512 | 0.803964 | 1.2438 | 3552 |  |
| unicode_char | valid | ok | 2000 | 2.73 MiB | 325698 | 2297365 | 1148.6825 | 7.0537 | 0.803788 | 1.2441 | 3530 |  |
| unicode_char | test | ok | 2000 | 2.71 MiB | 324637 | 2288387 | 1144.1935 | 7.0491 | 0.803907 | 1.2439 | 3461 |  |
| sp_bpe_8000_celik_gold_pilot | train | ok | 16000 | 21.68 MiB | 2592338 | 5014380 | 313.3988 | 1.9343 | 0.220545 | 4.5342 | 1541 |  |
| sp_bpe_8000_celik_gold_pilot | valid | ok | 2000 | 2.73 MiB | 325698 | 629955 | 314.9775 | 1.9342 | 0.220405 | 4.5371 | 1454 |  |
| sp_bpe_8000_celik_gold_pilot | test | ok | 2000 | 2.71 MiB | 324637 | 626297 | 313.1485 | 1.9292 | 0.220017 | 4.5451 | 1275 |  |
| sp_unigram_8000_celik_gold_pilot | train | ok | 16000 | 21.68 MiB | 2592338 | 4889671 | 305.6044 | 1.8862 | 0.215060 | 4.6499 | 1556 |  |
| sp_unigram_8000_celik_gold_pilot | valid | ok | 2000 | 2.73 MiB | 325698 | 614791 | 307.3955 | 1.8876 | 0.215099 | 4.6490 | 1415 |  |
| sp_unigram_8000_celik_gold_pilot | test | ok | 2000 | 2.71 MiB | 324637 | 611081 | 305.5405 | 1.8824 | 0.214672 | 4.6583 | 1297 |  |

## Handoff Notes

- Use the same raw split for every tokenizer run.
- Compare LM runs with byte-normalized validation/test loss.
- Token-level perplexity is not comparable across tokenizers by itself.
- The JSONL token files are private artifacts because tokens can reconstruct private corpus text.
- This prep step should be repeated after the final claim-grade corpus policy is fixed.
