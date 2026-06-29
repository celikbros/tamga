# Tiny LM Bits-Per-Byte Probe

Config: `configs/v3_1_sidecar_sp64k_retrained.toml`
Split dir: `artifacts/private/v3_1_vocab_ablation_split`
Dry run: `True`

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
| sp64k_retrained_protected_passthrough_sidecar | ok | 64256 | train | 32311 | 35511533 | 5712170 | 0.160854 | 0 | 0.000000 |  |
| sp64k_retrained_protected_passthrough_sidecar | ok | 64256 | valid | 4039 | 4404796 | 721359 | 0.163767 | 123 | 0.000171 |  |
| sp64k_retrained_protected_passthrough_sidecar | ok | 64256 | test | 4038 | 4435472 | 722436 | 0.162877 | 213 | 0.000295 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| dry_run | skipped | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  | no training run |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
