# Advisor Feedback Triage: Distilled Score Bound And Pruning

Date: 2026-06-11

## Advisor Claim

Fable5 corrected two important readings:

```text
1. Eval-side "1.00 crossing-rate" attribution is unreliable because many eval
   pieces occur only once or twice.
2. The real test of concentration is the pruning intervention itself.
```

The advisor's stronger reading:

```text
Probe A removed 4,329 train-side high-rate crossing pieces but deployed
crossings only fell 170 -> 139.

That means the remaining damage is not mostly a clean train-identifiable tail.
It is context-dependent conflict.
```

We accept this correction.

## New Controls Added

New script:

```text
scripts/audit_v2_eval_crossing_piece_sources.py
```

Tests:

```text
tests/test_v2_eval_crossing_piece_sources.py
```

Targeted tests:

```text
8 passed
```

The script re-attributes eval crossing pieces using train-side crossing
statistics and model scores. It also checks whether teacher-distilled crossing
pieces are floor-scored or counted-scored.

## Train-Side Attribution Result

Report:

```text
artifacts/v2_0_eval_crossing_piece_source_audit_challenge.md
```

Challenge result:

| Model | Crossed boundaries | Reliable train-rate >=0.70 share | Train-count <20 share | Low/benign train-rate share |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 170/305 | 0.4471 | 0.4412 | 0.1118 |
| teacher-distilled 16k | 139/305 | 0.3165 | 0.3453 | 0.3381 |
| pruned_ge070_nonword | 151/305 | 0.2980 | 0.5563 | 0.1457 |

Reading:

```text
Fable5 was right. The prior eval-side attribution overstated concentration.
After train-side attribution, the remaining damage is largely low-support or
context-dependent, especially after pruning.
```

## Teacher-Distilled Score Validity Check

The advisor asked whether crossing pieces in the distilled model carry floor
scores or counted scores.

Challenge:

```text
teacher-distilled 16k crossing pieces:
  counted-score crossed boundaries: 137/139
  floor-score crossed boundaries: 2/139
```

Gold:

```text
teacher-distilled 16k crossing pieces:
  counted-score crossed boundaries: 55/55
  floor-score crossed boundaries: 0/55
```

Reading:

```text
The distillation bound is mechanically valid. The crossings are not mostly a
serialization/floor-score bug. The limit is in the fixed-vocab global-score
family itself.
```

## Missing Gold 16k Bound

Report:

```text
artifacts/v2_0_teacher_distilled_sp_16000lines_ci_gold.md
```

Gold result:

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7551 | 2.5041 | 0.7314 | 2.5868 |
| teacher-distilled 16k | 0.8042 | 2.7686 | 0.8129 | 2.8430 |

Reading:

```text
Gold shows stronger morphology transfer than challenge. Challenge appears to
stress context-dependent residues and protected-adjacent cases more heavily.
Use both metrics instead of treating challenge F1 alone as the frontier.
```

## Closing Pruning Sweep

Fable5 recommended a small sweep as the closing measurement of the
context-free pruning program.

Cells:

```text
non_word_start, crossing_rate = 1.00, min_count >= 20
non_word_start, crossing_rate >= 0.90, min_count >= 20
non_word_start, crossing_rate >= 0.70, min_count >= 50
```

Challenge CI report:

```text
artifacts/v2_0_pruned_sp_closing_sweep_ci_challenge.md
```

Gold CI report:

```text
artifacts/v2_0_pruned_sp_closing_sweep_ci_gold.md
```

Challenge summary:

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word | Crossed boundaries |
| --- | ---: | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 2.2010 | 0.6755 | 2.2977 | 170/305 |
| pruned_ge070_nonword | 0.7486 | 2.2611 | 0.6875 | 2.3577 | 151/305 |
| pruned_rate100 | 0.7351 | 2.2010 | 0.6755 | 2.2977 | 170/305 |
| pruned_rate090 | 0.7482 | 2.2559 | 0.6871 | 2.3525 | 155/305 |
| pruned_rate070_count50 | 0.7497 | 2.2480 | 0.6897 | 2.3446 | 153/305 |
| teacher-distilled 16k | 0.7509 | 2.3525 | 0.7219 | 2.4413 | 139/305 |

Gold summary:

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7551 | 2.5041 | 0.7314 | 2.5868 |
| pruned_ge070_nonword | 0.7684 | 2.5785 | 0.7453 | 2.6612 |
| pruned_rate100 | 0.7551 | 2.5041 | 0.7314 | 2.5868 |
| pruned_rate090 | 0.7721 | 2.5785 | 0.7491 | 2.6612 |
| pruned_rate070_count50 | 0.7652 | 2.5537 | 0.7420 | 2.6364 |
| teacher-distilled 16k | 0.8042 | 2.7686 | 0.8129 | 2.8430 |

Reading:

```text
No pruning cell materially beats probe B. The best challenge point estimate is
pruned_rate070_count50, but it is a tiny gain over pruned_ge070_nonword and
inside the visible-eval uncertainty.
```

This closes simple train-side high-rate pruning as a path to the goal.

## Wrapper-Tax Contrast

Reports:

```text
artifacts/v2_0_finite_wrapper_eval_tax_challenge_pruned_ge070_all.md
artifacts/v2_0_finite_wrapper_eval_tax_challenge_pruned_ge070_nonword.md
artifacts/v2_0_finite_wrapper_eval_tax_challenge_teacher_distilled_16k.md
```

Challenge wrapper tax:

| Model | Bare F1 | Finite F1 | Tax |
| --- | ---: | ---: | ---: |
| SP64 | 0.7351 | 0.6755 | -0.0596 |
| pruned_ge070_all | 0.7447 | 0.6582 | -0.0865 |
| pruned_ge070_nonword | 0.7486 | 0.6875 | -0.0611 |
| teacher-distilled 16k | 0.7509 | 0.7219 | -0.0290 |

Key route reading:

```text
teacher-distilled 16k no_protected route:
  bare F1 0.7713
  finite F1 0.7757
  tax +0.0043

remaining tax is concentrated in numeric_like/file_like/protected-adjacent
cases, not ordinary normal text.
```

This makes wrapper-route redesign a higher-leverage engineering task than more
context-free pruning.

## Decision

Accepted:

```text
simple context-free score/pruning/inventory work is near its practical limit
challenge-only F1 is not a sufficient value function
wrapper tax is model-dependent and must be audited separately
```

Next recommended work:

```text
1. Build one consolidated four-model frontier table:
   SP64, pruned_ge070_nonword, teacher_distilled_16k, finite protected floor.
2. Prepare a fixed-byte tiny-LM calibration command for the user to run.
3. In parallel, start protected-wrapper route audit/redesign for numeric/file/
   apostrophe suffix cases.
```

Do not start MorphBPE yet.

Do not run more pruning sweeps.
