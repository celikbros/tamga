# v2.0 Boundary-Biased Lambda Decomposition

Date: 2026-06-10

## Purpose

This report separates three effects in the boundary-biased Unigram diagnostic:

```text
finite protected numeric-SP floor -> lambda 0: decoder/pipeline effect
lambda 0 -> lambda 4: morphology boundary penalty effect
lambda 4 -> lambda 8: high-F1 / high-cost effect
```

This is still an early 300-step tiny-LM screen, not final LLM evidence.

## Results

| Candidate | Test tokens/raw byte | Test BPB | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | --- |
| SP64 bare | 0.159620 | 4.860352 | 0.7351 | 1/25 |
| finite protected numeric-SP floor | 0.172734 | 4.911037 | 0.6913 | 25/25 |
| boundary-biased lambda 0 | 0.163839 | 4.769027 | 0.7422 | 25/25 |
| boundary-biased lambda 4 | 0.164686 | 4.721480 | 0.7701 | 25/25 |
| boundary-biased lambda 8 | 0.179299 | 4.850946 | 0.8225 | 25/25 |

## Decomposition

| Step | Test tokens/raw byte delta | Test BPB delta | Challenge F1 delta | Reading |
| --- | ---: | ---: | ---: | --- |
| floor -> lambda 0 | -0.008895 | -0.142010 | +0.0509 | large decoder/pipeline effect |
| lambda 0 -> lambda 4 | +0.000847 | -0.047547 | +0.0279 | smaller morphology-penalty effect |
| lambda 4 -> lambda 8 | +0.014613 | +0.129466 | +0.0524 | over-segmentation: more F1, worse BPB |

## Interpretation

The advisor warning was correct: lambda 0 already explains most of the BPB gain
from the protected floor to lambda 4.

However, lambda 4 is not empty. In this 300-step screen it improves over lambda
0 by:

```text
test BPB: -0.047547
Challenge F1: +0.0279
test tokens/raw byte: +0.000847
```

So the current honest claim is:

```text
The custom decoder/pipeline is a strong confound and must be audited.
Within that decoder family, morphology boundary bias at lambda 4 gives a
smaller but useful-looking gain over lambda 0.
```

## Decision

Do not promote lambda 4 yet.

The next required checks are:

```text
roundtrip/stateless decode audit
determinism audit
normal-text-only morphology F1
hidden/heldout or noisy morphology canary
longer/seeded BPB: lambda 0 vs lambda 4, not just lambda 4 vs SP64
```

Lambda 8 remains a high-F1 reference only.
