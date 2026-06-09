# Advisor Request: v2.0 Morphology-Aware Learned Tokenizer Direction

Date: 2026-06-10

## Context For A New Advisor

We are building a Turkish-primary tokenizer for a future LLM project. The long
term goal is not merely to wrap an existing tokenizer, but to investigate
whether Turkish morphology can be used as a useful mathematical/structural
prior for learned tokenization.

The current system is a research prototype, not a production tokenizer.

The high-level idea is:

```text
lossless tokenizer
+ Turkish morphology teacher
+ protected-span routing for code/file/URL/number/date-like spans
+ learned vocabulary for normal text
+ byte/finite fallback where needed
```

We have learned an important distinction:

```text
Pure custom deterministic morphology is valuable as a teacher and diagnostic
reference, but it is too risky and too token-heavy as a direct LLM tokenizer.

Plain SentencePiece/Unigram is compression-efficient but weak on Turkish
morphological boundary preservation and breaks protected spans.

The promising direction appears to be a hybrid learned tokenizer that uses
custom morphology as a soft prior, not as hard segmentation everywhere.
```

We want your critical advice on whether our conclusion is sound, and what the
next mechanism should be.

## Non-Negotiable Requirements

1. Tokenization must be lossless or effectively lossless for LLM pretraining.
2. Protected spans must not be broken:

```text
URLs, file names, code-ish tokens, package/version strings, numbers, dates
```

3. Turkish morphology should improve learned-tokenizer behavior only if the
token-pressure and language-modeling cost are justified.
4. We do not want to tune endlessly against a visible challenge set.
5. We do not want to create an unmaintainable pile of regex exceptions.

## Current Evaluation Sets And Metrics

Visible evals:

| Eval set | Role | Notes |
| --- | --- | --- |
| `tr_gold_expanded.tsv` | frozen policy/spec regression | Useful for conformance, not independent proof |
| `tr_challenge.tsv` | visible challenge/dev | Useful for morphology stress; not hidden |
| `multilingual_smoke.tsv` | smoke / do-no-harm | Small multilingual sanity set |
| `tr_stress_public.tsv` | protected-span stress | Used to check protected preservation |

Main metrics used so far:

```text
boundary F1
exact match vs expected tokenization
tokens/raw byte
protected span preserved count
tiny-LM bits-per-byte for selected branches
```

We know boundary F1 is not by itself LLM evidence. It is a diagnostic proxy.
Bits-per-byte is the better LLM-facing metric, but we only run tiny-LM when a
candidate has passed basic intrinsic/token-pressure gates.

## Baselines And Reference Points

Important reference values:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | --- |
| custom deterministic morphology | n/a | n/a | 0.9220 | 25/25 |
| SP64 Unigram reference | 0.159020 | 0.159620 | ~0.735 | 1/25 |
| finite protected SP64 floor | 0.182112 | 0.183362 | ~0.691 | 25/25 |

Interpretation:

```text
Bare SP64 is not a valid final baseline because it breaks protected spans.
The true protected null baseline is finite_protected_sp64_floor.
```

The deterministic custom tokenizer has strong morphology F1, but it is not yet
a safe production LLM tokenizer. It functions as a teacher/reference.

## Branches We Already Tried

### 1. Train-Only Marker Shaping

Idea:

```text
Insert morphology boundary markers only in the SentencePiece training view.
Normal encode-time text stays marker-free.
```

Results:

| Candidate | Test tokens/raw byte | Challenge F1 | Protected stress |
| --- | ---: | ---: | --- |
| suffix_chain2 marker-stripped | ~0.185337 | 0.7632 | 25/25 |
| all-soft marker-stripped | ~0.196954 | 0.7703 | 25/25 |

Tiny-LM 300-step BPB calibration:

| Candidate | Test BPB |
| --- | ---: |
| SP64 | 4.860352 |
| finite protected SP64 floor | 4.976850 |
| suffix_chain2 | 5.094965 |
| all-soft | 5.157444 |

Decision:

```text
Stop marker-dose tuning.
Markers improved visible morphology F1, but the token-pressure cost did not
pay back in tiny-LM BPB.
```

### 2. Morph Seed Bias Appendix

Idea:

```text
Append selected morph/suffix surfaces as a small train-only frequency-bias
appendix, without using markers and without enforcing user-defined symbols.
```

Weak appendix:

```text
augmentation bytes/base byte: 0.000022
valid/test tokens/raw byte: 0.158312 / 0.158901
finite-protected Challenge F1: 0.6913
```

Strong appendix:

```text
augmentation bytes/base byte: 0.011047
valid/test tokens/raw byte: 0.158315 / 0.158913
finite-protected Challenge F1: 0.6918
```

Decision:

```text
Stop simple seed appendix.
It is compression-safe, but it did not transfer the custom morphology teacher
signal into the learned Unigram vocabulary.
```

### 3. Safe UDS7

Idea:

```text
Use only a tiny, audited set of safe suffix surfaces as SentencePiece
user_defined_symbols.
```

Selected symbols:

```text
ecek
acak
ümüz
ımız
imiz
yecek
umuz
```

Selection came from train-only policy statistics:

```text
long suffix surfaces
low hard-boundary share
zero or near-zero exact surface collision
```

Results:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| SP64 reference | 0.159020 | 0.159620 |
| safe UDS7 | 0.159109 | 0.159684 |

Intrinsic:

| Model | Challenge F1 | Protected stress |
| --- | ---: | --- |
| safe UDS7, bare | 0.7556 | 1/25 |
| finite protected + safe UDS7 | 0.7081 | 25/25 |

Decision:

```text
Safe UDS7 is the best cheap structural morphology prior so far.
It gives a real morphology signal at almost no token-pressure cost.
But it is still not strong enough for tiny-LM or LLM handoff.
```

### 4. Expanded UDS22

Idea:

```text
Conservatively expand UDS beyond the 7-symbol pool using train-only thresholds.
```

Selection:

```text
recommendation == uds_or_seed_candidate
min_count >= 100
surface_len >= 3
hard_share <= 0.01
exact_collision_rate <= 0.001
```

Selected symbols: 22.

Results:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| safe UDS7 | 0.159109 | 0.159684 |
| expanded UDS22 | 0.183675 | 0.184059 |
| finite protected SP64 floor | 0.182112 | 0.183362 |
| suffix_chain2 marker branch | 0.184500 | 0.185337 |

Decision:

```text
Stop UDS expansion.
UDS7 is useful, but broadening UDS quickly behaves like hard segmentation and
raises token pressure into the marker/floor band.
```

## Current Interpretation

Our current internal conclusion:

```text
1. Keep finite protected routing.
2. Keep safe UDS7 as a small useful prior.
3. Stop marker-dose tuning.
4. Stop seed appendix.
5. Stop broad UDS expansion.
6. Move to a constrained/MorphBPE-style learned objective, or another learned
   mechanism that uses morphology as a soft preference rather than hard forcing.
```

The central design problem is now:

```text
How do we let the learned tokenizer benefit from Turkish morphological teacher
signals without forcing many suffixes as hard boundaries and without increasing
tokens/raw byte too much?
```

## Candidate Next Direction: Constrained / MorphBPE-Style Objective

We are considering a learned tokenizer where the custom deterministic morphology
engine provides boundary hints, but the learned tokenizer can override them
when compression or language-modeling evidence justifies it.

Possible mechanisms:

```text
1. Morphology-aware BPE merge scoring:
   penalize merges that cross high-confidence morphology boundaries, but do not
   forbid them.

2. Boundary-weighted Unigram:
   train Unigram with a weak prior that favors pieces aligned to frequent,
   reliable morph surfaces.

3. Protected-aware pretokenization:
   hard boundaries only for protected spans / whitespace / script transitions,
   soft boundaries for morphology.

4. Safe UDS7 retained:
   only the tiny proven-safe set remains as hard user-defined symbols.

5. Byte/finite fallback:
   keep lossless fallback for rare/unseen material.
```

## What We Need From You

Please be critical. We do not want approval-only feedback.

### Main Questions

1. Is our current conclusion sound?

```text
Safe UDS7 helps, UDS22 is too costly, marker-dose tuning and seed appendix are
not the right next levers.
```

2. Would you agree that the next meaningful branch should be constrained /
MorphBPE-style learning rather than more UDS or more marker policies?

3. If yes, what is the simplest constrained objective worth implementing first?

Options we are considering:

```text
A. Soft penalty against crossing high-confidence morph boundaries during BPE
   merge selection.
B. Reward/seed pieces that exactly match high-confidence morph surfaces, but
   do not force them as UDS.
C. Two-channel training view: hard protected pretokenization + soft morph
   boundary metadata.
D. Train ordinary SP/Unigram, then post-hoc adjust vocabulary with morph-aware
   replacement/pruning.
E. Something else.
```

4. How should the objective trade off compression and morphology?

For example:

```text
score(pair) = frequency(pair) - lambda * boundary_crossing_penalty
```

What should count as a boundary crossing? Should penalties differ for:

```text
derivational suffixes
inflectional suffixes
case/possessive suffixes
negative suffix
tense/aspect suffix
protected-tail suffixes
```

5. Should safe UDS7 stay as hard user-defined symbols in the next branch, or
should even those become soft hints?

6. Are we over-valuing boundary F1?

We know it is not final LLM evidence. But it has helped diagnose whether
morphology signal transferred into the learned tokenizer. What intrinsic metric
would you add before tiny-LM?

7. When should we unblock tiny-LM BPB again?

Possible gate:

```text
finite protected stress: 25/25
tokens/raw byte: preferably <= 0.17, absolutely not near 0.184 unless F1 gain is large
Challenge F1: must improve materially over finite_protected_sp64_floor and safe UDS7
```

Is this gate too strict, too weak, or mis-specified?

8. Does finite protected routing itself need redesign?

Observation:

```text
Bare learned models often have higher visible boundary F1 than the finite
protected wrapper, but bare models break protected spans badly.
```

Should we improve the protected wrapper scoring/segmentation, or accept the
F1 drop as a cost of correct protected behavior?

9. What is the most likely hidden failure mode in our current reasoning?

Examples:

```text
visible challenge overfitting
token-pressure proxy too strict
custom morphology teacher too brittle
small pilot corpus not representative
protected routing distorting morphology metrics
SentencePiece UDS behavior not comparable to a custom objective
```

10. If this were your project, what would you build next in one week?

Please give:

```text
the smallest useful experiment
the stop criteria
the success criteria
the artifact/results you would want to see before LLM-team handoff
```

## Our Current Proposed Next Step

Our current proposed next step is:

```text
Build a small prototype MorphBPE / constrained-BPE trainer on the 20k pilot
split.

Use:
  hard boundaries: protected spans, whitespace, script transitions
  soft boundaries: high-confidence morphology boundaries from custom teacher
  safe hard symbols: possibly UDS7 only

Compare against:
  SP64
  finite_protected_sp64_floor
  safe_uds_unigram_64000

Report:
  tokens/raw byte
  Challenge F1
  protected stress
  category F1
  only then maybe tiny-LM BPB
```

Please challenge this plan. If constrained/MorphBPE is premature, tell us what
to do instead.
