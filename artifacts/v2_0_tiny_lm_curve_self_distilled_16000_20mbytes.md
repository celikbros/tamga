# Tiny LM Bits-Per-Byte Probe

Config: `configs/v2_0_tiny_lm_matched_control.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Dry run: `False`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 6231 |
| eval_interval | 500 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| finite_protected_self_distilled_16000 | ok | 64630 | train | 16000 | 22819852 | 3639947 | 0.159508 | 1597 | 0.000439 |  |
| finite_protected_self_distilled_16000 | ok | 64630 | valid | 1994 | 2843294 | 466135 | 0.163942 | 208 | 0.000446 |  |
| finite_protected_self_distilled_16000 | ok | 64630 | test | 1998 | 2781995 | 458618 | 0.164852 | 357 | 0.000778 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| finite_protected_self_distilled_16000 | ok | 64630 | 19737600 | 16578048 | 3159552 | 6231 | 3190272 | 20000713 | 1.951182 | 1.951182 | 1.963184 |  |

## Loss Accounting

This table reports the same eval pass used for BPB, converted back
to bits/token. Values above `log2(vocab)` indicate an early or
pathological optimization regime and should not be read as
converged LM quality.

| Tokenizer | log2(vocab) | Valid bits/token | Test bits/token | Valid target tokens | Test target tokens | Valid evaluated bytes | Test evaluated bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finite_protected_self_distilled_16000 | 15.9799 | 11.9017 | 11.9088 | 466048 | 458496 | 2842769 | 2781261 |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
