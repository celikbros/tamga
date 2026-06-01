# Advisor Review Request: v1.8 Local LM Probe

Date: 2026-06-01

## Context

We are building a Turkish-primary, multilingual-aware tokenizer. The current
tokenizer is a research prototype, not a production tokenizer and not a final
LLM tokenizer selection.

The current tokenizer design is:

```text
high-precision deterministic Turkish morphology-aware tokenization
+ protected span handling
+ fallback behavior
```

The project goal is not to prove that morphological boundary F1 alone is enough.
The next question is whether the visible boundary advantage produces any useful
language-modeling signal.

## Current Status

Visible eval status:

| Eval set | Role | Current result |
| --- | --- | ---: |
| `tr_gold_expanded.tsv` | frozen policy regression | 50/50 exact, boundary F1 1.0000 |
| `tr_challenge.tsv` | visible challenge/dev | 44/108 exact, boundary F1 0.9220 |

Important caveat:

```text
tr_gold_expanded is policy-shaped and must be treated as regression/spec
conformance, not independent quality proof.
```

## SentencePiece Baseline Sweep

We trained clean local SentencePiece BPE and Unigram baselines on:

```text
data/train/claim_grade/celik_gold_clean_pilot.txt
```

This is a 100k-line clean pilot derived from the local clean corpus. It is not a
hidden eval set and not final pretraining evidence.

Sweep range:

```text
1k / 4k / 8k / 16k / 32k / 64k
BPE and Unigram
```

Key `tr_challenge.tsv` results:

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 | 44/108 |
| sp_bpe_32000_clean | 2.1645 | 0.6819 | 0/108 |
| sp_unigram_32000_clean | 2.1932 | 0.7353 | 0/108 |
| sp_bpe_64000_clean | 1.9817 | 0.6926 | 0/108 |
| sp_unigram_64000_clean | 2.0078 | 0.7327 | 0/108 |

Interpretation so far:

```text
The custom tokenizer keeps a visible boundary-F1 lead over SP BPE/Unigram,
including near the same token fertility. However, 64k SP uses fewer tokens per
word. Boundary F1 does not settle the LLM-tokenizer question.
```

## Leakage Hygiene

We checked eval leakage against the 100k pilot used for SP training:

| Eval set | Raw exact | Strict normalized full | Partial 8-gram | Notes |
| --- | ---: | ---: | ---: | --- |
| gold | 0 | 0 | 0 | 9 one-word `short_full` hits |
| challenge | 0 | 0 | 0 | no hits |

The one-word `short_full` hits are not treated as sentence leakage.

We also scanned the full clean corpus for multi-word eval overlap. That is
relevant for future LM eval hygiene, but it does not change the current SP pilot
comparison.

## Downstream Prep Already Done

We prepared a 20k-line raw split for local LM probing:

```text
train: 16,000 lines
valid: 2,000 lines
test:  2,000 lines
seed:  20260601
```

Corpus:

```text
data/train/claim_grade/celik_gold_clean_pilot.txt
```

Prepared tokenizer variants:

```text
custom_tr_morph
unicode_char
sp_bpe_8000_clean
sp_unigram_8000_clean
sp_bpe_16000_clean
sp_unigram_16000_clean
sp_bpe_32000_clean
sp_unigram_32000_clean
sp_bpe_64000_clean
sp_unigram_64000_clean
```

Validation split prep metrics:

| Tokenizer | Avg tokens/word | Tokens/byte | Bytes/token |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 1.4931 | 0.170166 | 5.8766 |
| sp_bpe_32000_clean | 1.5014 | 0.171116 | 5.8440 |
| sp_unigram_32000_clean | 1.4844 | 0.169170 | 5.9112 |
| sp_bpe_64000_clean | 1.3776 | 0.156997 | 6.3696 |
| sp_unigram_64000_clean | 1.3703 | 0.156169 | 6.4033 |
| unicode_char | 7.0540 | 0.803931 | 1.2439 |

This means:

```text
custom_tr_morph is close to the 32k SP baselines in fertility.
64k SP is more compressed.
The local LM probe must compare byte-normalized loss, not token perplexity.
```

## Proposed v1.8 Work

We are considering a small local LM probe before any v2.0 or LLM-team final
handoff.

This would not be final LLM evidence. It would be an early screening test:

```text
Does the morphology-aware tokenizer help, hurt, or tie clean SP baselines on
byte-normalized LM loss?
```

Proposed tokenizer comparison set:

```text
custom_tr_morph
sp_unigram_32000_clean
sp_bpe_32000_clean
sp_unigram_64000_clean
sp_unigram_16000_clean
unicode_char
```

Primary metrics:

```text
validation bits-per-byte
test bits-per-byte
```

Secondary metrics:

```text
tokens/sec
bytes/sec
GPU/CPU memory
max effective context in bytes
roundtrip/decode failures
training stability
```

Fairness rule:

```text
same raw split
same architecture
same optimizer/schedule
same budget definition
same seed if possible
report both tokens seen and bytes seen
```

## Candidate Tiny LM Setup

We have not implemented this yet. A possible first probe:

```text
5M-30M parameter causal LM
4-8 transformer layers
fixed token context, with byte-normalized reporting
1 seed first; 3 seeds only if the first result is ambiguous
small enough to run locally
```

The exact model size and budget are open for review.

## Questions For You

Please be critical. We are not looking for approval-only feedback.

1. Is this local bits-per-byte probe the right next step, or should we defer all
   LM loss testing until v2.0?

2. Is the tokenizer comparison set fair? Should we include/exclude any of:
   `sp_bpe_64000_clean`, `sp_bpe_16000_clean`, 8k baselines, or an existing
   production tokenizer?

3. What is the fairest training budget?
   - fixed tokens,
   - fixed bytes,
   - fixed wall-clock,
   - or report multiple budget views?

4. Is bits-per-byte sufficient as the primary metric for this screening probe,
   or should we use another byte-normalized objective?

5. What model size is large enough to make the signal meaningful but still small
   enough not to waste time?

6. What failure result would make you stop recommending the custom tokenizer for
   LLM use, even if boundary F1 stays high?

7. Are there leakage, corpus, or split risks that still make this probe
   misleading?

8. Are we accidentally comparing a rule-based tokenizer against SP baselines in
   a way that favors our design too much?

9. Should the local probe include multilingual/code-mixed validation slices, or
   should v1.8 stay Turkish-primary and leave multilingual probing to v2.0?

10. What would you require before this becomes safe to hand to the LLM team as
    anything more than an experimental screening package?

## Current Recommendation

Our current internal recommendation is:

```text
Do not send the tokenizer as a final LLM integration candidate before v2.0.
Do run or at least design a small local bits-per-byte probe in v1.8.
Use the result to decide whether the morphology-aware path deserves deeper v2.0
investment.
```

Please challenge this recommendation if it is premature or methodologically
weak.
