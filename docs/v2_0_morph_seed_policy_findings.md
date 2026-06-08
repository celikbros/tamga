# v2.0 Morph Seed Policy Findings

Date: 2026-06-09

## Summary

The morph seed policy confirms that the Turkish suffix inventory is small and
useful, but should not be forced broadly as user-defined symbols in the first
prototype.

Policy output:

```text
report: artifacts/v2_0_morph_seed_policy_selection.md
private TSV: artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv
```

## Key Numbers

```text
input unique suffixes: 244
input suffix occurrences: 925856
selected unique: 107
selected occurrences: 891105
selected occurrence share: 0.962466
heldout unique: 137
heldout occurrences: 34751
```

Action breakdown:

| Action | Unique | Occurrences | Share |
| --- | ---: | ---: | ---: |
| seed_bias | 100 | 881151 | 0.951715 |
| safe_uds_candidate_later | 7 | 9954 | 0.010751 |
| holdout | 137 | 34751 | 0.037534 |

## Interpretation

The important result is not the `safe_uds_candidate_later` pool. It is that
almost all useful suffix occurrences can be represented as a seed/bias policy
without forcing the tokenizer to hard-split every suffix.

This matches the v2.0 lesson from the marker branch:

```text
hard morphology pressure is expensive
soft morphology prior is still worth exploring
```

## Decision

First morph-seed prototype:

```text
use seed_bias pieces as a learned-vocab prior
do not promote safe_uds_candidate_later pieces automatically
hold out protected-tail pieces for finite protected routing review
compare against finite_protected_sp64_floor
```

The next prototype should avoid broad user-defined symbols. A later UDS branch
may use the 7 `safe_uds_candidate_later` pieces as an auditable experiment if
the softer seed/bias branch fails.

## Next Step

Design and implement a morph-seed training view or SentencePiece training
strategy that biases the learned vocabulary toward selected suffix/morph pieces
without inserting markers at normal encode time.

Candidate implementation options:

```text
1. train-view augmentation with repeated selected morph pieces
2. SentencePiece user_defined_symbols only for the 7 safe candidates
3. constrained Unigram/MorphBPE objective later, after a simpler seed-bias test
```

The first option is the lowest-risk next experiment.

## First Prototype Commands

Materialize the augmentation view:

```powershell
python scripts\materialize_v2_morph_seed_augmented_view.py
```

Train/evaluate the first morph-seed Unigram probe:

```powershell
python scripts\run_v2_candidate_sentencepiece_probe.py configs\v2_0_morph_seed_bias_sentencepiece.toml --force
```

This is still not a tiny-LM run. It only checks token pressure on raw
valid/test text.

Observed result:

```text
findings: docs/v2_0_morph_seed_bias_findings.md
augmentation bytes/base byte: 0.000022
valid/test tokens/raw byte: 0.158312 / 0.158901
decision: token-pressure gate passed
```
