# v2.0 Marker-Stripped Soft-Marker Findings

Date: 2026-06-03

## Status

```text
Exp 0 mechanism check complete
not a final tokenizer candidate
not an LLM handoff recommendation
```

Report:

```text
artifacts/v2_0_marker_stripped_soft_marker_diagnostic.md
```

## Question

The advisors asked whether the token-pressure cost of the all-soft marker
candidate comes mainly from emitting markers in the encode-time token stream.

Diagnostic:

```text
use the all-soft-marker-trained Unigram model
do not insert SOFT_MARKER into normal text at encode time
keep finite protected encoder unchanged
```

## Token Pressure

| Model | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| SP64 | 0.159020 | 0.159620 |
| all-soft in-stream marker | 0.251658 | 0.252212 |
| marker-stripped soft model | 0.195611 | 0.196236 |

Interpretation:

```text
marker-stripping removes most of the token-pressure penalty
the result meets the preferred <=0.20 token-pressure target
the in-stream marker cost is real and large
```

## Intrinsic Quality

Challenge:

| Model | Challenge F1 | Exact |
| --- | ---: | ---: |
| custom deterministic | 0.9220 | 44/108 |
| SP64 | 0.7351 | 0/108 |
| all-soft in-stream marker | 0.8259 | 0/108 |
| marker-stripped soft model | 0.7703 | 0/108 |

Protected stress:

| Model | Protected preserved |
| --- | ---: |
| custom deterministic | 25/25 |
| SP64 | 1/25 |
| marker-stripped soft model | 25/25 |

Interpretation:

```text
marker-stripped model remains above SP64 on visible challenge F1
the margin is only +0.0352, below the preferred +0.045 to +0.05 gate
it also falls below the 0.78-0.80 target
protected routing remains solved
```

## Decision

```text
do not return to the all-soft in-stream marker candidate
do not run tiny-LM for marker-stripped yet
do prioritize train-only vocab shaping / constrained Unigram style experiments
```

The marker-stripped result shows that morphology can shape the learned
vocabulary with much lower token pressure, but the current all-soft training
view does not preserve enough boundary signal after markers are stripped.

## Next Direction

Run a train-only vocab-shaping sweep:

```text
markers are allowed in the tokenizer training view
markers are not inserted at encode time
finite protected encoder remains frozen
```

Candidate priority functions:

```text
suffix-chain-depth budget sweep
high-value-suffix budget sweep
all-soft stripped baseline
raw/no-marker control
```

Go criteria before any tiny-LM:

```text
valid/test tokens/raw byte <= 0.20 preferred, <= 0.22 max
challenge F1 >= SP64 + 0.045 preferred
protected stress = 25/25
```

Stop marker-stripped/vocab-shaping path if:

```text
no training-view policy reaches the F1 gate while staying <=0.22 tokens/raw byte
```

