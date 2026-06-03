# Tiny LM Bits-Per-Byte Probe

Config: `configs/v2_0_tiny_lm_finite_protected_soft_marker_probe.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Dry run: `False`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 321 |
| eval_interval | 100 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| finite_protected_soft_marker | ok | 64630 | train | 16000 | 22819852 | 5663850 | 0.248198 | 1597 | 0.000282 |  |
| finite_protected_soft_marker | ok | 64630 | valid | 1994 | 2843294 | 715537 | 0.251658 | 194 | 0.000271 |  |
| finite_protected_soft_marker | ok | 64630 | test | 1998 | 2781995 | 701652 | 0.252212 | 249 | 0.000355 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| finite_protected_soft_marker | ok | 64630 | 19737600 | 16578048 | 3159552 | 321 | 164352 | 662180 | 5.224689 | 5.224689 | 5.263920 |  |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
