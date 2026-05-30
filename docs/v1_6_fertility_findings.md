# v1.6 Natural/Demo Corpus Fertility Findings

Date: 2026-05-30

Tokenizer behavior: not changed

## Purpose

Advisor feedback warned that visible gold/challenge sets are curated. v1.6a adds
a corpus-level fertility report on the existing demo training corpus:

```text
data/train/tr_bpe_train.txt
```

This is not a production benchmark and not a hidden eval. It is a small
distribution-shift check that asks:

```text
How many tokens per word/line do different tokenizers produce on a larger
plain-text demo corpus?
```

## Script And Report

Script:

```text
scripts/report_fertility.py
```

Report:

```text
artifacts/v1_6_fertility_report_demo_corpus.md
```

## Key Result

Corpus size:

```text
lines: 310
words: 1326
```

Summary:

| Model | Avg tokens/word | Avg tokens/line | Protected preserved | Unknown/byte rate |
| --- | ---: | ---: | ---: | ---: |
| custom_tr_morph | 1.9419 | 8.3065 | 16/16 | 0.0000 |
| toy_bpe_1000 | 2.1953 | 9.3903 | 0/16 | 0.0000 |
| sp_bpe | 2.2097 | 9.4516 | 0/16 | 0.0000 |
| sp_unigram | 2.4555 | 10.5032 | 0/16 | 0.0000 |
| qwen | 2.8190 | 12.0581 | 0/16 | 0.0000 |
| llama | 2.5505 | 10.9097 | 0/16 | 0.0000 |
| mistral | 3.9306 | 16.8129 | 0/16 | 0.0000 |
| unicode_char | 6.9110 | 29.5613 | 0/16 | 0.0000 |

## Interpretation

What this supports:

- On this demo corpus, the custom tokenizer has lower token fertility than the
  compared baselines.
- The custom protection layer preserves all auto-detected file-like/numeric-like
  candidates in this corpus.
- The result reduces, but does not remove, the concern that all evidence comes
  only from tiny visible gold sets.

What this does not prove:

- It does not prove independent linguistic quality.
- It does not prove downstream LLM benefit.
- It does not replace a larger natural heldout corpus.
- It does not mean the demo corpus is production representative.

## v1.6a Measurement Status

Completed:

1. Bootstrap confidence intervals.
2. Protected-span break metrics.
3. Natural/demo corpus fertility report.

Remaining methodological work:

1. Independent heldout eval with policy-vs-independent gold.
2. Inter-annotator agreement.
3. Stronger Turkish-trained BPE/Unigram and morphology-aware baselines.
4. Small LM/probe experiment for downstream evidence.

## Next Step

The measurement-first v1.6a minimum is now complete.

The next engineering step can be v1.6b:

```text
low-risk do-no-harm routing guard batch
```

Recommended first guard:

```text
technical comparator/package spans
```

Examples:

```text
transformers>=4.40
tokenizers>=0.19
```

Reason: this is narrower and less linguistically ambiguous than Azerbaijani or
general non-Turkish Latin routing.
