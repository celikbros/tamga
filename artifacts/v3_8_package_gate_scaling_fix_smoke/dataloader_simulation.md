# v3.2 Binary Dataloader Simulation

Manifest: `artifacts/private/v3_8_tokenize_corpus_smoke_w2/manifest.json`
Config: `C:/CELIK-GARDASH/configs/tokenizer_v3_0/tokenizer_config.json`
Batch shape: `batch_size=1`, `seq_len=128`
Batch limit: `2`
Status: `PASS`

This tokenizer-side simulation checks whether the binary fixture can be
turned into causal-LM input ids, shifted labels, and target-position loss
masks without relying on the future LLM engine.

## Summary

| Metric | Value |
| --- | ---: |
| tokens | 2088 |
| mask_bytes | 2088 |
| seq_len | 128 |
| batch_size | 1 |
| windows | 16 |
| full_batches | 16 |
| sampling_mode | evenly_spaced |
| max_batches | 2 |
| sampled_batches | 2 |
| sampled_windows | 2 |
| sampled_token_positions | 296 |
| train_label_positions | 245 |
| masked_label_positions | 11 |
| tail_tokens | 40 |
| tail_padded_tokens | 89 |
| tail_train_labels | 35 |
| sampled_sp_tokens | 296 |
| sampled_byte_fallback_tokens | 0 |
| sampled_control_tokens | 0 |
| sampled_max_token_id | 59180 |
| manifest_max_token_id | 59180 |
| effective_vocab_size | 64384 |
| pad_id | 64256 |
| bos_id | 1 |
| eos_id | 2 |
| control_sequence_len | 5 |

## Failures

None.

## Warnings

None.

## Interpretation

The binary token stream is internally consistent for packed causal-LM batching and target-position masking.
