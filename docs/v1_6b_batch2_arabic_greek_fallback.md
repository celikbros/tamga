# v1.6b Batch 2: Arabic/Greek Script Word Fallback

Date: 2026-05-30

Tokenizer behavior: changed narrowly

## Purpose

v1.6b Batch 2 implements R4 from
`docs/v1_6_do_no_harm_routing_plan.md`: Arabic and Greek script word fallback.

The goal is not to analyze Arabic or Greek morphology. The goal is simply to
avoid character-level fragmentation when the input is clearly in Arabic or Greek
script.

## Scope

New fallback behavior:

```text
مرحبا بالعالم. -> ▁مرحبا ▁بالعالم .
Αθήνα είναι όμορφη πόλη. -> ▁Αθήνα ▁είναι ▁όμορφη ▁πόλη .
```

The Arabic guard uses letter/mark ranges rather than the whole Arabic Unicode
block, so Arabic punctuation and digits are not made sticky as word text.

Non-goals:

- no Arabic morphology
- no Greek morphology
- no language detection
- no transliteration
- no Azerbaijani routing change
- no English/French/Italian apostrophe change
- no broad Turkish suffix rule changes

## Verification

```text
python -m pytest
112 passed

python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
exact_match: 44/108
f1: 0.8255

python scripts/evaluate_tokenizer.py data/eval/multilingual_smoke.tsv
exact_match: 11/20
f1: 0.7883
arabic: exact_match=2/2 f1=1.0000
greek: exact_match=1/1 f1=1.0000

python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_6b_batch2_public_stress_report.md
roundtrip_exact: 31/31
protected_spans_preserved: 25/25
```

All-baseline multilingual smoke report:

```text
artifacts/v1_6b_batch2_real_tokenizer_report_multilingual_smoke.md

custom_tr_morph exact_match: 11/20
custom_tr_morph boundary_f1: 0.8015
```

Bootstrap CI report:

```text
artifacts/v1_6b_batch2_ci_all_multilingual_smoke.md

custom_tr_morph exact_match_rate: 0.5500 [0.3238, 0.7500]
custom_tr_morph boundary_f1:      0.8015 [0.6588, 0.9199]
```

Protected-span report:

```text
artifacts/v1_6b_batch2_protected_span_report_stress.md

custom_tr_morph protected_preserved: 25/25
custom_tr_morph protected_broken:    0
custom_tr_morph break_rate:          0.0000
```

## Interpretation

This is a do-no-harm safety improvement. It makes non-Turkish script handling
less destructive without claiming multilingual tokenizer quality.

Remaining visible multilingual smoke failures are still expected:

- Azerbaijani words can still be over-split by Turkish morphology.
- English/French/Italian apostrophe words still split as Turkish apostrophe
  forms.
- Non-Turkish Latin letters such as `ñ`, `ß`, and `á` still need a separate
  guard.

## Next Candidate

Completed after this batch:

```text
R1 English/European apostrophe guard
```

See `docs/v1_6b_batch3_apostrophe_guard.md`.
