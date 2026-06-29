# v3.2 Binary Dataloader Simulation

Manifest: `artifacts/private/v3_8_tokenize_corpus_smoke_w2/manifest.json`
Config: `configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json`
Batch shape: `batch_size=4`, `seq_len=128`
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
| batch_size | 4 |
| windows | 16 |
| full_batches | 4 |
| used_windows | 16 |
| train_label_positions | 1952 |
| masked_label_positions | 96 |
| tail_tokens | 40 |
| tail_padded_tokens | 89 |
| tail_train_labels | 35 |
| sp_tokens | 2088 |
| byte_fallback_tokens | 0 |
| control_tokens_in_fixture | 0 |
| max_token_id | 59180 |
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
