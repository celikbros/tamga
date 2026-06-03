# Advisor Request: v2.0 Selective Soft-Marker Direction

Date: 2026-06-03

## Context

We are building a Turkish-primary, multilingual-aware tokenizer for possible
future LLM use. The project is still a research prototype. We are not asking
whether the current tokenizer is ready for handoff. It is not.

Current v2.0 direction:

```text
finite protected-aware learned hybrid
normal text: learned BPE/Unigram
protected spans: finite protected pieces + UTF-8 byte fallback
morphology: soft prior, not hard mandatory tokenization
decode(ids): stateless
```

Rejected designs:

```text
pure deterministic custom tokenizer as final LLM tokenizer
placeholder + side-channel payload decoding
open-vocabulary protected surface tokens
hard morphology boundary for every suffix
```

## Current Best Candidate

The current candidate is:

```text
finite_protected_soft_marker
```

It combines:

```text
normal text: train-only soft-marker Unigram model
protected spans: finite protected pieces + UTF-8 byte fallback
```

The soft-marker model inserts a private-use marker at morphology-proposed soft
boundaries during tokenizer training. At encode time, protected spans are routed
to a finite protected encoder, while normal text is encoded with the learned
soft-marker SentencePiece model.

## Intrinsic Results

Visible intrinsic evaluation:

```text
finite_protected_soft_marker protected stress: 25/25 preserved
finite_protected_soft_marker challenge boundary F1: 0.8259
SP64 challenge boundary F1: 0.7351
custom deterministic challenge boundary F1: 0.9220
multilingual smoke F1: 0.8015
```

Interpretation:

```text
protected routing works
soft morphology signal recovers a large part of the custom boundary advantage
the candidate remains below the custom deterministic boundary ceiling
```

## Token Pressure

Split-level token pressure:

```text
finite_protected_soft_marker valid/test tokens/raw byte: 0.251658 / 0.252212
SP64 valid/test tokens/raw byte: 0.159020 / 0.159620
```

Interpretation:

```text
the candidate uses about 1.58x as many model tokens per raw byte as SP64
this harms compute efficiency and effective context length
```

## Tiny-LM Smoke

This is an early smoke, not final LLM evidence.

Fixed-token / fixed-step view:

| Tokenizer | Steps | Tokens seen | Approx bytes seen | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_soft_marker | 200 | 102400 | 412573 | 7.067777 |
| SP64 | 200 | 102400 | 662011 | 5.966637 |

Approx iso-byte view:

| Tokenizer | Steps | Tokens seen | Approx bytes seen | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_soft_marker | 321 | 164352 | 662180 | 5.263920 |
| SP64 reference | 200 | 102400 | 662011 | 5.966637 |

Same-step SP64 control:

| Tokenizer | Steps | Tokens seen | Approx bytes seen | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_soft_marker | 321 | 164352 | 662180 | 5.263920 |
| SP64 | 321 | 164352 | 1062527 | 4.629442 |

Current interpretation:

```text
approx iso-byte view suggests morphology/protection signal can help BPB
same-token/same-step view strongly favors SP64
current candidate is promising but too token-expensive for LLM handoff
```

## Current Decision

We do not want to run broader tiny-LM matrices for this exact candidate.

The next design pressure is:

```text
keep protected-span and boundary gains
reduce token pressure toward SP64
avoid returning to pure custom tokenization pressure
```

Our working hypothesis:

```text
marking every morphology-proposed soft boundary is too expensive
selective soft markers may preserve most useful morphology signal at lower token cost
```

## Candidate Direction: Selective Soft Markers

Instead of marking every soft morphology boundary, train variants that mark only
some boundary classes.

Possible policies:

```text
none/raw-hard:
  no morphology marker, compression control

all-soft:
  current candidate, high morphology signal, high token pressure

suffix-chain-only:
  mark boundaries only inside words with 2+ suffix pieces

long-inflection-only:
  mark only words whose surface length or suffix count suggests high morphology load

high-value-suffix-only:
  mark only boundaries before suffixes/classes known to matter for Turkish LM:
  plural/case/possessive/tense/person/derivational chains

low-confidence-SP-only:
  mark only boundaries where plain SP64 visibly fails morphology alignment
  but avoid using visible challenge labels directly if this risks overfit

budgeted-marker-rate:
  choose markers until train-view token pressure target is met
```

Proposed first gate for a selective candidate:

```text
protected stress: 25/25
challenge boundary F1: > SP64 and target 0.78-0.80+
valid/test tokens/raw byte: <= 0.20 preferred, <= 0.22 maximum for tiny-LM screen
no broad LM run before these intrinsic/token-pressure gates pass
```

## Questions

Please be critical. We do not want approval-only feedback.

1. Is selective soft-marker training the right next design step, or should we
   abandon marker-based morphology and instead try seed vocabulary / merge
   constraints / hybrid Unigram priors?

2. Which selective marker policy is most defensible as a first experiment?
   Please rank:
   - suffix-chain-only
   - long-inflection-only
   - high-value-suffix-only
   - budgeted-marker-rate
   - low-confidence-SP-only

3. What token-pressure target is reasonable before another tiny-LM screen?
   Is `<=0.20` tokens/raw byte too strict, too lenient, or about right?

4. What minimum visible intrinsic quality should survive?
   Is `challenge F1 >=0.80` a reasonable threshold, or should the criterion be
   "materially above SP64" rather than an absolute target?

5. Should marker selection be based only on train-side morphology/frequency
   statistics, or may we use visible challenge category failures as a dev signal?
   How do we avoid overfitting?

6. Is the current finite protected encoder good enough to freeze while we tune
   normal-text morphology pressure, or should protected encoding be revisited
   first?

7. Would you run another tiny-LM screen after one selective candidate passes
   intrinsic gates, or should the next proof be a different metric first
   (e.g. token pressure + boundary F1 only)?

8. What result would make you stop marker-based morphology entirely and keep
   morphology only as analysis metadata?

9. Are we interpreting the iso-byte result correctly? It favors the candidate,
   but not under same compute/token budget. Is this still meaningful enough to
   justify one selective-marker iteration?

10. If this were your project, what exact next experiment would you run and what
    would your stop/go thresholds be?

## Our Current Lean

Our current lean, before advisor feedback:

```text
do one selective-marker intrinsic/token-pressure sweep, not another LM matrix
try 3-4 train-view policies:
  none/raw-hard control
  suffix-chain-only
  high-value-suffix-only
  budgeted-marker-rate
pick at most one candidate for a tiny-LM screen
stop if no candidate gets near <=0.20-0.22 tokens/raw byte while beating SP64 F1
```

