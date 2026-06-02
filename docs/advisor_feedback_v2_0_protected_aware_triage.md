# Advisor Feedback Triage: v2.0 Protected-Aware Architecture

Date: 2026-06-02

## Status

```text
new advisor feedback received
project was drifting into candidate-by-candidate probing
advisors converge on a specific architecture direction
```

## Accepted Decision

The v2.0 main architecture should be:

```text
hard pretokenization for protected spans and text regions
+ learned BPE/Unigram inside finite boundaries
+ dedicated protected-subword/byte fallback path
+ optional user-defined symbols for frequent protected literals/patterns
+ morphology as soft prior / marker / seed, not open-vocab labels
```

Short form:

```text
Option 1 + Option 3 hybrid
```

This means:

```text
protected spans must be operational in encode/training, not only metadata
protected handling must be finite-vocabulary and stateless-decode safe
protected spans should not use placeholder + side-channel payload decoding
plain SP64 remains the null hypothesis if morphology fails downstream
```

## Why This Fits Our Evidence

Recent local evidence:

| Candidate | Token pressure | Challenge F1 | Protected spans | Decision |
| --- | ---: | ---: | ---: | --- |
| pure custom lossless+64k | bad | 0.9220 | strong | not LLM-default |
| raw-hard SP64 | near SP64 | 0.5951 | 1/25 | reject |
| raw-soft-marker SP64 | medium | 0.6724 | 1/25 | reject |
| protected-aware diagnostic | diagnostic only | 0.8259 | 25/25 | direction signal |

Interpretation:

```text
compression alone is not enough
soft morphology markers alone are not enough
protected-aware routing is the missing operational layer
open-vocab protected tokens are useful for diagnosis but not final LLM design
```

## Rejected Options

### Placeholder + Payload

Rejected for LLM tokenizer use:

```text
not stateless decode
requires custom side-channel or bracket matching
generation can emit malformed placeholder sequences
does not fit ordinary HF/vLLM-style tokenizer expectations
```

### User-Defined Symbols Only

Insufficient as the main solution:

```text
helps frequent protected literals
does not protect unseen URL/file/number/code tail
should be used only as a supplement to protected pretoken + fallback
```

### Plain SP64 + Post-Analysis Metadata

Keep as null hypothesis:

```text
lowest engineering risk
but does not carry morphology/protection signal into model tokens
use if controlled BPB/LM probes show no real benefit from morphology-aware design
```

## Required Next Design

Build a finite protected-aware candidate with:

```text
1. deterministic protected-span pretokenizer
2. normal Turkish/text stream with optional soft morphology markers or seeds
3. protected stream encoded by finite protected-BPE/subword pieces plus byte fallback
4. optional user-defined symbols for frequent protected literals/patterns
5. no stateful placeholder payload decoding
6. decode(ids) remains a pure stateless function of token IDs
```

## Evaluation Gate

Before any tiny-LM run:

```text
protected span preservation should be near 25/25 on current stress set
challenge boundary F1 should be materially above SP64, target 0.80+
token pressure should remain much closer to SP64 than pure custom lossless
roundtrip must be lossless
```

Then, and only then:

```text
run controlled BPB/tiny-LM screening
keep plain SP64 as null baseline
```

## Immediate Next Step

Do not add another ad-hoc candidate.

Write the finite protected-aware tokenizer design/spec first:

```text
protected categories
protected internal encoding strategy
byte fallback token set
UDS promotion policy
decode invariants
evaluation gates
```

Then implement the smallest prototype against that spec.
