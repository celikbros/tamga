# Advisor Follow-Up: Boundary-Weighted Unigram/EM Result

Date: 2026-06-10

## Context

We are building a Turkish-primary tokenizer research prototype for future LLM
work.

Current architecture direction:

```text
finite protected routing
+ learned tokenizer for normal text
+ Turkish morphology teacher as a soft prior
+ lossless fallback
```

Recent closed branches:

```text
seed appendix
stock SentencePiece partial-boundary delimiter
post-hoc score shift
marker-dose policies
broad UDS expansion
runtime boundary-biased decoder as a candidate
```

Reason for the current experiment:

```text
SP64 vocabulary oracle showed that the existing SP64 vocab can express much
more morphology-aligned paths, but shallow post-hoc score shifting did not move
the deployed SentencePiece path.
```

So we built the smallest boundary-weighted Unigram/EM prototype.

## Prototype

Script:

```text
scripts/materialize_v2_boundary_weighted_unigram_em.py
```

Sweep runner:

```text
scripts/run_v2_boundary_weighted_unigram_em_sweep.py
```

Objective:

```text
path_weight(z) = P_unigram(z | theta) * exp(-lambda * crossings(z))
```

Where:

```text
crossings(z) = number of custom-teacher soft morphology boundaries crossed by
candidate pieces in the segmentation path
```

Implementation:

```text
SP64 candidate vocab + initial scores
per-normal-segment lattice
forward-backward with boundary penalty
expected piece counts
score update from expected counts
serialize adjusted .model
```

Tests:

```text
tests/test_v2_boundary_weighted_unigram_em.py
tests/test_v2_boundary_weighted_unigram_em_sweep.py
latest targeted result: 9 passed
```

## 2k One-Iteration Sweep

Command:

```powershell
python scripts\run_v2_boundary_weighted_unigram_em_sweep.py `
  --lambdas 0,1,2,4 `
  --iterations 1 `
  --max-lines 2000 `
  --progress 500 `
  --ci-samples 1000
```

All runs:

```text
lines: 2000
segments: 343822
skipped segments: 0
expected piece types: 40686
```

CI report:

```text
artifacts/v2_0_boundary_weighted_unigram_em_2000lines_ci.md
```

| Model | Bare Challenge F1 | Bare avg tokens/word | Finite Challenge F1 | Finite avg tokens/word |
| --- | ---: | ---: | ---: | ---: |
| lambda 0 | 0.7383 | 2.2402 | 0.6767 | 2.3368 |
| lambda 1 | 0.7396 | 2.2402 | 0.6780 | 2.3368 |
| lambda 2 | 0.7396 | 2.2402 | 0.6780 | 2.3368 |
| lambda 4 | 0.7391 | 2.2428 | 0.6802 | 2.3394 |

Interpretation:

```text
lambda 1/2/4 are flat versus lambda 0.
All F1 changes are inside the visible-eval CI noise floor.
```

## Expected Crossing Diagnostic

We added a training-lattice expected crossing metric after the 2k sweep.

100-line diagnostic:

| Lambda | Avg expected crossings/segment | Bare Challenge F1 | Bare avg tokens/word |
| ---: | ---: | ---: | ---: |
| 0 | 0.282770 | 0.7392 | 2.3133 |
| 4 | 0.256630 | 0.7308 | 2.3107 |
| 16 | 0.018998 | 0.7410 | 2.4230 |

Interpretation:

```text
The boundary penalty is mechanically active.

Low lambda reduces expected crossings only mildly and does not move eval.
High lambda sharply reduces expected crossings but increases token pressure and
still does not produce a clear visible F1 gain in the 100-line smoke.
```

## Current Honest Reading

This branch is mechanically valid:

```text
full lattice coverage
loadable SP model output
expected crossings respond to lambda
```

But transfer is weak:

```text
2k lambda curve is flat
high lambda looks like it will buy boundary compliance by token pressure rather
than by a clean frontier shift
```

This resembles the score-shift failure:

```text
SP64 has better morphology-compatible paths available, but shallow probability
reshaping does not reliably select them.
```

## Questions

Please be critical.

1. Is this enough evidence to stop the current shallow boundary-weighted
   Unigram-score branch?

2. Would you run one more EM experiment before stopping? If yes, which one?

Options:

```text
A. 2k or 5k lambda 8/16 with 1 iteration
B. 2k lambda 4/8/16 with 2-3 iterations
C. add aligned-piece reward in addition to crossing penalty
D. prune or heavily downweight high-crossing full-word pieces
E. train a new candidate inventory instead of only rescore SP64 vocab
F. stop and pivot to constrained MorphBPE / merge objective
```

3. Does the lambda16 diagnostic suggest the mechanism can work if made stronger,
   or does it mostly confirm the known hard-constraint tradeoff: better boundary
   behavior costs too much token pressure?

4. Should the next objective be:

```text
boundary-weighted Unigram with reward/pruning
constrained or penalized BPE/MorphBPE
runtime reranker made lossless
something else
```

5. Are we over-reading visible Challenge F1 here?

Current plan is not to run tiny-LM unless an intrinsic frontier moves beyond
the CI noise floor. Is that still correct, or would you now use tiny-LM to test
whether the flat F1 rows have any BPB value?

6. What would you do in the next one week if this were your tokenizer project?

Please give:

```text
smallest useful next experiment
stop criterion
success criterion
what report/artifact would convince you
```

## Current Internal Recommendation

Our current recommendation is:

```text
Do not run tiny-LM on the current EM models.
Do not blindly scale to 5k/multi-iteration.
Pause this EM branch as weak transfer.
Ask whether to try aligned-piece reward/pruning or pivot to constrained
MorphBPE where boundary-crossing merge decisions are explicit.
```
