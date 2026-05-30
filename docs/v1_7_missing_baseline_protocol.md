# v1.7 Missing Baseline Protocol

Date: 2026-05-31

## Purpose

This protocol defines the missing tokenizer baselines needed before stronger
claims about `tr-centric-tokenizer`.

Current comparisons are useful but incomplete:

- custom deterministic tokenizer
- unicode character baseline
- toy BPE
- local demo SentencePiece BPE/Unigram
- Qwen, Mistral, LLaMA tokenizer references

These show that the custom tokenizer preserves the project-defined Turkish
boundaries better than general-purpose tokenizers on visible eval sets. They do
not yet prove that the approach is the best practical Turkish tokenizer.

## Main Risk Addressed

The main methodological risk is:

```text
We may be comparing a Turkish morphology-aware tokenizer against baselines that
were not optimized for Turkish morphology.
```

Therefore v1.7 should add or specify baselines that are closer competitors.

## Baseline Classes

### B1: Turkish-Trained SentencePiece BPE

Purpose:

```text
Measure whether a normal subword tokenizer trained on Turkish data can close the
boundary-F1 and fertility gap.
```

Required variants:

```text
vocab_size: 1k, 4k, 8k, 16k, 32k
model_type: bpe
normalization: documented
training corpus: documented
```

Current repo has a small demo BPE/Unigram setup. That is enough for prototype
signals, not for strong claims.

### B2: Turkish-Trained SentencePiece Unigram

Purpose:

```text
Unigram is often a stronger morphology-adjacent subword baseline than BPE.
```

Required variants:

```text
vocab_size: 1k, 4k, 8k, 16k, 32k
model_type: unigram
```

Primary comparison:

```text
custom_tr_morph vs Turkish-trained SP Unigram at comparable fertility
```

### B3: Morfessor

Purpose:

```text
Compare against a classic unsupervised morphology segmentation baseline.
```

Status:

```text
Not implemented yet.
```

Decision needed:

- whether to add Morfessor as an optional dependency
- whether to shell out to an external Morfessor CLI
- whether to keep it as a protocol-only baseline until dependency policy is
  decided

Recommended v1.7 action:

```text
Document and prepare the wrapper interface, but do not make Morfessor mandatory.
```

### B4: Turkish-Specific Or Multilingual Encoder Tokenizers

Purpose:

```text
Compare against tokenizers that are closer to Turkish NLP practice than general
LLM tokenizers.
```

Candidate models:

```text
BERTurk
dbmdz/bert-base-turkish-cased
xlm-roberta-base
google/mt5-small
facebook/mbart-large-50
```

These should be treated as tokenizer references, not model-quality claims.

### B5: Production LLM Tokenizers

Already partially measured:

```text
Qwen/Qwen2.5-0.5B
mistralai/Mistral-7B-v0.1
meta-llama/Llama-3.2-1B
```

Purpose:

```text
Represent common real-world tokenizer choices for LLM projects.
```

Interpretation rule:

```text
Do not claim "we beat LLaMA" as a general model-quality claim.
Report this as Turkish morphological boundary preservation and fertility only.
```

## Required Metrics

For every baseline, report:

```text
exact_match_vs_gold
boundary precision / recall / f1
avg_tokens/example
avg_tokens/word
protected span break rate
roundtrip/decode status when available
byte/unknown/fallback rate when available
bootstrap confidence intervals
```

For multilingual or non-Turkish smoke sets, report per category. Aggregate-only
averages can hide language-specific failures.

## Evaluation Sets

Use these visible sets first:

```text
data/eval/tr_gold_expanded.tsv
data/eval/tr_challenge.tsv
data/eval/en_smoke.tsv
data/eval/multilingual_smoke.tsv
data/eval/tr_stress_public.tsv
```

Then use heldout sets when available:

```text
data/eval/private/tr_heldout_eval.tsv
```

Private examples must not be published; only aggregate metrics should be.

## Training Corpus Requirements

For Turkish-trained SentencePiece baselines, the current demo corpus is not
enough for strong claims.

Minimum practical corpus options:

```text
small_demo: existing data/train/tr_bpe_train.txt
medium_public: curated public Turkish text sample
domain_mixed: news + user-generated + technical/code-mixed
```

Every report must state:

```text
corpus source
line count
word count
dedup policy
eval leakage check
normalization
vocab size
model type
```

## Leakage Rules

Before training a Turkish baseline, run leakage checks against:

```text
tr_gold_expanded.tsv
tr_challenge.tsv
tr_heldout_eval.tsv when available
```

If exact eval sentences are found in training data, that run must be labeled
`leaky` and not used for claims.

## Pareto Reporting

For BPE/Unigram baselines, do not report a single vocabulary size only.

Required report shape:

```text
vocab_size | avg_tokens/word | boundary_f1 | protected_break_rate
```

The useful question is:

```text
At comparable token fertility, does morphology-aware segmentation preserve
Turkish boundaries better?
```

## Interpretation Rules

Allowed claims:

```text
On visible policy-gold Turkish boundary sets, custom_tr_morph preserves the
project-defined boundaries better than these baselines.
```

Not allowed yet:

```text
This tokenizer improves LLM quality.
This tokenizer is production-ready.
This tokenizer is the best Turkish tokenizer.
This tokenizer solves Turkic/multilingual routing.
```

Those require heldout eval and downstream probes.

## Implementation Plan

### Step 1: Protocol-Only Commit

Create this document and update roadmap references.

### Step 2: Script Inventory

Check whether existing scripts already support:

```text
SentencePiece multi-vocab training
HF tokenizer comparison
protected span reporting
confidence interval reporting
fertility reporting
```

### Step 3: Add Baseline Config File

Recommended future file:

```text
configs/v1_7_baselines.toml
```

It should list baseline names, model IDs, vocab sizes, local paths, and whether
download is allowed.

### Step 4: Generate Visible Reports

Recommended future artifacts:

```text
artifacts/v1_7_baseline_matrix_expanded.md
artifacts/v1_7_baseline_matrix_challenge.md
artifacts/v1_7_baseline_matrix_smoke.md
artifacts/v1_7_sentencepiece_pareto.md
```

### Step 5: Decide Downstream Probe Scope

After baseline matrix is visible, move to:

```text
docs/v1_7_downstream_probe_protocol.md
```

## Success Criteria

v1.7 missing-baseline work is complete when:

```text
baseline classes are documented
required metrics are fixed
leakage rules are fixed
SentencePiece Pareto plan is fixed
HF reference model list is fixed
Morfessor dependency decision is recorded
```

No tokenizer behavior change is required for this workstream.
