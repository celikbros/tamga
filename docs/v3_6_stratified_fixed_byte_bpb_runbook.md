# v3.6 Stratified Fixed-Byte BPB Runbook

Date: 2026-06-19

## Purpose

v3.6 closes the next tokenizer selection gate:

```text
v3.4-trained 48K sidecar model
vs
v3.4-trained 64K sidecar model
```

Both models already passed the v3.5 protected sidecar smoke on the broader
stratified sample. The remaining question is whether the 64K model's lower
token pressure is worth the larger embedding table in an LM-facing BPB probe.

## Inputs

Split:

```text
artifacts/private/v3_4_stratified_480mb_ablation_split
```

Models:

```text
artifacts/private/v3_4_vocab_ablation_sentencepiece/sp_unigram_48000_stratified_480mb.model
artifacts/private/v3_4_vocab_ablation_sentencepiece/sp_unigram_64000_stratified_480mb.model
```

Configs:

```text
configs/v3_5_sidecar_sp48k_stratified_480mb.toml
configs/v3_5_sidecar_sp64k_stratified_480mb.toml
```

## Dry-Run Calibration

| Candidate | Vocab | Train tokens/raw byte | Valid tokens/raw byte | Test tokens/raw byte | Test fallback rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| sp48k stratified sidecar | 48256 | 0.191076 | 0.190735 | 0.192455 | 0.000200 |
| sp64k stratified sidecar | 64256 | 0.184332 | 0.184123 | 0.185791 | 0.000207 |

64K is lower on test token pressure by:

```text
0.192455 - 0.185791 = 0.006664 tokens/raw byte
about 3.46% relative to 48K
```

## Fixed-Byte Step Plan

The tiny-LM probe consumes:

```text
seq_len * batch_size = 128 * 4 = 512 tokens/step
```

For an approximately 20M raw-byte budget:

| Candidate | Train tokens/raw byte | Steps | Approx raw bytes seen |
| --- | ---: | ---: | ---: |
| sp48k stratified sidecar | 0.191076 | 7464 | 20,000,251 |
| sp64k stratified sidecar | 0.184332 | 7200 | 19,998,698 |

## Commands

Run sequentially, not in parallel:

```powershell
python scripts\run_tiny_lm_bpb_probe.py configs\v3_5_sidecar_sp48k_stratified_480mb.toml `
  --tokenizer sp48k_stratified_480mb_protected_passthrough_sidecar `
  --max-steps 7464 `
  --eval-interval 1000 `
  --encode-progress 50000 `
  --report-out artifacts\v3_6_tiny_lm_sp48k_stratified_480mb_20m.md `
  --output-dir artifacts\private\v3_6_tiny_lm_sp48k_stratified_480mb_20m

python scripts\run_tiny_lm_bpb_probe.py configs\v3_5_sidecar_sp64k_stratified_480mb.toml `
  --tokenizer sp64k_stratified_480mb_protected_passthrough_sidecar `
  --max-steps 7200 `
  --eval-interval 1000 `
  --encode-progress 50000 `
  --report-out artifacts\v3_6_tiny_lm_sp64k_stratified_480mb_20m.md `
  --output-dir artifacts\private\v3_6_tiny_lm_sp64k_stratified_480mb_20m
```

## Gate

Prefer 64K only if it wins or ties BPB clearly enough to justify the larger
embedding table.

Prefer 48K if:

```text
64K's BPB gain is absent, tiny, or unstable
```

Prefer 64K if:

```text
64K has materially lower BPB or equal BPB with materially lower LM sequence
length pressure on the broad stratified sample
```

Do not treat this as final production evidence. It is a v3.x tokenizer
selection screen before a larger LLM-team integration smoke.

## Reports To Keep

```text
artifacts/v3_6_tiny_lm_sp48k_stratified_480mb_dry_run.md
artifacts/v3_6_tiny_lm_sp64k_stratified_480mb_dry_run.md
artifacts/v3_6_tiny_lm_sp48k_stratified_480mb_20m.md
artifacts/v3_6_tiny_lm_sp64k_stratified_480mb_20m.md
```
