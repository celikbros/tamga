# v1.5 Baseline Findings

Date: 2026-05-30

Tokenizer behavior: not changed

## Summary

v1.5 added comparison against stronger tokenizer baselines:

- toy BPE continuity baseline
- local SentencePiece BPE
- local SentencePiece Unigram
- Qwen tokenizer reference
- Mistral tokenizer reference
- official Meta LLaMA tokenizer reference
- Unicode character diagnostic baseline

The main result is:

```text
On the controlled Turkish morphology evals, tr-centric-tokenizer preserves
Turkish gold morpheme boundaries much better than the compared subword
tokenizers, while using comparable or fewer tokens per word.
```

This is not a claim that the prototype is production-ready. It is evidence that
the morphology-aware direction has a strong signal.

## Expanded Regression Set

Dataset:

```text
data/eval/tr_gold_expanded.tsv
```

This is the frozen 50-example regression set. It is small and hand-designed, so
it should be read as a core-behavior check, not a broad benchmark.

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.7438 | 1.0000 | 50/50 |
| toy_bpe_1000 | 2.7438 | 0.6277 | 1/50 |
| sp_bpe | 2.7273 | 0.6263 | 1/50 |
| sp_unigram | 3.0744 | 0.6325 | 0/50 |
| qwen | 3.0661 | 0.3317 | 0/50 |
| llama | 2.9008 | 0.3259 | 0/50 |
| mistral | 4.3306 | 0.5423 | 0/50 |
| unicode_char | 7.5041 | 0.4947 | 0/50 |

The official Meta LLaMA reference was evaluated with:

```text
meta-llama/Llama-3.2-1B
```

Reports:

```text
artifacts/v1_5_llama_report_expanded.md
artifacts/v1_5_llama_report_challenge.md
```

### Interpretation

The strongest comparison here is against `toy_bpe_1000` and `sp_bpe`, because
their token budgets are close to `custom_tr_morph`.

```text
custom_tr_morph: avg_tokens/word=2.7438, boundary_f1=1.0000
sp_bpe:          avg_tokens/word=2.7273, boundary_f1=0.6263
toy_bpe_1000:    avg_tokens/word=2.7438, boundary_f1=0.6277
```

At nearly the same token budget, the morphology-aware tokenizer preserves the
gold morpheme boundaries much better.

## Challenge Set

Dataset:

```text
data/eval/tr_challenge.tsv
```

This set is visible and intentionally harder. It is used for error analysis and
planning, not for final claims.

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 | 44/108 |
| toy_bpe_1000 | 2.7572 | 0.6610 | 0/108 |
| sp_bpe | 2.7807 | 0.6497 | 0/108 |
| sp_unigram | 2.9321 | 0.6225 | 0/108 |
| qwen | 2.8590 | 0.3511 | 0/108 |
| llama | 2.5744 | 0.3501 | 0/108 |
| mistral | 3.9426 | 0.5463 | 0/108 |
| unicode_char | 6.6214 | 0.4949 | 0/108 |

### Interpretation

The challenge result is more important than the expanded result because the
custom tokenizer no longer has perfect exact match. Even there, boundary F1
stays much higher than the compared baselines:

```text
custom_tr_morph: boundary_f1=0.9220
sp_bpe:          boundary_f1=0.6497
sp_unigram:      boundary_f1=0.6225
toy_bpe_1000:    boundary_f1=0.6610
mistral:         boundary_f1=0.5463
qwen:            boundary_f1=0.3511
```

This suggests that the deterministic Turkish morphology layer is not merely
memorizing the frozen regression set.

## What This Does Not Prove

These results do not prove:

- the tokenizer is production-ready
- the tokenizer is better for every downstream LLM task
- Qwen or Mistral are poor general tokenizers
- the current gold set is a complete independent linguistic benchmark
- deterministic rules alone are enough for v2.0

Qwen and Mistral are general multilingual LLM tokenizers. They were not trained
to optimize Turkish morpheme boundary F1. Their low boundary F1 here should be
interpreted as a task mismatch, not as general tokenizer failure.

## What This Does Support

These results support the following narrower claim:

```text
For selected Turkish morphology-focused eval sets, a Turkish-centered
morphology-aware tokenizer can preserve morpheme boundaries substantially better
than general subword tokenizers at comparable or lower token cost.
```

This is the right research signal for continuing toward:

```text
deterministic high-precision Turkish morphology layer
+ MorphBPE or Unigram fallback
+ protected code/file/URL/number spans
+ byte fallback for lossless multilingual coverage
```

## Current Risk Assessment

| Risk | Status |
| --- | --- |
| Overfitting to small gold sets | Still present. Hidden/heldout or larger public eval is needed. |
| False-positive Turkish suffix splitting | Still the highest tokenizer-quality risk. |
| Surface-stem vs lemma fragmentation | Accepted for v1.x; should be studied in v2.0 metadata or MorphBPE design. |
| Multilingual/Turkic silent errors | Must remain do-no-harm in v1.x; needs router/gating in v2.0. |
| External tokenizer boundary mapping | Approximate for HF tokenizers unless offset mapping is added. |

## Recommended Next Step

Do not add broad new morphology rules yet.

Recommended order:

1. Add offset-aware external tokenizer boundary extraction where possible.
2. Add protected-span metrics to `compare_real_tokenizers.py`.
3. Try an accessible LLaMA-family tokenizer if license/access allows.
4. Expand public eval cautiously, especially negative words, ambiguity, and
   code-mixed loanwords.
5. Begin a small MorphBPE design RFC only after the baseline methodology is
   stable.

## Report Files

```text
artifacts/v1_5_real_tokenizer_report_all_expanded.md
artifacts/v1_5_real_tokenizer_report_all_challenge.md
artifacts/v1_5_qwen_report_expanded.md
artifacts/v1_5_qwen_report_challenge.md
artifacts/v1_5_mistral_report_expanded.md
artifacts/v1_5_mistral_report_challenge.md
artifacts/v1_5_real_tokenizer_report_with_toy_expanded.md
```
