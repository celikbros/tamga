# Advisor Request: v2.0 Training-Time Morphology Objective Choice

Date: 2026-06-10

## Context

We are building a Turkish-primary tokenizer research prototype for a future LLM
project.

The long-term goal is not to wrap an existing tokenizer blindly. We want to
test whether Turkish morphology can be used as a useful structural prior for
learned tokenization.

The current project status is:

```text
research prototype
not production-ready
not final LLM-tokenizer handoff
```

## Current Architecture Direction

We no longer believe pure deterministic Turkish morphology should be the direct
LLM tokenizer.

Current target shape:

```text
lossless learned tokenizer
+ finite protected routing for URLs/code/files/numbers/dates/package-like spans
+ Turkish morphology teacher as a soft training-time prior
+ no broad runtime custom decoder if avoidable
```

## Hard Requirements

1. `decode(encode(text)) == text`.
2. Decode must be stateless: no side-channel payload.
3. Protected spans must be preserved or represented by a finite lossless route.
4. Morphology must improve tokenizer behavior only if token pressure and BPB
   justify it.
5. We do not want endless visible-challenge tuning.
6. We do not want an unmaintainable regex exception system.

## Important Baselines And Reference Points

| Candidate | Test tokens/raw byte | Test BPB | Challenge F1 | Protected stress | Status |
| --- | ---: | ---: | ---: | --- | --- |
| SP64 Unigram bare | 0.159620 | 4.860352 | 0.7351 | 1/25 | compression baseline only |
| finite protected numeric-SP floor | 0.172734 | 4.911037 | 0.6913 | 25/25 | active protected null |
| boundary-biased lambda0 runtime | 0.163839 | 4.769027 | 0.7422 | 25/25 | diagnostic only |
| boundary-biased lambda4 runtime | 0.164686 | 4.721480 | 0.7701 | 25/25 | diagnostic only |
| boundary-biased lambda8 runtime | 0.179299 | 4.850946 | 0.8225 | 25/25 | high-F1 reference |

## Branches Already Tried And Rejected

### Pure Custom Deterministic Morphology

Useful as a teacher and diagnostic reference, but too risky/token-heavy as a
direct LLM tokenizer.

### Train-Only Marker Shaping

Improved visible morphology F1 but did not pay back token pressure in tiny-LM
BPB.

Representative 300-step tiny-LM rows:

| Candidate | Test BPB |
| --- | ---: |
| SP64 | 4.860352 |
| finite protected SP64 floor | 4.976850 |
| suffix_chain2 marker-stripped | 5.094965 |
| all-soft marker-stripped | 5.157444 |

Decision:

```text
stop marker-dose tuning
```

### Morph Seed Appendix

Compression-safe, but did not transfer morphology signal.

Decision:

```text
stop simple seed appendix
```

### Safe UDS7 / Expanded UDS22

Safe UDS7 gave a small real signal at almost no token-pressure cost.
Expanded UDS22 quickly behaved like hard segmentation and raised token
pressure into the marker/floor band.

Decision:

```text
keep UDS7 as a small lesson
do not broaden UDS
```

## Runtime Boundary-Biased Decode: Diagnostic Only

We tested a custom Viterbi decoder over SP64 vocabulary:

```text
path_score = SP_unigram_score - lambda * morph_boundary_crossing_count
```

This looked promising at first:

| Candidate | Test tokens/raw byte | Test BPB | Challenge F1 |
| --- | ---: | ---: | ---: |
| lambda0 | 0.163839 | 4.769027 | 0.7422 |
| lambda4 | 0.164686 | 4.721480 | 0.7701 |
| lambda8 | 0.179299 | 4.850946 | 0.8225 |

But roundtrip audit found it is not a valid tokenizer path:

| Tokenizer | Valid exact roundtrip |
| --- | ---: |
| SP64 bare | 1985/1994 |
| finite protected numeric-SP floor | 17/1994 |
| boundary-biased lambda0 | 0/1994 |
| boundary-biased lambda4 | 0/1994 |

Failures are mostly whitespace / punctuation / apostrophe reconstruction
errors.

We also confirmed wrapper tax on clean no-protected lines:

| Candidate | Avg official SP tokens | Avg candidate tokens | Avg delta |
| --- | ---: | ---: | ---: |
| finite protected numeric-SP floor | 164.2955 | 171.9669 | +7.6715 |

Decision:

```text
runtime boundary-biased decoder is demoted to diagnostic evidence
do not run more BPB on it
do not send it as a tokenizer candidate
```

The useful lesson remains:

```text
morphology preference may help when applied as a segmentation prior,
but it should probably be baked into training rather than runtime decoding.
```

## New Toy Training-Time Objective Smoke

We implemented a tiny toy BPE trainer to test whether the training-time
objective direction is mechanically plausible.

Objective:

```text
score(pair) = pair_count - lambda * morph_boundary_crossing_count
```

Files:

```text
src/tr_tokenizer/boundary_weighted_bpe.py
scripts/run_v2_boundary_weighted_bpe_probe.py
docs/v2_0_boundary_weighted_bpe_probe_findings.md
```

Smoke setup:

```text
train lines: 100
vocab size: 120
lambdas: 0, 4, 8
```

Challenge result:

| Model | Avg tokens/word | Boundary F1 | Merges | Crossing merges |
| --- | ---: | ---: | ---: | ---: |
| lambda0 | 5.4856 | 0.5431 | 42 | 20 |
| lambda4 | 5.5587 | 0.5406 | 42 | 17 |
| lambda8 | 5.6214 | 0.5507 | 42 | 17 |

Interpretation:

```text
the penalty is wired correctly because crossing merges decrease
quality signal is weak at this tiny scale
toy Python BPE is too slow for serious sweeps
this is only an objective sanity check, not a tokenizer candidate
```

## Current Decision Point

We need to choose the first real training-time objective mechanism.

Options:

### A. Boundary-Weighted BPE

```text
merge_score = frequency - lambda * boundary_crossing_count
```

Pros:

```text
simple, inspectable, directly supported by toy smoke
```

Cons:

```text
less aligned with strongest current SP64 Unigram baseline
may require custom trainer and custom artifact
```

### B. Boundary-Weighted Unigram

```text
favor segmentation paths and/or pieces aligned with high-confidence
morphology boundaries during Unigram training
```

Pros:

```text
closer to current strongest baseline
matches the lambda decoder evidence
more likely to produce a standard-ish tokenizer artifact
```

Cons:

```text
harder to implement and easier to get train/inference mismatch wrong
```

### C. Standard SP/Unigram + Post-Hoc Morph-Aware Score Adjustment

```text
train ordinary SP64, then adjust/prune/reweight pieces with morphology stats
```

Pros:

```text
lower implementation risk and closer ecosystem compatibility
```

Cons:

```text
may be too weak, similar to seed appendix
may distort probabilities without a principled training objective
```

## Questions

Please be critical. We do not want approval-only feedback.

1. Is our demotion of the runtime boundary-biased decoder correct?

2. Do you agree that the next meaningful branch should be a training-time
   objective rather than more marker/UDS/runtime-decoder work?

3. Which mechanism should we implement first?

```text
A. boundary-weighted BPE
B. boundary-weighted Unigram
C. standard SP + post-hoc score/vocab adjustment
D. another mechanism
```

4. If you choose boundary-weighted Unigram, what is the simplest objective
   worth implementing first?

Examples:

```text
path penalty for pieces crossing teacher boundaries
piece prior reward for exact high-confidence morph surfaces
EM count reweighting by boundary alignment
candidate vocabulary pruning by boundary cost
```

5. Should protected routing be kept outside the learned objective as a hard
   wrapper, or should protected-span constraints be included in the training
   objective itself?

6. How should boundary confidence be defined?

Possible classes:

```text
high confidence: suffix boundaries from deterministic teacher
medium confidence: derivational/ambiguous suffixes
low confidence: informal/unknown forms
hard: protected span / script / maybe whitespace
```

7. What intrinsic gate should a first training-time objective candidate pass
   before tiny-LM?

Current proposed gate:

```text
exact roundtrip
protected stress 25/25
tokens/raw byte close to finite_protected_sp64_numeric_sp_floor
normal-text-only F1 improves materially over protected floor and SP64
multilingual/code smoke does not bloat badly
```

8. Is the toy boundary-weighted BPE smoke useful, or too small/misleading to
   guide objective choice?

9. What is the biggest hidden failure mode now?

Examples:

```text
teacher brittleness
small curated eval overfitting
wrapper tax hiding true baseline
objective improves F1 but worsens BPB
standard tokenizer artifact becomes impossible
multilingual/code degradation
```

10. If this were your project, what would you build in the next one week?

Please give:

```text
smallest useful experiment
stop criteria
success criteria
reports required before any LLM-team experimental handoff
```

## Our Current Leaning

Our current internal leaning:

```text
do not expand toy BPE
do not revive runtime decoder
design a minimal boundary-weighted Unigram trainer/prototype, because it is
closer to the SP64 baseline and to the lambda decoder evidence
```

Please challenge this if boundary-weighted BPE or another route is more
defensible.
