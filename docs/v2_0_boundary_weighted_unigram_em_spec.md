# v2.0 Boundary-Weighted Unigram/EM Spec

Date: 2026-06-10

## Goal

Build the smallest real learned-tokenizer objective that can test whether
Turkish morphology teacher boundaries improve a Unigram tokenizer when the
prior enters training directly.

This is not a production tokenizer yet.

## Why This Branch

Closed branches:

```text
stock SentencePiece partial-boundary delimiter
seed appendix
broad UDS expansion
post-hoc score shift
runtime boundary-biased decoder as a candidate
```

Key diagnostics:

```text
SP64 oracle_best_f1 on challenge: 0.8417
SP64 lambda0 Challenge F1: 0.7422
post-hoc score-shift lambda 1/2/4/8: no meaningful F1 movement
```

Interpretation:

```text
SP64 vocab can express more morphology-aligned paths, but shallow score patches
do not move the chosen path. The prior needs to enter learning, not only
post-hoc decode scores.
```

## Non-Negotiable Invariants

1. Normal encode/decode must be byte-exact or have documented byte fallback.
2. No side-channel payloads.
3. Finite protected routing remains separate and exact.
4. Development metric for the normal-text objective is **bare F1**.
5. Finite-wrapper tax is tracked separately.
6. No tuning against individual visible challenge examples.

## Objective Shape

Start from a Unigram candidate vocabulary and train scores with a morphology
weighted EM variant.

For a sentence `x`, a segmentation path `z`, and teacher soft-boundary count:

```text
crossings(z) = number of high-confidence teacher boundaries crossed by pieces
aligned(z)   = optional count of pieces that exactly align to teacher morph spans
```

Primary first objective:

```text
path_weight(z) = P_unigram(z | theta) * exp(-lambda * crossings(z))
```

Equivalently in log-space:

```text
log_weight(z) = sum(log p(piece)) - lambda * crossings(z)
```

E-step:

```text
compute expected piece counts under path_weight(z)
```

M-step:

```text
normalize expected counts into updated piece probabilities
```

Pruning:

```text
remove pieces with low posterior mass, but keep required chars/meta pieces
```

## Boundary Source

Use the existing custom morphology teacher:

```text
scripts.materialize_v2_soft_morph_artifacts.analyze_line
```

Boundary classes:

```text
hard boundaries:
  whitespace
  protected span boundaries
  script transitions
  punctuation where the protected/router layer owns behavior

soft boundaries:
  teacher morphology boundaries inside normal Turkish text
```

First implementation should use one soft boundary class only:

```text
crossing penalty = 1 per crossed teacher soft boundary
```

Do not add suffix-category-specific weights in the first prototype.

## Candidate Vocabulary

Initial prototype options, in preferred order:

1. Use SP64 vocab as the initial candidate set.
2. Add required single-character pieces for lossless fallback.
3. Do not add broad UDS.
4. Keep safe UDS7 out of the first objective unless needed for a controlled
   comparison.

Rationale:

```text
The oracle ceiling showed SP64 vocab can express much better morphology paths.
The first question is whether objective learning can move probabilities,
not whether a new vocabulary inventory is needed.
```

## First Prototype Scope

Use the 20k pilot train split only:

```text
train: artifacts/private/v1_8_local_lm_probe/.../filtered_split/train.txt
valid/test: existing filtered_split valid/test
```

Recommended first prototype scale:

```text
train lines: 2k or 5k for debug
vocab: SP64 candidate set, optionally top-N subset for speed
lambda: 0, 0.5, 1, 2, 4
iterations: 2-5 EM iterations
```

`lambda=0` must reproduce or approximate normal Unigram behavior. If it does
not, debug before interpreting morphology results.

## Evaluation

Primary intrinsic:

```text
bare Challenge F1
bare tokens/raw byte or tokens/word
```

Secondary:

```text
finite-wrapper Challenge F1
finite-wrapper tax by route tag
protected stress 25/25
roundtrip audit
category F1
```

Do not run tiny-LM until:

```text
bare F1 improves beyond the current CI noise floor
token pressure remains controlled
roundtrip/protected invariants pass
```

## Success Gate

A first prototype is worth deeper work if:

```text
bare Challenge F1 improves by a material amount over SP64
  target: >= +0.02 absolute over 0.7351, or clearly outside current CI overlap
bare token pressure remains near SP64/floor
  target: tokens/raw byte <= 0.17 on valid/test
finite protected stress remains 25/25 after wrapper application
lambda curve is monotonic or has an interpretable knee
```

## Stop Gate

Stop or redesign if:

```text
lambda=0 cannot reproduce the reference path well enough
lambda increases token pressure but bare F1 stays inside the CI noise floor
EM becomes too slow on 2k-5k lines without a clear optimization path
the resulting artifact cannot be made lossless / stateless
```

## Implementation Notes

For speed, the first implementation may be a prototype, not full SentencePiece
compatibility:

```text
read SP64 vocab + scores
build per-word lattice from candidate pieces
run forward-backward with boundary penalty
update scores
serialize an adjusted .model or diagnostic vocab
```

Initial implementation status:

```text
script: scripts/materialize_v2_boundary_weighted_unigram_em.py
unit tests: tests/test_v2_boundary_weighted_unigram_em.py -> 5 passed
100-line lambda=1 smoke:
  report: artifacts/v2_0_boundary_weighted_unigram_em_lambda1_iter1_100lines.md
  normal segments: 25486
  skipped segments: 0
  changed scores: 15479
  diagnostic bare Challenge F1: 0.7404
100-line lambda=0/lambda=1 CI:
  report: artifacts/v2_0_boundary_weighted_unigram_em_100lines_ci.md
  lambda0 bare Challenge F1: 0.7392
  lambda1 bare Challenge F1: 0.7404
```

The 100-line run only proves that the lattice/EM/model-writing path is wired
correctly. It should not be interpreted as a candidate result.

Next controlled smoke:

```text
lambda: 0, 1, 2, 4
train lines: 2000 first; 5000 if runtime is acceptable
iterations: 1 first, then 2-3 only if lambda0 is sane
primary readout: bare Challenge F1 + tokens/word + skipped segments
```

However, a candidate cannot become an LLM handoff artifact until it has:

```text
standard-ish encode/decode path
roundtrip proof
protected routing proof
token pressure report
tiny-LM BPB calibration
```

## Parallel Wrapper Work

Finite-wrapper tax should be improved separately:

```text
numeric_like route F1 delta: -0.4416
file_like route F1 delta: -0.3042
apostrophe/hard_suffix feature delta: -0.1587
```

This is not the normal-text objective's responsibility. Keep it as a separate
protected-tail route design task.
