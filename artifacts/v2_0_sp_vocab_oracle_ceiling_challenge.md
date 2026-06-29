# v2.0 SP Vocab Oracle Ceiling Audit

Eval: `data/eval/tr_challenge.tsv`
Vocab: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab`

This diagnostic estimates whether the existing SP vocabulary can express
morphology-aligned paths before we invest in a custom trainer.

Modes:

- `lambda0`: in-family best-score lattice path with no boundary penalty.
- `no_cross`: best-score path that does not cross teacher soft boundaries.
- `oracle_best_f1`: path chosen to maximize internal teacher-boundary F1
  within each segment, with score only as a tie-breaker.

## Summary

| Mode | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 vs eval | Exact match | Crossed teacher boundaries | Teacher boundaries |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lambda0` | 108 | 7.3704 | 2.0783 | 0.7422 | 0/108 | 171 | 305 |
| `no_cross` | 108 | 9.0463 | 2.5509 | 0.8407 | 0/108 | 0 | 305 |
| `oracle_best_f1` | 108 | 9.0278 | 2.5457 | 0.8417 | 0/108 | 0 | 305 |

## Category F1

| Category | `lambda0` | `no_cross` | `oracle_best_f1` |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8125 | 0.9159 | 0.9159 |
| code_mixed | 0.6301 | 0.7485 | 0.7485 |
| informal | 0.7586 | 0.7692 | 0.7692 |
| negative_word | 0.8269 | 0.8448 | 0.8522 |
| numbers_dates | 0.8411 | 0.8870 | 0.8870 |
| proper_name | 0.7105 | 0.8506 | 0.8555 |
| punctuation | 0.7460 | 0.7786 | 0.7786 |
| question | 0.8522 | 0.9134 | 0.9134 |
| softening | 0.6875 | 0.7891 | 0.7891 |
| suffix_chain | 0.6310 | 0.8638 | 0.8638 |
| verb_future | 0.6942 | 0.7852 | 0.7852 |
| verb_past | 0.8212 | 0.9325 | 0.9325 |

## Reading

If `oracle_best_f1` is still close to SP64, score-side mechanisms cannot
recover much morphology signal. If it is much higher, the vocabulary
already contains useful paths and score/objective work is justified.
