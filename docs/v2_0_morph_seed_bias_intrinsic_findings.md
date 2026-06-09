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

## Strong Seed-Bias Follow-Up

We ran one stronger bounded augmentation:

```text
augmentation report: artifacts/v2_0_morph_seed_bias_strong_augmented_view.md
SP probe report: artifacts/v2_0_morph_seed_bias_strong_sentencepiece_probe.md
intrinsic report: artifacts/v2_0_morph_seed_bias_strong_finite_protected_intrinsic_eval.md
```

The stronger appendix stayed within the train-view gate:

```text
augmentation bytes/base byte: 0.011047
output bytes/base byte: 1.011047
valid/test tokens/raw byte: 0.158315 / 0.158913
```

But it still did not improve the visible morphology signal:

```text
challenge F1, bare strong morph-seed model: 0.7356
challenge F1, finite protected + strong morph-seed: 0.6918
protected stress, finite protected + strong morph-seed: 25/25
```

The difference from the weak appendix is too small to justify tiny-LM.

## Updated Decision

Stop the simple morph-seed appendix branch for now.

It is compression-safe, but it does not transfer the custom morphology teacher
signal into the learned Unigram vocabulary. The next mechanism should be more
structural than repeated seed appendix lines: a small audited UDS experiment,
true seed vocabulary injection if SentencePiece supports it for our setup, or a
custom constrained/MorphBPE objective.
