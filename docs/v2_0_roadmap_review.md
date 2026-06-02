# v2.0 Roadmap Review

Date: 2026-06-02

## Current Position

```text
v1.x deterministic Turkish morphology core: useful but not LLM-final
v1.8 tiny-LM smoke: informative but not decisive
v2.0 direction: learned hybrid vocabulary with morphology as soft prior
```

The project should not return to broad hand-written morphology rules now. The
main engineering problem is no longer "can we split Turkish suffixes?" It is:

```text
can we keep morphology/protection signal while reducing lossless LM token pressure?
```

## What Is Done

Evidence and hygiene:

```text
visible eval baselines
SentencePiece sweep
eval leakage checks
tiny-LM smoke
token accounting audit
soft-morph materialization
seed vocab analysis
seed policy selection
```

Most important results:

```text
pure custom lossless mode is too token-expensive for direct LLM handoff
standard custom is close to SP64 in token pressure but not generation-safe
lossless+64k byte fallback is about 2.66x-2.67x SP64 tokens/byte on valid/test
64k seed policy covers 95.11% of non-whitespace seed occurrences
suffix inventory is small and cheap to seed
main remaining pressure is word_start long-tail + whitespace serialization
```

## Current Candidate

```text
protected_hard_soft_morph_seeded_sp64
```

Policy:

```text
hard boundaries: whitespace/protected/script/punctuation
soft boundaries: morphology suffix boundaries
seed all suffix tokens
seed punctuation/symbol tokens
seed protected surface tokens only when count >= 10
seed top word_start pieces up to 64k budget
do not seed the word_start long-tail by default
learned tokenizer must handle long-tail without byte fallback explosion
```

## Roadmap

### Phase 1: Candidate Serialization

Goal:

```text
turn the selected seed policy + soft/hard boundary JSONL into a training-ready
prototype corpus
```

Deliverables:

```text
private candidate training corpus
public serialization report
roundtrip design note
tokens/byte estimate before training
```

Current script:

```text
scripts/materialize_v2_candidate_serialization.py
scripts/materialize_v2_candidate_split_views.py
```

Current output:

```text
artifacts/v2_0_candidate_serialization.md
artifacts/v2_0_candidate_split_views.md
hard segments/raw byte: 0.130918
valid hard segments/raw byte: 0.130737
test hard segments/raw byte: 0.130560
train-view/raw bytes: 1.511092
```

Phase 1 status:

```text
train/valid/test candidate views are materialized
```

Gate:

```text
do not train a tokenizer if the serialization itself cannot be decoded losslessly
or if it already looks close to pure custom token pressure
do not evaluate a learned tokenizer on train-only serialization
```

### Phase 2: Learned Tokenizer Prototype

Goal:

```text
train one small learned tokenizer candidate using the candidate serialization
```

Initial candidate:

```text
protected_hard_soft_morph_seeded_sp64
```

Control baselines:

```text
custom_tr_morph_lossless
sp_bpe_64000_train_only
hybrid_hard_unigram_64000
```

Gate:

```text
candidate must materially reduce tokens/byte versus custom_lossless_64000_byte_fallback
candidate must not destroy protected-span behavior
candidate must keep visible boundary F1 advantage over SP64
```

### Phase 3: Intrinsic Evaluation

Run only after one candidate exists:

```text
roundtrip
tokens/byte
avg tokens/word
byte fallback/source fallback rate
protected span break rate
boundary F1 on gold/challenge
canary diagnostics
```

Gate:

```text
if protected span break rate is nonzero, fix serialization before LM probes
if tokens/byte is still close to pure custom, redesign candidate before LM probes
```

### Phase 4: Tiny-LM Screening

Run only for the best 1-2 candidates.

Budget views:

```text
fixed-token/fixed-step
approx iso-byte
optional iso-compute control if results are close or advisor asks
```

Gate:

```text
do not treat tiny-LM as final LLM proof
do not hand off if candidate loses badly on both fixed-token and iso-byte views
```

### Phase 5: Experimental Handoff Package

Only if Phase 2-4 pass:

```text
tokenizer artifact
training recipe
roundtrip/protected-span report
baseline comparison table
tiny-LM BPB report
known limitations
integration notes for LLM team
```

This handoff is experimental, not final production approval.

## Stop Conditions

Stop or redesign the v2.0 candidate if:

```text
lossless roundtrip fails
protected spans break
tokens/byte remains near pure custom
word_start long-tail still falls to byte fallback heavily
implementation requires hand-writing Turkic morphology for each language
```

## What Not To Do Now

```text
do not expand Turkish rules against visible challenge examples
do not train a full LLM
do not build Turkic morphology layers
do not send pure custom as final LLM tokenizer
do not seed every protected surface form
do not run broad tiny-LM matrices before a real v2.0 candidate exists
```

## Next Immediate Step

Build Phase 1:

```text
candidate serialization for protected_hard_soft_morph_seeded_sp64
```

This is the smallest useful step toward LLM readiness.
