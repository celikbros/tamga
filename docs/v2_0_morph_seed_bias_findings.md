# v2.0 Morph Seed Bias Findings

Date: 2026-06-09

## Summary

The first morph-seed bias prototype passed the token-pressure gate.

It uses a tiny train-only augmentation appendix rather than in-stream markers
or broad user-defined symbols.

Reports:

```text
artifacts/v2_0_morph_seed_augmented_view.md
artifacts/v2_0_morph_seed_bias_sentencepiece_probe.md
```

## Augmentation

```text
base lines: 16000
selected policy entries: 100
augmentation lines: 100
augmentation bytes: 492
augmentation bytes/base byte: 0.000022
output bytes/base byte: 1.000022
```

Interpretation:

```text
the augmentation is tiny
the normal encode-time text remains marker-free
the train view is not inflated like the marker branch
```

## Token Pressure

| Split | SP tokens/raw byte |
| --- | ---: |
| train | 0.153985 |
| valid | 0.158312 |
| test | 0.158901 |

Comparison:

```text
SP64 dry-run valid/test:                 0.159020 / 0.159620
morph_seed_bias valid/test:              0.158312 / 0.158901
finite_protected_sp64_floor valid/test:  0.182112 / 0.183362
marker suffix_chain2 valid/test:         0.184500 / 0.185337
marker all_soft valid/test:              0.196313 / 0.196954
```

The morph-seed bias prototype is close to SP64 compression and better than the
marker-shaped candidates on raw learned-tokenizer pressure.

## Decision

This candidate is worth intrinsic evaluation with finite protected routing.

Do not run tiny-LM yet. The next gate is visible intrinsic behavior:

```text
protected stress: should stay 25/25 via finite protected routing
challenge F1: should beat finite_protected_sp64_floor and preferably improve
over bare SP64 without increasing token pressure
roundtrip/protected behavior: must remain lossless and stateless
```

## Next Command

Run:

```powershell
python scripts\evaluate_v2_finite_protected_sp64_intrinsic.py `
  --sp64-model artifacts\private\v2_0_morph_seed_vocab\morph_seed_bias_unigram_64000.model `
  --report-out artifacts\v2_0_morph_seed_bias_finite_protected_intrinsic_eval.md
```

The script name still says `sp64`, but the `--sp64-model` argument points it at
the morph-seed model. Interpret the finite protected row as:

```text
finite protected routing + morph_seed_bias_unigram_64000
```

