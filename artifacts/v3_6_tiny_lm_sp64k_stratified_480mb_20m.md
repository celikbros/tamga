# Tiny LM Bits-Per-Byte Probe

Config: `configs/v3_5_sidecar_sp64k_stratified_480mb.toml`
Split dir: `artifacts/private/v3_4_stratified_480mb_ablation_split`
Dry run: `False`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 7200 |
| eval_interval | 1000 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp64k_stratified_480mb_protected_passthrough_sidecar | ok | 64256 | train | 398469 | 396217280 | 73035656 | 0.184332 | 6131 | 0.000084 |  |
| sp64k_stratified_480mb_protected_passthrough_sidecar | ok | 64256 | valid | 49809 | 49279753 | 9073527 | 0.184123 | 1418 | 0.000156 |  |
| sp64k_stratified_480mb_protected_passthrough_sidecar | ok | 64256 | test | 49808 | 50024285 | 9294075 | 0.185791 | 1922 | 0.000207 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| sp64k_stratified_480mb_protected_passthrough_sidecar | ok | 64256 | 19641856 | 16482304 | 3159552 | 7200 | 3686400 | 19998662 | 2.316947 | 2.316947 | 2.340260 |  |

## Loss Accounting

This table reports the same eval pass used for BPB, converted back
to bits/token. Values above `log2(vocab)` indicate an early or
pathological optimization regime and should not be read as
converged LM quality.

| Tokenizer | log2(vocab) | Valid bits/token | Test bits/token | Valid target tokens | Test target tokens | Valid evaluated bytes | Test evaluated bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp64k_stratified_480mb_protected_passthrough_sidecar | 15.9715 | 12.5837 | 12.5962 | 9073408 | 9293952 | 49279112 | 50023628 |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
