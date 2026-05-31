# v1.7 SentencePiece Sweep: challenge

Dataset: `data/eval/tr_challenge.tsv`
Corpus: `data/train/claim_grade/celik_gold_clean_pilot.txt`
Corpus label: `local_celik_gold_clean_100k_pilot_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| sp_bpe_8000_celik_gold_clean | ok | 9.1389 | 2.5770 | 0.6690 | 0/108 |  |
| sp_unigram_8000_celik_gold_clean | ok | 9.2037 | 2.5953 | 0.7369 | 0/108 |  |
| sp_bpe_16000_celik_gold_clean | ok | 8.3148 | 2.3446 | 0.6837 | 0/108 |  |
| sp_unigram_16000_celik_gold_clean | ok | 8.5093 | 2.3995 | 0.7340 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_8000_celik_gold_clean F1 | sp_unigram_8000_celik_gold_clean F1 | sp_bpe_16000_celik_gold_clean F1 | sp_unigram_16000_celik_gold_clean F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.7327 | 0.7885 | 0.7423 | 0.8081 |
| code_mixed | 0.9315 | 0.5426 | 0.6339 | 0.5682 | 0.6477 |
| informal | 0.8649 | 0.7629 | 0.7368 | 0.7912 | 0.7097 |
| negative_word | 0.8317 | 0.7438 | 0.8136 | 0.7679 | 0.8393 |
| numbers_dates | 0.9649 | 0.6047 | 0.6822 | 0.5785 | 0.6777 |
| proper_name | 1.0000 | 0.7702 | 0.7901 | 0.7922 | 0.8077 |
| punctuation | 0.9921 | 0.6383 | 0.6667 | 0.6466 | 0.6815 |
| question | 0.9500 | 0.7068 | 0.7786 | 0.7520 | 0.8130 |
| softening | 0.8906 | 0.6569 | 0.6939 | 0.6565 | 0.6383 |
| suffix_chain | 0.8958 | 0.5960 | 0.7461 | 0.6105 | 0.7351 |
| verb_future | 0.8246 | 0.6667 | 0.7206 | 0.6822 | 0.7176 |
| verb_past | 0.9554 | 0.7152 | 0.8250 | 0.7222 | 0.7763 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
