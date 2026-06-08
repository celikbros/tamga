# v2.0 Train-Only Marker Findings

Date: 2026-06-08

## Summary

Train-only marker shaping is the right mechanism direction, but the current
marker policies are not strong enough to justify another tiny-LM probe.

The key improvement is token pressure:

```text
all-soft in-stream markers:        test ~0.2522 tokens/raw byte
all-soft train-only marker model:  test ~0.1962 tokens/raw byte
suffix-chain2 train-only model:    test ~0.1846 tokens/raw byte
high-value suffix train-only model:test ~0.1911 tokens/raw byte
SP64 reference:                    test ~0.1596 tokens/raw byte
```

The problem is visible intrinsic strength:

```text
SP64 challenge F1:                 0.7351
all-soft train-only challenge F1:  0.7703
suffix-chain2 challenge F1:        0.7632
high-value suffix challenge F1:    0.7665
preferred gate: materially above SP64, ideally >= ~0.78-0.80
```

So the train-only approach is promising, but this exact policy family is still
below the preferred intrinsic gate.

## Frontier

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress | Decision |
| --- | ---: | ---: | ---: | --- | --- |
| SP64 reference | 0.159020 | 0.159620 | 0.7351 | 1/25 | null baseline |
| finite protected + SP64 | n/a | n/a | 0.6913 | 25/25 | true protected floor, but weaker F1 |
| all-soft train-only marker-stripped | 0.195611 | 0.196236 | 0.7703 | 25/25 | promising, but below preferred F1 gate |
| suffix-chain2 train-only marker-stripped | 0.183799 | 0.184619 | 0.7632 | 25/25 | best pressure, weaker F1 |
| high-value suffix train-only marker-stripped | 0.190346 | 0.191068 | 0.7665 | 25/25 | slightly better F1 than suffix-chain2, worse pressure |

## Follow-Up Controls

Marker vocab audit:

```text
report: artifacts/v2_0_sentencepiece_marker_vocab_audit.md
all train-only marker models learned only one marker-containing piece: the
standalone U+E000 marker
no marker+surface pieces were found
```

This reduces the risk that the marker-stripped results are caused by a large
unusable marker+surface vocabulary artifact.

Challenge F1 bootstrap CI:

```text
report: artifacts/v2_0_train_only_marker_frontier_ci.md
all-soft marker-stripped: 0.7703 [0.7326, 0.8046]
suffix-chain2: 0.7632 [0.7273, 0.7962]
high-value suffix: 0.7665 [0.7306, 0.7977]
```

The intervals overlap heavily. The apparent F1 ordering among train-only marker
policies should not be treated as reliable.

## Interpretation

The current frontier says:

```text
train-only marker shaping reduces token pressure enough to stay in the
candidate space, marker-vocab artifacts are not severe, but the visible F1
ranking is too noisy to justify more marker-dose tuning.
```

This is not a failure of the whole v2.0 direction. It narrows the search:

```text
keep finite protected routing
keep marker-free normal encode
avoid in-stream all-soft markers
look for a better learned prior than the current simple marker policies
```

## Next Decision

Do not run more marker-dose intrinsic variants.

The next useful step is either:

```text
1. run a calibrated BPB/tiny-LM probe on bracketing candidates to test whether
   boundary F1 predicts language-modeling value; or
2. switch to a genuinely different mechanism, e.g. selected suffix/morph seed
   vocabulary or curated morph pieces, instead of changing marker density.
```

Do not tune directly against visible challenge examples.
