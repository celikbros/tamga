# Advisor Follow-Up: Matched Non-Morph Control Result

Date: 2026-06-11

## Context

You warned that the 2M-byte `teacher_distilled_16000` BPB gain might be caused
by generic same-vocabulary score re-estimation / effective-vocabulary geometry
rather than morphology.

We accepted that critique and ran the requested matched non-morph control.

## Clarification

`teacher_distilled_16000` is not a 16k-vocabulary model.

All finite-protected rows use the same effective tiny-LM vocab size:

```text
vocab_size: 64630
```

The `16000` suffix means:

```text
global SP64 Unigram scores re-estimated from 16k train lines
```

## Accounting Audit

We also ran a BPB accounting audit:

```text
report: artifacts/v2_0_tiny_lm_context_free_ladder_bpb_accounting_audit.md
```

Result:

| Tokenizer | Uniform bits/token | Test bits/token | Reading |
| --- | ---: | ---: | --- |
| finite_protected_sp64_numeric_sp_floor | 15.9799 | 20.2221 | undertrained |
| finite_protected_pruned_ge070_nonword | 15.9799 | 19.9407 | undertrained |
| finite_protected_teacher_distilled_16000 | 15.9799 | 18.0679 | undertrained |
| finite_protected_teacher_distilled_2000 | 15.9799 | 17.0457 | undertrained |

We agree this means:

```text
The 2M-byte ladder is early-learning calibration, not converged LM quality.
```

## Matched Control

We built:

```text
finite_protected_self_distilled_16000
```

Mechanism:

```text
fixed SP64 vocabulary
same finite protected wrapper
same 16k train-line score re-estimation
official SentencePiece segmentation counts
no morphology teacher boundaries
```

Materialization:

```text
report: artifacts/v2_0_self_distilled_16000lines_materialization.md
model: artifacts/private/v2_0_self_distilled_sp/self_distilled_16000lines_unigram_64000.model
vocab: artifacts/private/v2_0_self_distilled_sp/self_distilled_16000lines_unigram_64000.vocab
lines: 16000
segments: 2854463
counted tokens: 3509481
counted piece types: 60120
changed scores: 63997
```

Dry-run token pressure:

| Tokenizer | Train tokens/byte | Valid tokens/byte | Test tokens/byte |
| --- | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.159113 | 0.163567 | 0.164497 |
| finite_protected_self_distilled_16000 | 0.159508 | 0.163942 | 0.164852 |
| finite_protected_teacher_distilled_16000 | 0.172603 | 0.177073 | 0.177859 |

## 2M-Byte Result

Same tiny-LM setup:

```text
seq_len=128
batch_size=4
d_model=256
n_layers=4
n_heads=4
fixed approximately 2M raw bytes seen
```

| Tokenizer | Test tokens/byte | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.164497 | 2,001,501 | 3.307829 | 3.326482 |
| finite_protected_self_distilled_16000 | 0.164852 | 1,999,750 | 3.312045 | 3.343937 |
| finite_protected_teacher_distilled_16000 | 0.177859 | 2,002,277 | 3.192085 | 3.213530 |

Delta:

| Comparison | Test BPB delta |
| --- | ---: |
| self_distilled_16000 vs SP64 floor | +0.017455 |
| teacher_distilled_16000 vs SP64 floor | -0.112952 |
| teacher_distilled_16000 vs self_distilled_16000 | -0.130407 |

## Current Reading

The matched non-morph control does not reproduce the teacher-distilled gain.
It is slightly worse than the protected SP64 floor.

Therefore:

```text
The 16k teacher-distilled gain is not explained by same-vocabulary score
re-estimation alone.
```

This does not remove the undertrained tiny-LM caveat. It does improve
attribution: the positive BPB signal now points more strongly toward the
morphology teacher.

## Questions

Please be critical.

1. Does this matched-control result satisfy the attribution concern enough to
   proceed to confirmation?

2. What should be the next confirmation step now?

Options:

```text
A. second seed for SP64 floor vs teacher_distilled_16000
B. longer fixed-byte learning curve for SP64 floor vs teacher_distilled_16000
C. three-row learning curve: SP64 floor / self_distilled_16000 / teacher_distilled_16000
D. mixed-domain/code-mixed canary before more training
E. slightly larger model
```

3. Given the accounting audit, should the next run target convergence evidence
   rather than another 2M endpoint?

4. Would you now treat `teacher_distilled_16000` as:

```text
upper-bound target only
candidate branch
evidence for a static deployable approximation
evidence for a training-time objective
evidence for a lossless reranker
```

5. What exact stop/success threshold would you pre-register for the next run?

6. What report would you want before showing this as an experimental result to
   the LLM team?

## Proposed Next Step

Our proposed next step is now:

```text
Do not run broad sweeps.
Run a three-row learning-curve confirmation:
  SP64 floor
  self_distilled_16000
  teacher_distilled_16000
at a larger fixed-byte budget, with evaluation checkpoints.

If teacher_distilled_16000 stays clearly below both controls across the curve,
then morphology-aware scoring deserves a deployable objective/reranker branch.

If the gap shrinks or crosses, treat the 2M result as early-convergence help
rather than durable tokenizer quality.
```

Please challenge this plan.
