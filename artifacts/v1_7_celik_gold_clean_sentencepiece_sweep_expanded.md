# v1.7 SentencePiece Sweep: expanded

Dataset: `data/eval/tr_gold_expanded.tsv`
Corpus: `data/train/claim_grade/celik_gold_clean_pilot.txt`
Corpus label: `local_celik_gold_clean_100k_pilot_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| sp_bpe_8000_celik_gold_clean | ok | 7.1800 | 2.9669 | 0.6633 | 0/50 |  |
| sp_unigram_8000_celik_gold_clean | ok | 7.1800 | 2.9669 | 0.7377 | 0/50 |  |
| sp_bpe_16000_celik_gold_clean | ok | 6.4600 | 2.6694 | 0.6919 | 0/50 |  |
| sp_unigram_16000_celik_gold_clean | ok | 6.6200 | 2.7355 | 0.7425 | 0/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_8000_celik_gold_clean F1 | sp_unigram_8000_celik_gold_clean F1 | sp_bpe_16000_celik_gold_clean F1 | sp_unigram_16000_celik_gold_clean F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.5532 | 0.6170 | 0.5977 | 0.6353 |
| informal | 1.0000 | 0.7222 | 0.6000 | 0.7429 | 0.5946 |
| negative_word | 1.0000 | 0.7636 | 0.8148 | 0.7925 | 0.8627 |
| proper_name | 1.0000 | 0.7816 | 0.8780 | 0.8293 | 0.9024 |
| question | 1.0000 | 0.7586 | 0.8000 | 0.7857 | 0.8070 |
| softening | 1.0000 | 0.6133 | 0.6234 | 0.6479 | 0.6400 |
| suffix_chain | 1.0000 | 0.5895 | 0.7692 | 0.5581 | 0.7640 |
| verb_future | 1.0000 | 0.6531 | 0.8085 | 0.6957 | 0.7391 |
| verb_past | 1.0000 | 0.6190 | 0.7391 | 0.6667 | 0.6829 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
