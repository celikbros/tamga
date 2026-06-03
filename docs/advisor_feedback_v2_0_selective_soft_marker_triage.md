# Advisor Feedback Triage: v2.0 Selective Soft-Marker

Date: 2026-06-03

## Summary

Advisor feedback broadly agrees with the current diagnosis:

```text
finite protected routing works
all-soft marker morphology signal is useful
current all-soft marker candidate is too token-expensive
do not run broader tiny-LM matrices for the same candidate
```

The strongest new recommendation is:

```text
before a selective-marker sweep, run a marker-stripped mechanism check
```

Question:

```text
is the 1.58x token-pressure cost mainly caused by markers being present in the
encode-time ID stream, or by morphology-friendly segmentation itself?
```

If the cost mostly disappears when markers are used only for vocabulary shaping
but not emitted at encode time, the project should pivot toward train-only
vocab shaping / constrained Unigram rather than in-stream markers.

## Consensus Points

### Freeze Protected Encoder

```text
protected stress is already 25/25
protected routing is orthogonal to normal-text marker pressure
do not revisit protected encoding unless new stress failures appear
```

Decision:

```text
freeze finite protected encoder for the next normal-text experiments
```

### Do Not Tune On Challenge Failures

```text
marker policy must be train-side only
visible challenge categories must not choose marker classes
challenge remains reporting/stop-go only
```

Decision:

```text
no challenge-driven marker selection
```

### Token Pressure Is The Main Bottleneck

Current candidate:

```text
valid/test tokens/raw byte: 0.251658 / 0.252212
SP64 valid/test tokens/raw byte: 0.159020 / 0.159620
```

Advisor thresholds:

```text
preferred target: <= 0.20 tokens/raw byte
maximum for next tiny-LM screen: about <= 0.21-0.225
```

Decision:

```text
use <=0.20 as preferred target
use <=0.22 as practical maximum gate
```

### Boundary F1 Gate

Advisors prefer a relative gate over a rigid absolute gate:

```text
challenge F1 should be materially above SP64
target: >= SP64 + 0.04 to +0.05
stretch: >= 0.80
```

Decision:

```text
candidate must beat SP64 by a meaningful margin and preferably reach 0.78-0.80+
```

## Conflict / Nuance

### Which Selective Policy First?

Advisor rankings differ:

```text
Grok43: budgeted-marker-rate first, high-value-suffix second
Gemini35: high-value-suffix first, budgeted-marker-rate second
Opus48: suffix-chain priority first, budget sweep as mechanism
```

Common resolution:

```text
do not test ad-hoc single-point policies
run a budget sweep over one train-side priority function
then optionally compare a second priority function at matched budgets
```

Decision:

```text
Exp 0 first: marker-stripped mechanism check
Exp 1 if needed: suffix-chain-depth priority with budget sweep
Exp 1b optional: high-value-suffix priority with same budgets
```

### Marker vs Constrained Training

Advisors warn that in-stream markers may be the wrong mechanism:

```text
markers can fragment vocabulary and add direct token cost
constrained Unigram / train-only vocab shaping may preserve morphology without
emitting marker tokens
```

Decision:

```text
add a no-marker/vocab-shaping diagnostic arm before selective marker work
```

## Immediate Next Experiment: Exp 0

Run marker-stripped diagnostic:

```text
train artifact: existing all-soft marker Unigram model
encode-time behavior: do not insert SOFT_MARKER into normal text
protected behavior: keep finite protected encoder
measure:
  valid/test tokens/raw byte
  protected stress
  challenge boundary F1
```

Interpretation:

```text
if tokens/raw byte drops near SP64 and F1 remains above SP64:
  marker cost was mostly in-stream; pivot to train-only vocab shaping

if tokens/raw byte drops but F1 collapses near SP64/raw-hard:
  markers are needed for boundary behavior; selective markers remain relevant

if tokens/raw byte remains near 0.25:
  cost is intrinsic to current morphology-friendly model; selective/budget sweep
  is the next lever
```

## Revised Roadmap

```text
1. Exp 0 marker-stripped diagnostic
2. if Exp 0 succeeds: design train-only vocab-shaping / constrained Unigram path
3. if Exp 0 fails or F1 collapses: run selective marker budget sweep
4. only one surviving candidate gets another tiny-LM screen
```

## What Not To Do

```text
do not run more tiny-LM rows for the all-soft candidate
do not choose marker classes from visible challenge failures
do not broaden Turkish morphology rules
do not change protected encoder before normal-text pressure is understood
```

