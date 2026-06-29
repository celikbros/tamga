# v3.2 Binary Dataloader Simulation

Manifest: `C:/CELIK-GARDASH/datasets/tokenizer_v3_7_smoke/sp64k_stratified_50k/manifest.json`
Config: `configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json`
Batch shape: `batch_size=4`, `seq_len=128`
Status: `PASS`

This tokenizer-side simulation checks whether the binary fixture can be
turned into causal-LM input ids, shifted labels, and target-position loss
masks without relying on the future LLM engine.

## Summary

| Metric | Value |
| --- | ---: |
| tokens | 9060436 |
| mask_bytes | 9060436 |
| seq_len | 128 |
| batch_size | 4 |
| windows | 70784 |
| full_batches | 17696 |
| used_windows | 70784 |
| train_label_positions | 8485153 |
| masked_label_positions | 575199 |
| tail_tokens | 84 |
| tail_padded_tokens | 45 |
| tail_train_labels | 77 |
| sp_tokens | 9055084 |
| byte_fallback_tokens | 5352 |
| control_tokens_in_fixture | 0 |
| max_token_id | 64243 |
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
