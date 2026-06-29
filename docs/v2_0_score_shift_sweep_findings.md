# v2.0 Score-Shift Sweep Findings

Date: 2026-06-10

## Purpose

Fable5 warned that closing score-shift after a single `lambda=0.5` probe was
premature. We accepted that critique and ran a cached score-shift sweep.

The goal was to test whether a standard SentencePiece artifact can be improved
by post-hoc score penalties for pieces that frequently cross custom-teacher
soft morphology boundaries.

## Precondition: Vocab Oracle Ceiling

Before the sweep, we measured the SP64 vocabulary oracle ceiling.

Report:

```text
artifacts/v2_0_sp_vocab_oracle_ceiling_challenge.md
```

Challenge:

| Mode | Avg tokens/word | Boundary F1 |
| --- | ---: | ---: |
| lambda0 | 2.0783 | 0.7422 |
| no_cross | 2.5509 | 0.8407 |
| oracle_best_f1 | 2.5457 | 0.8417 |

Interpretation:

```text
SP64 vocab can express much better morphology-compatible paths, but those
paths are longer. The vocabulary is not the immediate ceiling; score/objective
work is still meaningful in principle.
```

## Sweep Setup

Train-only crossing stats:

```text
artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json
```

Score-shift parameters:

```text
penalty_mode = mass
lambda = 1, 2, 4, 8
min_count = 20
min_crossing_count = 20
min_crossing_rate = 0
min_surface_len = 2
max_penalty = 8
adjusted pieces = 4592
```

The cap did not hide the sweep: top deltas increased from roughly `-0.53`
at lambda 1 to roughly `-4.24` at lambda 8.

## Results

| Candidate | Bare Challenge F1 | Finite-protected Challenge F1 | Bare avg tokens/word | Finite avg model tokens/word |
| --- | ---: | ---: | ---: | ---: |
| score-shift mass lambda 1 | 0.7351 | 0.6755 | 2.2010 | 2.2977 |
| score-shift mass lambda 2 | 0.7351 | 0.6755 | 2.2010 | 2.2977 |
| score-shift mass lambda 4 | 0.7351 | 0.6755 | 2.2010 | 2.2977 |
| score-shift mass lambda 8 | 0.7364 | 0.6768 | 2.2010 | 2.2977 |

Reports:

```text
artifacts/v2_0_score_shift_mass_lambda1_intrinsic_eval.md
artifacts/v2_0_score_shift_mass_lambda2_intrinsic_eval.md
artifacts/v2_0_score_shift_mass_lambda4_intrinsic_eval.md
artifacts/v2_0_score_shift_mass_lambda8_intrinsic_eval.md
```

## Interpretation

Post-hoc score-shift does not produce a meaningful dose-response in this form.

The SP64 vocabulary has higher morphology-compatible paths available, but
simple global score penalties do not move the deployed SentencePiece argmax
path toward them.

This suggests the morphology prior needs to enter a real training objective,
not just a post-hoc score patch.

## Decision

Close the current post-hoc score-shift branch.

Do not run tiny-LM on these score-shift candidates.

## Next

Proceed to a true training-time objective, preferably boundary-weighted
Unigram/EM because:

```text
it matches the SP64 Unigram baseline family
it can reshape both piece scores and vocabulary probabilities during learning
it has a path to a standard-ish SentencePiece artifact
```

Before heavy implementation, also do the two methodology chores Fable5 flagged:

```text
bootstrap CI/noise floor for visible challenge metrics
wrapper-tax decomposition for the finite protected route
```
