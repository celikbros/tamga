# v3.8 Production-Final Closure

Date: 2026-06-24

## Decision

The v3.8 Turkish-primary tokenizer and its full Faz 2 tokenized package are
accepted and frozen for Faz 4 pretraining.

```text
tokenizer: sp64k_final_protected_passthrough_sidecar_controls128
effective vocab size: 64,384
input lines: 6,027,968
tokens: 2,499,949,602
tokens/raw byte: 0.184311
SP alignment mismatches: 0
max token id: 64,244
```

## Evidence

```text
v3.8 model hash verified by LLM team
full-corpus tokenization completed after the U+2581 detector fix
checksum validation: PASS
fixture validation: PASS
LLM production binary_loader: PASS
single label shift: PASS
loss_mask -> -100: PASS
```

The production loader validated 1,220,678 sequences at sequence length 2,048.
The output binaries are now the Faz 4 pretraining input.

## Scope Of Finality

Production-final means frozen for this Turkish-primary Faz 4 run:

```text
SP model and vocabulary
64,384-id contract
control-token registry
tokenizer config
sidecar schema
tokens.bin and loss_mask.bin
```

Future multilingual or code expansion requires an explicit new tokenizer
version and compatibility decision. It does not alter this v3.8 closure.

## Maintenance Follow-Up

The tokenizer-side Python dataloader simulation was too slow for a 2.5B-token
exhaustive scan. The gate now defaults to 4,096 evenly spaced batches and can be
configured with `--dataloader-max-batches`. Full checksum and fixture validation
remain exhaustive.

## Ownership

```text
Tokenizer team: v3.8 Faz 2 contract CLOSED
LLM team: Faz 4 pretraining owner
```
