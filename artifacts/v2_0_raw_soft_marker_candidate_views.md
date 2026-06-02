# v2.0 Raw-Soft-Marker Candidate Views

Source candidate: `protected_hard_soft_morph_seeded_sp64`
Target candidate: `protected_hard_soft_marker_raw_sp64`
Source root: `artifacts/private/v2_0_candidate`
Soft marker: `U+E000`

This candidate keeps hard boundaries as train-view whitespace and
serializes only soft morphology boundaries with a private-use marker.
It avoids custom token labels such as word-start markers or suffix
prefixes.

## Summary

| Split | Lines | Raw bytes | View bytes | View/raw bytes | Segments | Segments/raw byte | Soft markers | Hard boundaries | Max segments/line | JSONL | Train view |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| train | 16000 | 22819852 | 25980615 | 1.138509 | 2987536 | 0.130918 | 894466 | 5481707 | 890 | `artifacts/private/v2_0_candidate/protected_hard_soft_marker_raw_sp64.train.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_soft_marker_raw_sp64.train.txt` |
| valid | 1994 | 2843294 | 3238834 | 1.139113 | 371724 | 0.130737 | 112121 | 682277 | 649 | `artifacts/private/v2_0_candidate/protected_hard_soft_marker_raw_sp64.valid.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_soft_marker_raw_sp64.valid.txt` |
| test | 1998 | 2781995 | 3167803 | 1.138680 | 363218 | 0.130560 | 109169 | 666137 | 723 | `artifacts/private/v2_0_candidate/protected_hard_soft_marker_raw_sp64.test.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_soft_marker_raw_sp64.test.txt` |

## Gate

Train SentencePiece on this view and compare token pressure with
raw-hard and SP64. If pressure is acceptable, run visible intrinsic
boundary diagnostics before tiny-LM.
