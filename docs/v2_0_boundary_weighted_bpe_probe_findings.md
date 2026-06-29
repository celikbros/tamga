# v2.0 Boundary-Weighted BPE Probe Findings

Date: 2026-06-10

## Purpose

After demoting the runtime boundary-biased decoder, we need a training-time
objective direction.

This probe implements a small toy BPE trainer whose merge score is:

```text
score(pair) = pair_count - lambda * morph_boundary_crossing_count
```

It is a research prototype only. It does not produce a production tokenizer or
a SentencePiece `.model`.

## Files

Implementation:

```text
src/tr_tokenizer/boundary_weighted_bpe.py
scripts/run_v2_boundary_weighted_bpe_probe.py
tests/test_boundary_weighted_bpe.py
```

Smoke report:

```text
artifacts/v2_0_boundary_weighted_bpe_probe_smoke_small.md
```

Private smoke models:

```text
artifacts/private/v2_0_boundary_weighted_bpe_smoke_small/
```

## Smoke Setup

```text
train lines: 100
vocab size: 120
lambdas: 0, 4, 8
```

This is deliberately tiny so we can verify the mechanism before spending time
on a larger run.

## Smoke Result

Challenge:

| Model | Avg tokens/word | Boundary F1 | Merges | Crossing merges |
| --- | ---: | ---: | ---: | ---: |
| lambda 0 | 5.4856 | 0.5431 | 42 | 20 |
| lambda 4 | 5.5587 | 0.5406 | 42 | 17 |
| lambda 8 | 5.6214 | 0.5507 | 42 | 17 |

Gold:

| Model | Avg tokens/word | Boundary F1 | Merges | Crossing merges |
| --- | ---: | ---: | ---: | ---: |
| lambda 0 | 5.9752 | 0.5424 | 42 | 20 |
| lambda 4 | 6.1240 | 0.5427 | 42 | 17 |
| lambda 8 | 6.3058 | 0.5508 | 42 | 17 |

## Interpretation

The mechanism is wired correctly:

```text
boundary penalty reduces crossing merges
```

The quality signal is weak but in the expected direction at lambda 8:

```text
slightly higher morphology F1
slightly higher token pressure
```

This is not enough to claim success. It is enough to justify one better
engineering pass if we want to pursue a real training-time objective.

## Important Caveat

The prototype is slow at larger settings. A 500-line / 500-vocab smoke timed
out before completing all lambdas. This toy implementation is acceptable for
mechanism validation, but not for serious sweep scale.

## Decision

Continue the training-time objective direction, but do not over-invest in the
toy Python BPE trainer.

Next practical options:

```text
1. optimize the toy trainer enough for a 1k-line / 1k-vocab intrinsic sweep
2. prototype the same penalty inside a real trainer path
3. prepare an advisor request asking whether to implement boundary-weighted
   BPE first or boundary-weighted Unigram first
```

Current recommendation:

```text
use the toy BPE only as an objective sanity check
design the real v2.0 candidate as boundary-weighted Unigram or constrained
learned tokenizer with standard-ish encode/decode behavior
```
