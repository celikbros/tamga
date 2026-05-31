# v1.7 SentencePiece Sweep: expanded

Dataset: `data/eval/tr_gold_expanded.tsv`
Corpus: `data/train/claim_grade/celik_ai_claim_sample.txt`
Corpus label: `local_celik_ai_75k_line_pilot_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| sp_bpe_4000_celik_pilot | ok | 8.0000 | 3.3058 | 0.6614 | 0/50 |  |
| sp_unigram_4000_celik_pilot | ok | 7.9400 | 3.2810 | 0.7091 | 0/50 |  |
| sp_bpe_8000_celik_pilot | ok | 7.0200 | 2.9008 | 0.6792 | 0/50 |  |
| sp_unigram_8000_celik_pilot | ok | 7.2400 | 2.9917 | 0.7441 | 0/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_4000_celik_pilot F1 | sp_unigram_4000_celik_pilot F1 | sp_bpe_8000_celik_pilot F1 | sp_unigram_8000_celik_pilot F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.5417 | 0.6186 | 0.5714 | 0.6292 |
| informal | 1.0000 | 0.7179 | 0.5238 | 0.7222 | 0.7778 |
| negative_word | 1.0000 | 0.6557 | 0.6984 | 0.7547 | 0.8302 |
| proper_name | 1.0000 | 0.8261 | 0.8706 | 0.7907 | 0.8810 |
| question | 1.0000 | 0.6875 | 0.7742 | 0.7458 | 0.8136 |
| softening | 1.0000 | 0.6000 | 0.6118 | 0.6053 | 0.6000 |
| suffix_chain | 1.0000 | 0.6796 | 0.7216 | 0.6739 | 0.7216 |
| verb_future | 1.0000 | 0.6154 | 0.7451 | 0.6531 | 0.7600 |
| verb_past | 1.0000 | 0.6222 | 0.8085 | 0.6341 | 0.7826 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
