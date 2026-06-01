# v1.8 Tokenizer Roundtrip Report

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SentencePiece config: `configs/v1_8_train_only_sentencepiece_sweep.toml`

This report checks whether each tokenizer can exactly reconstruct each
input line after encode/decode. It does not include private corpus text.

## Summary

| Tokenizer | Split | Status | Lines | Failures | Failure rate | Avg tokens/line | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | train | ok | 16000 | 0 | 0.000000 | 398.5108 |  |
| custom_tr_morph | valid | ok | 1994 | 0 | 0.000000 | 398.3942 |  |
| custom_tr_morph | test | ok | 1998 | 0 | 0.000000 | 388.0410 |  |
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

No roundtrip failures found.
