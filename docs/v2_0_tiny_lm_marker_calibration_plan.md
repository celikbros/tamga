# v2.0 Tiny-LM Marker Calibration Plan

Date: 2026-06-08

## Purpose

This is not an LLM handoff run. It is a calibration probe to answer:

```text
Does tiny-LM BPB track boundary F1, token pressure, or neither?
```

The probe should be interpreted as a ranking/diagnostic check, not a final
tokenizer decision.

## Candidate Set

Config:

```text
configs/v2_0_tiny_lm_marker_calibration.toml
```

Enabled tokenizers:

```text
sp_unigram_64000_train_only
finite_protected_sp64_floor
suffix_chain2_marker_stripped
all_soft_marker_stripped
```

Disabled but available:

```text
high_value_suffix_marker_stripped
```

## Encoder Fix

The calibration config uses:

```text
kind = "finite_protected_marker_stripped"
```

This is important. It keeps finite protected routing but does not insert the
private soft marker into normal encode-time text. That matches the train-only
marker design.

## Smoke Result

Single-tokenizer dry-run smoke:

```text
report: artifacts/v2_0_tiny_lm_marker_calibration_suffix_chain2_dry_run.md
tokenizer: suffix_chain2_marker_stripped
train tokens/raw byte: 0.181276
valid tokens/raw byte: 0.184500
test tokens/raw byte: 0.185337
valid protected byte fallback tokens: 194
test protected byte fallback tokens: 249
```

The slight difference from the intrinsic diagnostic token-pressure reports is
expected because the tiny-LM encoding includes EOS tokens.

## Full Dry-Run Result

Full encode/token-pressure dry-run:

```text
report: artifacts/v2_0_tiny_lm_marker_calibration_dry_run.md
private stats: artifacts/private/v2_0_tiny_lm_marker_calibration_dry_run/encoded_stats.jsonl
```

| Tokenizer | Valid tokens/raw byte | Test tokens/raw byte | Protected fallback source tokens valid/test |
| --- | ---: | ---: | ---: |
| sp_unigram_64000_train_only | 0.159020 | 0.159620 | 0 / 0 |
| finite_protected_sp64_floor | 0.182112 | 0.183362 | 194 / 249 |
| suffix_chain2_marker_stripped | 0.184500 | 0.185337 | 194 / 249 |
| all_soft_marker_stripped | 0.196313 | 0.196954 | 194 / 249 |

This confirms the intended calibration bracket:

```text
SP64 is the compression floor but breaks protected spans.
finite_protected_sp64_floor is the protected floor.
suffix_chain2 is the cheap train-only morphology point.
all_soft_marker_stripped is the higher-F1/higher-pressure morphology point.
```

## User-Run Dry-Run Command

This command performs full encode/token-pressure accounting for all enabled
calibration candidates. It does not train a model.

```powershell
python scripts\run_tiny_lm_bpb_probe.py configs\v2_0_tiny_lm_marker_calibration.toml `
  --dry-run `
  --encode-progress 5000 `
  --report-out artifacts\v2_0_tiny_lm_marker_calibration_dry_run.md `
  --output-dir artifacts\private\v2_0_tiny_lm_marker_calibration_dry_run
```

Expected behavior:

```text
progress every 5,000 lines for slower finite-protected candidates
public report written under artifacts/
private encoded stats written under artifacts/private/
```

## After Dry-Run

Dry-run has passed.

Run short per-tokenizer BPB probes rather than launching all candidates at once.
This keeps failures isolated and makes progress visible.

Recommended order:

```text
1. sp_unigram_64000_train_only
2. finite_protected_sp64_floor
3. suffix_chain2_marker_stripped
4. all_soft_marker_stripped
```

Use the same `--max-steps` for all four so this is a calibrated ranking check.
