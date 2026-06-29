# v2.0 Distilled Score Bound Findings

Date: 2026-06-10

## Purpose

Fable5 pointed out that our boundary-weighted EM expected-crossing metric was
computed under the tilted training posterior, not under the deployed serialized
SentencePiece Viterbi path.

We therefore added two probes:

```text
1. deployed SP Viterbi crossing audit
2. teacher-distilled SP score probe
```

These probes ask whether context-free global Unigram scores can carry the
Turkish morphology teacher signal.

## New Scripts

```text
scripts/audit_v2_deployed_sp_crossings.py
scripts/materialize_v2_teacher_distilled_sp_model.py
```

Tests:

```text
tests/test_v2_deployed_sp_crossings.py
tests/test_v2_teacher_distilled_sp_model.py
```

Targeted test result:

```text
4 passed
```

## Probe 1: Deployed Viterbi Crossing, EM 2k

Report:

```text
artifacts/v2_0_deployed_sp_crossing_audit_challenge_em2k.md
```

| Model | Crossed boundaries | Crossed boundary rate | Pieces/word |
| --- | ---: | ---: | ---: |
| SP64 | 170/305 | 0.557377 | 1.9060 |
| EM lambda 0 2k | 157/305 | 0.514754 | 1.9373 |
| EM lambda 1 2k | 157/305 | 0.514754 | 1.9373 |
| EM lambda 2 2k | 157/305 | 0.514754 | 1.9373 |
| EM lambda 4 2k | 157/305 | 0.514754 | 1.9399 |

Interpretation:

```text
EM projection slightly changes deployed Viterbi versus SP64, but lambda does
not create a useful curve. The training-time boundary penalty is not surviving
as a controllable deployed-path preference in the current score-only form.
```

Attribution:

```text
For EM rows, about 96.8% of crossed boundaries come from pieces that cross in
100% of their eval occurrences.
```

This is not diffuse medium-rate damage; the remaining damage is concentrated in
high-rate crossing pieces.

## Probe 2: Teacher-Distilled Score Bound, 2k Train Lines

Materialization:

```text
artifacts/v2_0_teacher_distilled_sp_2000lines_materialization.md
```

Model:

```text
artifacts/private/v2_0_teacher_distilled_sp/teacher_distilled_2000lines_unigram_64000.model
```

Training materialization:

```text
lines: 2000
segments: 343822
skipped segments: 0
counted tokens: 521014
counted piece types: 27754
missing piece tokens: 0
changed scores: 63997
```

Challenge CI:

```text
artifacts/v2_0_teacher_distilled_sp_2000lines_ci.md
```

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 2.2010 | 0.6755 | 2.2977 |
| teacher-distilled 2k | 0.7447 | 2.5065 | 0.7179 | 2.5927 |

Gold CI:

```text
artifacts/v2_0_teacher_distilled_sp_2000lines_ci_gold.md
```

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7551 | 2.5041 | 0.7314 | 2.5868 |
| teacher-distilled 2k | 0.7952 | 2.9256 | 0.7896 | 3.0000 |

Interpretation:

```text
Teacher-distilled global scores reduce crossings and improve some F1, but the
improvement is not near the SP64 vocab oracle ceiling on challenge.

The cost is substantial token pressure.
```

## Deployed Crossing, Teacher-Distilled 2k

Challenge:

```text
artifacts/v2_0_deployed_sp_crossing_audit_challenge_teacher_distilled.md
```

| Model | Crossed boundaries | Crossed boundary rate | Pieces/word |
| --- | ---: | ---: | ---: |
| SP64 | 170/305 | 0.557377 | 1.9060 |
| teacher-distilled 2k | 119/305 | 0.390164 | 2.2010 |

Gold:

```text
artifacts/v2_0_deployed_sp_crossing_audit_gold_teacher_distilled.md
```

| Model | Crossed boundaries | Crossed boundary rate | Pieces/word |
| --- | ---: | ---: | ---: |
| SP64 | 79/153 | 0.516340 | 2.2231 |
| teacher-distilled 2k | 50/153 | 0.326797 | 2.6364 |

Attribution:

```text
Challenge teacher-distilled:
  79.0% of crossed boundaries are in 1.00-rate pieces
  94.96% are in >=0.70-rate pieces

Gold teacher-distilled:
  96.0% are in 1.00-rate pieces
```

## Decision Reading

Fable5's proposed kill criterion was:

```text
distilled F1 < 0.76 and < 50% of crossings attributable to pieces with
crossing rate > 0.7 kills all context-free work permanently
```

Our 2k result:

```text
distilled Challenge F1: 0.7447
crossing share from >0.7-rate pieces: about 95%
```

Therefore:

```text
score-only global Unigram looks weak
but context-free inventory/pruning is not killed by this criterion
```

The most defensible next local step is not another EM lambda sweep. It is either:

```text
1. run the same teacher-distilled bound on the full 16k train split to confirm
   whether 2k underestimates the score-space bound
2. if full bound remains low, try a targeted high-rate crossing-piece pruning /
   inventory experiment
```

## Current Recommendation

Do not run tiny-LM yet.

Do not return to low-lambda EM sweeps.

Run full 16k teacher-distilled score bound if runtime is acceptable. If it still
lands below about 0.76 Challenge F1 while crossings remain concentrated in
high-rate pieces, move to targeted inventory/pruning rather than MorphBPE or
another score-only EM sweep.

## Full 16k Teacher-Distilled Bound

The full train split bound was run after the 2k probe.

Materialization:

```text
artifacts/v2_0_teacher_distilled_sp_16000lines_materialization.md
```

Model:

```text
artifacts/private/v2_0_teacher_distilled_sp/teacher_distilled_16000lines_unigram_64000.model
```

Training materialization:

```text
lines: 16000
segments: 2854463
skipped segments: 0
counted tokens: 4313410
counted piece types: 53493
missing piece tokens: 0
changed scores: 63997
```

Challenge CI:

```text
artifacts/v2_0_teacher_distilled_sp_16000lines_ci.md
```

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 2.2010 | 0.6755 | 2.2977 |
| teacher-distilled 16k | 0.7509 | 2.3525 | 0.7219 | 2.4413 |

Deployed crossing:

```text
artifacts/v2_0_deployed_sp_crossing_audit_challenge_teacher_distilled_16k.md
```

| Model | Crossed boundaries | Crossed boundary rate | Pieces/word |
| --- | ---: | ---: | ---: |
| SP64 | 170/305 | 0.557377 | 1.9060 |
| teacher-distilled 16k | 139/305 | 0.455738 | 2.0548 |

Attribution:

```text
teacher-distilled 16k:
  86.33% of crossed boundaries are from 1.00-rate pieces
  94.96% are from >=0.70-rate pieces
```

Updated reading:

```text
Full-data score distillation is more efficient than 2k distillation, but it
still does not approach the SP64 vocabulary oracle ceiling on challenge.

This weakens score-only Unigram further.

However, remaining crossing damage is still highly concentrated in high-rate
pieces, so a targeted inventory/pruning probe remains justified.
```

Updated recommendation:

```text
Do not run more score-only EM or teacher-distillation sweeps.
Do not run tiny-LM.
Run one targeted high-rate crossing-piece pruning/flooring probe.
```

## Targeted High-Rate Crossing-Piece Pruning

Follow-up findings:

```text
docs/v2_0_pruned_sp_probe_findings.md
```

New script:

```text
scripts/materialize_v2_pruned_sp_model.py
```

The pruning probe used train-side crossing statistics only:

```text
artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json
```

### Aggressive All-Scope Pruning

Policy:

```text
crossing_rate >= 0.70
min_count >= 20
min_crossing_count >= 20
piece_scope = all
score_floor = -30
selected pieces = 4329
```

Result:

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word | Crossed boundaries |
| --- | ---: | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 2.2010 | 0.6755 | 2.2977 | 170/305 |
| pruned_ge070_all | 0.7447 | 2.3525 | 0.6582 | 2.4491 | 139/305 |

Reading:

```text
This is too blunt. It reduces crossings but hurts the finite-wrapper row,
probably because it floors many high-frequency word-start/full-word pieces.
```

### Non-Word-Start Pruning

Policy:

```text
crossing_rate >= 0.70
min_count >= 20
min_crossing_count >= 20
piece_scope = non_word_start
score_floor = -30
selected pieces = 403
```

Result:

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word | Crossed boundaries |
| --- | ---: | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 2.2010 | 0.6755 | 2.2977 | 170/305 |
| pruned_ge070_nonword | 0.7486 | 2.2611 | 0.6875 | 2.3577 | 151/305 |

Reading:

```text
This is the best small inventory probe so far, but still not enough to unblock
tiny-LM. The improvement is small and still near the visible-eval noise band.
```

Updated recommendation:

```text
Do not promote pruning yet.
Do not run tiny-LM.
If continuing, run only a small predeclared non-word-start threshold sweep:
  - crossing_rate >= 0.90
  - crossing_rate = 1.00
  - crossing_rate >= 0.70 with min_count >= 50
  - optional score_floor -20 vs -30
Then ask advisor review before any heavier custom objective.
```

## Fable5 Correction And Closing Measurements

Fable5 corrected our attribution reading:

```text
eval-side 1.00 crossing-rate is unreliable because many eval pieces occur once
or twice
```

We added a train-side attribution and score-source audit:

```text
script: scripts/audit_v2_eval_crossing_piece_sources.py
challenge report: artifacts/v2_0_eval_crossing_piece_source_audit_challenge.md
gold report: artifacts/v2_0_eval_crossing_piece_source_audit_gold.md
triage: docs/advisor_feedback_v2_0_distilled_score_bound_triage.md
```

Challenge train-side attribution:

| Model | Crossed boundaries | Reliable train-rate >=0.70 share | Train-count <20 share |
| --- | ---: | ---: | ---: |
| SP64 | 170/305 | 0.4471 | 0.4412 |
| teacher-distilled 16k | 139/305 | 0.3165 | 0.3453 |
| pruned_ge070_nonword | 151/305 | 0.2980 | 0.5563 |

Score-source audit:

```text
teacher-distilled 16k challenge:
  137/139 crossed boundaries came from counted-score pieces
  2/139 came from floor-score pieces

teacher-distilled 16k gold:
  55/55 crossed boundaries came from counted-score pieces
```

Interpretation:

```text
The teacher-distilled bound is mechanically valid.
The remaining damage is not mostly a serialization/floor-score bug.
The context-free global-score/inventory family is close to its practical limit.
```

Gold 16k bound:

```text
report: artifacts/v2_0_teacher_distilled_sp_16000lines_ci_gold.md
```

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7551 | 2.5041 | 0.7314 | 2.5868 |
| teacher-distilled 16k | 0.8042 | 2.7686 | 0.8129 | 2.8430 |

Closing pruning sweep:

```text
artifacts/v2_0_pruned_sp_closing_sweep_ci_challenge.md
artifacts/v2_0_pruned_sp_closing_sweep_ci_gold.md
artifacts/v2_0_pruned_sp_closing_sweep_crossing_sources_challenge.md
```

The three extra pruning cells did not materially beat
`pruned_ge070_nonword`. This closes simple high-rate pruning.

Wrapper-tax contrast:

```text
artifacts/v2_0_finite_wrapper_eval_tax_challenge_pruned_ge070_all.md
artifacts/v2_0_finite_wrapper_eval_tax_challenge_pruned_ge070_nonword.md
artifacts/v2_0_finite_wrapper_eval_tax_challenge_teacher_distilled_16k.md
```

| Model | Bare F1 | Finite F1 | Tax |
| --- | ---: | ---: | ---: |
| SP64 | 0.7351 | 0.6755 | -0.0596 |
| pruned_ge070_all | 0.7447 | 0.6582 | -0.0865 |
| pruned_ge070_nonword | 0.7486 | 0.6875 | -0.0611 |
| teacher-distilled 16k | 0.7509 | 0.7219 | -0.0290 |

Updated recommendation:

```text
Do not continue score-only EM/distillation.
Do not continue high-rate pruning sweeps.
Do not start MorphBPE yet.
Build the consolidated four-model frontier table and use it for one fixed-byte
tiny-LM calibration if budget allows.
In parallel, audit/redesign wrapper routes because finite F1 is strongly
wrapper-dependent.
```
