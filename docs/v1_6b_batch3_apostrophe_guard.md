# v1.6b Batch 3: English/European Apostrophe Guard

Date: 2026-05-30

Tokenizer behavior: changed narrowly

## Purpose

v1.6b Batch 3 implements R1 from
`docs/v1_6_do_no_harm_routing_plan.md`: English and European apostrophe
guarding.

Before this batch, every apostrophe form that matched the pretokenizer shape was
treated like a Turkish apostrophe suffix form:

```text
Don't  -> ▁Don ' +t
John's -> ▁John ' +s
L'amico -> ▁L ' +amico
```

The new behavior only splits apostrophe forms when the right-hand side can be
parsed as a known Turkish apostrophe suffix chain.

## Scope

Now preserved as surface words:

```text
Don't
John's
We're
LLaMA's
d'Istanbul
L'amico
aujourd'hui
```

Still split as Turkish apostrophe suffix forms:

```text
Türkiye'den -> ▁Türkiye ' +den
Ali'nin -> ▁Ali ' +nin
API'den -> ▁API ' +den
README.md'yi -> ▁README.md ' +yi
2026'da -> ▁2026 ' +da
5'inci -> ▁5 ' +inci
```

Non-goals:

- no full English tokenization
- no French/Italian/Spanish/German Latin-letter guard yet
- no language detection
- no broad Turkish suffix rule changes
- no Azerbaijani routing change

## Verification

```text
python -m pytest
114 passed

python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
exact_match: 44/108
f1: 0.8255

python scripts/evaluate_tokenizer.py data/eval/en_smoke.tsv
exact_match: 8/10
f1: 0.8889
english_apostrophe: exact_match=2/2 f1=1.0000

python scripts/evaluate_tokenizer.py data/eval/multilingual_smoke.tsv
exact_match: 12/20
f1: 0.8542
```

All-baseline English smoke report:

```text
artifacts/v1_6b_batch3_real_tokenizer_report_english_smoke.md

custom_tr_morph exact_match: 8/10
custom_tr_morph boundary_f1: 0.9155
```

All-baseline multilingual smoke report:

```text
artifacts/v1_6b_batch3_real_tokenizer_report_multilingual_smoke.md

custom_tr_morph exact_match: 12/20
custom_tr_morph boundary_f1: 0.8392
```

Bootstrap CI reports:

```text
artifacts/v1_6b_batch3_ci_all_en_smoke.md
custom_tr_morph exact_match_rate: 0.8000 [0.5000, 1.0000]
custom_tr_morph boundary_f1:      0.9155 [0.8047, 1.0000]

artifacts/v1_6b_batch3_ci_all_multilingual_smoke.md
custom_tr_morph exact_match_rate: 0.6000 [0.3500, 0.8000]
custom_tr_morph boundary_f1:      0.8392 [0.6993, 0.9469]
```

Protected-span report:

```text
artifacts/v1_6b_batch3_protected_span_report_stress.md

custom_tr_morph protected_preserved: 25/25
custom_tr_morph protected_broken:    0
custom_tr_morph break_rate:          0.0000
```

## Interpretation

This removes a high-visibility non-Turkish false positive without weakening the
Turkish apostrophe suffix flow.

Remaining visible failures are expected:

- `code`, `data`, `OpenAI`, and `code-mixed` still need a separate ASCII
  English/code-mixed guard.
- `à`, `ñ`, `ß`, `á` and similar non-Turkish Latin letters were addressed in
  v1.6b Batch 4.
- Azerbaijani over-splitting remains intentionally deferred.

## Next Candidate

Completed after this batch:

```text
R2 non-Turkish Latin word guard
```

See `docs/v1_6b_batch4_non_turkish_latin_guard.md`.
