# v1.7 SentencePiece Sweep: expanded

Dataset: `data/eval/tr_gold_expanded.tsv`
Corpus: `data/train/claim_grade/celik_gold_filtered_pilot.txt`
Corpus label: `local_celik_gold_100k_filtered_pilot_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| sp_bpe_4000_celik_gold_pilot | ok | 8.0000 | 3.3058 | 0.6424 | 0/50 |  |
| sp_unigram_4000_celik_gold_pilot | ok | 8.1600 | 3.3719 | 0.7125 | 0/50 |  |
| sp_bpe_8000_celik_gold_pilot | ok | 7.1800 | 2.9669 | 0.6633 | 0/50 |  |
| sp_unigram_8000_celik_gold_pilot | ok | 7.1800 | 2.9669 | 0.7445 | 0/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_4000_celik_gold_pilot F1 | sp_unigram_4000_celik_gold_pilot F1 | sp_bpe_8000_celik_gold_pilot F1 | sp_unigram_8000_celik_gold_pilot F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.5417 | 0.6667 | 0.5532 | 0.6596 |
| informal | 1.0000 | 0.6842 | 0.6341 | 0.7222 | 0.6000 |
| negative_word | 1.0000 | 0.6984 | 0.7419 | 0.7636 | 0.8148 |
| proper_name | 1.0000 | 0.8261 | 0.8667 | 0.7816 | 0.8780 |
| question | 1.0000 | 0.6769 | 0.7059 | 0.7586 | 0.8000 |
| softening | 1.0000 | 0.5926 | 0.5952 | 0.6133 | 0.6234 |
| suffix_chain | 1.0000 | 0.5800 | 0.6667 | 0.5895 | 0.7692 |
| verb_future | 1.0000 | 0.6154 | 0.7755 | 0.6531 | 0.8085 |
| verb_past | 1.0000 | 0.5778 | 0.7917 | 0.6190 | 0.7391 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
