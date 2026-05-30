# v1.6b Batch 1: Technical Comparator Span Guard

Date: 2026-05-30

Tokenizer behavior: changed narrowly

## Purpose

v1.6b starts the do-no-harm routing work with the lowest-risk candidate from
`docs/v1_6_do_no_harm_routing_plan.md`: technical comparator/package spans.

The goal is to keep common package/version expressions intact before Turkish
morphology runs.

## Scope

Protected forms:

```text
name>=1.2
name<=1.2
name==1.2
name~=1.2
name!=1.2
```

Examples:

```text
transformers>=4.40 -> ▁transformers>=4.40
tokenizers>=0.19  -> ▁tokenizers>=0.19
```

Non-goals:

- no broad Turkish suffix rule changes
- no English apostrophe fix yet
- no non-Turkish Latin routing yet
- no Azerbaijani morphology or routing change
- no attempt to make `>`, `<`, or `=` sticky in ordinary prose

## Implementation Notes

The pretokenizer now recognizes technical comparator spans before file-like and
numeric-like spans. The encoder marks these spans with the normal word-start
marker and skips Turkish suffix splitting for them.

Coverage and fertility reports also classify these spans as protected technical
tokens so protected-span metrics can see them.

## Verification

```text
python -m pytest
108 passed

python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
exact_match: 44/108
f1: 0.8255

python scripts/evaluate_tokenizer.py data/eval/en_smoke.tsv
exact_match: 6/10
f1: 0.8000

python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_6b_public_stress_report.md
roundtrip_exact: 29/29
protected_spans_preserved: 25/25
```

Protected-span baseline report:

```text
artifacts/v1_6b_protected_span_report_stress.md

custom_tr_morph protected_preserved: 25/25
custom_tr_morph protected_broken:    0
custom_tr_morph break_rate:          0.0000
```

English smoke all-baseline report:

```text
artifacts/v1_6b_real_tokenizer_report_english_smoke.md

custom_tr_morph exact_match: 6/10
custom_tr_morph boundary_f1: 0.8667
custom_tr_morph technical category f1: 1.0000
```

Bootstrap CI report:

```text
artifacts/v1_6b_ci_all_en_smoke.md

custom_tr_morph exact_match_rate: 0.6000 [0.3000, 0.9000]
custom_tr_morph boundary_f1:      0.8667 [0.7544, 0.9765]
```

## Interpretation

This is a small safety improvement, not a multilingual solution.

It proves that the tokenizer can protect a narrow class of technical spans
without hurting the frozen Turkish regression set. It does not address English
apostrophes, non-Turkish Latin words, Azerbaijani routing, or downstream LLM
quality.

## Next Candidate

Next recommended v1.6b batch:

```text
R4 Arabic/Greek script word fallback
```

That candidate is still a do-no-harm guard, not a Turkish morphology expansion.
