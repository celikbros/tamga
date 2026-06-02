# v2.0 Protected Route Materialization

Input: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
JSONL output: `artifacts/private/v2_0_protected_aware/protected_routes.train.jsonl`
Inventory output: `artifacts/private/v2_0_protected_aware/protected_route_inventory.train.tsv`
Max lines: `all`

This is the first finite protected-aware implementation step. It
does not train a tokenizer. It records which current tokenizer
pieces route to protected encoders and which Turkish suffix tails
attach after protected bases.

## Summary

| Lines | Bytes | Protected pieces | Protected pieces/byte | Unique protected surfaces | Suffix tails after protected | Unique suffix tails | Max routes/line |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16000 | 22819852 | 96132 | 0.004213 | 29811 | 6618 | 159 | 114 |

## Next Use

Use the inventory to select finite protected pieces and UDS candidates.
Do not promote rare full protected surfaces by default.
