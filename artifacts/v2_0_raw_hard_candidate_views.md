# v2.0 Raw-Hard Candidate Views

Source candidate: `protected_hard_soft_morph_seeded_sp64`
Target candidate: `protected_hard_raw_sp64`
Source root: `artifacts/private/v2_0_candidate`

This candidate keeps hard boundaries as train-view whitespace but
collapses soft morphology boundaries back into raw surface text. It
avoids serializing custom token labels such as word-start markers,
suffix prefixes, or soft-marker characters into the learned tokenizer
training view.

## Summary

| Split | Lines | Raw bytes | View bytes | View/raw bytes | Segments | Segments/raw byte | Soft boundaries collapsed | Hard boundaries | Max segments/line | JSONL | Train view |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| train | 16000 | 22819852 | 23297217 | 1.020919 | 2987536 | 0.130918 | 894466 | 5481707 | 890 | `artifacts/private/v2_0_candidate/protected_hard_raw_sp64.train.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_raw_sp64.train.txt` |
| valid | 1994 | 2843294 | 2902471 | 1.020813 | 371724 | 0.130737 | 112121 | 682277 | 649 | `artifacts/private/v2_0_candidate/protected_hard_raw_sp64.valid.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_raw_sp64.valid.txt` |
| test | 1998 | 2781995 | 2840296 | 1.020957 | 363218 | 0.130560 | 109169 | 666137 | 723 | `artifacts/private/v2_0_candidate/protected_hard_raw_sp64.test.jsonl` | `artifacts/private/v2_0_candidate/protected_hard_raw_sp64.test.txt` |

## Gate

Train SentencePiece on this raw-hard view before any tiny-LM run.
If token pressure remains near pure custom lossless pressure, the
hard-boundary policy is still too aggressive or the view needs a
different learned-tokenizer design.
