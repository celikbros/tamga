# v2.0 Expanded UDS22 Probe Plan

Date: 2026-06-10

## Purpose

The 7-symbol safe UDS probe improved visible morphology behavior with nearly
no token-pressure cost. This branch tests one conservative expansion before
moving to a more structural constrained/MorphBPE design.

## Selection Rule

The expanded pool is selected only from train-side morphology candidate
statistics:

```text
recommendation == uds_or_seed_candidate
min_count >= 100
surface_len >= 3
hard_share <= 0.01
exact_collision_rate <= 0.001
max_symbols = 64
```

Expected size from the current train split: 22 symbols.

This deliberately excludes short ambiguous suffixes and higher-collision cases.

## Commands

Materialize symbols:

```powershell
python scripts\materialize_v2_expanded_uds_symbols.py
```

Train/evaluate SentencePiece token pressure:

```powershell
python scripts\run_v2_candidate_sentencepiece_probe.py configs\v2_0_expanded_uds22_sentencepiece.toml --force
```

If token pressure is acceptable, run intrinsic eval:

```powershell
python scripts\evaluate_v2_finite_protected_sp64_intrinsic.py `
  --sp64-model artifacts\private\v2_0_expanded_uds22\expanded_uds22_unigram_64000.model `
  --reference-label expanded_uds22_unigram_64000 `
  --finite-label finite_protected_expanded_uds22 `
  --report-out artifacts\v2_0_expanded_uds22_finite_protected_intrinsic_eval.md
```

## Gates

Continue only if:

```text
valid/test tokens/raw byte remains near the safe UDS result
finite protected stress remains 25/25
Challenge F1 improves materially over safe UDS, not only by noise
```

If this does not improve enough, stop UDS expansion and move to
constrained/MorphBPE design.
