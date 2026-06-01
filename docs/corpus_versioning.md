# Corpus Versioning

Date: 2026-06-01

## Rationale

Corpus files now influence tokenizer baselines, leakage checks, and LLM probe
handoffs. File names should make the corpus role and version visible without
opening the file.

The current names are useful locally, but ambiguous:

```text
celik_gold_corpus.clean.jsonl
celik_gold_clean_pilot.txt
```

They say "clean", but not which cleaning policy, which date, or whether the file
is a full corpus or a pilot slice.

## Naming Convention

Use this pattern for future corpus artifacts:

```text
<project>_<langmix>_<role>_<version>_<date>.<format>
```

Recommended fields:

| Field | Example | Meaning |
| --- | --- | --- |
| `project` | `celik` | Corpus family or source project |
| `langmix` | `tr_primary_multilingual_mix` | Main language mix; Turkish-primary, multilingual-aware content |
| `role` | `pretrain_clean`, `tokenizer_pilot`, `lm_probe_pilot` | Intended use |
| `version` | `v1_0` | Cleaning/version policy |
| `date` | `20260601` | Freeze date |
| `format` | `jsonl`, `txt` | Storage format |

Examples:

```text
celik_tr_primary_multilingual_mix_pretrain_clean_v1_0_20260601.jsonl
celik_tr_primary_multilingual_mix_tokenizer_pilot_100k_v1_0_20260601.txt
celik_tr_primary_multilingual_mix_lm_probe_pilot_20k_v1_0_20260601.txt
```

## Current Registry

| Current path | Proposed canonical name | Status |
| --- | --- | --- |
| `data/train/private/celik_ai/celik_gold_corpus.clean.jsonl` | `celik_tr_primary_multilingual_mix_pretrain_clean_v1_0_20260601.jsonl` | current full clean corpus |
| `data/train/claim_grade/celik_gold_clean_pilot.txt` | `celik_tr_primary_multilingual_mix_tokenizer_pilot_100k_v1_0_20260601.txt` | current clean SP/downstream pilot |

## Policy

- Do not rename large private corpus files casually after configs and reports
  depend on them.
- When a new corpus version is frozen, create a new versioned file name and keep
  the old file archived or referenced as a legacy alias.
- Public reports should use the versioned corpus label even when local paths keep
  older names for compatibility.
- Private tokenized outputs should include the corpus version in their output
  directory once the next corpus freeze is made.

## Next Rename Window

The safest rename point is the next corpus freeze, before a new set of
SentencePiece baselines or LLM probe outputs is generated.

For the current v1.7 handoff, keep the existing paths stable and document the
version mapping above.
