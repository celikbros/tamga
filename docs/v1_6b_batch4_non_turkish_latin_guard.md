# v1.6b Batch 4: Non-Turkish Latin Word Guard

Date: 2026-05-30

Tokenizer behavior: changed narrowly

## Purpose

v1.6b Batch 4 implements R2 from
`docs/v1_6_do_no_harm_routing_plan.md`: a narrow non-Turkish Latin word guard.

The goal is not language detection. The goal is to avoid fragmenting words that
contain Latin letters outside the Turkish alphabet.

Before this batch, examples such as these were fragmented:

```text
Straße -> ▁Stra ß ▁e
niño -> ▁ni ñ ▁o
Bogotá -> ▁Bogot á
all'università -> ▁all'universit à
```

The new behavior keeps those surface words intact.

## Scope

Now preserved as surface words:

```text
Straße
groß
niño
comió
piñata
Bogotá
università
all'università
```

Still intentionally out of scope:

- no English dictionary guard for ASCII-only words such as `code` or `data`
- no camel-case/code-mixed guard for `OpenAI`
- no hyphenated English guard for `Turkic-speaking`
- no Azerbaijani routing change
- no language detection
- no broad Turkish suffix rule changes

## Verification

```text
python -m pytest --basetemp C:\tmp\pytest-basetemp
116 passed

python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
exact_match: 44/108
f1: 0.8255

python scripts/evaluate_tokenizer.py data/eval/en_smoke.tsv
exact_match: 8/10
f1: 0.8889

python scripts/evaluate_tokenizer.py data/eval/multilingual_smoke.tsv
exact_match: 17/20
f1: 0.9404
```

Category improvements in `multilingual_smoke.tsv`:

```text
french:  exact_match=2/2 f1=1.0000
german:  exact_match=2/2 f1=1.0000
spanish: exact_match=1/1 f1=1.0000
italian: exact_match=1/1 f1=1.0000
```

Public stress report:

```text
artifacts/v1_6b_batch4_public_stress_report.md

examples: 34
roundtrip_exact: 34/34
protected_spans_preserved: 25/25
```

Protected-span report:

```text
artifacts/v1_6b_batch4_protected_span_report_stress.md

custom_tr_morph protected_preserved: 25/25
custom_tr_morph protected_broken:    0
custom_tr_morph break_rate:          0.0000
```

All-baseline multilingual smoke report:

```text
artifacts/v1_6b_batch4_real_tokenizer_report_multilingual_smoke.md

custom_tr_morph exact_match: 17/20
custom_tr_morph boundary_f1: 0.9551
custom_tr_morph avg_tokens/word: 2.0000
```

Bootstrap CI report:

```text
artifacts/v1_6b_batch4_ci_all_multilingual_smoke.md

custom_tr_morph exact_match_rate: 0.8500 [0.7000, 1.0000]
custom_tr_morph boundary_f1:      0.9551 [0.8990, 1.0000]
custom_tr_morph avg_tokens/word:  2.0000 [1.3980, 3.4753]
```

## Interpretation

This batch removes clear Latin-script false fragmentation without pretending to
solve multilingual routing.

Remaining visible failures are expected:

- Azerbaijani words with Turkish-like suffix shapes are still over-split.
- `Turkic-speaking` is still split at the hyphen.
- ASCII-only English/code-mixed words such as `code`, `data`, and `OpenAI`
  remain a separate, riskier problem.

## Next Candidate

Next recommended v1.6b step:

```text
R3 Azerbaijani routing guard design review
```

R3 is riskier than the previous batches. It should not be implemented as a broad
Latin/Turkic language detector without a short design review and explicit revert
criteria.
