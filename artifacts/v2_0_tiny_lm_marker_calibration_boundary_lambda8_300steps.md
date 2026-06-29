# Tiny LM Bits-Per-Byte Probe

Config: `configs/v2_0_tiny_lm_marker_calibration.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Dry run: `False`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 300 |
| eval_interval | 100 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| boundary_biased_lambda8_numeric_sp | ok | 64630 | train | 16000 | 22819852 | 3984444 | 0.174604 | 1597 | 0.000401 |  |
| boundary_biased_lambda8_numeric_sp | ok | 64630 | valid | 1994 | 2843294 | 508167 | 0.178725 | 200 | 0.000394 |  |
| boundary_biased_lambda8_numeric_sp | ok | 64630 | test | 1998 | 2781995 | 498808 | 0.179299 | 249 | 0.000499 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| boundary_biased_lambda8_numeric_sp | ok | 64630 | 19737600 | 16578048 | 3159552 | 300 | 153600 | 879703 | 4.816592 | 4.816592 | 4.850946 |  |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
