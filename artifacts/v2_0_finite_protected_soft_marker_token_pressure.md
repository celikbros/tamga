# v2.0 Finite Protected Soft-Marker Token Pressure

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Soft-marker model: `artifacts/private/v2_0_candidate_sentencepiece/protected_hard_soft_marker_raw_sp64_unigram_64000.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`

This report measures split-level token pressure for the finite protected
soft-marker prototype before any tiny-LM screening.

## Token Pressure

| Split | Lines | Bytes | Words | Logical tokens | Model tokens | Model tokens/byte | Logical tokens/byte | Model tokens/word | Protected piece tokens | Protected byte tokens | Protected byte-token rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 2603245 | 4301501 | 5608759 | 0.245784 | 0.188498 | 2.1545 | 507327 | 1597 | 0.003138 |
| valid | 1994 | 2843294 | 324001 | 544778 | 708383 | 0.249142 | 0.191601 | 2.1864 | 63317 | 194 | 0.003055 |
| test | 1998 | 2781995 | 316406 | 532983 | 694826 | 0.249758 | 0.191583 | 2.1960 | 64103 | 249 | 0.003869 |

## Baseline Anchors

```text
SP64 baseline valid/test: about 0.1566 / 0.1570 tokens/raw byte
raw-soft-marker candidate valid/test: about 0.2367 / 0.2367 tokens/raw byte
custom lossless+64k valid/test: about 0.4162 / 0.4194 tokens/raw byte
```

## Gate

The prototype should be closer to raw-soft-marker/SP64 than to pure
custom lossless pressure before tiny-LM screening.
