# Tiny LM Bits-Per-Byte Probe

Config: `configs/v3_5_sidecar_sp48k_stratified_480mb.toml`
Split dir: `artifacts/private/v3_4_stratified_480mb_ablation_split`
Dry run: `False`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 7464 |
| eval_interval | 1000 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp48k_stratified_480mb_protected_passthrough_sidecar | ok | 48256 | train | 398469 | 396217280 | 75707519 | 0.191076 | 6131 | 0.000081 |  |
| sp48k_stratified_480mb_protected_passthrough_sidecar | ok | 48256 | valid | 49809 | 49279753 | 9399388 | 0.190735 | 1418 | 0.000151 |  |
| sp48k_stratified_480mb_protected_passthrough_sidecar | ok | 48256 | test | 49808 | 50024285 | 9627399 | 0.192455 | 1922 | 0.000200 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp48k_stratified_480mb_protected_passthrough_sidecar | ok | 48256 | 15545856 | 12386304 | 3159552 | 7464 | 3821568 | 20000276 | 2.363120 | 2.363120 | 2.386732 |  |

## Loss Accounting

This table reports the same eval pass used for BPB, converted back
to bits/token. Values above `log2(vocab)` indicate an early or
pathological optimization regime and should not be read as
converged LM quality.

| Tokenizer | log2(vocab) | Valid bits/token | Test bits/token | Valid target tokens | Test target tokens | Valid evaluated bytes | Test evaluated bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp48k_stratified_480mb_protected_passthrough_sidecar | 15.5584 | 12.3895 | 12.4015 | 9399296 | 9627392 | 49279276 | 50024254 |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
