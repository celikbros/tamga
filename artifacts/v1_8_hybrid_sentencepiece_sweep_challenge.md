# v1.7 SentencePiece Sweep: challenge

Dataset: `data/eval/tr_challenge.tsv`
Corpus: `artifacts/private/v1_8_hybrid_morph_pretok/train.morph_pretok.txt`
Corpus label: `v1_8_hybrid_morph_pretok_train_only_not_claim_grade`
Status: `demo-only`
Max sentence length: `20000`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| hybrid_morph_pretok_bpe_32000_train_only | ok | 8.7870 | 2.4778 | 0.7255 | 0/108 |  |
| hybrid_morph_pretok_unigram_32000_train_only | ok | 9.6944 | 2.7337 | 0.7580 | 0/108 |  |
| hybrid_morph_pretok_bpe_64000_train_only | ok | 8.2222 | 2.3185 | 0.7370 | 0/108 |  |
| hybrid_morph_pretok_unigram_64000_train_only | ok | 9.0000 | 2.5379 | 0.7633 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | hybrid_morph_pretok_bpe_32000_train_only F1 | hybrid_morph_pretok_unigram_32000_train_only F1 | hybrid_morph_pretok_bpe_64000_train_only F1 | hybrid_morph_pretok_unigram_64000_train_only F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.8200 | 0.8077 | 0.8163 | 0.8000 |
| code_mixed | 0.9315 | 0.5943 | 0.5946 | 0.6012 | 0.6171 |
| informal | 0.8649 | 0.7416 | 0.6735 | 0.7674 | 0.6882 |
| negative_word | 0.8317 | 0.8000 | 0.8500 | 0.8302 | 0.8393 |
| numbers_dates | 0.9649 | 0.6929 | 0.7246 | 0.6942 | 0.7273 |
| proper_name | 1.0000 | 0.7952 | 0.8471 | 0.8125 | 0.8659 |
| punctuation | 0.9921 | 0.7007 | 0.6759 | 0.7111 | 0.6901 |
| question | 0.9500 | 0.8000 | 0.7737 | 0.8130 | 0.8154 |
| softening | 0.8906 | 0.6714 | 0.7887 | 0.6716 | 0.7737 |
| suffix_chain | 0.8958 | 0.6667 | 0.8190 | 0.6778 | 0.8163 |
| verb_future | 0.8246 | 0.7612 | 0.7429 | 0.7874 | 0.7407 |
| verb_past | 0.9554 | 0.7532 | 0.7975 | 0.7600 | 0.7826 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
