# v2.0 Train-Only Marker View Materialization

Source candidate: `protected_hard_soft_morph_seeded_sp64`
Target candidate: `protected_hard_train_only_suffix_chain2`
Source root: `artifacts/private/v2_0_candidate`
Policy: `suffix_chain`
Soft marker: `U+E000`
Minimum suffix count: `2`
High-value suffix allowlist size: `35`

This materializes markerized SentencePiece training views for
train-only vocabulary shaping. The marker is not intended to be
inserted into normal text at encode time.

## Summary

| Split | Lines | Raw bytes | View bytes | View/raw bytes | Segments | Soft boundaries | Markers kept | Marker keep rate | Markers/raw byte | Collapsed soft boundaries | Suffix groups | Marked suffix groups | Hard boundaries | Max segments/line | JSONL | Train view |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| valid | 1994 | 2843294 | 3090649 | 1.086996 | 371724 | 112121 | 62726 | 0.559449 | 0.022061 | 49395 | 77848 | 28873 | 682277 | 649 | `artifacts/private/v2_0_candidate/protected_hard_train_only_suffix_chain2.valid.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_train_only_suffix_chain2.valid.txt` |

## Next Use

Train a train-only Unigram model on the train view, then evaluate it
with markers stripped at encode time. Do not run tiny-LM before
token-pressure and visible intrinsic gates pass.
