# v2.0 Morph Seed Bias Intrinsic Findings

Date: 2026-06-09

## Summary

The first morph-seed bias prototype passed token pressure but did not improve
visible intrinsic morphology behavior.

Report:

```text
artifacts/v2_0_morph_seed_bias_finite_protected_intrinsic_eval.md
```

## Result

Challenge F1:

| Model | Challenge F1 | Protected stress |
| --- | ---: | --- |
| custom_tr_morph | 0.9220 | 25/25 |
| morph_seed_bias_unigram_64000, bare SP row | 0.7351 | 1/25 |
| finite protected + morph_seed_bias_unigram_64000 | 0.6913 | 25/25 |

Protected stress:

```text
bare morph_seed_bias model: 1/25
finite protected + morph_seed_bias: 25/25
```

## Interpretation

The finite protected path still works, but the very small seed-bias appendix did
not move morphology F1. This is consistent with the augmentation size:

```text
augmentation bytes/base byte: 0.000022
output bytes/base byte: 1.000022
```

So the first run was almost a no-op for SentencePiece learning. It is useful as
a low-risk control, but not as a serious morphology-prior test.

## Decision

Do not run tiny-LM on this weak seed-bias candidate.

Do not abandon the seed-bias branch yet. Instead, run one stronger bounded
augmentation that still keeps the train view below the 1.02 output/base-byte
gate.

## Next Strong Seed-Bias Probe

Materialize a stronger augmentation:

```powershell
python scripts\materialize_v2_morph_seed_augmented_view.py `
  --repeat-divisor 10 `
  --max-repeat-per-entry 2048 `
  --include-safe-uds-later `
  --out artifacts\private\v2_0_morph_seed_vocab\morph_seed_bias_strong_augmented_train.txt `
  --report-out artifacts\v2_0_morph_seed_bias_strong_augmented_view.md
```

Train/evaluate the strong Unigram probe:

```powershell
python scripts\run_v2_candidate_sentencepiece_probe.py configs\v2_0_morph_seed_bias_strong_sentencepiece.toml --force
```

Only if token pressure remains acceptable should we run finite-protected
intrinsic eval on the strong model.

Use explicit labels so the report does not describe the supplied morph-seed
model as the default SP64 baseline:

```powershell
python scripts\evaluate_v2_finite_protected_sp64_intrinsic.py `
  --sp64-model artifacts\private\v2_0_morph_seed_vocab\morph_seed_bias_strong_unigram_64000.model `
  --reference-label morph_seed_bias_strong_unigram_64000 `
  --finite-label finite_protected_morph_seed_bias_strong `
  --report-out artifacts\v2_0_morph_seed_bias_strong_finite_protected_intrinsic_eval.md
```
