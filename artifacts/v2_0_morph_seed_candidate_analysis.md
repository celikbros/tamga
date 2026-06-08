# v2.0 Morph Seed Candidate Analysis

Boundary JSONL: `artifacts/private/v2_0_soft_morph/soft_morph_boundaries.train.jsonl`
Private candidate TSV: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv`

This analysis uses train-only custom morphology pieces to identify
suffix/morph candidates for the next learned-tokenizer branch. It does
not train a tokenizer and does not tune against visible challenge rows.

## Parameters

| Parameter | Value |
| --- | ---: |
| min_count | 100 |
| min_surface_len | 3 |
| max_collision_rate | 0.050000 |
| protected_tail_hard_share | 0.250000 |

## Summary

| Metric | Value |
| --- | ---: |
| lines | 16000 |
| pieces | 6376173 |
| suffix unique | 244 |
| suffix occurrences | 925856 |
| uds_or_seed_candidate unique | 46 |
| uds_or_seed_candidate occurrences | 410170 |
| seed_bias_candidate unique | 61 |
| seed_bias_candidate occurrences | 480935 |
| protected_tail_review unique | 19 |
| protected_tail_review occurrences | 26131 |

## Recommendation Buckets

| Recommendation | Unique suffixes | Occurrences | Share of suffix occurrences |
| --- | ---: | ---: | ---: |
| low_count | 115 | 2015 | 0.002176 |
| protected_tail_review | 19 | 26131 | 0.028224 |
| review | 3 | 6605 | 0.007134 |
| seed_bias_candidate | 61 | 480935 | 0.519449 |
| uds_or_seed_candidate | 46 | 410170 | 0.443017 |

## Interpretation

`uds_or_seed_candidate` means the suffix is frequent, mostly introduced
by soft morphology boundaries, and has low exact surface collision with
non-suffix pieces in the train split.

`seed_bias_candidate` means the suffix may still be useful as a learned
prior, but should not be forced broadly as a user-defined symbol without
additional checks.

`protected_tail_review` means the suffix frequently appears after hard
apostrophe/protected boundaries and should be handled together with the
finite protected routing path, not blindly as a normal-text morph piece.

## Next Use

Use the private TSV to build a challenge-blind morph-piece policy. The
next tokenizer candidate should be compared against
`finite_protected_sp64_floor`, not bare SP64.
