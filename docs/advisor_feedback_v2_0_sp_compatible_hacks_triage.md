# Advisor Feedback Triage: SP-Compatible Hacks

Date: 2026-06-10

## Advisor Takeaway

Fable5 agreed that the stock SentencePiece partial-boundary branch should be
closed, but warned that closing score-shift after only `lambda=0.5` is
premature.

Key correction:

```text
Before building a custom trainer, identify whether SP64 vocabulary already has
high-quality morphology-compatible paths.
```

## Accepted Decisions

Close:

```text
stock SP partial-boundary delimiter rho=0.10/0.25/0.50
```

Reason:

```text
compression stayed near SP64, but there was no monotonic or material F1 gain
```

Keep alive briefly:

```text
post-hoc score-shift
```

Reason:

```text
lambda=0.5 was only one weak point
score-shift yields a standard SentencePiece artifact
the sweep is cheap if crossing stats are cached
```

## New Diagnostic

Added:

```text
scripts/audit_v2_sp_vocab_oracle_ceiling.py
```

Challenge result:

| Mode | Avg tokens/word | Boundary F1 vs eval | Crossed teacher boundaries |
| --- | ---: | ---: | ---: |
| lambda0 | 2.0783 | 0.7422 | 171 |
| no_cross | 2.5509 | 0.8407 | 0 |
| oracle_best_f1 | 2.5457 | 0.8417 | 0 |

Interpretation:

```text
SP64 vocabulary is not the main ceiling. It can express much better
morphology-aligned paths, but the paths are longer. Score/objective work is
still justified before a full custom trainer.
```

Report:

```text
artifacts/v2_0_sp_vocab_oracle_ceiling_challenge.md
```

## Score-Shift Tool Update

Updated:

```text
scripts/materialize_v2_score_shifted_sp_model.py
```

New support:

```text
--stats-out / --stats-in
--penalty-mode rate|mass|hybrid
--min-crossing-count
```

This lets us run a real cached sweep without rescanning the train split for
each lambda.

## Next Step

Run one cached score-shift sweep before declaring score-side methods dead.

Suggested sweep:

```text
penalty_mode = mass
lambda = 1, 2, 4, 8
max_penalty high enough not to hide the sweep
min_crossing_rate = 0.0
min_crossing_count = 20
min_count = 20
```

Gate:

```text
If the best score-shift model stays near bare F1 ~0.735-0.74 while tokens/raw
byte rises toward 0.17, stop score-shift permanently and move to a real
boundary-weighted Unigram/EM objective.
```

## Additional Advisor Warnings

Do soon:

```text
bootstrap CIs / hidden split
wrapper-tax decomposition
one tiny-LM calibration only for the next valid winner
```

Do not:

```text
optimize endlessly on visible challenge
use finite-protected F1 as the development metric without separately tracking
wrapper tax
```
