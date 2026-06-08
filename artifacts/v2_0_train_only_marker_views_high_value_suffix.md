# v2.0 Train-Only Marker View Materialization

Source candidate: `protected_hard_soft_morph_seeded_sp64`
Target candidate: `protected_hard_train_only_high_value_suffix`
Source root: `artifacts/private/v2_0_candidate`
Policy: `high_value_suffix`
Soft marker: `U+E000`
Minimum suffix count: `2`
High-value suffix allowlist size: `35`

This materializes markerized SentencePiece training views for
train-only vocabulary shaping. The marker is not intended to be
inserted into normal text at encode time.

## Summary

| Split | Lines | Raw bytes | View bytes | View/raw bytes | Segments | Soft boundaries | Markers kept | Marker keep rate | Markers/raw byte | Collapsed soft boundaries | Suffix groups | Marked suffix groups | Hard boundaries | Max segments/line | JSONL | Train view |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| train | 16000 | 22819852 | 24793995 | 1.086510 | 2987536 | 894466 | 498926 | 0.557792 | 0.021864 | 395540 | 0 | 0 | 5481707 | 890 | `artifacts/private/v2_0_candidate/protected_hard_train_only_high_value_suffix.train.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_train_only_high_value_suffix.train.txt` |
| valid | 1994 | 2843294 | 3090448 | 1.086925 | 371724 | 112121 | 62659 | 0.558852 | 0.022037 | 49462 | 0 | 0 | 682277 | 649 | `artifacts/private/v2_0_candidate/protected_hard_train_only_high_value_suffix.valid.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_train_only_high_value_suffix.valid.txt` |
| test | 1998 | 2781995 | 3022513 | 1.086455 | 363218 | 109169 | 60739 | 0.556376 | 0.021833 | 48430 | 0 | 0 | 666137 | 723 | `artifacts/private/v2_0_candidate/protected_hard_train_only_high_value_suffix.test.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_train_only_high_value_suffix.test.txt` |

## Next Use

Train a train-only Unigram model on the train view, then evaluate it
with markers stripped at encode time. Do not run tiny-LM before
token-pressure and visible intrinsic gates pass.
