# Advisor Request: v2.0 Train-Only Marker Frontier

Date: 2026-06-08

## Context

We are building a Turkish-primary tokenizer for possible LLM use. The current
v2.0 direction is:

```text
finite protected-span routing
+ learned Unigram/BPE for normal text
+ morphology as a soft learned prior, not mandatory hard tokenization
+ stateless decode(ids)
```

We have rejected:

```text
pure deterministic custom as final LLM tokenizer
open-vocabulary protected surface tokens
placeholder/payload side-channel decoding
in-stream all-soft morphology markers as the main solution
```

The current problem:

```text
finite protected + all-soft in-stream markers preserve morphology/protection,
but token pressure is too high for LLM handoff.
```

So we tested train-only marker shaping:

```text
markers appear only in the SentencePiece training view
normal encode strips markers and uses raw text plus finite protected routing
```

## Baseline References

| Model | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | --- |
| SP64 reference | 0.159020 | 0.159620 | 0.7351 | 1/25 |
| finite protected + all-soft in-stream | 0.251658 | 0.252212 | 0.8259 | 25/25 |
| all-soft marker-stripped | 0.195611 | 0.196236 | 0.7703 | 25/25 |

Interpretation so far:

```text
in-stream marker cost is a major bottleneck
train-only marker shaping keeps protected spans and reduces token pressure
but current F1 is below the preferred intrinsic gate
```

## New Train-Only Marker Policies Tested

### Policy A: suffix_chain2

Definition:

```text
insert train-view soft marker only for suffix groups with at least 2 soft
suffix boundaries
```

Reports:

```text
view: artifacts/v2_0_train_only_marker_views_suffix_chain2.md
SP probe: artifacts/v2_0_train_only_suffix_chain2_sentencepiece_probe.md
diagnostic: artifacts/v2_0_train_only_suffix_chain2_marker_stripped_diagnostic.md
```

Results:

| Metric | Value |
| --- | ---: |
| valid tokens/raw byte | 0.183799 |
| test tokens/raw byte | 0.184619 |
| challenge F1 | 0.7632 |
| protected stress | 25/25 |

### Policy B: high_value_suffix

Definition:

```text
insert train-view soft marker only before suffixes in a fixed high-value
Turkish suffix allowlist
```

Reports:

```text
view: artifacts/v2_0_train_only_marker_views_high_value_suffix.md
SP probe: artifacts/v2_0_train_only_high_value_suffix_sentencepiece_probe.md
diagnostic: artifacts/v2_0_train_only_high_value_suffix_marker_stripped_diagnostic.md
```

Results:

| Metric | Value |
| --- | ---: |
| valid tokens/raw byte | 0.190346 |
| test tokens/raw byte | 0.191068 |
| challenge F1 | 0.7665 |
| protected stress | 25/25 |

## Current Frontier

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | --- |
| SP64 reference | 0.159020 | 0.159620 | 0.7351 | 1/25 |
| all-soft marker-stripped | 0.195611 | 0.196236 | 0.7703 | 25/25 |
| suffix_chain2 marker-stripped | 0.183799 | 0.184619 | 0.7632 | 25/25 |
| high_value_suffix marker-stripped | 0.190346 | 0.191068 | 0.7665 | 25/25 |

## Gate

Preferred next-candidate target:

```text
valid/test tokens/raw byte <= 0.20 preferred
valid/test tokens/raw byte <= 0.22 maximum
challenge F1 materially above SP64, preferably >= 0.78-0.80
protected stress: 25/25
```

Current simple train-only policies:

```text
pass token-pressure target
preserve protected spans
do not yet pass preferred visible intrinsic F1 target
```

## Questions

Please be critical.

1. Should we continue train-only marker shaping, or is the F1 ceiling here a
   sign that markers are too weak as a learned prior?

2. Which next lever is most defensible?

```text
a. selected user-defined suffix/morph pieces
b. seed vocabulary constraints
c. marker classes by morphology category
d. soft-boundary dropout/subword regularization during SP training
e. a constrained Unigram/MorphBPE training objective
f. stop this branch and return to plain SP64 + finite protected routing
```

3. Is the preferred F1 gate too strict for this stage, given that protected
   spans are fixed and token pressure is now under 0.20?

4. Should we treat all-soft marker-stripped as the current best candidate
   despite higher token pressure, or prefer suffix_chain2 because it is cheaper?

5. What experiment would you run next if we allow only one more local
   intrinsic probe before stopping this branch?

6. Do these results justify any tiny-LM BPB probe, or should tiny-LM remain
   blocked until challenge F1 reaches the preferred gate?

## Current Internal Recommendation

```text
Do not run tiny-LM yet.
Keep finite protected routing.
Keep normal encode marker-free.
Use this frontier to choose one stronger train-only learned-prior experiment.
Do not tune directly against visible challenge examples.
```
