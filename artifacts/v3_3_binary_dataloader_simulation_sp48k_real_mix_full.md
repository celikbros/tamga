# v3.2 Binary Dataloader Simulation

Manifest: `C:/CELIK-GARDASH/datasets/tokenizer_v3_3_smoke/sp48k_real_mix_full/manifest.json`
Config: `C:/CELIK-GARDASH/configs/tokenizer_v3_0/tokenizer_config.v3_2.sp48k_integration_smoke.json`
Batch shape: `batch_size=4`, `seq_len=128`
Status: `PASS`

This tokenizer-side simulation checks whether the binary fixture can be
turned into causal-LM input ids, shifted labels, and target-position loss
masks without relying on the future LLM engine.

## Summary

| Metric | Value |
| --- | ---: |
| tokens | 7350435 |
| mask_bytes | 7350435 |
| seq_len | 128 |
| batch_size | 4 |
| windows | 57425 |
| full_batches | 14356 |
| used_windows | 57424 |
| train_label_positions | 7071403 |
| masked_label_positions | 278869 |
| tail_tokens | 163 |
| tail_padded_tokens | 0 |
| tail_train_labels | 124 |
| sp_tokens | 7350099 |
| byte_fallback_tokens | 336 |
| control_tokens_in_fixture | 0 |
| max_token_id | 48244 |
| effective_vocab_size | 48384 |
| pad_id | 48256 |
| bos_id | 1 |
| eos_id | 2 |
| control_sequence_len | 5 |

## Failures

None.

## Warnings

None.

## Interpretation

The binary token stream is internally consistent for packed causal-LM batching and target-position masking.
