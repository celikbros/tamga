# v2.0 Morph Seed Vocabulary Plan

Date: 2026-06-09

## Context

The train-only marker branch is closed.

Result:

```text
marker shaping improved visible boundary F1
marker shaping worsened tiny-LM BPB versus finite_protected_sp64_floor
more marker dose increased token pressure and BPB
```

The next branch must change the mechanism. We keep:

```text
finite protected routing
marker-free normal encode
stateless decode requirement
```

We stop:

```text
in-stream morphology markers
more marker-density tuning
promoting marker-trained candidates to larger LM probes as-is
```

## Goal

Build a learned tokenizer candidate that uses Turkish morphology as a
vocabulary prior rather than as in-stream markers.

The target is:

```text
finite protected routing
+ learned Unigram/BPE core
+ selected morph seed vocabulary / curated morph pieces
+ UTF-8 byte fallback
+ stateless lossless decode
```

The seed vocabulary should improve Turkish morphology behavior without
forbidding useful learned merges or inflating token pressure.

## Baseline

The true protected null baseline is:

```text
finite_protected_sp64_floor
```

Reason:

```text
bare SP64 has better BPB but breaks protected spans
finite_protected_sp64_floor preserves protected stress 25/25
future candidates must beat or tie this protected floor, not just bare SP64
```

Current calibration:

```text
bare SP64 test BPB:                4.860352
finite protected SP64 test BPB:    4.976850
suffix_chain2 marker test BPB:     5.094965
all_soft marker test BPB:          5.157444
```

## Candidate Mechanism

Use train-only custom morphology analysis to identify suffix/morph pieces that
are likely to help a learned tokenizer.

Candidate categories:

```text
uds_or_seed_candidate
  frequent suffixes with high soft-boundary share and low exact collision risk

seed_bias_candidate
  useful as a prior, but too short or collision-prone to force broadly

protected_tail_review
  suffixes that often appear after apostrophe/protected hard boundaries; these
  should be handled with protected routing rather than blindly forced into
  normal text
```

Important distinction:

```text
not every Turkish suffix should become a user-defined symbol
short suffixes can create false positives
seed/bias is safer than hard forcing when ambiguity is high
```

## First Implementation Step

Script:

```text
scripts/analyze_v2_morph_seed_candidates.py
```

Purpose:

```text
scan train-only soft-morph boundary JSONL
summarize suffix frequencies
measure hard/soft boundary share
measure exact surface collisions with non-suffix pieces
write a private candidate TSV
write a public aggregate report
```

Default input:

```text
artifacts/private/v2_0_soft_morph/soft_morph_boundaries.train.jsonl
```

Default outputs:

```text
artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv
artifacts/v2_0_morph_seed_candidate_analysis.md
```

User-run command:

```powershell
python scripts\analyze_v2_morph_seed_candidates.py --progress 1000
```

This does not train a tokenizer.

## Second Implementation Step

Script:

```text
scripts/select_v2_morph_seed_policy.py
```

Purpose:

```text
turn the suffix candidate analysis into a challenge-blind policy
keep ambiguous/short suffixes as seed-bias candidates, not forced UDS
hold out protected-tail suffixes for finite protected routing review
identify a small safe_uds_candidate_later pool without promoting it yet
```

Default input:

```text
artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv
```

Default outputs:

```text
artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv
artifacts/v2_0_morph_seed_policy_selection.md
```

User-run command:

```powershell
python scripts\select_v2_morph_seed_policy.py
```

This also does not train a tokenizer.

## Gates

Before any tiny-LM run, a morph-seed candidate must pass:

```text
protected stress: 25/25
roundtrip: lossless
test tokens/raw byte: close to finite_protected_sp64_floor
challenge F1: materially above SP64 or at least not below the protected floor
fallback rate: low
```

The first tiny-LM BPB run should include only:

```text
finite_protected_sp64_floor
best morph-seed candidate
optional bare SP64 reference
```

No broad matrix until a candidate passes intrinsic gates.

## Non-Goals

Do not:

```text
tune against visible challenge examples
force all suffixes as user-defined symbols
use morphology markers at normal encode time
build full multilingual morphology layers now
hand off any v2.0 candidate as production tokenizer before BPB evidence
```

## Open Design Questions

The next implementation decision is how to inject the selected morph pieces:

```text
1. user_defined_symbols for only very safe surface pieces
2. seed/bias corpus augmentation for ambiguous pieces
3. constrained Unigram/MorphBPE objective for a later branch
```

The analysis report should decide which of these is safe enough for the first
prototype.
