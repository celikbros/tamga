# SentencePiece Marker Vocabulary Audit

This checks whether train-only marker models learned vocabulary pieces
containing the private-use soft-boundary marker. Marker-containing pieces
consume vocab capacity and are not directly usable when normal encode
strips markers from raw text.

## Summary

| Model | Vocab | Marker pieces | Marker piece rate | Exact marker | Marker+surface | Prefix | Suffix | Internal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp64 | 64000 | 0 | 0.000000 | 0 | 0 | 0 | 0 | 0 |
| all_soft | 64000 | 1 | 0.000016 | 1 | 0 | 0 | 0 | 0 |
| suffix_chain2 | 64000 | 1 | 0.000016 | 1 | 0 | 0 | 0 | 0 |
| high_value_suffix | 64000 | 1 | 0.000016 | 1 | 0 | 0 | 0 | 0 |

## Examples

### sp64
No marker-containing pieces.

### all_soft
- `<M>`

### suffix_chain2
- `<M>`

### high_value_suffix
- `<M>`
