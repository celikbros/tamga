# v2.0 Boundary-Weighted BPE Probe

Train corpus: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Max train lines: `100`
Vocab size: `120`
Min merge score: `2.0`

This is a research prototype for the training-time objective direction.
It is not a production tokenizer and does not claim LLM readiness.

## Summary

| Dataset | Model | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Merges | Crossing merges |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gold | boundary_weighted_bpe_lambda0 | 50 | 14.4600 | 5.9752 | 0.5424 | 0/50 | 42 | 20 |
| challenge | boundary_weighted_bpe_lambda0 | 108 | 19.4537 | 5.4856 | 0.5431 | 0/108 | 42 | 20 |
| gold | boundary_weighted_bpe_lambda4 | 50 | 14.8200 | 6.1240 | 0.5427 | 0/50 | 42 | 17 |
| challenge | boundary_weighted_bpe_lambda4 | 108 | 19.7130 | 5.5587 | 0.5406 | 0/108 | 42 | 17 |
| gold | boundary_weighted_bpe_lambda8 | 50 | 15.2600 | 6.3058 | 0.5508 | 0/50 | 42 | 17 |
| challenge | boundary_weighted_bpe_lambda8 | 108 | 19.9352 | 5.6214 | 0.5507 | 0/108 | 42 | 17 |

## Category F1

### challenge

| Category | boundary_weighted_bpe_lambda0 | boundary_weighted_bpe_lambda4 | boundary_weighted_bpe_lambda8 |
| --- | ---: | ---: | ---: |
| ambiguity | 0.5930 | 0.6012 | 0.5909 |
| code_mixed | 0.5172 | 0.5119 | 0.5310 |
| informal | 0.4878 | 0.4908 | 0.4848 |
| negative_word | 0.5022 | 0.4956 | 0.4706 |
| numbers_dates | 0.4907 | 0.4862 | 0.4932 |
| proper_name | 0.6074 | 0.5964 | 0.6043 |
| punctuation | 0.5192 | 0.5263 | 0.5333 |
| question | 0.5024 | 0.5024 | 0.5455 |
| softening | 0.5502 | 0.5447 | 0.5785 |
| suffix_chain | 0.5959 | 0.5838 | 0.5988 |
| verb_future | 0.4793 | 0.4856 | 0.4876 |
| verb_past | 0.6260 | 0.6260 | 0.6449 |

### gold

| Category | boundary_weighted_bpe_lambda0 | boundary_weighted_bpe_lambda4 | boundary_weighted_bpe_lambda8 |
| --- | ---: | ---: | ---: |
| code_mixed | 0.5000 | 0.4964 | 0.5180 |
| informal | 0.4483 | 0.4333 | 0.4262 |
| negative_word | 0.5217 | 0.5161 | 0.4571 |
| proper_name | 0.5752 | 0.5828 | 0.5752 |
| question | 0.5217 | 0.5319 | 0.5833 |
| softening | 0.5410 | 0.5238 | 0.5538 |
| suffix_chain | 0.6211 | 0.6098 | 0.6258 |
| verb_future | 0.4337 | 0.4941 | 0.5000 |
| verb_past | 0.6452 | 0.6349 | 0.6562 |

## Model Artifacts

- `boundary_weighted_bpe_lambda0`: `artifacts/private/v2_0_boundary_weighted_bpe_smoke_small/boundary_weighted_bpe_lambda0_vocab120.json`
- `boundary_weighted_bpe_lambda4`: `artifacts/private/v2_0_boundary_weighted_bpe_smoke_small/boundary_weighted_bpe_lambda4_vocab120.json`
- `boundary_weighted_bpe_lambda8`: `artifacts/private/v2_0_boundary_weighted_bpe_smoke_small/boundary_weighted_bpe_lambda8_vocab120.json`

## Gate

Continue this branch only if boundary penalties move F1 upward
without simply exploding token count. If the useful signal appears,
the next step is a real learned tokenizer objective, not this toy BPE.
