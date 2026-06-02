# v2.0 Candidate Split Views

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Selected seed TSV: `artifacts/private/v2_0_soft_morph/protected_hard_soft_morph_seeded_sp64.selected_seed.tsv`

This report completes Phase 1 candidate serialization for non-train
splits. The selected seed policy is still train-derived; valid/test
diagnostic seed TSV files are private diagnostics only.

## Summary

| Split | Lines | Raw bytes | Soft pieces/byte | Train-view bytes/raw byte | Hard segments/raw byte | Selected piece rate | Unselected word_start pieces | Boundary JSONL | Candidate JSONL | Train view |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| valid | 1994 | 2843294 | 0.279394 | 1.511517 | 0.130737 | 0.569395 | 25748 | `artifacts/private/v2_0_soft_morph/soft_morph_boundaries.valid.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_soft_morph_seeded_sp64.valid.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_soft_morph_seeded_sp64.valid.txt` |
| test | 1998 | 2781995 | 0.278687 | 1.510259 | 0.130560 | 0.569111 | 25499 | `artifacts/private/v2_0_soft_morph/soft_morph_boundaries.test.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_soft_morph_seeded_sp64.test.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_soft_morph_seeded_sp64.test.txt` |

## Gate

The next learned-tokenizer prototype should train on the train view and
measure token pressure on the valid/test train views before any tiny-LM
screening.
