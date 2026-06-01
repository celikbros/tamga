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
| sp_bpe_1000_celik_gold_clean | ok | 14.1800 | 5.8595 | 0.5122 | 0/50 |  |
| sp_unigram_1000_celik_gold_clean | ok | 14.5600 | 6.0165 | 0.5375 | 0/50 |  |
| sp_bpe_4000_celik_gold_clean | ok | 8.0000 | 3.3058 | 0.6424 | 0/50 |  |
| sp_unigram_4000_celik_gold_clean | ok | 8.1600 | 3.3719 | 0.7125 | 0/50 |  |
| sp_bpe_8000_celik_gold_clean | ok | 7.1800 | 2.9669 | 0.6633 | 0/50 |  |
| sp_unigram_8000_celik_gold_clean | ok | 7.1800 | 2.9669 | 0.7377 | 0/50 |  |
| sp_bpe_16000_celik_gold_clean | ok | 6.4600 | 2.6694 | 0.6919 | 0/50 |  |
| sp_unigram_16000_celik_gold_clean | ok | 6.6200 | 2.7355 | 0.7425 | 0/50 |  |
| sp_bpe_32000_celik_gold_clean | ok | 6.0600 | 2.5041 | 0.6916 | 0/50 |  |
| sp_unigram_32000_celik_gold_clean | ok | 6.0600 | 2.5041 | 0.7290 | 1/50 |  |
| sp_bpe_64000_celik_gold_clean | ok | 5.6000 | 2.3140 | 0.6992 | 2/50 |  |
| sp_unigram_64000_celik_gold_clean | ok | 5.6200 | 2.3223 | 0.7329 | 2/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_1000_celik_gold_clean F1 | sp_unigram_1000_celik_gold_clean F1 | sp_bpe_4000_celik_gold_clean F1 | sp_unigram_4000_celik_gold_clean F1 | sp_bpe_8000_celik_gold_clean F1 | sp_unigram_8000_celik_gold_clean F1 | sp_bpe_16000_celik_gold_clean F1 | sp_unigram_16000_celik_gold_clean F1 | sp_bpe_32000_celik_gold_clean F1 | sp_unigram_32000_celik_gold_clean F1 | sp_bpe_64000_celik_gold_clean F1 | sp_unigram_64000_celik_gold_clean F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.4697 | 0.5224 | 0.5417 | 0.6667 | 0.5532 | 0.6170 | 0.5977 | 0.6353 | 0.6000 | 0.6265 | 0.6316 | 0.6753 |
| informal | 1.0000 | 0.5263 | 0.3871 | 0.6842 | 0.6341 | 0.7222 | 0.6000 | 0.7429 | 0.5946 | 0.7429 | 0.6667 | 0.7647 | 0.7429 |
| negative_word | 1.0000 | 0.4694 | 0.4615 | 0.6984 | 0.7419 | 0.7636 | 0.8148 | 0.7925 | 0.8627 | 0.8077 | 0.8750 | 0.8511 | 0.9130 |
| proper_name | 1.0000 | 0.5417 | 0.6111 | 0.8261 | 0.8667 | 0.7816 | 0.8780 | 0.8293 | 0.9024 | 0.8395 | 0.9136 | 0.8052 | 0.8421 |
| question | 1.0000 | 0.5393 | 0.5684 | 0.6769 | 0.7059 | 0.7586 | 0.8000 | 0.7857 | 0.8070 | 0.7857 | 0.8000 | 0.8000 | 0.7925 |
| softening | 1.0000 | 0.5000 | 0.5313 | 0.5926 | 0.5952 | 0.6133 | 0.6234 | 0.6479 | 0.6400 | 0.6377 | 0.6087 | 0.6269 | 0.5846 |
| suffix_chain | 1.0000 | 0.5590 | 0.5867 | 0.5800 | 0.6667 | 0.5895 | 0.7692 | 0.5581 | 0.7640 | 0.5301 | 0.6585 | 0.5250 | 0.6585 |
| verb_future | 1.0000 | 0.4557 | 0.4198 | 0.6154 | 0.7755 | 0.6531 | 0.8085 | 0.6957 | 0.7391 | 0.6829 | 0.7143 | 0.7179 | 0.7317 |
| verb_past | 1.0000 | 0.5246 | 0.6774 | 0.5778 | 0.7917 | 0.6190 | 0.7391 | 0.6667 | 0.6829 | 0.6842 | 0.7179 | 0.7027 | 0.7368 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
