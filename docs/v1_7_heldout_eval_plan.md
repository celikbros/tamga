# v1.7 Heldout Evaluation Plan

Date: 2026-05-31

## Purpose

v1.7 heldout eval is designed to reduce the main methodological risk:

```text
curated policy-gold success != independent linguistic validity
```

The goal is not to chase challenge-set exact match. The goal is to measure how
well the tokenizer generalizes on text that was not used to design the rules.

## Current Baseline

Current visible metrics after v1.6b Batch 4:

```text
tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

tr_challenge.tsv
exact_match: 44/108
f1: 0.8255

multilingual_smoke.tsv
exact_match: 17/20
f1: 0.9404
```

These are useful engineering signals, but they are not enough for strong
research claims.

## Dataset Status

The heldout set must not be committed with filled examples if it is intended to
stay hidden.

Public repo may contain:

```text
data/eval/templates/tr_heldout_eval_template.tsv
docs/v1_7_heldout_eval_plan.md
aggregate reports only
```

Private or reviewer-controlled storage should contain:

```text
data/eval/private/tr_heldout_eval.tsv
```

## Recommended First Pass

Practical first pass:

```text
80-120 examples
```

Minimum acceptable first pass:

```text
40 examples
```

Research-strength later pass:

```text
300-500 examples
```

The project should not block tokenizer/LLM design forever waiting for the full
research-strength set. Use the first pass as a decision signal, then expand.

## Domains

Recommended first-pass mix:

| Domain | Target Share | Purpose |
| --- | ---: | --- |
| news / formal prose | 20% | ordinary standard Turkish |
| user-generated / informal | 25% | informal endings, spelling variation |
| technical / code-mixed | 20% | protected spans, English/Turkish mixing |
| public institutional / legal-like | 15% | long suffix chains, formal style |
| names / numbers / dates | 10% | apostrophe, number/date guards |
| adversarial ambiguity / negative words | 10% | false-positive split risk |

## Annotation Format

Use a two-gold format:

```text
id
domain
category_hint
text
gold_independent
gold_policy
divergence_note
visibility
review_status
```

Definitions:

- `gold_independent`: linguistically motivated segmentation from annotator or
  external reference.
- `gold_policy`: expected output under this tokenizer's documented
  surface-preserving policy.
- `divergence_note`: required when the two golds differ.
- `visibility`: `private`, `rotated_public`, or `calibration`.
- `review_status`: `draft`, `calibrated`, `adjudicated`, or `rejected`.

## Labeling Guidance

The annotator should not read implementation code.

They may read a short labeler packet explaining:

- token format: `▁` for word start, `+` for suffix pieces
- tokenizer is surface-preserving
- tokenizer is not a normalizer
- ambiguous forms may have policy/independent divergence

Existing useful docs:

```text
docs/hidden_eval_labeler_packet.md
docs/hidden_eval_labeling_guideline.md
docs/hidden_eval_protocol.md
```

## Calibration

Before full annotation:

```text
5 public calibration examples
```

Rules:

- calibration examples are not part of the hidden set
- reviewer checks format and policy/independent distinction
- if calibration fails badly, revise guideline before continuing

## Metrics

Report aggregate only:

```text
exact_match
boundary precision/recall/f1
category-level f1
protected span break rate
token fertility
bootstrap confidence intervals
policy-vs-independent gap
```

Do not publish private examples or token lists.

## Decision Use

The heldout set should answer:

1. Does the tokenizer follow its own policy outside curated examples?
2. Does the policy align with independent Turkish morphology?
3. Where are false-positive splits still happening?
4. Are protected spans robust in natural text?
5. Is morphology-aware tokenization worth a downstream probe?

## Non-Goals

Heldout eval should not be used to:

- tune rules directly against private examples
- force challenge exact match to 100%
- add broad suffix splitting
- implement Azerbaijani/Turkic routing

## Immediate Next Step

Create or select examples using the template:

```text
data/eval/templates/tr_heldout_eval_template.tsv
```

Then prepare an aggregate-only evaluator or adapt existing scripts to the
two-gold format.
