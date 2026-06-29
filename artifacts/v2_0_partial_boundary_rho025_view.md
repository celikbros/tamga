# v2.0 Partial-Boundary SentencePiece Train View

Input: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output: `artifacts/private/v2_0_partial_boundary_sp/partial_boundary_rho025.train.txt`
rho: `0.25`
seed: `20260610`
marker: ``

This view inserts a train-only pretokenization delimiter at custom
soft morphology boundaries for only a fraction of training lines.
Validation/test text remains delimiter-free.

## Summary

| Lines | Raw bytes | View bytes | View/raw bytes | Marked lines | Marked line rate | Inserted markers |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16000 | 22819852 | 23491924 | 1.029451 | 3941 | 0.246312 | 224024 |

Config:

`configs/v2_0_partial_boundary_rho025_sentencepiece.toml`

## Next

Train with `scripts/run_v2_candidate_sentencepiece_probe.py` and
compare token pressure plus intrinsic morphology/protected reports
against the repaired finite protected numeric-SP floor.
