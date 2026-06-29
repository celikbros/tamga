# v2.0 Context-Free Frontier And Next Steps

Date: 2026-06-11

## Current Reading

Fable5's latest review changed the interpretation:

```text
The context-free Unigram/pruning program has been bounded.
The old eval-side crossing concentration statistic was misleading.
The remaining crossing damage is mostly low-support or context-dependent.
```

This does not mean the tokenizer project failed. It means this particular
family of mechanisms is reaching its practical limit:

```text
fixed SP64 vocabulary
+ global score reshaping
+ train-side high-rate pruning
```

## Key Evidence

Train-side attribution:

```text
report: artifacts/v2_0_eval_crossing_piece_source_audit_challenge.md
```

| Model | Crossed boundaries | Reliable train-rate >=0.70 share | Train-count <20 share |
| --- | ---: | ---: | ---: |
| SP64 | 170/305 | 0.4471 | 0.4412 |
| pruned_ge070_nonword | 151/305 | 0.2980 | 0.5563 |
| teacher-distilled 16k | 139/305 | 0.3165 | 0.3453 |

Score validity:

```text
teacher-distilled 16k crossing pieces are almost entirely counted-score pieces,
not floor-score artifacts.
```

So the score bound is valid, and the remaining weakness is not mostly a
serialization bug.

## Frontier Table

Challenge:

| Model | Challenge bare F1 | Challenge finite F1 | Bare tokens/word | Finite tokens/word | Crossed boundaries | Wrapper tax |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 0.6755 | 2.2010 | 2.2977 | 170/305 | -0.0596 |
| pruned_ge070_nonword | 0.7486 | 0.6875 | 2.2611 | 2.3577 | 151/305 | -0.0611 |
| teacher-distilled 16k | 0.7509 | 0.7219 | 2.3525 | 2.4413 | 139/305 | -0.0290 |

Gold:

| Model | Gold bare F1 | Gold finite F1 | Bare tokens/word | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7551 | 0.7314 | 2.5041 | 2.5868 |
| pruned_ge070_nonword | 0.7684 | 0.7453 | 2.5785 | 2.6612 |
| teacher-distilled 16k | 0.8042 | 0.8129 | 2.7686 | 2.8430 |

Closing pruning sweep:

```text
rate=1.00/count20: no movement versus SP64
rate>=0.90/count20: no material improvement over pruned_ge070_nonword
rate>=0.70/count50: no material improvement over pruned_ge070_nonword
```

Decision:

```text
simple high-rate pruning is closed
```

## What This Means

Do not read this as "we cannot build a tokenizer."

Read it as:

```text
The cheap context-free routes have been exhausted with useful evidence.
The next decision must be calibrated by LM loss and wrapper-route behavior,
not by more visible Challenge F1 tuning.
```

The remaining viable paths are:

```text
1. Fix/improve finite protected wrapper routes.
2. Use one fixed-byte tiny-LM calibration to test whether boundary compliance
   has BPB value despite token pressure.
3. If BPB rewards boundary compliance, consider a scoped lossless reranker or
   a more serious objective.
4. If BPB is flat/negative, keep the tokenizer close to repaired SP64+finite
   routing and move morphology prior to LM/data objectives instead.
```

## Prepared Tiny-LM Ladder Config

Config:

```text
configs/v2_0_tiny_lm_context_free_ladder.toml
```

Tokenizer ladder:

```text
finite_protected_sp64_numeric_sp_floor
finite_protected_pruned_ge070_nonword
finite_protected_teacher_distilled_16000
finite_protected_teacher_distilled_2000
```

Dry-run completed after user run:

```text
report: artifacts/v2_0_tiny_lm_context_free_ladder_dry_run.md
private stats: artifacts/private/v2_0_tiny_lm_context_free_ladder_dry_run/encoded_stats.jsonl
```

Encoding summary:

| Tokenizer | Train tokens/byte | Valid tokens/byte | Test tokens/byte |
| --- | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.159113 | 0.163567 | 0.164497 |
| finite_protected_pruned_ge070_nonword | 0.161121 | 0.165813 | 0.166698 |
| finite_protected_teacher_distilled_16000 | 0.172603 | 0.177073 | 0.177859 |
| finite_protected_teacher_distilled_2000 | 0.186778 | 0.190499 | 0.191208 |

Fixed-byte step counts:

| Tokenizer | Steps for 1M bytes | Steps for 2M bytes |
| --- | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 311 | 622 |
| finite_protected_pruned_ge070_nonword | 315 | 630 |
| finite_protected_teacher_distilled_16000 | 338 | 675 |
| finite_protected_teacher_distilled_2000 | 365 | 730 |

Recommended calibration:

```text
Use the 2M-byte target if local runtime is acceptable.
Use the 1M-byte target only as a quick smoke.
```

The training commands should be run one tokenizer at a time so each candidate
uses its own fixed-byte step count.

## 2M-Byte Tiny-LM Calibration Commands

Completed rows:

| Tokenizer | Steps | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 622 | 2,001,501 | 3.307829 | 3.326482 |
| finite_protected_pruned_ge070_nonword | 630 | 2,001,977 | 3.298657 | 3.324067 |
| finite_protected_teacher_distilled_16000 | 675 | 2,002,277 | 3.192085 | 3.213530 |
| finite_protected_teacher_distilled_2000 | 730 | 2,001,090 | 3.233118 | 3.259261 |

Pending rows:

```text
none
```

Final 2M-byte ladder reading:

```text
The pruned row is only marginally better than the protected SP64 floor.
The teacher-distilled 16k row is materially better on 2M-byte tiny-LM BPB,
despite higher token pressure.
The teacher-distilled 2k row is still better than the protected SP64 floor,
but worse than the 16k row.

This is not final LLM evidence, but it is the strongest signal so far that
morphology-compliant scoring can carry LM value when the tokenizer remains
lossless and protected-aware. The curve also warns against over-hardening the
teacher: more boundary pressure eventually costs too much token pressure.

Current balanced point:
  finite_protected_teacher_distilled_16000

Current interpretation:
  morphology signal looks useful, but the deployable mechanism is still open.
  Do not promote teacher-distilled scoring directly as production. Use it as a
  bound/target for the next lossless, maintainable objective or reranker.
```

## 2M-Byte Ladder Delta Versus Protected SP64 Floor

| Tokenizer | Test tokens/byte delta | Test BPB delta | Reading |
| --- | ---: | ---: | --- |
| finite_protected_pruned_ge070_nonword | +0.002201 | -0.002415 | too small to matter alone |
| finite_protected_teacher_distilled_16000 | +0.013362 | -0.112952 | strongest current signal |
| finite_protected_teacher_distilled_2000 | +0.026711 | -0.067221 | useful but over-hardened versus 16k |

```powershell
python scripts\run_tiny_lm_bpb_probe.py configs\v2_0_tiny_lm_context_free_ladder.toml `
  --tokenizer finite_protected_sp64_numeric_sp_floor `
  --max-steps 622 `
  --encode-progress 1000 `
  --report-out artifacts\v2_0_tiny_lm_context_free_ladder_sp64_floor_2mbytes.md `
  --output-dir artifacts\private\v2_0_tiny_lm_context_free_ladder_sp64_floor_2mbytes
```

```powershell
python scripts\run_tiny_lm_bpb_probe.py configs\v2_0_tiny_lm_context_free_ladder.toml `
  --tokenizer finite_protected_pruned_ge070_nonword `
  --max-steps 630 `
  --encode-progress 1000 `
  --report-out artifacts\v2_0_tiny_lm_context_free_ladder_pruned_ge070_nonword_2mbytes.md `
  --output-dir artifacts\private\v2_0_tiny_lm_context_free_ladder_pruned_ge070_nonword_2mbytes
```

```powershell
python scripts\run_tiny_lm_bpb_probe.py configs\v2_0_tiny_lm_context_free_ladder.toml `
  --tokenizer finite_protected_teacher_distilled_16000 `
  --max-steps 675 `
  --encode-progress 1000 `
  --report-out artifacts\v2_0_tiny_lm_context_free_ladder_teacher_distilled_16000_2mbytes.md `
  --output-dir artifacts\private\v2_0_tiny_lm_context_free_ladder_teacher_distilled_16000_2mbytes
```

```powershell
python scripts\run_tiny_lm_bpb_probe.py configs\v2_0_tiny_lm_context_free_ladder.toml `
  --tokenizer finite_protected_teacher_distilled_2000 `
  --max-steps 730 `
  --encode-progress 1000 `
  --report-out artifacts\v2_0_tiny_lm_context_free_ladder_teacher_distilled_2000_2mbytes.md `
  --output-dir artifacts\private\v2_0_tiny_lm_context_free_ladder_teacher_distilled_2000_2mbytes
```

## Recommended Next Order

1. Run the dry-run ladder to get exact tokens/byte for all four candidates.
2. Compute fixed-byte step counts from the dry-run.
3. Run one fixed-byte tiny-LM calibration, preferably longer than 300 steps if
   local runtime is acceptable.
4. In parallel, audit/redesign wrapper route behavior for:

```text
numeric_like
file_like
apostrophe + hard_suffix
```

5. Write a decision memo:

```text
if BPB rewards crossing reduction:
  fund scoped lossless reranker / stronger objective
else:
  close tokenizer-level morphology prior and keep repaired SP64+finite routing
```
