# v2.0 Expanded UDS22 Findings

Date: 2026-06-10

## Summary

The expanded 22-symbol UDS probe failed the token-pressure gate.

Report:

```text
artifacts/v2_0_expanded_uds22_sentencepiece_probe.md
```

## Token Pressure

| Candidate | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| SP64 reference | 0.159020 | 0.159620 |
| safe UDS7 | 0.159109 | 0.159684 |
| expanded UDS22 | 0.183675 | 0.184059 |
| finite protected SP64 floor | 0.182112 | 0.183362 |
| suffix_chain2 marker branch | 0.184500 | 0.185337 |

The expanded UDS22 candidate jumped from the safe UDS compression band into the
finite-protected/marker-branch pressure band.

## Interpretation

The 7-symbol UDS result showed that carefully selected user-defined suffix
pieces can add a morphology prior almost for free.

The 22-symbol expansion shows the limit of this simple approach: forcing more
suffixes as UDS starts acting like a hard segmentation policy and increases
token count substantially.

Because token pressure failed before intrinsic evaluation, we did not run
finite-protected intrinsic eval for this candidate.

## Decision

Stop UDS expansion at this point.

Keep the 7-symbol safe UDS result as the best cheap structural morphology prior
observed so far, but do not broaden UDS by train-statistics thresholds alone.

Next work should move to a constrained/MorphBPE-style objective or another
learned mechanism that can use morphology as a soft preference without forcing
many suffix surfaces as hard user-defined symbols.
