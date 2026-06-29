# v2.1 Presplit Sidecar Fallback Decomposition

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`

This report decomposes UTF-8 byte fallback in the pre-split sidecar
encoder. Fallback bytes equal fallback tokens because every fallback
token represents one source byte.

## Summary

| Split | Lines | Raw bytes | Tokens | Tokens/raw byte | Fallback bytes | Fallback token rate | Fallback byte coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | 1994 | 2843294 | 467892 | 0.164560 | 9931 | 0.021225 | 0.003493 |
| test | 1998 | 2781995 | 459131 | 0.165037 | 9824 | 0.021397 | 0.003531 |

## Reason Breakdown

| Split | Reason | Fallback bytes | Share of raw bytes |
| --- | --- | ---: | ---: |
| valid | `dummy_prefix_missing_piece` | 9903 | 0.003483 |
| valid | `dummy_prefix_rewritten_piece` | 0 | 0.000000 |
| valid | `sp_unk` | 28 | 0.000010 |
| test | `dummy_prefix_missing_piece` | 9680 | 0.003480 |
| test | `dummy_prefix_rewritten_piece` | 0 | 0.000000 |
| test | `sp_unk` | 144 | 0.000052 |