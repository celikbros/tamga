# v2.0 Soft Morph Artifact Materialization

Input: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
JSONL output: `artifacts/private/v2_0_soft_morph/soft_morph_boundaries.train.jsonl`
Seed output: `artifacts/private/v2_0_soft_morph/soft_morph_seed_vocab.train.tsv`
Max lines: `all`

This is a prototype artifact, not a production tokenizer. It records
custom morphology boundaries as soft hints while treating whitespace,
punctuation, apostrophes, script guards, and protected spans as hard
boundaries for later learned-vocabulary experiments.

## Summary

| Lines | Bytes | Pieces | Pieces/byte | Avg pieces/line | Seed tokens | Unique seed tokens | Soft boundaries | Hard boundaries | Whitespace pieces | Protected pieces | Suffix pieces | Max pieces/line |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16000 | 22819852 | 6376173 | 0.279413 | 398.5108 | 3882002 | 218981 | 894466 | 5481707 | 2494171 | 96132 | 925856 | 1541 |

## Boundary Meaning

- `soft`: morphology-proposed boundary; learned merges may cross it.
- `hard`: whitespace/protected/punctuation/script boundary; learned merges should not cross it in protected-aware candidates.

## Next Use

Use the JSONL to prototype soft-boundary learning or seeded-vocabulary
training. Use the seed TSV to inspect the actual custom pieces and
their frequencies before deciding which pieces should be seeded.
