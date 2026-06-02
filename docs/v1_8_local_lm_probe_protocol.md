# v1.8 Local LM Probe Protocol

Date: 2026-06-01

## Status

```text
draft protocol
do not run until fairness prerequisites are implemented
not final LLM tokenizer evidence
```

## Purpose

The v1.8 local LM probe is an adversarial screening test:

```text
Can the morphology-aware tokenizer survive a byte-normalized LM-loss comparison
against fair train-only SP and hybrid baselines?
```

It is not intended to certify production readiness or final LLM integration.

## Required Prerequisites

### P1. Frozen Raw Split

Use the same 20k-line clean pilot split:

```text
train: 16,000 lines
valid: 2,000 lines
test:  2,000 lines
seed:  20260601
```

The split source is currently:

```text
data/train/claim_grade/celik_gold_clean_pilot.txt
```

Materialization config:

```text
configs/v1_8_local_lm_probe_split.toml
```

Command:

```powershell
python scripts/materialize_probe_split.py configs/v1_8_local_lm_probe_split.toml
```

Private output directory:

```text
artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/
```

Status:

```text
completed; see artifacts/v1_8_local_lm_probe_split_materialization.md
```

### P2. Train-Only SP Vocabularies

For LM-loss comparison, do not reuse SP vocabularies trained on the full 100k
pilot.

Train SP baselines only on the 16k train split:

```text
sp_bpe_16000_train_only
sp_unigram_16000_train_only
sp_bpe_32000_train_only
sp_unigram_32000_train_only
sp_bpe_64000_train_only
sp_unigram_64000_train_only
```

Train-only SP config:

```text
configs/v1_8_train_only_sentencepiece_sweep.toml
```

Command, after the raw split has been materialized:

```powershell
python scripts/run_sentencepiece_sweep.py configs/v1_8_train_only_sentencepiece_sweep.toml
```

Status:

```text
completed; see docs/v1_8_train_only_sentencepiece_findings.md
```

### P3. Hybrid Baseline

Add at least one morphology/protection-aware learned baseline:

```text
hybrid_morph_pretok_unigram_train_only
```

or:

```text
hybrid_morph_pretok_bpe_train_only
```

This baseline should use the tokenizer's morphology/protected-span signal as a
pretokenization prior, then learn subword merges from the train split only.

If the hybrid baseline is not implemented, v1.8 should be treated as incomplete.

Status:

```text
completed for intrinsic screening; see docs/v1_8_hybrid_sentencepiece_findings.md
hybrid pretokenized train corpus is materialized
hybrid SP sweep was run with max_sentence_length = 20000
```

### P4. Lossless Roundtrip Checks

Before LM training, each tokenizer must pass:

```text
decode(encode(x)) == x
```

on train, valid, test, and canary text.

Roundtrip failure count must be reported. Any failure disqualifies a tokenizer
from generation-oriented LLM use.

Status:

```text
completed; see docs/v1_8_roundtrip_findings.md
custom_tr_morph passes only with preserve_whitespace=True lossless mode
all checked train-only SP baselines pass
```

### P5. Split Overlap Check

Run n-gram or MinHash-style near-duplicate checks between:

```text
train <-> valid
train <-> test
valid <-> test
```

Report exact and near-duplicate overlap before using valid/test losses.

Status:

```text
checked and filtered; see docs/v1_8_split_overlap_findings.md
no exact duplicates found
8 train-to-eval near-overlap candidates were excluded from filtered valid/test
filtered split recheck is clean
```

### P6. Canary Diagnostics

Primary scores remain Turkish-primary, but include a small diagnostic canary:

```text
noisy Turkish
ASCII-folded Turkish
code-mixed Turkish/English
technical/code spans
non-Turkish multilingual snippets
```

Canary metrics:

```text
roundtrip failures
tokens/byte
catastrophic fragmentation examples
optional bits-per-byte if included in the LM probe
```

Status:

```text
completed; see docs/v1_8_canary_diagnostics_findings.md
custom_tr_morph_lossless has 0 roundtrip failures on the public/synthetic canary
custom_tr_morph_lossless preserved 7/7 auto-detected protected spans
```

## Tokenizer Matrix

Minimum matrix:

```text
custom_tr_morph
utf8_byte
unicode_char
sp_bpe_16000_train_only
sp_unigram_16000_train_only
sp_bpe_32000_train_only
sp_unigram_32000_train_only
sp_bpe_64000_train_only
sp_unigram_64000_train_only
hybrid_morph_pretok_unigram_train_only
```

Optional:

```text
sp_bpe_8000_train_only
sp_unigram_8000_train_only
existing production tokenizer anchor
```

## Budget And Reporting

Primary x-axis:

```text
bytes seen
```

Primary metric:

```text
validation bits-per-byte
test bits-per-byte
```

Always report:

```text
tokens seen
bytes seen
steps
tokens/sec
bytes/sec
wall-clock
GPU/CPU memory
total parameters
embedding parameters
non-embedding parameters
```

If training is implemented with fixed token batches, still report bytes seen per
checkpoint and plot/compare bits-per-byte against bytes seen.

## Model Setup

Use one small causal LM architecture across tokenizers.

Recommended first setting:

```text
fixed transformer body
tied embeddings
6-8 layers
d_model chosen so the body is not dominated by embeddings
roughly 10M-30M non-embedding parameters if feasible
1 seed first
3 seeds only if results are close or surprising
```

Because 32k/64k vocabularies consume many embedding parameters, report parameter
allocation for every tokenizer.

## Pre-Registered Interpretation

### Continue Pure Custom Path

Continue investing in pure `custom_tr_morph` if:

```text
custom_tr_morph is comparable or better than the strongest SP/hybrid baselines
on validation/test bits-per-byte and has acceptable throughput, context pressure,
and roundtrip behavior.
```

### Pivot Toward Hybrid

Prioritize hybrid v2.0 if:

```text
custom_tr_morph loses on bits-per-byte, but hybrid morphology-aware baselines
match or beat SP.
```

### Deprioritize Pure Custom For LLM Default

Deprioritize pure deterministic custom as the default LLM tokenizer if:

```text
custom_tr_morph is worse than the strongest comparable SP/hybrid baseline by
more than 0.15-0.25 bits/byte on both validation and test after all fairness
fixes, with no compensating operational advantage.
```

Do not abandon morphology entirely on this basis; keep it as a v2.0 hybrid prior
unless hybrid baselines also fail.

## What Not To Conclude

Do not conclude:

```text
boundary F1 alone proves LLM value
small-probe BPB alone proves final LLM integration readiness
an SP win in an unfair setup kills morphology
a custom win on clean pilot proves multilingual robustness
```

## Next Implementation Steps

1. Completed: write train/valid/test split materialization for the 20k pilot.
2. Completed: train train-only SP baselines from the 16k train split.
3. Completed: implement and report a hybrid morphology-aware SP baseline.
4. Completed: add roundtrip and split-overlap reports.
5. Completed: add canary text and diagnostics.
6. Prepared: tiny LM bits-per-byte runner; see docs/v1_8_tiny_lm_bpb_probe_runner.md.
7. Completed: run full encoding dry-run; see docs/v1_8_tiny_lm_bpb_probe_encoding_findings.md.
8. Completed: run narrow 500-step smoke for custom_tr_morph_lossless and sp_bpe_64000_train_only.
9. Next: run iso-byte SP 200-step follow-up; see docs/v1_8_tiny_lm_bpb_smoke_findings.md.
