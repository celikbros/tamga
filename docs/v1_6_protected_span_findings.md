# v1.6 Protected Span Findings

Date: 2026-05-30

Tokenizer behavior: not changed

## Purpose

Advisor feedback asked for a metric that is separate from morphology boundary F1:

```text
Do code/file/URL/number/date-like protected spans stay intact?
```

v1.6a adds a protected-span baseline report for public stress examples. This
does not judge ordinary word segmentation. It only checks spans explicitly marked
as protected in the stress TSV.

## Script And Report

Script:

```text
scripts/report_protected_spans.py
```

Report:

```text
artifacts/v1_6_protected_span_report_stress.md
```

Input:

```text
data/eval/tr_stress_public.tsv
```

## Key Result

```text
custom_tr_morph
protected_preserved: 23/23
protected_broken:    0
break_rate:          0.0000
avg_tokens/word:     1.5274
```

Selected baselines:

| Model | Protected preserved | Break rate | Avg tokens/word |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 23/23 | 0.0000 | 1.5274 |
| toy_bpe_1000 | 1/23 | 0.9565 | 3.8356 |
| sp_bpe | 1/23 | 0.9565 | 3.4658 |
| sp_unigram | 0/23 | 1.0000 | 3.7055 |
| qwen | 1/23 | 0.9565 | 2.9384 |
| llama | 1/23 | 0.9565 | 2.7329 |
| mistral | 1/23 | 0.9565 | 3.5959 |

## v1.6b Batch 1 Update

The technical comparator guard added two more protected spans to the public
stress set:

```text
transformers>=4.40
tokenizers>=0.19
```

Updated report:

```text
artifacts/v1_6b_protected_span_report_stress.md

custom_tr_morph
protected_preserved: 25/25
protected_broken:    0
break_rate:          0.0000
avg_tokens/word:     1.4805
```

## v1.6b Batch 2 Update

Arabic and Greek public stress rows were added after the script word fallback.
They are not protected spans, but they do verify roundtrip behavior for
non-Turkish scripts.

Updated report:

```text
artifacts/v1_6b_batch2_protected_span_report_stress.md

examples: 31
custom_tr_morph
protected_preserved: 25/25
protected_broken:    0
break_rate:          0.0000
avg_tokens/word:     1.5325
```

## Interpretation

This is a do-no-harm metric, not a full tokenizer-quality metric.

What it supports:

- The custom pretokenizer currently keeps public stress protected spans intact.
- The protection layer is doing useful work before morphology.
- General BPE/LLM tokenizers often split these spans into subwords, which is
  expected but important to make visible.

What it does not prove:

- It does not prove better language modeling.
- It does not prove better Turkish morphology on independent gold.
- It does not mean ordinary words should always be single tokens.
- It does not remove the need for hidden/heldout eval.

## Why This Matters For v1.6b

Future routing guards must preserve this result:

```text
protected span break rate must remain 0.0000 on public stress for custom_tr_morph
```

If a routing guard fixes English or multilingual smoke examples but breaks
`README.md`, URLs, dates, file names, Uzbek apostrophe-like lexical spans, or
code-like spans, the guard should be reverted or narrowed.

## Next Step

The v1.6a natural/demo corpus fertility report is complete. v1.6b Batch 1
protected technical comparator spans, and Batch 2 added Arabic/Greek script word
fallback. The next guard candidate is:

```text
R1 English/European apostrophe guard
```
