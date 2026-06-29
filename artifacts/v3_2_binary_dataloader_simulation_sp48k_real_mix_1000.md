# v3.2 Binary Dataloader Simulation

Manifest: `C:/CELIK-GARDASH/datasets/tokenizer_v3_2_smoke/sp48k_real_mix_1000/manifest.json`
Config: `C:/CELIK-GARDASH/configs/tokenizer_v3_0/tokenizer_config.v3_2.sp48k_integration_smoke.json`
Batch shape: `batch_size=4`, `seq_len=128`
Status: `PASS`

This tokenizer-side simulation checks whether the binary fixture can be
turned into causal-LM input ids, shifted labels, and target-position loss
masks without relying on the future LLM engine.

## Summary

| Metric | Value |
| --- | ---: |
| tokens | 352871 |
| mask_bytes | 352871 |
| seq_len | 128 |
| batch_size | 4 |
| windows | 2756 |
| full_batches | 689 |
| used_windows | 2756 |
| train_label_positions | 342387 |
| masked_label_positions | 10381 |
| tail_tokens | 103 |
| tail_padded_tokens | 26 |
| tail_train_labels | 96 |
| sp_tokens | 352869 |
| byte_fallback_tokens | 2 |
| control_tokens_in_fixture | 0 |
| max_token_id | 48195 |
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
