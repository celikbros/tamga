# v1.7 SentencePiece Sweep: challenge

Dataset: `data/eval/tr_challenge.tsv`
Corpus: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/train.txt`
Corpus label: `v1_8_train_split_only_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| sp_bpe_16000_train_only | ok | 8.7963 | 2.4804 | 0.6937 | 0/108 |  |
| sp_unigram_16000_train_only | ok | 9.1019 | 2.5666 | 0.7227 | 0/108 |  |
| sp_bpe_32000_train_only | ok | 8.1852 | 2.3081 | 0.7036 | 0/108 |  |
| sp_unigram_32000_train_only | ok | 8.4630 | 2.3864 | 0.7412 | 0/108 |  |
| sp_bpe_64000_train_only | ok | 7.6667 | 2.1619 | 0.7032 | 0/108 |  |
| sp_unigram_64000_train_only | ok | 7.8056 | 2.2010 | 0.7351 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_16000_train_only F1 | sp_unigram_16000_train_only F1 | sp_bpe_32000_train_only F1 | sp_unigram_32000_train_only F1 | sp_bpe_64000_train_only F1 | sp_unigram_64000_train_only F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.7400 | 0.8235 | 0.7158 | 0.8081 | 0.7234 | 0.8041 |
| code_mixed | 0.9315 | 0.6102 | 0.5889 | 0.6082 | 0.6322 | 0.6380 | 0.6310 |
| informal | 0.8649 | 0.6947 | 0.6939 | 0.7500 | 0.7312 | 0.7765 | 0.7586 |
| negative_word | 0.8317 | 0.8103 | 0.8099 | 0.7965 | 0.8142 | 0.7850 | 0.8269 |
| numbers_dates | 0.9649 | 0.6066 | 0.6720 | 0.6102 | 0.7049 | 0.6195 | 0.7119 |
| proper_name | 1.0000 | 0.7625 | 0.8050 | 0.7871 | 0.8077 | 0.7763 | 0.8133 |
| punctuation | 0.9921 | 0.6714 | 0.6763 | 0.6615 | 0.7015 | 0.6562 | 0.7121 |
| question | 0.9500 | 0.7218 | 0.7846 | 0.7559 | 0.8226 | 0.7642 | 0.8333 |
| softening | 0.8906 | 0.6475 | 0.6806 | 0.6718 | 0.6963 | 0.6562 | 0.6769 |
| suffix_chain | 0.8958 | 0.7021 | 0.6869 | 0.6995 | 0.6848 | 0.6782 | 0.6272 |
| verb_future | 0.8246 | 0.5865 | 0.7121 | 0.6047 | 0.7087 | 0.6179 | 0.6942 |
| verb_past | 0.9554 | 0.7895 | 0.8000 | 0.8054 | 0.8354 | 0.7832 | 0.8158 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
