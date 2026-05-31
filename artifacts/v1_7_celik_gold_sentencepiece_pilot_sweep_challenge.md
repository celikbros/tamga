# v1.7 SentencePiece Sweep: challenge

Dataset: `data/eval/tr_challenge.tsv`
Corpus: `data/train/claim_grade/celik_gold_filtered_pilot.txt`
Corpus label: `local_celik_gold_100k_filtered_pilot_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| sp_bpe_4000_celik_gold_pilot | ok | 10.4074 | 2.9347 | 0.6506 | 0/108 |  |
| sp_unigram_4000_celik_gold_pilot | ok | 10.6574 | 3.0052 | 0.7101 | 0/108 |  |
| sp_bpe_8000_celik_gold_pilot | ok | 9.1389 | 2.5770 | 0.6690 | 0/108 |  |
| sp_unigram_8000_celik_gold_pilot | ok | 9.2130 | 2.5979 | 0.7388 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_4000_celik_gold_pilot F1 | sp_unigram_4000_celik_gold_pilot F1 | sp_bpe_8000_celik_gold_pilot F1 | sp_unigram_8000_celik_gold_pilot F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.7143 | 0.7692 | 0.7327 | 0.7885 |
| code_mixed | 0.9315 | 0.5200 | 0.6502 | 0.5426 | 0.6339 |
| informal | 0.8649 | 0.7184 | 0.6931 | 0.7629 | 0.7368 |
| negative_word | 0.8317 | 0.7101 | 0.7286 | 0.7438 | 0.8136 |
| numbers_dates | 0.9649 | 0.5882 | 0.6618 | 0.6047 | 0.6822 |
| proper_name | 1.0000 | 0.7314 | 0.8023 | 0.7702 | 0.8025 |
| punctuation | 0.9921 | 0.6267 | 0.6533 | 0.6383 | 0.6667 |
| question | 0.9500 | 0.6621 | 0.6897 | 0.7068 | 0.7786 |
| softening | 0.8906 | 0.6711 | 0.6543 | 0.6569 | 0.6939 |
| suffix_chain | 0.8958 | 0.5837 | 0.6761 | 0.5960 | 0.7461 |
| verb_future | 0.8246 | 0.6849 | 0.7273 | 0.6667 | 0.7206 |
| verb_past | 0.9554 | 0.6871 | 0.8276 | 0.7152 | 0.8323 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
