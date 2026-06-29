# Tiny LM Bits-Per-Byte Probe

Config: `configs/v3_1_sidecar_sp48k.toml`
Split dir: `artifacts/private/v3_1_vocab_ablation_split`
Dry run: `False`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 646 |
| eval_interval | 100 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp48k_protected_passthrough_sidecar | ok | 48256 | train | 32311 | 35511533 | 5872835 | 0.165378 | 0 | 0.000000 |  |
| sp48k_protected_passthrough_sidecar | ok | 48256 | valid | 4039 | 4404796 | 738870 | 0.167742 | 123 | 0.000166 |  |
| sp48k_protected_passthrough_sidecar | ok | 48256 | test | 4038 | 4435472 | 739408 | 0.166703 | 213 | 0.000288 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp48k_protected_passthrough_sidecar | ok | 48256 | 15545856 | 12386304 | 3159552 | 646 | 330752 | 1999973 | 3.297038 | 3.297038 | 3.276116 |  |

## Loss Accounting

This table reports the same eval pass used for BPB, converted back
to bits/token. Values above `log2(vocab)` indicate an early or
pathological optimization regime and should not be read as
converged LM quality.

| Tokenizer | log2(vocab) | Valid bits/token | Test bits/token | Valid target tokens | Test target tokens | Valid evaluated bytes | Test evaluated bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp48k_protected_passthrough_sidecar | 15.5584 | 19.6554 | 19.6524 | 738816 | 739328 | 4404480 | 4434998 |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
