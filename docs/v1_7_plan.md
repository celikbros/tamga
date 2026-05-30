# v1.7 Plan

Date: 2026-05-31

## Purpose

v1.7 is a measurement and methodology phase.

It should not start by adding new tokenizer rules. The goal is to answer whether
the tokenizer's visible gains are robust beyond curated policy-gold examples and
whether the morphology-aware segmentation is useful enough for later LLM
tokenizer design.

## Starting Point

v1.6b closed after Batch 4:

```text
tr_gold_expanded.tsv: 50/50
tr_challenge.tsv: 44/108, f1=0.8255
en_smoke.tsv: 8/10, f1=0.8889
multilingual_smoke.tsv: 17/20, f1=0.9404
protected span break_rate: 0.0000
```

R3 Azerbaijani routing was deferred because the fix requires span-level routing,
which belongs to v2.0 router/MorphBPE planning.

## Non-Goals

v1.7 should not:

- add broad Turkish suffix rules
- add Azerbaijani/Turkic morphology
- implement sentence-level language routing
- claim production readiness
- claim downstream LLM improvement without a probe

## Workstream 1: Independent/Heldout Eval Plan

Create a practical heldout evaluation plan that can be run with or without
external labelers.

Required outputs:

```text
docs/v1_7_heldout_eval_plan.md
data/eval/templates/tr_heldout_eval_template.tsv
```

The plan should define:

- sampling domains
- target example count for a practical first pass
- `policy_gold` vs `independent_gold`
- annotation uncertainty / IAA plan if multiple labelers exist
- aggregate-only reporting rules
- bootstrap confidence intervals

## Workstream 2: Missing Baseline Protocol

Define what baselines are needed before stronger claims:

```text
Morfessor
Turkish-trained SentencePiece BPE
Turkish-trained SentencePiece Unigram
BERTurk / XLM-R / mT5 tokenizers
production LLM tokenizers already measured: Qwen, Mistral, LLaMA
```

Required output:

```text
docs/v1_7_missing_baseline_protocol.md
configs/v1_7_baselines.toml
scripts/report_baseline_matrix.py
```

This protocol should separate:

- morphology-boundary intrinsic metrics
- token fertility / byte fallback / protected-span metrics
- downstream probe metrics

Implementation prep:

- keep the visible baseline set in a config file rather than scattered shell
  commands
- keep Hugging Face references disabled by default unless local cache or
  explicit download permission is available
- generate one Markdown matrix report per visible eval set

## Workstream 3: Small Downstream Probe Protocol

Define a small, cheap test for whether tokenization helps language modeling.

Candidate metric:

```text
byte-normalized loss / bits-per-byte / bits-per-character
```

Required output:

```text
docs/v1_7_downstream_probe_protocol.md
```

This should be a protocol first, not a full training run.

## Workstream 4: v2.0 Router/MorphBPE RFC Skeleton

Create a non-binding RFC skeleton for the later tokenizer architecture:

```text
raw input + offset map
light reversible cleanup
cross-language protection
script/language router
Turkish deterministic morphology
learned fallback for non-Turkish/Turkic spans
byte fallback
```

Required output:

```text
docs/v2_0_router_morphbpe_rfc.md
```

The RFC should include the R3 Azerbaijani deferral as a motivating example.

## Success Criteria

v1.7 is successful if it produces decision-ready protocols and keeps the current
tokenizer stable:

```text
python -m pytest
tr_gold_expanded.tsv remains 50/50
protected span break_rate remains 0.0000
no new broad tokenizer behavior is shipped without a pre-registered reason
```

## Recommended Order

1. `docs/v1_7_heldout_eval_plan.md` (started)
2. `docs/v1_7_missing_baseline_protocol.md` (started)
3. `docs/v1_7_downstream_probe_protocol.md` (started)
4. `docs/v2_0_router_morphbpe_rfc.md` (started)

This order keeps the project focused on evidence before architecture.
