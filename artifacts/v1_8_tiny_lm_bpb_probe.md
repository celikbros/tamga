# v1.8 Tiny LM Bits-Per-Byte Probe

Config: `configs/v1_8_tiny_lm_bpb_probe.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Dry run: `False`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 500 |
| eval_interval | 100 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp_bpe_64000_train_only | ok | 64000 | train | 16000 | 22819852 | 3500397 | 0.153393 | 0 | 0.000000 |  |
| sp_bpe_64000_train_only | ok | 64000 | valid | 1994 | 2843294 | 445176 | 0.156571 | 0 | 0.000000 |  |
| sp_bpe_64000_train_only | ok | 64000 | test | 1998 | 2781995 | 436852 | 0.157028 | 0 | 0.000000 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp_bpe_64000_train_only | ok | 64000 | 19576320 | 16416768 | 3159552 | 500 | 256000 | 1668920 | 3.729064 | 3.729064 | 3.745292 |  |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the v1.8 protocol caveats.
