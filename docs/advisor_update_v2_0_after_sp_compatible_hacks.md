# Advisor Update: After SP-Compatible Morphology Prior Attempts

Date: 2026-06-10

## Context

We are building a Turkish-primary tokenizer research prototype for future LLM
work. The current architecture direction is:

```text
finite protected routing
+ learned tokenizer for normal text
+ Turkish morphology teacher as a soft prior
+ lossless fallback
```

We previously demoted the runtime boundary-biased decoder because it failed
exact roundtrip, even though it had promising 300-step BPB diagnostics.

We then repaired the finite protected wrapper:

```text
valid exact roundtrip: 1994/1994
test exact roundtrip: 1998/1998
protected stress: 25/25
```

The active protected baseline is therefore valid again, but it is not a
morphology-improving tokenizer:

```text
repaired finite protected numeric-SP floor Challenge F1: ~0.6755
```

## Stock SentencePiece Partial-Boundary Attempt

We tried standard SentencePiece `pretokenization_delimiter` using U+E000.

Mechanism:

```text
insert delimiter at custom soft morphology boundaries in a fraction rho of
train lines
train ordinary SP Unigram 64k
encode valid/test text without markers
wrap with finite protected routing
```

Results:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Bare Challenge F1 | Finite-protected Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | ---: | --- |
| SP64 reference | 0.159020 | 0.159620 | ~0.7351 | n/a | 1/25 |
| repaired finite protected numeric-SP floor | ~0.162866 | ~0.163779 | n/a | 0.6755 | 25/25 |
| partial boundary rho=0.10 | 0.158404 | 0.159029 | 0.7361 | 0.6750 | 25/25 |
| partial boundary rho=0.25 | 0.158458 | 0.159060 | 0.7380 | 0.6782 | 25/25 |
| partial boundary rho=0.50 | 0.158676 | 0.159231 | 0.7361 | 0.6777 | 25/25 |

Decision:

```text
Close stock SP partial-boundary pretokenization.
It is compression-safe but does not transfer a meaningful morphology signal.
```

## Post-Hoc Score-Shift Attempt

We then tried a lighter SP-compatible approximation of a boundary-weighted
Unigram objective.

Mechanism:

```text
use train split only
observe official SP64 pieces that cross custom-teacher soft morphology
boundaries
lower scores for high-crossing pieces in the SP64 .model
keep the same vocabulary and standard SentencePiece encode/decode path
```

First probe:

```text
penalty_lambda: 0.5
min_count: 20
min_crossing_rate: 0.50
min_surface_len: 2
max_penalty: 2.0
adjusted pieces: 4878
alignment failures: 0
```

Result:

| Candidate | Bare Challenge F1 | Finite-protected Challenge F1 |
| --- | ---: | ---: |
| score-shift lambda=0.5 | 0.7364 | 0.6768 |

Decision:

```text
Do not run tiny-LM on this candidate.
At lambda=0.5, post-hoc score shifting is also too weak.
```

## Current Interpretation

The following low-complexity mechanisms have now failed to move the frontier:

```text
seed appendix
stock SP partial-boundary delimiter
small post-hoc score shift
marker-dose policies improve F1 but do not pay for their token/BPB cost
broad UDS quickly becomes hard segmentation
runtime boundary-biased decode is diagnostic but not lossless
```

The surviving interpretation is:

```text
The morphology prior probably must enter the learned objective more directly,
not as an external marker dose, appendix, broad UDS, or shallow score patch.
```

## Questions

Please be critical.

1. Are we right to close the stock SP partial-boundary branch after rho
   0.10/0.25/0.50?

2. Should we run a stronger cached post-hoc score-shift sweep
   (`lambda=1,2,4`) before abandoning score-shift, or is the lambda=0.5 result
   enough to classify it as a weak approximation?

3. If score-shift is worth one more sweep, what should be varied?

```text
penalty lambda
min crossing rate
piece count threshold
separate penalties for full-word pieces vs suffix pieces
reward aligned morph pieces in addition to penalizing crossing pieces
```

4. If you would stop SP-compatible hacks now, what is the smallest real
   objective to implement next?

Options:

```text
A. boundary-weighted Unigram trainer / EM variant
B. constrained or penalized BPE merge trainer
C. reranking lattice decoder that is made byte-exact/lossless
D. hybrid: train ordinary SP, then train a small deterministic finite protected
   + morph reranker only for Turkish normal words
E. something else
```

5. What is the correct success gate for the next branch?

Current proposed gate:

```text
exact roundtrip on valid/test
protected stress 25/25
test tokens/raw byte near repaired finite floor, ideally <= 0.17
finite-protected Challenge F1 materially above 0.6755 and preferably above
0.72 without visible overfitting
no tiny-LM until the intrinsic frontier moves
```

Is this too strict, too weak, or mis-specified?

6. What hidden failure mode should we be most afraid of now?

```text
teacher morphology brittleness
visible challenge overfitting
wrong protected-wrapper abstraction
SP64 vocabulary already near optimal for LM despite low morphology F1
small pilot corpus too narrow
custom objective not producing a standard deployable artifact
```

7. If this were your project, what would you build in the next one week?

Please give:

```text
smallest useful experiment
stop criteria
success criteria
what report/artifact would convince you
```
