# Tiny LM Bits-Per-Byte Probe

Config: `configs/v3_1_sidecar_sp64k_retrained.toml`
Split dir: `artifacts/private/v3_1_vocab_ablation_split`
Dry run: `False`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 628 |
| eval_interval | 100 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp64k_retrained_protected_passthrough_sidecar | ok | 64256 | train | 32311 | 35511533 | 5712170 | 0.160854 | 0 | 0.000000 |  |
| sp64k_retrained_protected_passthrough_sidecar | ok | 64256 | valid | 4039 | 4404796 | 721359 | 0.163767 | 123 | 0.000171 |  |
| sp64k_retrained_protected_passthrough_sidecar | ok | 64256 | test | 4038 | 4435472 | 722436 | 0.162877 | 213 | 0.000295 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp64k_retrained_protected_passthrough_sidecar | ok | 64256 | 19641856 | 16482304 | 3159552 | 628 | 321536 | 1998931 | 3.342602 | 3.342602 | 3.321394 |  |

## Loss Accounting

This table reports the same eval pass used for BPB, converted back
to bits/token. Values above `log2(vocab)` indicate an early or
pathological optimization regime and should not be read as
converged LM quality.

| Tokenizer | log2(vocab) | Valid bits/token | Test bits/token | Valid target tokens | Test target tokens | Valid evaluated bytes | Test evaluated bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp64k_retrained_protected_passthrough_sidecar | 15.9715 | 20.4108 | 20.3921 | 721280 | 722432 | 4404320 | 4435454 |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
