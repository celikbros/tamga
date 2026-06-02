# v2.0 Protected Route Inventory Analysis

Inventory: `artifacts/private/v2_0_protected_aware/protected_route_inventory.train.tsv`

This public report summarizes the private protected-route inventory
without listing raw protected surfaces. It is used to choose finite
protected pieces and user-defined-symbol thresholds.

## Inventory Summary

| Metric | Value |
| --- | ---: |
| protected unique surfaces | 29811 |
| protected occurrences | 96132 |
| protected surface bytes weighted by count | 596123 |
| suffix-tail unique surfaces | 159 |
| suffix-tail occurrences | 6618 |

## Protected Routes

| Route | Unique surfaces | Occurrences | Occurrence share | Weighted bytes |
| --- | ---: | ---: | ---: | ---: |
| apostrophe_surface | 2538 | 5477 | 0.056974 | 64350 |
| arabic_word | 86 | 100 | 0.001040 | 1148 |
| azerbaijani_word | 7 | 8 | 0.000083 | 98 |
| cyrillic_word | 11 | 13 | 0.000135 | 186 |
| file_like | 7204 | 9795 | 0.101891 | 174559 |
| greek_word | 41 | 479 | 0.004983 | 1078 |
| non_turkish_latin_word | 5716 | 15154 | 0.157637 | 130408 |
| numeric_like | 14199 | 65092 | 0.677111 | 224203 |
| uzbek_apostrophe_word | 9 | 14 | 0.000146 | 93 |

## Protected UDS Threshold Coverage

| Min count | Unique surfaces kept | Covered occurrences | Coverage |
| ---: | ---: | ---: | ---: |
| 1 | 29811 | 96132 | 1.000000 |
| 2 | 8134 | 74455 | 0.774508 |
| 5 | 2274 | 59707 | 0.621094 |
| 10 | 944 | 51231 | 0.532923 |
| 25 | 359 | 42878 | 0.446033 |
| 50 | 191 | 37194 | 0.386906 |
| 100 | 99 | 31005 | 0.322525 |

## Suffix Tails After Protected Bases

| Route | Unique surfaces | Occurrences | Occurrence share | Weighted bytes |
| --- | ---: | ---: | ---: | ---: |
| suffix_tail_after_file_like | 28 | 202 | 0.030523 | 485 |
| suffix_tail_after_non_turkish_latin_word | 55 | 1103 | 0.166667 | 2957 |
| suffix_tail_after_numeric_like | 76 | 5313 | 0.802811 | 12014 |

## Decision Hint

Do not promote all protected surfaces. If high thresholds cover little,
the protected encoder should favor subword pieces and byte fallback
over memorizing full protected strings.
