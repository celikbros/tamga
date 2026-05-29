# v1.4 Candidate Shortlist

Status: Batch 1 implemented
Date: 2026-05-29
Tokenizer behavior: not changed

## Purpose

This document turns the v1.4 decision framework into an actionable shortlist.
It is still not an implementation plan for broad morphology expansion.

The goal is to select the smallest safe batch that can improve visible challenge
errors without weakening the frozen regression set or the public stress guards.

## Inputs

| Input | Current signal |
| --- | --- |
| `docs/v1_4_decision_framework.md` | Safe-rule candidates and revert criteria are defined. |
| `data/eval/tr_challenge_labeled.tsv` | Seven visible rows are labeled `safe_rule_candidate`. |
| `artifacts/v1_4_challenge_mismatch_analysis.md` | Current challenge mismatch report. |
| `docs/ai_expert_review_triage.md` | v1.x guardrails: no broad greedy suffixes, no generic apostrophe, no global normalization. |
| `docs/v1_3_closing_report.md` | v1.4 entry criteria. |

## Current Baseline

Frozen regression remains the main safety gate:

```text
tr_gold_expanded.tsv: 50/50 exact match, f1=1.0000
```

Visible challenge remains a dev/error-analysis set:

```text
tr_challenge.tsv: 40/108 exact match, f1=0.8184
```

Public stress remains the surface-preservation guard:

```text
tr_stress_public.tsv: 28/28 roundtrip, 23/23 protected spans
```

## Shortlist Decision

The first v1.4 batch should be limited to exact lexical protection candidates.
These reduce false-positive splitting without broadening suffix behavior.

| Priority | Candidate | Action | Why now | Risk |
| --- | --- | --- | --- | --- |
| 1 | S6 protect `peki` | Add exact protected lexical item for `peki`. | `Peki...` currently over-splits as `Pe +ki`; exact protection is low risk. | Low |
| 2 | S7 protect `yeni` | Add exact protected lexical item for `yeni`. | `(Ankara'dan) yeni döndüm.` currently over-splits as `ye +ni`; exact protection is low risk. | Low |

These two are preferred because they do not require:

- new suffix inventory
- broad greedy splitting
- apostrophe policy changes
- Unicode or normalization changes
- Turkish morphology on non-Turkish input

## Hold For Later

The following candidates may be useful, but they should not be in the first
v1.4 batch.

| Candidate | Reason to hold |
| --- | --- |
| S1 buffered possessive+ablative | Useful but touches suffix-chain behavior; needs person-suffix and negative-word regressions. |
| S2 explicit `başla` past split | Contained, but it is a secondary verb-past issue inside a numbers/date row. |
| S3 explicit `satır` stem | Adds a short `+ı` object-case path; needs more negative regressions. |
| S4a explicit `tarih` stem | Adds short `+in/+de` behavior around a new stem. |
| S4b explicit `yazıl` passive stem | Requires a passive-stem policy decision. |
| S5 explicit `yap +ma` | High risk because word-final `ma` is productive and ambiguous. |

## Required Tests Before Batch 1

Positive tests:

```text
Peki... sonra ne oldu?
(Ankara'dan) yeni döndüm.
```

Negative/protected tests:

```text
Arabalarımızdakilerdenmişsiniz.
Ankara'dakilerden biri geldi.
Kadın yakın altın kedi.
Yazın tatile gittik.
Yazarım ama göndermem.
OpenAIlaştırılamayanlardanmış.
Don't split John's book.
Oʻzbekcha: gʻisht, sanʼat, maʼno.
```

Required commands after implementation:

```powershell
python -m pytest
python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_3_public_stress_report.md
python scripts/report_coverage.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_3_coverage_stress.md
```

## Revert Criteria

Batch 1 should be reverted if any of these happen:

- `tr_gold_expanded.tsv` drops below 50/50.
- Public stress drops below 28/28 roundtrip.
- `peki` or `yeni` still over-splits after implementation.
- Existing `+ki` behavior in known correct cases breaks.
- Negative-word or ambiguity examples start receiving broader false-positive
  splits.
- English/European/Uzbek apostrophe stress examples change unexpectedly.

## Decision

Proceed to v1.4 Batch 1 only with exact lexical protection for `peki` and
`yeni`.

Do not implement S1-S5 in the same batch.

After Batch 1, re-run the challenge analysis and decide whether S1 is worth a
separate medium-risk batch.

S1 risk notes are tracked separately in
`docs/v1_4_s1_buffered_ablative_analysis.md`.

## Batch 1 Result

Implemented:

- exact protected lexical item: `peki`
- exact protected lexical item: `yeni`

Verification:

```text
python -m pytest
80 passed

tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

tr_challenge.tsv
exact_match: 43/108
f1: 0.8233

tr_stress_public.tsv
roundtrip_exact: 28/28
protected_spans_preserved: 23/23
```

Category movement:

| Category | Before Batch 1 | After Batch 1 |
| --- | ---: | ---: |
| punctuation exact match | 6/9 | 8/9 |
| punctuation F1 | 0.9388 | 0.9793 |
| code_mixed exact match | 3/9 | 4/9 |
| code_mixed F1 | 0.8485 | 0.8659 |
| overall exact match | 40/108 | 43/108 |
| overall F1 | 0.8184 | 0.8233 |

No broad suffix rule was added. `negative_word`, `ambiguity`, frozen regression,
and public stress guards remained stable.
