# v2.0 Boundary-Biased Unigram Decode Sweep

SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
SP vocab: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Lambdas: `0.0, 2.0, 4.0, 8.0`

This is a diagnostic decode-time sweep. It does not train a tokenizer
and it does not change the SP64 vocabulary. Normal text is decoded with
a Viterbi lattice that subtracts a lambda penalty when a candidate piece
crosses custom-teacher soft morphology boundaries. Protected spans remain
hard-routed; numeric-like protected spans use the SP passthrough floor.

## Eval Summary

| Dataset | Model | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| gold | `finite_protected_sp64_numeric_sp_floor` | 50 | 6.0200 | 6.5400 | 2.7025 | 0.7317 | 1/50 |
| challenge | `finite_protected_sp64_numeric_sp_floor` | 108 | 7.7500 | 8.4907 | 2.3943 | 0.6913 | 0/108 |
| gold | `boundary_biased_lambda_0` | 50 | 5.8200 | 6.3400 | 2.6198 | 0.7572 | 1/50 |
| challenge | `boundary_biased_lambda_0` | 108 | 7.3704 | 8.1111 | 2.2872 | 0.7422 | 0/108 |
| gold | `boundary_biased_lambda_2` | 50 | 5.8200 | 6.3400 | 2.6198 | 0.7878 | 1/50 |
| challenge | `boundary_biased_lambda_2` | 108 | 7.3981 | 8.1389 | 2.2950 | 0.7606 | 0/108 |
| gold | `boundary_biased_lambda_4` | 50 | 5.9200 | 6.4400 | 2.6612 | 0.8144 | 1/50 |
| challenge | `boundary_biased_lambda_4` | 108 | 7.4907 | 8.2315 | 2.3211 | 0.7701 | 0/108 |
| gold | `boundary_biased_lambda_8` | 50 | 6.7200 | 7.2400 | 2.9917 | 0.9014 | 1/50 |
| challenge | `boundary_biased_lambda_8` | 108 | 8.2870 | 9.0278 | 2.5457 | 0.8225 | 0/108 |

## Protected Stress

| Model | Examples | Protected preserved | Break rate | Avg model tokens/example |
| --- | ---: | ---: | ---: | ---: |
| `finite_protected_sp64_numeric_sp_floor` | 34 | 25/25 | 0.0000 | 23.4412 |
| `boundary_biased_lambda_0` | 34 | 25/25 | 0.0000 | 22.5000 |
| `boundary_biased_lambda_2` | 34 | 25/25 | 0.0000 | 22.5000 |
| `boundary_biased_lambda_4` | 34 | 25/25 | 0.0000 | 22.5000 |
| `boundary_biased_lambda_8` | 34 | 25/25 | 0.0000 | 22.9118 |

## Split Token Pressure

Counts exclude per-line EOS tokens. Tiny-LM encoded split reports
will be slightly higher by roughly one EOS token per line.

| Split | Model | Lines | Raw bytes | Model tokens | Tokens/raw byte |
| --- | --- | ---: | ---: | ---: | ---: |
| test | `finite_protected_sp64_numeric_sp_floor` | 1998 | 2781995 | 478546 | 0.172015 |
| test | `boundary_biased_lambda_0` | 1998 | 2781995 | 453800 | 0.163120 |
| test | `boundary_biased_lambda_2` | 1998 | 2781995 | 453968 | 0.163181 |
| test | `boundary_biased_lambda_4` | 1998 | 2781995 | 456158 | 0.163968 |
| test | `boundary_biased_lambda_8` | 1998 | 2781995 | 496810 | 0.178580 |

## Challenge Category F1

| Category | `finite_protected_sp64_numeric_sp_floor` | `boundary_biased_lambda_0` | `boundary_biased_lambda_2` | `boundary_biased_lambda_4` | `boundary_biased_lambda_8` |
| --- | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0.7835 | 0.8125 | 0.8542 | 0.8542 | 0.8800 |
| code_mixed | 0.5906 | 0.6301 | 0.6438 | 0.6438 | 0.7097 |
| informal | 0.7416 | 0.7586 | 0.7586 | 0.7727 | 0.7865 |
| negative_word | 0.8269 | 0.8269 | 0.8269 | 0.8269 | 0.8440 |
| numbers_dates | 0.7963 | 0.8411 | 0.8411 | 0.8411 | 0.9027 |
| proper_name | 0.7059 | 0.7105 | 0.7237 | 0.7403 | 0.8193 |
| punctuation | 0.6569 | 0.7460 | 0.7460 | 0.7460 | 0.7656 |
| question | 0.7143 | 0.8522 | 0.8696 | 0.8696 | 0.9032 |
| softening | 0.6615 | 0.6875 | 0.7031 | 0.7132 | 0.7704 |
| suffix_chain | 0.6036 | 0.6310 | 0.6706 | 0.7011 | 0.8469 |
| verb_future | 0.6774 | 0.6942 | 0.6942 | 0.6942 | 0.7302 |
| verb_past | 0.6667 | 0.8212 | 0.8816 | 0.9091 | 0.9182 |

## Reading

- If increasing lambda raises Challenge F1 at near-flat token pressure,
  decode preference is a real bottleneck and a constrained objective is
  worth building.
- If lambda mostly raises token pressure or fails to improve F1, the
  current SP64 vocabulary/decoder is not easily rescued by boundary
  bias alone.
