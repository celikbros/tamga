# Advisor Update: v2.0 Context-Free Morphology BPB Ladder

Date: 2026-06-11

## Context

We are building a Turkish-primary tokenizer research prototype for future LLM
work.

Current architecture direction:

```text
finite protected routing
+ learned SP64-family tokenizer for normal text
+ Turkish morphology teacher as a soft/diagnostic prior
+ lossless UTF-8 fallback where needed
```

The active protected baseline is:

```text
finite_protected_sp64_numeric_sp_floor
```

It is exact-roundtrip on the v1.8 valid/test split and preserves protected
stress cases:

```text
valid exact roundtrip: 1994/1994
test exact roundtrip: 1998/1998
protected stress: 25/25
```

Recent advisor feedback pushed us to stop interpreting eval-side crossing
concentration naively, close simple high-rate pruning, and run a fixed-byte
tiny-LM calibration ladder before deciding whether morphology-compliant scoring
has any language-modeling value.

## What Was Calibrated

All rows below use the same tiny causal LM:

```text
seq_len=128
batch_size=4
d_model=256
n_layers=4
n_heads=4
```

Each tokenizer was run to approximately 2M raw bytes seen, using tokenizer-
specific step counts from a dry-run token/byte estimate.

Tokenizer ladder:

```text
finite_protected_sp64_numeric_sp_floor
finite_protected_pruned_ge070_nonword
finite_protected_teacher_distilled_16000
finite_protected_teacher_distilled_2000
```

## Results

| Tokenizer | Test tokens/raw byte | Steps | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.164497 | 622 | 2,001,501 | 3.307829 | 3.326482 |
| finite_protected_pruned_ge070_nonword | 0.166698 | 630 | 2,001,977 | 3.298657 | 3.324067 |
| finite_protected_teacher_distilled_16000 | 0.177859 | 675 | 2,002,277 | 3.192085 | 3.213530 |
| finite_protected_teacher_distilled_2000 | 0.191208 | 730 | 2,001,090 | 3.233118 | 3.259261 |

Delta versus protected SP64 floor:

| Tokenizer | Test tokens/raw byte delta | Test BPB delta | Reading |
| --- | ---: | ---: | --- |
| pruned_ge070_nonword | +0.002201 | -0.002415 | marginal / probably too small alone |
| teacher_distilled_16000 | +0.013362 | -0.112952 | strongest current signal |
| teacher_distilled_2000 | +0.026711 | -0.067221 | still positive, but worse than 16k |

## Related Intrinsic Frontier

Challenge:

| Model | Challenge bare F1 | Challenge finite F1 | Bare tokens/word | Finite tokens/word | Crossed boundaries |
| --- | ---: | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 0.6755 | 2.2010 | 2.2977 | 170/305 |
| pruned_ge070_nonword | 0.7486 | 0.6875 | 2.2611 | 2.3577 | 151/305 |
| teacher-distilled 16k | 0.7509 | 0.7219 | 2.3525 | 2.4413 | 139/305 |

Gold:

| Model | Gold bare F1 | Gold finite F1 | Bare tokens/word | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7551 | 0.7314 | 2.5041 | 2.5868 |
| pruned_ge070_nonword | 0.7684 | 0.7453 | 2.5785 | 2.6612 |
| teacher-distilled 16k | 0.8042 | 0.8129 | 2.7686 | 2.8430 |

## Current Interpretation

Our current honest reading:

```text
1. Simple pruning is not enough. It barely improves BPB.
2. Teacher-distilled scoring has a real BPB signal at fixed bytes.
3. The 16k distilled row is better than the 2k distilled row, so the curve is
   not "more morphology pressure is always better."
4. The result supports morphology-compliant scoring as a useful target/bound,
   but not necessarily the exact teacher-distilled implementation as a
   deployable tokenizer.
```

This is the strongest evidence so far that Turkish morphology can be useful for
LM loss when the tokenizer stays protected-aware and lossless.

But we are still cautious:

```text
tiny-LM scale is small
only one seed so far
teacher-distilled scoring is a bound-like mechanism, not yet a clean production
artifact
visible Challenge/Gold are not hidden evals
```

## Questions

Please be critical.

1. Does this 2M-byte ladder change your recommendation?

```text
teacher_distilled_16000 improves test BPB by -0.112952 versus the protected
SP64 floor despite +8.1% test tokens/raw byte.
```

Is this enough to keep morphology-compliant scoring as a primary v2.0 path?

2. How should we interpret the 2k distilled row?

```text
It remains better than SP64 floor, but worse than 16k.
```

Does this imply an optimal intermediate regularization strength, or could it be
tiny-LM/seed noise?

3. What is the next confirmation step?

Options:

```text
A. repeat the 2M-byte ladder with a second seed
B. run only SP64 floor vs teacher_distilled_16000 at a longer fixed-byte budget
C. run a slightly larger tiny model for SP64 floor vs teacher_distilled_16000
D. first improve/audit finite protected wrapper routes
E. run hidden/noisy/code-mixed canary before more BPB
```

4. Should teacher_distilled_16000 be treated as:

```text
A. a candidate tokenizer branch
B. an upper-bound/teacher target only
C. evidence that we should build a lossless reranker
D. evidence that we should build a training-time objective
E. evidence that morphology should move into the LM/data objective instead
```

5. What minimum package would you require before showing this to the LLM team
as an experimental tokenizer candidate, not a final production choice?

6. What is the biggest remaining hidden failure mode?

Examples:

```text
small-model artifact
single-seed artifact
pilot corpus too narrow
teacher-distilled implementation not deployable
protected-wrapper route tax still distorting metrics
non-Turkish/code-mixed degradation
visible-eval overfitting
```

7. If this were your project, what would you build or run next in one week?

Please give:

```text
smallest useful next experiment
stop criterion
success criterion
artifact/report you would want to see
```

## Proposed Next Step

Our proposed next step is:

```text
Do not run more broad intrinsic sweeps.
Treat teacher_distilled_16000 as the current best bound/target.
Run one confirmation experiment:
  SP64 protected floor vs teacher_distilled_16000
  same fixed-byte budget, second seed or longer budget
Then decide whether to invest in a deployable lossless reranker or a true
training-time morphology-aware objective.
```

Please challenge this plan.
