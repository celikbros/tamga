# v2.0 Targeted High-Rate Crossing Piece Pruning Findings

Date: 2026-06-10

## Purpose

Fable5's deployed-crossing critique changed the question from:

```text
does the training posterior reduce expected crossings?
```

to:

```text
which pieces still cross teacher morphology boundaries in the deployed
SentencePiece Viterbi path?
```

The teacher-distilled score bound showed that global score-only Unigram is
weak, but it also showed that remaining crossing damage is highly concentrated
in high-rate crossing pieces. This justified one targeted inventory/pruning
probe before abandoning context-free inventory work.

## New Script

```text
scripts/materialize_v2_pruned_sp_model.py
```

Test:

```text
tests/test_v2_pruned_sp_model.py
```

The script floors selected SP64 pieces using train-side crossing statistics:

```text
artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json
```

This keeps selection challenge-blind.

## Probe 1: Aggressive All-Scope Pruning

Materialization:

```text
artifacts/v2_0_pruned_sp_highrate_ge070_all_floor_materialization.md
```

Model:

```text
artifacts/private/v2_0_pruned_sp/highrate_ge070_all_floor_unigram_64000.model
```

Policy:

```text
min_count: 20
min_crossing_count: 20
min_crossing_rate: 0.70
min_surface_len: 2
piece_scope: all
score_floor: -30
```

Selected pieces:

```text
4329
```

Challenge CI:

```text
artifacts/v2_0_pruned_sp_highrate_ge070_all_floor_ci.md
```

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 2.2010 | 0.6755 | 2.2977 |
| pruned_ge070_all | 0.7447 | 2.3525 | 0.6582 | 2.4491 |

Deployed crossing:

```text
artifacts/v2_0_deployed_sp_crossing_audit_challenge_pruned_ge070_all.md
```

| Model | Crossed boundaries | Crossed boundary rate | Pieces/word |
| --- | ---: | ---: | ---: |
| SP64 | 170/305 | 0.557377 | 1.9060 |
| pruned_ge070_all | 139/305 | 0.455738 | 2.0157 |

Reading:

```text
The all-scope prune reduces crossings, but it is too blunt. It floors many
high-frequency full-word pieces and worsens finite-wrapper F1.
```

Do not promote this branch.

## Probe 2: Non-Word-Start High-Rate Pruning

Materialization:

```text
artifacts/v2_0_pruned_sp_highrate_ge070_nonword_floor_materialization.md
```

Model:

```text
artifacts/private/v2_0_pruned_sp/highrate_ge070_nonword_floor_unigram_64000.model
```

Policy:

```text
min_count: 20
min_crossing_count: 20
min_crossing_rate: 0.70
min_surface_len: 2
piece_scope: non_word_start
score_floor: -30
```

Selected pieces:

```text
403
```

Challenge CI:

```text
artifacts/v2_0_pruned_sp_highrate_ge070_nonword_floor_ci.md
```

| Model | Bare F1 | Bare tokens/word | Finite F1 | Finite tokens/word |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.7351 | 2.2010 | 0.6755 | 2.2977 |
| pruned_ge070_nonword | 0.7486 | 2.2611 | 0.6875 | 2.3577 |

Deployed crossing:

```text
artifacts/v2_0_deployed_sp_crossing_audit_challenge_pruned_ge070_nonword.md
```

| Model | Crossed boundaries | Crossed boundary rate | Pieces/word |
| --- | ---: | ---: | ---: |
| SP64 | 170/305 | 0.557377 | 1.9060 |
| pruned_ge070_nonword | 151/305 | 0.495082 | 1.9556 |

Initial eval-side attribution after pruning looked concentrated in 1.00-rate
pieces. Fable5 pointed out that this was an eval small-denominator artifact.
We accepted the critique and added train-side attribution:

```text
script: scripts/audit_v2_eval_crossing_piece_sources.py
report: artifacts/v2_0_eval_crossing_piece_source_audit_challenge.md
```

Corrected attribution for `pruned_ge070_nonword`:

```text
reliable train-rate >=0.70 share: about 29.8%
train-count <20 share: about 55.6%
```

This means the remaining damage is mostly low-support/context-dependent, not a
clean train-identifiable high-rate tail.

Reading:

```text
This is the best small inventory probe so far:
  - modest token cost
  - small F1 lift
  - finite-wrapper F1 does not collapse

But the gain is still inside or near the visible-eval noise band. It is not
enough for tiny-LM or LLM handoff.
```

## Current Interpretation

Targeted inventory work was not dead before the corrected attribution, but the
closing sweep now shows that simple high-rate pruning is near its practical
limit.

The useful lesson is narrower:

```text
avoid broad full-word pruning
if pruning is continued, keep it suffix/internal-piece focused and train-side
```

Fable5 recommended a small predeclared threshold sweep as a closing
measurement:

```text
non_word_start, crossing_rate >= 0.90
non_word_start, crossing_rate = 1.00
non_word_start, crossing_rate >= 0.70 with min_count >= 50
```

That sweep has now been run.

Reports:

```text
artifacts/v2_0_pruned_sp_closing_sweep_ci_challenge.md
artifacts/v2_0_pruned_sp_closing_sweep_ci_gold.md
artifacts/v2_0_pruned_sp_closing_sweep_crossing_sources_challenge.md
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

The best pruning cell does not materially beat `pruned_ge070_nonword`; all
point-estimate differences remain inside or near the visible-eval noise band.

## Decision

Do not promote all-scope pruning.

Keep `pruned_ge070_nonword` and `teacher_distilled_16k` as diagnostic frontier
points only.

Do not run more pruning sweeps.

Simple context-free high-rate pruning is closed as a route to the goal.

The next useful work is:

```text
1. build a consolidated frontier table
2. calibrate BPB on the four-model ladder if budget allows
3. audit/redesign finite protected wrapper routes
```
