# v2.0 Morph Surface Vocabulary Coverage

Policy TSV: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv`
Private row diagnostics: `artifacts/private/v2_0_morph_vocab_coverage.rows.jsonl`

This audit separates vocabulary availability from decode preference.
It does not train a tokenizer and does not use challenge labels.

## Models

| Model | Path |
| --- | --- |
| `sp64` | `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model` |
| `safe_uds7` | `artifacts/private/v2_0_safe_uds/safe_uds_unigram_64000.model` |

## Summary

| Model | Entries | Occurrences | Exact-piece occurrence share | Vocab-surface occurrence share | Standalone-single occurrence share | Weighted avg standalone pieces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `sp64` | 100 | 881151 | 0.963019 | 0.963019 | 0.534474 | 1.465526 |
| `safe_uds7` | 100 | 881151 | 0.962751 | 0.962751 | 0.455065 | 1.544935 |

## Top Not Standalone-Encoded: `sp64`

These surfaces may still exist as exact vocab pieces. This table
shows decode preference on standalone suffix strings, not strict
vocab absence.

| Token | Surface | Count | Action | Recommendation | Standalone pieces |
| --- | --- | ---: | --- | --- | --- |
| `+ler` | `ler` | 47826 | `seed_bias` | `uds_or_seed_candidate` | `▁` `ler` |
| `+lar` | `lar` | 40249 | `seed_bias` | `uds_or_seed_candidate` | `▁` `lar` |
| `+mış` | `mış` | 28812 | `seed_bias` | `uds_or_seed_candidate` | `▁` `mış` |
| `+miş` | `miş` | 26859 | `seed_bias` | `uds_or_seed_candidate` | `▁` `miş` |
| `+ni` | `ni` | 25810 | `seed_bias` | `seed_bias_candidate` | `▁` `ni` |
| `+tır` | `tır` | 24886 | `seed_bias` | `uds_or_seed_candidate` | `▁` `tır` |
| `+dan` | `dan` | 24188 | `seed_bias` | `uds_or_seed_candidate` | `▁da` `n` |
| `+dir` | `dir` | 20823 | `seed_bias` | `uds_or_seed_candidate` | `▁` `dir` |
| `+nı` | `nı` | 20654 | `seed_bias` | `seed_bias_candidate` | `▁` `nı` |
| `+den` | `den` | 20194 | `seed_bias` | `uds_or_seed_candidate` | `▁de` `n` |
| `+sın` | `sın` | 19333 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `ın` |
| `+dır` | `dır` | 19230 | `seed_bias` | `uds_or_seed_candidate` | `▁` `dır` |
| `+lık` | `lık` | 14033 | `seed_bias` | `uds_or_seed_candidate` | `▁` `lık` |
| `+sin` | `sin` | 11735 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `in` |
| `+ım` | `ım` | 10481 | `seed_bias` | `seed_bias_candidate` | `▁ı` `m` |
| `+ın` | `ın` | 9016 | `seed_bias` | `seed_bias_candidate` | `▁` `ın` |
| `+eme` | `eme` | 8135 | `seed_bias` | `uds_or_seed_candidate` | `▁` `eme` |
| `+muş` | `muş` | 7410 | `seed_bias` | `uds_or_seed_candidate` | `▁` `muş` |
| `+ız` | `ız` | 3796 | `seed_bias` | `seed_bias_candidate` | `▁ı` `z` |
| `+sun` | `sun` | 3257 | `seed_bias` | `seed_bias_candidate` | `▁su` `n` |

## Top Missing Exact Vocab Piece: `sp64`

| Token | Surface | Count | Action | Recommendation | Standalone pieces |
| --- | --- | ---: | --- | --- | --- |
| `+sın` | `sın` | 19333 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `ın` |
| `+sin` | `sin` | 11735 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `in` |
| `+SİN` | `SİN` | 305 | `seed_bias` | `uds_or_seed_candidate` | `▁S` `İN` |
| `+SIN` | `SIN` | 273 | `seed_bias` | `uds_or_seed_candidate` | `▁S` `IN` |
| `+abil` | `abil` | 244 | `seed_bias` | `uds_or_seed_candidate` | `▁a` `bil` |
| `+EME` | `EME` | 183 | `seed_bias` | `uds_or_seed_candidate` | `▁E` `ME` |
| `+LAŞ` | `LAŞ` | 181 | `seed_bias` | `uds_or_seed_candidate` | `▁L` `AŞ` |
| `+sün` | `sün` | 178 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `ün` |
| `+UL` | `UL` | 154 | `seed_bias` | `seed_bias_candidate` | `▁U` `L` |

## Top Not Standalone-Encoded: `safe_uds7`

These surfaces may still exist as exact vocab pieces. This table
shows decode preference on standalone suffix strings, not strict
vocab absence.

| Token | Surface | Count | Action | Recommendation | Standalone pieces |
| --- | --- | ---: | --- | --- | --- |
| `+ler` | `ler` | 47826 | `seed_bias` | `uds_or_seed_candidate` | `▁` `ler` |
| `+lar` | `lar` | 40249 | `seed_bias` | `uds_or_seed_candidate` | `▁` `lar` |
| `+mış` | `mış` | 28812 | `seed_bias` | `uds_or_seed_candidate` | `▁` `mış` |
| `+miş` | `miş` | 26859 | `seed_bias` | `uds_or_seed_candidate` | `▁` `miş` |
| `+ni` | `ni` | 25810 | `seed_bias` | `seed_bias_candidate` | `▁` `ni` |
| `+tır` | `tır` | 24886 | `seed_bias` | `uds_or_seed_candidate` | `▁` `tır` |
| `+dan` | `dan` | 24188 | `seed_bias` | `uds_or_seed_candidate` | `▁da` `n` |
| `+tir` | `tir` | 23709 | `seed_bias` | `uds_or_seed_candidate` | `▁` `tir` |
| `+lik` | `lik` | 22111 | `seed_bias` | `uds_or_seed_candidate` | `▁` `lik` |
| `+dir` | `dir` | 20823 | `seed_bias` | `uds_or_seed_candidate` | `▁` `dir` |
| `+nı` | `nı` | 20654 | `seed_bias` | `seed_bias_candidate` | `▁` `nı` |
| `+den` | `den` | 20194 | `seed_bias` | `uds_or_seed_candidate` | `▁` `den` |
| `+sın` | `sın` | 19333 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `ın` |
| `+dır` | `dır` | 19230 | `seed_bias` | `uds_or_seed_candidate` | `▁` `dır` |
| `+lık` | `lık` | 14033 | `seed_bias` | `uds_or_seed_candidate` | `▁` `lık` |
| `+sin` | `sin` | 11735 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `in` |
| `+nu` | `nu` | 11647 | `seed_bias` | `seed_bias_candidate` | `▁` `nu` |
| `+um` | `um` | 11128 | `seed_bias` | `seed_bias_candidate` | `▁` `um` |
| `+ım` | `ım` | 10481 | `seed_bias` | `seed_bias_candidate` | `▁ı` `m` |
| `+ın` | `ın` | 9016 | `seed_bias` | `seed_bias_candidate` | `▁` `ın` |

## Top Missing Exact Vocab Piece: `safe_uds7`

| Token | Surface | Count | Action | Recommendation | Standalone pieces |
| --- | --- | ---: | --- | --- | --- |
| `+sın` | `sın` | 19333 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `ın` |
| `+sin` | `sin` | 11735 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `in` |
| `+yacak` | `yacak` | 480 | `seed_bias` | `uds_or_seed_candidate` | `▁y` `acak` |
| `+SİN` | `SİN` | 305 | `seed_bias` | `uds_or_seed_candidate` | `▁S` `İN` |
| `+SIN` | `SIN` | 273 | `seed_bias` | `uds_or_seed_candidate` | `▁S` `IN` |
| `+EME` | `EME` | 183 | `seed_bias` | `uds_or_seed_candidate` | `▁E` `ME` |
| `+LAŞ` | `LAŞ` | 181 | `seed_bias` | `uds_or_seed_candidate` | `▁L` `AŞ` |
| `+sün` | `sün` | 178 | `seed_bias` | `uds_or_seed_candidate` | `▁s` `ün` |
| `+UL` | `UL` | 154 | `seed_bias` | `seed_bias_candidate` | `▁U` `L` |

## Interpretation Gate

If high-value morph surfaces already exist as exact vocab pieces,
the next problem is decode preference, not vocabulary coverage. If
they are not available, seed/UDS/vocab construction remains the
bottleneck.

`finite_protected_sp64_numeric_sp_floor` uses the same normal-text SP64
vocabulary as `sp64`; numeric routing changes protected number spans,
not morph surface vocabulary coverage.
