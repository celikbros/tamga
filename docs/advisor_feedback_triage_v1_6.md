# Advisor Feedback Triage for v1.6

Date: 2026-05-30

Tokenizer behavior: not changed

## Purpose

This document triages the latest advisor feedback on:

- v1.5 baseline findings
- English/multilingual smoke findings
- v1.6 do-no-harm routing plan

The goal is to avoid rushing into brittle guard implementation before the
methodology is strong enough.

## High-Level Read

The advisors broadly agree that:

- The project is on a promising path.
- The Turkish morphology-aware direction has a real signal.
- The tokenizer is not production-ready.
- v1.6 should not add broad Turkish morphology rules.
- Do-no-harm routing is important.
- Hidden/heldout evaluation is now necessary.
- Boundary F1 is useful but not enough.

The most important correction:

```text
The top risk is not only multilingual leakage.
The top risk is construct validity: are we measuring a real tokenizer-quality
claim, or only compliance with our own policy gold?
```

## Advisor Consensus

### What They Support

| Topic | Consensus |
| --- | --- |
| Surface stem | Keep it for tokenizer output; do not lemmatize in v1.x. |
| v1.6 scope | Focus on routing/protection, not new broad morphology rules. |
| Baseline comparisons | Useful, but should be framed carefully. |
| Hidden eval | Needed now, not later. |
| Multilingual/Turkic | v1.x should be do-no-harm; full Turkic morphology is v2.0+ and risky. |

### What They Warn Against

| Risk | Advisor concern |
| --- | --- |
| Circular evaluation | `50/50` may measure policy compliance, not linguistic quality. |
| Weak sample size | `50`, `108`, `10`, and `20` examples are too small for broad claims. |
| Missing baselines | Morfessor, Turkish-trained BPE/Unigram at larger vocab, BERTurk/XLM-R/mT5 tokenizers. |
| Downstream gap | Boundary F1 has not yet been tied to LM quality or downstream behavior. |
| Routing false positives | Guards themselves are classifiers and can introduce new errors. |

## Revised Risk Ranking

Previous internal ranking put multilingual leakage first.

After advisor review, the revised ranking is:

1. **Construct validity / independent evaluation**
   - Policy gold may be circular.
   - Boundary F1 may not predict language-model quality.
   - Need independent gold, IAA, and at least one downstream or LM-normalized
     metric.

2. **Small curated evals / uncertainty not reported**
   - Current metrics are point estimates.
   - Need bootstrap confidence intervals and larger heldout sets.
   - Need natural corpus fertility/span-break/fallback reporting.

3. **Multilingual and code-mixed routing leakage**
   - Real and important, but more engineering-bounded than risks 1 and 2.
   - v1.6 should address it carefully and with regression tracking.

4. **Baseline fairness**
   - Need Turkish-trained larger BPE/Unigram baselines.
   - Need morphology-aware baselines such as Morfessor.
   - Need Turkish/multilingual model tokenizers such as BERTurk, XLM-R, mT5.

## What We Should Change In Our Framing

Avoid:

```text
We beat Qwen/LLaMA/Mistral.
```

Use:

```text
On selected Turkish morphology-focused evals, the Turkish-centered tokenizer
preserves policy-gold morpheme boundaries better than general subword
tokenizers at comparable or lower token cost.
```

Even better after independent eval:

```text
On independent Turkish morphology boundary annotations, ...
```

## v1.6 Plan Adjustment

The earlier v1.6 plan remains directionally right, but implementation order
should become more conservative.

### Revised Order

1. **Measurement first**
   - Add bootstrap confidence intervals for boundary F1 and exact match.
   - Add protected-span break metrics to real-baseline comparison.
   - Add natural/demo corpus fertility report across tokenizers.

2. **Low-risk technical/script protection**
   - Technical comparator spans: `transformers>=4.40`, `tokenizers>=0.19`.
   - Arabic/Greek script-span fallback.

3. **Apostrophe guard**
   - English/French/Italian apostrophes.
   - Must preserve Turkish apostrophe behavior:
     `Türkiye'den`, `Ali'nin`, `README.md'yi`, `2026'da`.

4. **Non-Turkish Latin guard**
   - `Straße`, `niño`, `Bogotá`, `università`.
   - Needs careful tests because it is a routing classifier.

5. **Azerbaijani guard**
   - Keep as do-no-harm/pass-through in v1.x.
   - Do not claim Azerbaijani morphology.
   - Avoid deterministic Turkic morphology expansion before v2.0.

### Why This Change?

Advisors flagged that guard rules can create new hidden regressions. Therefore
we should first improve measurement, then implement the least ambiguous routing
fixes.

## Immediate Action Items

### A1: Add Confidence Intervals

Add script support for bootstrap CIs:

```text
boundary_f1_ci
exact_match_ci
avg_tokens_per_word_ci
```

Apply to:

```text
tr_gold_expanded.tsv
tr_challenge.tsv
en_smoke.tsv
multilingual_smoke.tsv
```

### A2: Add Protected Span Break Rate To Baseline Reports

Current smoke reports know protected spans, but real-baseline reports mostly
compare boundary F1.

Add:

```text
protected_span_preserved
protected_span_broken
protected_span_break_rate
```

### A3: Add Natural Corpus Fertility Report

Use existing demo/public corpus first:

```text
data/train/tr_bpe_train.txt
```

Report per tokenizer:

```text
avg_tokens/word
avg_tokens/line
byte/unknown fallback proxy
protected span behavior where applicable
```

This is not a final benchmark, but it reduces curated-set bias.

### A4: Plan Independent Heldout Eval

Revive hidden/heldout evaluation as a methodological requirement, not optional
decoration.

Suggested target:

```text
300-500 sentences minimum for first real heldout
2 independent annotators
IAA report
policy gold + independent gold distinction
```

### A5: Add Missing Baseline Plan

Plan, not necessarily implement immediately:

- Morfessor 2.0
- Turkish-trained SentencePiece BPE/Unigram at larger vocab sizes
- BERTurk tokenizer
- XLM-R tokenizer
- mT5 tokenizer

## What Not To Do Next

Do not:

- start with Azerbaijani morphology rules
- add broad suffix inventory
- chase smoke exact-match with ad hoc exceptions
- claim production multilingual behavior
- claim downstream LLM benefit before a small LM/probe experiment

## Updated Next Step

The next commit should not be a tokenizer behavior change.

Recommended next work:

```text
v1.6a: evaluation-strengthening
```

Minimum scope:

1. bootstrap CI script/report
2. protected-span break metric plan or implementation
3. updated findings docs with uncertainty language

Only after that:

```text
v1.6b: low-risk do-no-harm routing guard batch
```

## Short Answer

We are still on a good path, but the advisors are right:

```text
The next smart move is not more rules.
The next smart move is stronger evidence and safer routing metrics.
```
