# v1.6 Confidence Interval Findings

Date: 2026-05-30

Tokenizer behavior: not changed

## Purpose

Advisor feedback flagged that current metrics were point estimates on small,
curated sets. v1.6a adds bootstrap confidence intervals so reports can separate
observed score from sampling uncertainty.

This does not solve annotation uncertainty or hidden-eval independence. It only
answers a narrower question:

```text
If the current visible examples were resampled, how stable would the metric be?
```

## Reports

Core reports:

```text
artifacts/v1_6_ci_expanded.md
artifacts/v1_6_ci_challenge.md
```

All-baseline reports:

```text
artifacts/v1_6_ci_all_expanded.md
artifacts/v1_6_ci_all_challenge.md
artifacts/v1_6_ci_all_en_smoke.md
artifacts/v1_6_ci_all_multilingual_smoke.md
```

Script:

```text
scripts/report_confidence_intervals.py
```

## Key Results

### Expanded Regression Set

`tr_gold_expanded.tsv` remains a policy-regression set, not an independent
quality benchmark.

```text
custom_tr_morph
exact_match_rate: 1.0000 [1.0000, 1.0000]
boundary_f1:      1.0000 [1.0000, 1.0000]
avg_tokens/word:  2.7438 [2.4542, 3.1402]
```

Interpretation:

- The frozen regression behavior is stable on the visible set.
- This still mainly measures policy fidelity, not independent linguistic
  validity.

### Challenge Set

```text
custom_tr_morph
exact_match_rate: 0.4074 [0.3056, 0.5093]
boundary_f1:      0.9220 [0.9043, 0.9382]
avg_tokens/word:  2.1749 [2.0544, 2.3080]
```

Selected baselines on the same challenge set:

| Model | Boundary F1 95% CI | Avg tokens/word 95% CI |
| --- | ---: | ---: |
| custom_tr_morph | 0.9220 [0.9043, 0.9382] | 2.1749 [2.0544, 2.3080] |
| toy_bpe_1000 | 0.6610 [0.6329, 0.6887] | 2.7572 [2.5988, 2.9089] |
| sp_bpe | 0.6497 [0.6228, 0.6758] | 2.7807 [2.6365, 2.9459] |
| sp_unigram | 0.6225 [0.6005, 0.6452] | 2.9321 [2.7930, 3.0761] |
| qwen | 0.3511 [0.3155, 0.3835] | 2.8590 [2.7242, 3.0014] |
| llama | 0.3501 [0.3166, 0.3824] | 2.5744 [2.4441, 2.7235] |
| mistral | 0.5463 [0.5231, 0.5686] | 3.9426 [3.7500, 4.1805] |

Interpretation:

- On visible Turkish morphology-focused evals, custom boundary F1 remains
  clearly separated from these baselines.
- Exact-match uncertainty is wide on the challenge set because `44/108` is a
  modest sample.
- This still does not prove downstream LLM benefit.

## Limits

The bootstrap intervals are useful but narrow:

- They do not measure annotator disagreement.
- They do not make visible evals independent.
- They do not replace hidden/heldout evaluation.
- They do not validate that boundary F1 improves LM loss or downstream quality.

## Smoke Set Reading

English and multilingual smoke intervals are intentionally wide:

```text
en_smoke custom_tr_morph
exact_match_rate: 0.5000 [0.2000, 0.8000]
boundary_f1:      0.7949 [0.6433, 0.9452]

multilingual_smoke custom_tr_morph
exact_match_rate: 0.4000 [0.2000, 0.6000]
boundary_f1:      0.6775 [0.5236, 0.8455]
```

Interpretation:

- These smoke sets are observability tools, not stable benchmark claims.
- They are still useful for finding do-no-harm failures such as apostrophe and
  non-Turkish Latin routing problems.
- They are too small to justify fine-grained language-level conclusions.

## Next Measurement Step

Proceed with v1.6a measurement hardening:

1. Add protected-span break rate to baseline reports.
2. Add natural/demo corpus fertility reporting.
3. Plan independent heldout eval with policy-vs-independent gold and IAA.

Only after that should v1.6b routing guards begin.
