# Advisor Update: Deployed Crossing + Teacher-Distilled Score Bound

Date: 2026-06-10

## Context

You warned that our expected-crossing metric under boundary-weighted EM was
computed under the tilted training posterior, not the deployed serialized
SentencePiece Viterbi path.

We accepted that critique and added the two probes you requested:

```text
1. deployed Viterbi crossing audit
2. teacher-distilled score probe
```

## Probe 1: Deployed Viterbi Crossing For EM 2k Models

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

Reading:

```text
EM projection changes the deployed path slightly versus SP64, but lambda
does not create a useful deployed-crossing curve.
```

Attribution:

```text
For EM rows, ~96.8% of crossed boundaries come from pieces that cross in 100%
of their eval occurrences.
```

## Probe 2: Teacher-Distilled Score Bound, 2k Train Lines

Materialization:

```text
artifacts/v2_0_teacher_distilled_sp_2000lines_materialization.md
```

Training stats:

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

Deployed crossing:

```text
artifacts/v2_0_deployed_sp_crossing_audit_challenge_teacher_distilled.md
artifacts/v2_0_deployed_sp_crossing_audit_gold_teacher_distilled.md
```

| Dataset | Model | Crossed boundaries | Crossed boundary rate | Pieces/word |
| --- | --- | ---: | ---: | ---: |
| challenge | SP64 | 170/305 | 0.557377 | 1.9060 |
| challenge | teacher-distilled 2k | 119/305 | 0.390164 | 2.2010 |
| gold | SP64 | 79/153 | 0.516340 | 2.2231 |
| gold | teacher-distilled 2k | 50/153 | 0.326797 | 2.6364 |

Attribution:

```text
Challenge teacher-distilled:
  ~79.0% of crossed boundaries are from 1.00-rate pieces
  ~94.96% are from >=0.70-rate pieces

Gold teacher-distilled:
  ~96.0% are from 1.00-rate pieces
```

## Current Reading

Your warning was correct:

```text
the tilted posterior metric was not enough
```

The deployed crossing audit shows:

```text
EM score projection slightly reduces crossings, but lambda does not matter
after projection
```

The teacher-distilled bound shows:

```text
global score-space over fixed SP64 vocab is not jumping toward 0.80+ on
challenge at 2k lines
```

But attribution does **not** look diffuse:

```text
remaining crossing damage is concentrated in high-rate crossing pieces
```

So we are reading this as:

```text
score-only Unigram is weak
targeted inventory/pruning may still have headroom
context-free work is not killed by your stated criterion, because high-rate
crossing attribution is well above 50%
```

## Questions

Please be critical.

1. Is 2k teacher-distilled enough to interpret the score-space bound, or should
   we run the full 16k train split before deciding?

2. Given:

```text
distilled Challenge F1 = 0.7447
distilled deployed crossing rate = 0.390164
crossing attribution >=0.70-rate share ~95%
```

would you proceed to targeted high-rate crossing-piece pruning/inventory
shaping, or still stop context-free work?

3. If pruning/inventory is the next step, what exact first probe would you run?

Possible options:

```text
A. remove or floor pieces with eval/train crossing rate >=0.7 and count >=N
B. remove only full-word high-crossing pieces, keep suffix fragments
C. retrain candidate inventory from teacher no-cross paths
D. tilted full Unigram training where boundary penalty affects pruning/survival
E. constrained MorphBPE despite your warning
```

4. Should we treat the finite-wrapper F1 gain in the distilled model
(`0.6755 -> 0.7179`) as meaningful, or mostly as a side-effect of higher token
pressure and wrapper behavior?

5. Would any of these rows justify a tiny-LM calibration now?

Our current answer is still no, unless you think the crossing reduction itself
has LM value independent of visible F1.

## Current Internal Recommendation

```text
Do not run tiny-LM.
Do not continue low-lambda EM.
Run full 16k teacher-distilled bound if advisor agrees 2k may understate score
space.
If full bound remains <~0.76 challenge F1 and high-rate attribution stays
concentrated, try one targeted high-rate crossing-piece pruning/inventory
probe before abandoning context-free inventory work.
```

## Addendum: Full 16k Teacher-Distilled Bound

After preparing the update above, we ran the full 16k train split.

Materialization:

```text
artifacts/v2_0_teacher_distilled_sp_16000lines_materialization.md
```

Training stats:

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

Updated internal reading:

```text
Full-data score distillation remains below the ~0.76 challenge-F1 threshold
and far below the oracle ceiling, so score-only Unigram is weak.

But the remaining crossing damage is concentrated in high-rate pieces, so one
targeted high-rate crossing-piece pruning/flooring probe is still justified.
```

Updated question:

```text
Would you now run that pruning/flooring probe, and if yes should it target:
  A. all >=0.70-rate crossing pieces
  B. only 1.00-rate pieces
  C. only full-word high-crossing pieces
  D. only suffix-like high-crossing pieces
  E. train-side high-crossing pieces rather than eval-side high-crossing pieces
```

## Addendum: First Targeted Pruning Probe Results

We ran the first pruning/flooring probe using **train-side** crossing
statistics, not eval-side selection:

```text
stats: artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json
script: scripts/materialize_v2_pruned_sp_model.py
findings: docs/v2_0_pruned_sp_probe_findings.md
```

### Probe A: All High-Rate Pieces

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
All-scope pruning reduces crossings but is too blunt; finite-wrapper F1 gets
worse.
```

### Probe B: Non-Word-Start High-Rate Pieces

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
This is the best small inventory result so far:
  - small F1 lift
  - modest token cost
  - finite-wrapper row does not collapse

But it is still not a large enough move to justify tiny-LM.
```

Remaining crossing attribution after non-word pruning:

```text
about 96% of remaining crossed boundaries still come from 1.00-rate pieces
```

## New Questions

Please be critical.

1. Does `pruned_ge070_nonword` justify a small predeclared threshold sweep, or
   should we stop pruning/inventory work now?

2. If you would run one sweep, which exact cells would you choose?

Current candidate cells:

```text
non_word_start, crossing_rate >= 0.90, min_count >= 20, floor -30
non_word_start, crossing_rate = 1.00, min_count >= 20, floor -30
non_word_start, crossing_rate >= 0.70, min_count >= 50, floor -30
non_word_start, crossing_rate >= 0.70, min_count >= 20, floor -20
```

3. Should we avoid flooring full-word / word-start pieces entirely, given the
   finite-wrapper regression in the all-scope probe?

4. Does the fact that remaining damage is still mostly 1.00-rate after
   non-word pruning mean:

```text
A. keep pruning with stricter/high-confidence suffix-like filters
B. build a new inventory from teacher no-cross paths
C. pivot to constrained MorphBPE
D. accept that SP64-like context-free inventory is near its practical limit
```

5. What evidence would now be enough to unblock tiny-LM?

Our current internal answer:

```text
not yet; we need a row that clears visible CI noise or gives a much better
tokens/F1 frontier than pruned_ge070_nonword.
```
