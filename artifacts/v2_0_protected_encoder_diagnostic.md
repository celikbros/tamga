# v2.0 Protected Encoder Diagnostic

Inventory: `artifacts/private/v2_0_protected_aware/protected_route_inventory.train.tsv`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`

This diagnostic evaluates a stateless protected encoder that greedily
uses finite protected pieces and falls back to UTF-8 byte tokens for
all remaining protected text. It does not train a tokenizer.

## Summary

| Metric | Value |
| --- | ---: |
| protected unique surfaces | 29811 |
| protected occurrences | 96132 |
| source bytes | 596123 |
| selected protected pieces | 374 |
| mandatory byte fallback pieces | 256 |
| encoded tokens | 508924 |
| piece tokens | 507327 |
| byte fallback tokens | 1597 |
| tokens/source byte | 0.853723 |
| byte fallback byte rate | 0.002679 |
| byte token rate | 0.003138 |

## Route Summary

| Route | Unique surfaces | Occurrences | Source bytes | Tokens/source byte | Byte fallback byte rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| apostrophe_surface | 2538 | 5477 | 64350 | 0.927382 | 0.000000 |
| arabic_word | 86 | 100 | 1148 | 0.643728 | 0.306620 |
| azerbaijani_word | 7 | 8 | 98 | 0.959184 | 0.163265 |
| cyrillic_word | 11 | 13 | 186 | 1.000000 | 1.000000 |
| file_like | 7204 | 9795 | 174559 | 0.754541 | 0.000000 |
| greek_word | 41 | 479 | 1078 | 0.656772 | 0.313544 |
| non_turkish_latin_word | 5716 | 15154 | 130408 | 0.820954 | 0.005161 |
| numeric_like | 14199 | 65092 | 224203 | 0.930688 | 0.000018 |
| uzbek_apostrophe_word | 9 | 14 | 93 | 0.924731 | 0.301075 |

## Decision Hint

If byte fallback rate is low, the finite protected-piece path is
viable enough for a full tokenizer prototype. If it is high on
file/code/URL routes, protected piece selection needs another pass.
