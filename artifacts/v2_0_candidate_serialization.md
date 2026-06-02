# v2.0 Candidate Serialization

Candidate: `protected_hard_soft_morph_seeded_sp64`

Boundary JSONL: `artifacts/private/v2_0_soft_morph/soft_morph_boundaries.train.jsonl`
Selected seed TSV: `artifacts/private/v2_0_soft_morph/protected_hard_soft_morph_seeded_sp64.selected_seed.tsv`
Private candidate JSONL: `artifacts/private/v2_0_candidate/protected_hard_soft_morph_seeded_sp64.train.jsonl`
Private train view: `artifacts/private/v2_0_candidate/protected_hard_soft_morph_seeded_sp64.train.txt`
Max lines: `all`

The candidate JSONL keeps raw `text` for lossless reconstruction. The
plain train view is only a learned-tokenizer training view; it is not
by itself a complete decoder artifact.

## Summary

| Lines | Raw bytes | Train-view bytes | Train-view/raw bytes | Pieces | Selected pieces | Selected piece rate | Unselected non-whitespace pieces | Unselected word_start pieces | Whitespace pieces | Protected pieces | Soft boundaries | Hard segments | Hard segments/raw byte | Max segments/line |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16000 | 22819852 | 34482902 | 1.511092 | 6376173 | 3692289 | 0.579076 | 189713 | 144812 | 2494171 | 96132 | 894466 | 2987536 | 0.130918 | 890 |

## Serialization Rules

- Soft morphology boundaries are represented with `SOFT_MARKER_U+E000` in the train view.
- Hard boundaries become train-view whitespace.
- Whitespace pieces are preserved in the candidate JSONL, but not as separate train-view tokens.
- Selected seed membership is recorded per piece in the candidate JSONL.

## Gate

Before training, verify that this train view does not recreate pure-custom
token pressure and that the JSONL remains the source for lossless decode.
The hard-segment/raw-byte value is only a segmentation floor; the learned
tokenizer can still split hard segments into more tokens.
