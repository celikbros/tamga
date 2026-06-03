# v2.0 Selective Soft-Marker Plan

Date: 2026-06-03

## Why This Exists

The finite protected soft-marker candidate gave a useful but expensive signal:

```text
protected stress: 25/25
challenge boundary F1: 0.8259
valid/test tokens/raw byte: 0.251658 / 0.252212
same-step tiny-LM: SP64 wins
approx iso-byte tiny-LM: finite protected soft-marker wins
```

The result says:

```text
morphology/protection signal may help after equal raw-byte exposure
current all-soft-marker design is too token-expensive for LLM handoff
```

The next design iteration should reduce marker pressure before any broader LM
probe.

## Objective

Find a lower-pressure learned candidate that preserves the useful parts of:

```text
finite protected routing
soft morphology prior
stateless decode
SP64-like compression behavior
```

This is not a new morphology-rule project. It is a marker-budget project.

## Non-Goals

```text
do not add broad Turkish morphology rules
do not tune directly against individual challenge examples
do not run another broad tiny-LM matrix
do not change protected encoder unless diagnostics show a problem
do not hand off to the LLM team from this stage
```

## Current Anchors

```text
SP64 valid/test tokens/raw byte: 0.159020 / 0.159620
raw-hard candidate valid/test tokens/raw byte: 0.162884 / 0.163117
raw-soft-marker candidate valid/test tokens/raw byte: about 0.2367 / 0.2367
finite protected soft-marker valid/test tokens/raw byte: 0.251658 / 0.252212
pure custom lossless+64k valid/test tokens/raw byte: about 0.4162 / 0.4194
```

Visible boundary anchors:

```text
custom deterministic challenge F1: 0.9220
finite protected soft-marker challenge F1: 0.8259
SP64 challenge F1: 0.7351
raw-hard challenge F1: 0.5951
```

## Candidate Policies

### Policy A: raw-hard control

```text
marker: none
purpose: compression/null control
expected: near SP64 pressure, weak morphology
```

Already mostly measured. Keep as a control, not a candidate.

### Policy B: all-soft marker

```text
marker: every soft morphology boundary
purpose: upper morphology signal
expected: high morphology, too much pressure
```

Already measured. This is the current expensive candidate.

### Policy C: suffix-chain-only

```text
marker: only words with 2+ suffix pieces
purpose: keep signal where agglutinative structure matters most
expected: lower pressure than all-soft; stronger F1 than SP64
```

This is the preferred first selective policy because it is train-side,
language-motivated, and not directly tuned to challenge examples.

### Policy D: high-value-suffix-only

```text
marker: only boundaries before selected suffix classes
candidate suffix classes:
  plural
  case
  possessive
  tense/aspect/person chains
  derivational/long suffixes
purpose: prioritize morphologically informative boundaries
```

Risk:

```text
requires reliable suffix class labels or a curated suffix-class map
could become hand-tuned morphology if we overdo it
```

### Policy E: budgeted-marker-rate

```text
marker: choose train-side marker classes until token-pressure target is met
target: valid/test <=0.20 tokens/raw byte preferred
purpose: force compression discipline
```

Risk:

```text
if optimized only for pressure, it may erase useful morphology
```

### Policy F: low-confidence-SP-only

```text
marker: only where SP64 tends to miss morphology boundaries
purpose: focus markers on learned tokenizer blind spots
```

Risk:

```text
can overfit visible challenge if implemented naively
requires train-side or heldout diagnostics to be claim-grade
```

Do not start here unless advisors recommend it.

## First Implementation Step

Implement a marker-policy materializer that reuses the existing soft-morph
analysis but can emit train views with marker policies:

```text
none
all_soft
suffix_chain_only
high_value_suffix_only
budgeted_suffix_chain
```

Suggested script:

```text
scripts/materialize_v2_selective_soft_marker_views.py
```

Inputs:

```text
filtered train/valid/test split
existing analyze_line output
policy name
optional marker budget / suffix allowlist
```

Outputs:

```text
private train/valid/test views
public materialization report
marker count
view/raw bytes
soft markers/raw byte
estimated hard/protected segments
```

## Evaluation Order

### Gate 1: View pressure before training

Reject a policy if:

```text
view/raw bytes is close to all-soft marker
marker density is close to all-soft marker
```

### Gate 2: SentencePiece token pressure

Train only small train-only Unigram 64k candidates for policies that pass Gate 1.

Reject a policy if:

```text
valid/test model tokens/raw byte > 0.22
```

Preferred target:

```text
valid/test model tokens/raw byte <= 0.20
```

### Gate 3: Intrinsic behavior

Reject a policy if:

```text
protected stress < 25/25
challenge boundary F1 <= SP64 by a meaningful margin
```

Preferred target:

```text
challenge boundary F1 >= 0.78
better: >= 0.80
```

### Gate 4: Tiny-LM

Run tiny-LM only for at most one candidate that passes Gates 1-3.

Required comparison:

```text
same-token/same-step vs SP64
approx iso-byte vs SP64
explicit tokens/raw byte penalty
```

Do not run a broad matrix.

## Initial Stop/Go Thresholds

Go to one tiny-LM screen only if:

```text
protected stress = 25/25
challenge F1 >= 0.78
valid/test tokens/raw byte <= 0.22
fallback byte-token rate remains low
```

Strong candidate if:

```text
challenge F1 >= 0.80
valid/test tokens/raw byte <= 0.20
same-step BPB gap vs SP64 narrows materially
```

Stop marker path if:

```text
no selective policy beats SP64 F1 while staying <=0.22 tokens/raw byte
or tiny-LM same-step gap remains large after pressure reduction
```

## Advisor Checkpoint

Before implementation, ask advisors:

```text
is suffix-chain-only the right first policy?
are <=0.20 preferred / <=0.22 max reasonable token-pressure thresholds?
should visible challenge category failures influence marker selection?
would they use seed vocab / merge constraints instead of markers?
```

Advisor request:

```text
docs/advisor_request_v2_0_selective_soft_marker.md
```

## Current Recommendation

Proceed with a small selective-marker intrinsic/token-pressure sweep only.

Do not run another LM experiment until a candidate has lower token pressure.

