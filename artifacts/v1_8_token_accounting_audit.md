# v1.8 Token Accounting Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SentencePiece model: `artifacts/private/v1_8_train_only_sentencepiece/sp_bpe_64000_train_only.model`
Custom vocab cap: `64000`
Max lines per split: `all`

This audit explains tokenizer accounting differences before using the
tiny-LM BPB smoke as evidence. It deliberately compares multiple custom
encoding modes on the same raw split.

## Summary

| Mode | Split | Lines | Bytes | Tokens | Tokens/byte | Bytes/token | Vocab | Unique source tokens | Whitespace source tokens | Fallback source tokens | Fallback byte ids | Fallback source rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_standard_no_whitespace | train | 16000 | 22819852 | 3897827 | 0.170809 | 5.854506 |  | 219124 | 0 | 0 | 0 | 0.000000 |  |
| custom_lossless_open_vocab | train | 16000 | 22819852 | 6392173 | 0.280115 | 3.569968 |  | 218982 | 2494171 | 0 | 0 | 0.000000 |  |
| custom_lossless_64000_byte_fallback | train | 16000 | 22819852 | 8799765 | 0.385619 | 2.593234 | 64000 |  | 0 | 181264 | 2588856 | 0.020599 | same custom encoding mode used by tiny-LM BPB probe |
| sp_bpe_64000_train_only | train | 16000 | 22819852 | 3500397 | 0.153393 | 6.519218 | 64000 |  | 0 | 0 | 0 | 0.000000 | SentencePiece model: artifacts/private/v1_8_train_only_sentencepiece/sp_bpe_64000_train_only.model |
| custom_standard_no_whitespace | valid | 1994 | 2843294 | 485814 | 0.170863 | 5.852639 |  | 56194 | 0 | 0 | 0 | 0.000000 |  |
| custom_lossless_open_vocab | valid | 1994 | 2843294 | 796392 | 0.280095 | 3.570219 |  | 56176 | 310553 | 0 | 0 | 0.000000 |  |
| custom_lossless_64000_byte_fallback | valid | 1994 | 2843294 | 1183395 | 0.416206 | 2.402658 | 64000 |  | 0 | 30852 | 417855 | 0.026071 | same custom encoding mode used by tiny-LM BPB probe |
| sp_bpe_64000_train_only | valid | 1994 | 2843294 | 445176 | 0.156571 | 6.386899 | 64000 |  | 0 | 0 | 0 | 0.000000 | SentencePiece model: artifacts/private/v1_8_train_only_sentencepiece/sp_bpe_64000_train_only.model |
| custom_standard_no_whitespace | test | 1998 | 2781995 | 474340 | 0.170504 | 5.864981 |  | 55943 | 0 | 0 | 0 | 0.000000 |  |
| custom_lossless_open_vocab | test | 1998 | 2781995 | 777304 | 0.279405 | 3.579031 |  | 55926 | 302919 | 0 | 0 | 0.000000 |  |
| custom_lossless_64000_byte_fallback | test | 1998 | 2781995 | 1166895 | 0.419445 | 2.384101 | 64000 |  | 0 | 30665 | 420256 | 0.026279 | same custom encoding mode used by tiny-LM BPB probe |
| sp_bpe_64000_train_only | test | 1998 | 2781995 | 436852 | 0.157028 | 6.368278 | 64000 |  | 0 | 0 | 0 | 0.000000 | SentencePiece model: artifacts/private/v1_8_train_only_sentencepiece/sp_bpe_64000_train_only.model |

## How To Read This

- `custom_standard_no_whitespace` matches the older intrinsic/fertility-style custom view.
- `custom_lossless_open_vocab` adds whitespace-preserving serialization pressure.
- `custom_lossless_64000_byte_fallback` is the tiny-LM custom mode and is the row that should be compared to BPB runs.
- If the old custom tokens/byte is near SP but the lossless/fallback row is much larger, the apparent contradiction is an encoding-mode change, not a BPB discovery.
- BPB claims should use the lossless mode because generation needs `decode(encode(x)) == x`.
- If `--max-lines` is used for a smoke test, fallback rates may be exaggerated because the temporary custom vocabulary is built from a tiny train subset.

## Decision Rule

Do not treat the v1.8 iso-byte smoke as a strong morphology data-efficiency claim until this audit and an iso-compute/learning-curve control are recorded.
