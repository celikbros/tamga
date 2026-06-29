# Advisor Request: Broad v2.0 Tokenizer Review + Boundary-Biased Decode Result

Date: 2026-06-10

## What We Need From You

You are a tokenizer specialist, so please do not only review the newest lambda
result. We want you to audit the whole project direction and tell us if we are
missing a basic tokenizer-design error.

In particular, please look for:

```text
methodological mistakes
unfair baselines
wrong interpretation of BPB or F1
decode / training mismatch
lossless or stateless-decode risks
production integration risks
places where a simpler standard tokenizer design would be better
```

## Context

We are building a Turkish-primary tokenizer research prototype for a future LLM
project. The current direction is hybrid:

```text
finite protected routing
+ learned SP64 Unigram vocabulary for normal text
+ Turkish morphology teacher as a soft prior
+ byte/finite fallback where needed
```

This is not production-ready and not a final LLM handoff. We are trying to
decide the next v2.0 mechanism.

## Project Goal And Non-Goals

The goal is not just to wrap an existing tokenizer. We are testing whether
Turkish morphology can be used as a mathematical/structural prior for learned
tokenization.

Current hypothesis:

```text
Turkish morphology should not be hard-forced everywhere.
It may be useful as a soft preference over learned tokenizer choices.
```

Non-goals for the current phase:

```text
not a production tokenizer yet
not a final LLM-team handoff yet
not a claim that boundary F1 alone proves LLM utility
not a plan to hand-code every Turkic/multilingual morphology rule
not a regex-exception pile
```

Hard requirements:

```text
lossless or effectively lossless encode/decode
stateless decode(ids)
protected spans preserved
reasonable tokens/raw byte
byte-normalized LM evidence before LLM-team handoff
```

Protected spans include:

```text
URLs, file names, code-ish tokens, package/version strings, numbers, dates
```

## Current Architecture Sketch

The current research architecture is:

```text
1. Turkish-aware pretokenization / protected span detection
2. deterministic Turkish morphology teacher
3. finite protected routing for protected spans
4. learned SP64 Unigram vocabulary for normal text
5. optional morphology-aware decode/objective bias
6. byte/finite fallback for rare or protected material
```

Important design distinction:

```text
custom deterministic morphology = teacher/reference/diagnostic
learned SP64 vocabulary = normal text compression engine
finite protected routing = hard safety layer
boundary-biased decode = current soft morphology mechanism
```

Current active protected floor:

```text
finite_protected_sp64_numeric_sp_floor
```

Meaning:

```text
normal text: SP64
protected spans: finite protected routing
numeric_like protected spans: SP64 passthrough for model-token efficiency
logical protected spans: still preserved as whole logical spans
```

## Data And Evaluation Hygiene

Main local data used so far:

```text
celik_gold_clean_pilot.txt: 100k clean pilot lines
v1.8/v2.0 local LM split: 20k lines from pilot
  train: 16k
  valid: 2k
  test: 2k
```

Known limitations:

```text
pilot is clean and likely in-domain
visible challenge set is small and not hidden
tr_gold_expanded is policy/spec regression, not independent proof
we do not yet have a large independent human-labeled heldout set
tiny-LM is a screening proxy, not final LLM evidence
```

Leakage/hygiene already done:

```text
eval leakage against the 100k SP pilot:
  gold raw exact: 0
  gold normalized full: 0
  gold partial 8-gram: 0
  challenge raw exact: 0
  challenge normalized full: 0
  challenge partial 8-gram: 0

short one-word hits were tracked separately and not counted as sentence leakage.
```

We know these checks are not enough for final claims; they are only hygiene for
the local screening stage.

## Earlier Lessons

### Pure deterministic custom tokenizer

The pure custom morphology tokenizer has strong visible Turkish boundary F1,
but it is risky as a direct LLM tokenizer:

```text
too token-heavy in lossless+fallback mode
too much hand-written behavior
multilingual/code-mixed brittleness risk
not yet proven as a stable production LLM tokenizer
```

It remains valuable as:

```text
teacher
diagnostic reference
source of high-confidence morphology boundaries
```

### Plain SP64

SP64 is compression-efficient, but:

```text
breaks protected spans badly
has weaker Turkish morphology boundary behavior
```

Bare SP64 is therefore not the deployable final baseline, but it remains an
important compression and BPB reference.

### Finite protected routing

Finite protected routing is non-negotiable because it recovers protected-span
safety:

```text
protected stress: 25/25
```

But it initially added token pressure. We reduced this through route-cost work:

```text
finite protected floor test tokens/raw byte:
  old: 0.183362
  after route fixes: 0.177726
  numeric-SP protected floor: 0.172734
```

The numeric-SP floor is not necessarily the final numeric codec; it is the best
current experimental protected null baseline.

## Current Protected Baseline

Bare SP64 is not a valid final baseline because it breaks protected spans.

Current active protected null baseline:

```text
finite_protected_sp64_numeric_sp_floor
```

Meaning:

```text
normal text: SP64
protected spans: finite protected routing
numeric_like protected spans: SP64 passthrough for model-token efficiency
logical protected spans: still preserved as whole logical spans
```

Reference rows:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Tiny-LM valid BPB | Tiny-LM test BPB | Challenge F1 | Protected |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| SP64 bare | 0.159020 | 0.159620 | 4.827723 | 4.860352 | 0.7351 | 1/25 |
| finite protected numeric-SP floor | 0.171903 | 0.172734 | 4.875198 | 4.911037 | 0.6913 | 25/25 |

## Branches Already Rejected

We tried several morphology-transfer mechanisms:

```text
train-only markers
marker-stripped all-soft
suffix-chain2 markers
seed appendix
safe UDS7
expanded UDS22
```

Summary:

```text
marker-dose and broad UDS can raise visible F1, but token pressure and/or
tiny-LM BPB did not justify them.

seed appendix was compression-safe but did not transfer enough morphology
signal.

morph vocabulary coverage showed that SP64 already contains most high-value
morph surfaces; the likely bottleneck is decode preference, not vocabulary
absence.
```

More detail:

```text
train-only marker shaping:
  suffix_chain2: F1 0.7632, test tpb ~0.185337, test BPB 5.094965
  all-soft:      F1 0.7703, test tpb ~0.196954, test BPB 5.157444
  decision: morphology F1 gain did not pay in BPB

seed appendix:
  compression-safe
  did not move finite-protected Challenge F1 meaningfully
  decision: not enough signal

safe UDS7:
  almost no token-pressure cost
  gives some morph signal
  not strong enough

expanded UDS22:
  token pressure jumped toward finite/marker band
  decision: broad UDS behaves too much like hard segmentation

morph vocab coverage:
  SP64 exact-piece occurrence share for selected morph surfaces: 0.963019
  safe UDS7 exact-piece occurrence share: 0.962751
  diagnosis: surface availability is not the main bottleneck
```

## New Experiment: Boundary-Biased Unigram Decode

We kept the SP64 model and vocabulary unchanged.

For normal text, we ran a diagnostic Viterbi decoder over SP64 vocab pieces.
The decoder subtracts a lambda penalty when a candidate SP piece crosses a
high-confidence custom-teacher morphology boundary.

Protected routing stays hard and finite. Numeric-like protected spans continue
to use SP passthrough.

This is a decode-time mechanism probe, not a trained constrained objective yet.

Important possible caveat:

```text
Our diagnostic Viterbi decoder uses SP64 .vocab piece scores and a custom
lattice. It may not exactly reproduce SentencePiece's internal Unigram decoder
at lambda 0 because of implementation details such as dummy prefix handling,
normalization, unknown handling, and Unigram model internals.

Therefore lambda 0 already differs from the official SP64 row. We need you to
tell us whether this makes the comparison unfair, or whether it is acceptable
as a diagnostic of an alternative decoder over the same vocabulary.
```

This caveat is important: we do not want to accidentally mistake a decoder
implementation artifact for a morphology result.

## Intrinsic / Pressure Sweep

Counts below exclude per-line EOS in the pressure-only sweep. The tiny-LM
encoding table below includes EOS.

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected |
| --- | ---: | ---: | ---: | --- |
| finite protected numeric-SP floor | 0.171202 | 0.172015 | 0.6913 | 25/25 |
| boundary-biased lambda 0 | 0.162451 | 0.163120 | 0.7422 | 25/25 |
| boundary-biased lambda 2 | 0.162522 | 0.163181 | 0.7606 | 25/25 |
| boundary-biased lambda 4 | 0.163313 | 0.163968 | 0.7701 | 25/25 |
| boundary-biased lambda 8 | 0.178023 | 0.178580 | 0.8225 | 25/25 |

## Tiny-LM 300-Step Calibration

Same tiny causal LM setup:

```text
seq_len=128
batch_size=4
max_steps=300
d_model=256
n_layers=4
n_heads=4
```

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Valid BPB | Test BPB | Challenge F1 | Protected |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| SP64 bare | 0.159020 | 0.159620 | 4.827723 | 4.860352 | 0.7351 | 1/25 |
| finite protected numeric-SP floor | 0.171903 | 0.172734 | 4.875198 | 4.911037 | 0.6913 | 25/25 |
| boundary-biased lambda 4 | 0.164015 | 0.164686 | 4.686700 | 4.721480 | 0.7701 | 25/25 |
| boundary-biased lambda 8 | 0.178725 | 0.179299 | 4.816592 | 4.850946 | 0.8225 | 25/25 |

Current interpretation:

```text
lambda 4 is the balanced candidate.
lambda 8 is a high-F1 reference and still slightly BPB-positive vs SP64, but
it costs more tokens and has worse BPB than lambda 4.
```

## Why This Matters

This is the first v2.0 hybrid row that:

```text
preserves protected spans: 25/25
improves visible Turkish morphology F1 over the protected floor
beats both SP64 and the protected floor on tiny-LM BPB
keeps token pressure close to SP64 for lambda 4
```

It suggests that morphology is useful when applied as decode/objective
preference, not as hard marker dose or broad UDS forcing.

## Questions

Please be critical; we do not want approval-only feedback.

1. Is our interpretation sound?

```text
SP64 already has many morph surfaces, but plain Unigram decode underuses them;
boundary-biased decoding exposes a useful morphology prior.
```

2. Is the lambda-0 comparison methodologically valid?

```text
Our custom Viterbi over .vocab scores is not necessarily identical to official
SentencePiece Unigram decoding. If lambda 0 is already better than SP64, is that
a valid alternative-decoder result, or a red flag that our decoder is not
comparable?
```

3. Should lambda 4 be promoted to the next v2.0 prototype branch, or do we need
   more confirmation before promotion?

4. Is lambda 8 worth further testing, or should it remain only a high-F1/high-cost
   reference?

5. What should be the next confirmation test?

Options:

```text
A. longer tiny-LM run, e.g. 1000-2000 steps
B. second random seed at 300 steps
C. slightly larger tiny model
D. hidden/heldout intrinsic eval
E. noisy/code-mixed robustness canary
F. roundtrip/stateless decode audit
G. official SentencePiece-compatible implementation audit
H. decoder latency/complexity benchmark
```

6. Is the current BPB win at 300 steps likely to be meaningful, or could it be a
   small-model / early-training artifact?

7. Does decode-time boundary bias itself look like a viable tokenizer mechanism,
   or should it only be treated as evidence for a future constrained objective?

8. If we build the next real objective, should it be:

```text
A. boundary-biased Unigram decode wrapper
B. constrained/MorphBPE training objective
C. boundary-weighted Unigram trainer
D. finite protected routing + ordinary SP64 + learned post-decoder only
E. something else
```

9. What hidden failure mode worries you most now?

Examples:

```text
visible challenge overfitting
teacher morphology brittleness
longer training reversing the BPB ranking
decode-time cost/latency
generation robustness
multilingual/code-mixed degradation
stateless decode complexity
```

10. Please audit our earlier rejected branches. Did we reject anything too early?

Examples:

```text
train-only markers
seed appendix
safe UDS7
expanded UDS22
pure custom morphology
finite protected wrapper design
numeric-SP passthrough
```

11. Are we overfitting to visible Challenge F1 even though BPB now looks good?

12. Is our protected-wrapper design distorting the morphology metric?

Observation:

```text
bare SP64 has better Challenge F1 than the protected numeric floor, but breaks
protected spans. Boundary-biased decode recovers F1 while preserving protection.
```

Is this the right way to score protected-aware tokenizers, or should protected
spans be excluded / scored separately in morphology F1?

13. Does the current design scale to multilingual LLM tokenization?

We are Turkish-primary now, but future corpora include English, German, French,
Chinese, Japanese, Korean, Spanish, Russian, code, and mixed text. We do not
want Turkish morphology rules to damage non-Turkish input.

What minimum multilingual/do-no-harm tests would you require before handoff?

14. What minimum evidence would you require before we can send this to the LLM
   team as an experimental tokenizer candidate, not final production?

15. What would you build next in one week?

Please give:

```text
smallest useful next experiment
stop criteria
success criteria
handoff criteria
```

## Current Proposed Next Step

Our proposed next step:

```text
Treat lambda 4 as the current balanced v2.0 candidate.
Run one confirmation step before engineering a heavier constrained objective:
  either longer tiny-LM at lambda 4 vs SP64/floor,
  or hidden/robustness canary if you think eval overfitting is now the larger risk.
Do not return to marker-dose tuning, broad UDS, or seed appendix.
```

Please challenge this plan.
