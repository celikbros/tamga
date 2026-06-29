# Advisor Follow-Up: Unigram Decomposition Result

Date: 2026-06-12

## Context

You asked us to run a zero-training unigram-entropy BPB decomposition before
starting the larger learning-curve run.

Goal:

```text
Decide whether the teacher_distilled_16000 tiny-LM BPB gain is already present
in static token distribution geometry, or whether it appears only after
contextual modeling.
```

## Setup

Tokenizers:

```text
finite_protected_sp64_numeric_sp_floor
finite_protected_self_distilled_16000
finite_protected_teacher_distilled_16000
```

All use:

```text
vocab_size: 64630
same finite protected wrapper
same train/test split
same UTF-8 fallback path
```

Unigram method:

```text
tokenize train/test exactly as the LM sees the stream
estimate smoothed unigram distribution from train tokens
evaluate test negative log likelihood
normalize by raw test bytes
alpha = 0.1
```

Report:

```text
artifacts/v2_0_unigram_entropy_bpb_matched_control.md
```

## Result

| Tokenizer | Test tokens/byte | Test bits/token | Test unigram BPB | Delta vs SP64 |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.164497 | 12.322119 | 2.026952 | +0.000000 |
| finite_protected_self_distilled_16000 | 0.164852 | 12.303881 | 2.028322 | +0.001370 |
| finite_protected_teacher_distilled_16000 | 0.177859 | 11.873857 | 2.111869 | +0.084916 |

For reference, the 2M-byte tiny-LM result was:

| Tokenizer | Test BPB |
| --- | ---: |
| finite_protected_sp64_numeric_sp_floor | 3.326482 |
| finite_protected_self_distilled_16000 | 3.343937 |
| finite_protected_teacher_distilled_16000 | 3.213530 |

## Current Reading

`teacher_distilled_16000` has lower unigram bits/token, but its higher
tokens/byte makes its unigram BPB worse than SP64.

Therefore:

```text
The teacher_distilled_16000 tiny-LM BPB win is not already present in static
unigram BPB.
```

This points more toward contextual/morphological usefulness than toward static
token-distribution geometry.

The undertrained tiny-LM caveat remains:

```text
2M tiny-LM BPB is still above each model's unigram BPB floor.
```

## Runner Fix

We updated the tiny-LM runner so future runs report:

```text
valid_bits_per_token
valid_target_tokens
valid_evaluated_bytes
valid_evaluated_fraction
```

The public report now includes a `Loss Accounting` section with:

```text
log2(vocab)
valid/test bits per token
valid/test target-token counts
valid/test evaluated byte denominators
```

We also added:

```text
--eval-interval
```

so longer learning curves can use fewer full-eval passes.

## Proposed Next Run

Three-row learning curve:

```text
finite_protected_sp64_numeric_sp_floor
finite_protected_self_distilled_16000
finite_protected_teacher_distilled_16000
```

Budget:

```text
~20M raw bytes seen
eval every 500 steps
log BPB versus steps, tokens, and bytes
```

Approx step counts:

```text
SP64 floor: 6216 steps
self_distilled_16000: 6231 steps
teacher_distilled_16000: 6743 steps
```

## Questions

Please be critical.

1. Does the unigram decomposition strengthen the contextual/morphological
   interpretation enough to run the 20M three-row curve?

2. Is 20M bytes sufficient, or should we choose 10M first as a cheaper curve
   smoke?

3. Should all three rows be run, or is it enough to run SP64 floor and
   teacher_distilled_16000 now that self_distilled is weak in both tiny-LM and
   unigram BPB?

4. What exact pass/fail rule should we use at 20M?

Candidate:

```text
teacher_distilled_16000 must stay below both controls by >=0.03 test BPB after
10M bytes and at final checkpoint, and the gap must not monotonically shrink
toward crossover.
```

5. Should we run a code-mixed/noisy canary before or after the 20M curve?

## Current Proposed Action

Run the three-row 20M learning curve unless you think the canary should block
it.

Treat the result as:

```text
experimental evidence only
not production handoff
not final tokenizer selection
```
