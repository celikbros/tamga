# v2.0 Morph Seed Policy Selection

Source candidate TSV: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv`
Private policy TSV: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv`

This policy is challenge-blind. It selects morph pieces for a seed/bias
branch without forcing every suffix as a user-defined symbol.

## Parameters

| Parameter | Value |
| --- | ---: |
| min_count | 100 |
| safe_uds_min_len | 4 |
| safe_uds_max_collision | 0.001000 |
| safe_uds_max_hard_share | 0.010000 |

## Summary

| Metric | Value |
| --- | ---: |
| input unique | 244 |
| input occurrences | 925856 |
| selected unique | 107 |
| selected occurrences | 891105 |
| selected occurrence share | 0.962466 |
| heldout unique | 137 |
| heldout occurrences | 34751 |

## Action Summary

| Action | Unique | Occurrences | Share of input occurrences |
| --- | ---: | ---: | ---: |
| holdout | 137 | 34751 | 0.037534 |
| safe_uds_candidate_later | 7 | 9954 | 0.010751 |
| seed_bias | 100 | 881151 | 0.951715 |

## Reason Summary

| Reason | Unique | Occurrences | Share of input occurrences |
| --- | ---: | ---: | ---: |
| ambiguous_or_short_seed_only | 61 | 480935 | 0.519449 |
| below_policy_min_count | 115 | 2015 | 0.002176 |
| long_low_collision_low_hard_share | 7 | 9954 | 0.010751 |
| protected_tail_route_review | 19 | 26131 | 0.028224 |
| recommendation_review | 3 | 6605 | 0.007134 |
| safe_seed_not_forced | 39 | 400216 | 0.432266 |

## Decision

The first prototype should treat `seed_bias` pieces as a learned-vocab
prior, not as hard user-defined symbols.

`safe_uds_candidate_later` pieces are not automatically promoted in
the first run. They are only a small, auditable pool for a later UDS
experiment if the softer seed/bias branch fails.

`holdout` pieces stay out of the normal-text morph seed path. In
particular, protected-tail pieces belong with finite protected routing.
