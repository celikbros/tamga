# v2.0 Protected Piece Vocabulary Selection

Source inventory: `artifacts/private/v2_0_protected_aware/protected_route_inventory.train.tsv`
Private selected TSV: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`

This report records a conservative finite protected-piece selection.
It does not list private protected surfaces or selected raw pieces.

## Policy

```text
select character pieces from protected surfaces above threshold
select delimiter/operator runs above threshold
select file/URL-like extensions above threshold
select only stable common literals such as http/https/www/operators
do not promote rare full protected surfaces
keep 256 UTF-8 byte fallback pieces mandatory
```

## Thresholds

| Threshold | Value |
| --- | ---: |
| min char count | 25 |
| min delimiter count | 5 |
| min extension count | 5 |
| min literal count | 5 |

## Summary

| Metric | Value |
| --- | ---: |
| protected-piece budget | 4096 |
| selected unique pieces | 374 |
| unused budget | 3722 |
| candidate unique pieces | 2741 |
| selected weighted candidate count | 558306 |
| total weighted candidate count | 562108 |
| selected weighted coverage | 0.993236 |
| mandatory byte fallback pieces | 256 |

## Selected Pieces By Category

| Category | Unique selected | Weighted count | Share of selected count |
| --- | ---: | ---: | ---: |
| char_ascii_alpha | 52 | 276174 | 0.494664 |
| char_digit | 10 | 187837 | 0.336441 |
| char_non_ascii_alpha | 41 | 47335 | 0.084783 |
| char_punct_or_symbol | 12 | 35663 | 0.063877 |
| delimiter_run | 1 | 7 | 0.000013 |
| extension | 258 | 11290 | 0.020222 |

## Decision Hint

This is a finite protected-piece vocabulary proposal, not a final
tokenizer. The next gate is a stateless protected encoder that uses
these pieces greedily, then falls back to UTF-8 bytes for all
remaining protected text.
