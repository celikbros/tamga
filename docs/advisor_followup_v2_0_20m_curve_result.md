# Advisor Follow-Up: 20M Learning Curve Result

Date: 2026-06-12

## Context

You asked us not to trust the 2M endpoint and to run a healthier learning curve
with better accounting.

We did:

```text
SP64 protected floor
self_distilled_16000 matched non-morph control
teacher_distilled_16000 morphology-teacher score model
```

All rows use:

```text
same fixed SP64 vocabulary size: 64630
same finite protected wrapper
same tiny LM architecture
same approximately 20M raw bytes seen
```

## 20M Result

| Tokenizer | Test tokens/byte | Approx bytes seen | Valid BPB | Test BPB | Test bits/token |
| --- | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.164497 | 20,002,137 | 1.951192 | 1.962704 | 11.9316 |
| finite_protected_self_distilled_16000 | 0.164852 | 20,000,713 | 1.951182 | 1.963184 | 11.9088 |
| finite_protected_teacher_distilled_16000 | 0.177859 | 20,002,006 | 1.971752 | 1.983360 | 11.1513 |

Unigram baselines:

| Tokenizer | Test unigram BPB | 20M test BPB |
| --- | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 2.026952 | 1.962704 |
| finite_protected_self_distilled_16000 | 2.028322 | 1.963184 |
| finite_protected_teacher_distilled_16000 | 2.111869 | 1.983360 |

Health:

```text
log2(vocab): 15.9799
all rows are below the uniform reference at 20M
all rows beat their own zero-training unigram BPB baselines
```

## Curve Reading

At 2M:

```text
teacher_distilled_16000 looked best
```

At 20M:

```text
teacher_distilled_16000 loses on BPB
```

The teacher row still has much lower bits/token:

```text
SP64 floor: 11.9316
self_distilled_16000: 11.9088
teacher_distilled_16000: 11.1513
```

But its token pressure is too high:

```text
SP64 floor test tokens/byte: 0.164497
teacher_distilled_16000 test tokens/byte: 0.177859
```

So the static morphology-compliant score model does not produce a durable BPB
win in this healthier checkpoint.

## Current Decision

Our current decision:

```text
Do not promote teacher_distilled_16000 as a tokenizer candidate.
Do not build a broad lossless reranker just to reproduce this branch.
Keep finite_protected_sp64_numeric_sp_floor as the practical tokenizer floor.
Treat morphology as useful signal, but move it away from static tokenization
pressure unless a more selective mechanism is proposed.
```

## Questions

Please be critical.

1. Do you agree that this closes `teacher_distilled_16000` as a tokenizer
   candidate on BPB evidence?

2. Does the low bits/token but worse BPB imply:

```text
morphology helps predictability,
but the static tokenizer tax is too high
```

or is there another interpretation?

3. Should the next branch move morphology into:

```text
A. auxiliary LM training objective
B. morphology-aware data curriculum/filtering
C. selective tokenizer changes only for narrow suffix classes
D. route/wrapper improvements only
E. a more selective deployable objective/reranker
F. pause morphology-tokenizer work and consolidate SP64+finite
```

4. Before involving the LLM team, would you now recommend:

```text
SP64+finite as the tokenizer candidate
teacher_distilled_16000 as diagnostic evidence only
morphology as an optional auxiliary task/data signal
```

5. What is the smallest useful next experiment after this negative 20M
   tokenizer result?

## Our Proposed Next Step

Do not run more broad BPB sweeps.

Consolidate:

```text
finite_protected_sp64_numeric_sp_floor
```

as the current practical tokenizer baseline.

Use the teacher-distilled result to design a separate morphology auxiliary
experiment, not a new tokenizer branch, unless you see a selective tokenizer
mechanism that avoids the token-pressure tax.
