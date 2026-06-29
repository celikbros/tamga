# v2.0 Morph Vocabulary Coverage Findings

Date: 2026-06-10

## Why This Step Happened

After promoting `finite_protected_sp64_numeric_sp_floor` as the active protected
floor, the next Fable5 diagnostic was to separate two hypotheses:

```text
H1: the learned tokenizer does not contain the teacher morph surfaces.
H2: the learned tokenizer contains them, but decode/Viterbi does not prefer them.
```

If H1 were true, we would need more seed/UDS/vocab construction. If H2 is true,
the next useful mechanism is decode-time boundary bias or a constrained
objective, not more suffix inventory expansion.

## Audit

Script:

```text
scripts/audit_v2_morph_vocab_coverage.py
```

Report:

```text
artifacts/v2_0_morph_vocab_coverage.md
```

Private rows:

```text
artifacts/private/v2_0_morph_vocab_coverage.rows.jsonl
```

Input policy:

```text
artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv
```

Scope:

```text
action == seed_bias
100 selected morph/suffix surfaces
881151 weighted occurrences
```

## Result

| Model | Exact-piece occurrence share | Vocab-surface occurrence share | Standalone-single occurrence share | Weighted avg standalone pieces |
| --- | ---: | ---: | ---: | ---: |
| SP64 | 0.963019 | 0.963019 | 0.534474 | 1.465526 |
| safe UDS7 | 0.962751 | 0.962751 | 0.455065 | 1.544935 |

Important reading:

```text
Exact-piece coverage is already very high.
Safe UDS7 does not improve broad morph-surface coverage.
Standalone-single is lower mostly because SentencePiece's dummy prefix can
encode suffix strings as `▁` + suffix, even when the suffix itself exists as an
exact piece.
```

Examples:

```text
ler exists as an exact piece, but standalone "ler" may encode as: ▁ + ler
lar exists as an exact piece, but standalone "lar" may encode as: ▁ + lar
mış exists as an exact piece, but standalone "mış" may encode as: ▁ + mış
```

## Interpretation

H1 is not the main bottleneck for the selected high-value morph surfaces.

The next issue is H2:

```text
The vocabulary mostly has the pieces.
The decoder/objective does not reliably choose morph-aligned segmentations in
real word contexts.
```

This explains why:

```text
simple seed appendix did not move F1,
safe UDS7 helped only modestly,
expanded UDS became too expensive,
marker shaping improved F1 but did not pay back BPB.
```

## Decision

Do not spend the next iteration on more suffix inventory or broad UDS expansion.

The next useful experiment is a decode-time boundary-biased Unigram/Viterbi
sweep:

```text
score(piece path) = SP unigram score - lambda * morphology_boundary_crossing
```

The goal is to test whether the existing SP64 vocabulary can express the
morphology teacher's preferred boundaries if the decoder is nudged, before
building a new constrained/MorphBPE trainer.

## Next Gate

Run a challenge-blind lambda sweep on visible diagnostics only as an engineering
probe:

```text
baseline: finite_protected_sp64_numeric_sp_floor
vocab: SP64 normal-text vocabulary
hard path: finite protected routing
soft signal: teacher morphology boundaries
primary diagnostics: tokens/raw byte, challenge F1, protected stress
promotion gate: materially better F1 than active protected floor without moving
token pressure toward marker/UDS22 levels
```
