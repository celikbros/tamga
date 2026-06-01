# v1.8 Tiny LM BPB Probe Runner

Date: 2026-06-02

## Status

```text
runner prepared
training not yet run
screening only
not final LLM tokenizer evidence
```

## Purpose

This runner prepares and optionally trains a small causal LM for comparing
tokenizers with byte-normalized loss.

It exists to answer one narrow screening question:

```text
Does the morphology-aware tokenizer survive a fair tiny LM bits-per-byte check?
```

## Config

```text
configs/v1_8_tiny_lm_bpb_probe.toml
```

The config uses the filtered v1.8 split:

```text
artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/
```

## Important Caveat

`custom_tr_morph_lossless` currently uses a temporary train-only vocabulary:

```text
train custom tokens -> temporary vocab
valid/test unseen custom tokens -> <unk>
```

This is not a final tokenizer vocabulary design. The report includes OOV counts
so the temporary custom-vocab penalty is visible.

## Commands

Full encoding dry-run, no training:

```powershell
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml --dry-run
```

Single-tokenizer training smoke:

```powershell
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml --tokenizer custom_tr_morph_lossless
```

Strong SP comparison run:

```powershell
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml --tokenizer sp_unigram_64000_train_only
```

Full matrix training is possible, but should be run manually because it may take
substantial local time:

```powershell
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml
```

## Outputs

Public aggregate report:

```text
artifacts/v1_8_tiny_lm_bpb_probe.md
```

Private encoded stats and metric logs:

```text
artifacts/private/v1_8_tiny_lm_bpb_probe/
```

## Progress Behavior

The script prints progress while encoding each tokenizer and during training:

```text
Encoding tokenizer=...
Encoded tokenizer=...
tokenizer: step=... tokens_seen=... approx_bytes_seen=... valid_bpb=...
```

If a command appears silent for a long time, stop it and rerun with a narrower
`--tokenizer` selection first.

## Interpretation

Do not compare token-level perplexity across tokenizers.

Use:

```text
validation bits-per-byte
test bits-per-byte
```

and keep the v1.8 protocol caveats attached to every result.
