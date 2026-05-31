# v1.7 Downstream Probe Prep Report

Config: `configs/v1_7_downstream_probe_demo.toml`
Corpus: `data/train/tr_bpe_train.txt`
Seed: `20260531`
Split parts: `8:1:1`
Tokenized output dir: `artifacts/private/v1_7_downstream_probe/demo`
Tokenized outputs written: `True`

This report prepares tokenizer inputs for a later LM probe. It does not
train a model and does not report bits-per-byte yet.

Public reports must not include raw corpus text or tokenized private lines.

## Split Summary

| Split | Lines | Bytes | Chars | Words |
| --- | ---: | ---: | ---: | ---: |
| train | 248 | 8.65 KiB | 8014 | 1058 |
| valid | 31 | 1.15 KiB | 1062 | 133 |
| test | 31 | 1.10 KiB | 1027 | 135 |

## Tokenizer Prep Summary

| Tokenizer | Split | Status | Lines | Bytes | Words | Tokens | Avg tokens/line | Avg tokens/word | Tokens/byte | Bytes/token | Max tokens/line | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | train | ok | 248 | 8.65 KiB | 1058 | 2049 | 8.2621 | 1.9367 | 0.231369 | 4.3221 | 15 |  |
| custom_tr_morph | valid | ok | 31 | 1.15 KiB | 133 | 265 | 8.5484 | 1.9925 | 0.225532 | 4.4340 | 15 |  |
| custom_tr_morph | test | ok | 31 | 1.10 KiB | 135 | 261 | 8.4194 | 1.9333 | 0.230973 | 4.3295 | 16 |  |
| unicode_char | train | ok | 248 | 8.65 KiB | 1058 | 7265 | 29.2944 | 6.8667 | 0.820348 | 1.2190 | 43 |  |
| unicode_char | valid | ok | 31 | 1.15 KiB | 133 | 969 | 31.2581 | 7.2857 | 0.824681 | 1.2126 | 46 |  |
| unicode_char | test | ok | 31 | 1.10 KiB | 135 | 930 | 30.0000 | 6.8889 | 0.823009 | 1.2151 | 44 |  |
| sp_bpe_1000_demo | train | ok | 248 | 8.65 KiB | 1058 | 2329 | 9.3911 | 2.2013 | 0.262986 | 3.8025 | 19 |  |
| sp_bpe_1000_demo | valid | ok | 31 | 1.15 KiB | 133 | 317 | 10.2258 | 2.3835 | 0.269787 | 3.7066 | 15 |  |
| sp_bpe_1000_demo | test | ok | 31 | 1.10 KiB | 135 | 284 | 9.1613 | 2.1037 | 0.251327 | 3.9789 | 13 |  |
| sp_unigram_1000_demo | train | ok | 248 | 8.65 KiB | 1058 | 2575 | 10.3831 | 2.4338 | 0.290763 | 3.4392 | 20 |  |
| sp_unigram_1000_demo | valid | ok | 31 | 1.15 KiB | 133 | 354 | 11.4194 | 2.6617 | 0.301277 | 3.3192 | 18 |  |
| sp_unigram_1000_demo | test | ok | 31 | 1.10 KiB | 135 | 327 | 10.5484 | 2.4222 | 0.289381 | 3.4557 | 16 |  |

## Handoff Notes

- Use the same raw split for every tokenizer run.
- Compare LM runs with byte-normalized validation/test loss.
- Token-level perplexity is not comparable across tokenizers by itself.
- The JSONL token files are private artifacts because tokens can reconstruct private corpus text.
- This prep step should be repeated after the final claim-grade corpus policy is fixed.
