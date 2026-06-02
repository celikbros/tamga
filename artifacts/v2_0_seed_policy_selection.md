# v2.0 Seed Policy Selection

Source seed vocab: `artifacts/private/v2_0_soft_morph/soft_morph_seed_vocab.train.tsv`
Private selected TSV: `artifacts/private/v2_0_soft_morph/protected_hard_soft_morph_seeded_sp64.selected_seed.tsv`

This report records the first seed policy for the
`protected_hard_soft_morph_seeded_sp64` prototype without listing raw
private corpus tokens.

## Policy

```text
include all suffix tokens
include all punctuation/symbol tokens
include protected tokens with count >= 10
include other non-word-start tokens
fill remaining budget with high-frequency word_start tokens
do not seed the word_start long-tail by default
```

## Summary

| Metric | Value |
| --- | ---: |
| budget | 64000 |
| selected unique | 64000 |
| unused budget | 0 |
| total seed unique | 218981 |
| selected token count | 3692289 |
| total seed token count | 3882002 |
| selected coverage | 0.951130 |
| word_start available slots after mandatory groups | 62560 |
| word_start min count | 2 |
| protected min count | 10 |

## Selected Coverage By Group

| Group | Unique selected | Covered token count | Share of all seed tokens |
| --- | ---: | ---: | ---: |
| other | 100 | 584 | 0.000150 |
| protected | 944 | 51231 | 0.013197 |
| punct_or_symbol | 152 | 430085 | 0.110789 |
| suffix | 244 | 925856 | 0.238500 |
| word_start | 62560 | 2284533 | 0.588494 |

## Selected Coverage By Reason

| Reason | Unique selected | Covered token count | Share of all seed tokens |
| --- | ---: | ---: | ---: |
| all_other | 100 | 584 | 0.000150 |
| all_punct_or_symbol | 152 | 430085 | 0.110789 |
| all_suffix | 244 | 925856 | 0.238500 |
| protected_count_ge_10 | 944 | 51231 | 0.013197 |
| top_word_start | 62560 | 2284533 | 0.588494 |

## Interpretation

This is a seed-selection policy, not a trained tokenizer. The next
prototype must show whether the unseeded word_start long-tail can be
handled by learned merges without falling back to bytes.
