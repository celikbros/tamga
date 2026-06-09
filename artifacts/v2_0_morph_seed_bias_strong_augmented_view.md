# v2.0 Morph Seed Augmented Train View

Base train: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Policy TSV: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv`
Augmented train view: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_bias_strong_augmented_train.txt`

This is a train-only SentencePiece view. It appends selected morph
seed surfaces as a small frequency-bias appendix. Normal encode-time
text does not contain these synthetic appendix lines.

## Parameters

| Parameter | Value |
| --- | ---: |
| repeat_divisor | 10 |
| max_repeat_per_entry | 2048 |
| include_safe_uds_later | True |

## Summary

| Metric | Value |
| --- | ---: |
| base lines | 16000 |
| base bytes | 22819852 |
| selected policy entries | 107 |
| augmentation lines | 107 |
| augmentation bytes | 252084 |
| augmentation bytes/base byte | 0.011047 |
| output lines | 16107 |
| output bytes | 23071936 |
| output bytes/base byte | 1.011047 |
| total weighted repeats | 66885 |

## Gate

The augmentation should stay small. If output bytes/base byte grows
substantially above 1.02, reduce repeats before training a tokenizer.
