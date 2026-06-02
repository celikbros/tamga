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
| max_steps | 1258 |
| eval_interval | 100 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph_lossless | ok | 64000 | train | 16000 | 22819852 | 8799765 | 0.385619 | 181264 | 0.020599 |  |
| custom_tr_morph_lossless | ok | 64000 | valid | 1994 | 2843294 | 1183395 | 0.416206 | 30852 | 0.026071 |  |
| custom_tr_morph_lossless | ok | 64000 | test | 1998 | 2781995 | 1166895 | 0.419445 | 30665 | 0.026279 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph_lossless | ok | 64000 | 19576320 | 16416768 | 3159552 | 1258 | 644096 | 1670292 | 2.943302 | 2.943302 | 2.961183 |  |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the v1.8 protocol caveats.
