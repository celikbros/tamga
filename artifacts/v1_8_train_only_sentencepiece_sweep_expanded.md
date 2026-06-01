# v1.7 SentencePiece Sweep: expanded

Dataset: `data/eval/tr_gold_expanded.tsv`
Corpus: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/train.txt`
Corpus label: `v1_8_train_split_only_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| sp_bpe_16000_train_only | ok | 6.8400 | 2.8264 | 0.7038 | 0/50 |  |
| sp_unigram_16000_train_only | ok | 7.0400 | 2.9091 | 0.7123 | 0/50 |  |
| sp_bpe_32000_train_only | ok | 6.4600 | 2.6694 | 0.7171 | 0/50 |  |
| sp_unigram_32000_train_only | ok | 6.4600 | 2.6694 | 0.7423 | 0/50 |  |
| sp_bpe_64000_train_only | ok | 5.8200 | 2.4050 | 0.7228 | 0/50 |  |
| sp_unigram_64000_train_only | ok | 6.0600 | 2.5041 | 0.7551 | 1/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_16000_train_only F1 | sp_unigram_16000_train_only F1 | sp_bpe_32000_train_only F1 | sp_unigram_32000_train_only F1 | sp_bpe_64000_train_only F1 | sp_unigram_64000_train_only F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.5882 | 0.6512 | 0.6173 | 0.6747 | 0.6494 | 0.6829 |
| informal | 1.0000 | 0.5128 | 0.6154 | 0.5556 | 0.7778 | 0.5882 | 0.7222 |
| negative_word | 1.0000 | 0.7925 | 0.8462 | 0.8077 | 0.8462 | 0.8235 | 0.8980 |
| proper_name | 1.0000 | 0.8434 | 0.8706 | 0.8434 | 0.8780 | 0.8642 | 0.9000 |
| question | 1.0000 | 0.7797 | 0.7797 | 0.7931 | 0.8070 | 0.8148 | 0.8000 |
| softening | 1.0000 | 0.6400 | 0.6667 | 0.6667 | 0.6286 | 0.6364 | 0.6087 |
| suffix_chain | 1.0000 | 0.7556 | 0.6598 | 0.7273 | 0.6889 | 0.6667 | 0.6988 |
| verb_future | 1.0000 | 0.6383 | 0.6383 | 0.6522 | 0.6667 | 0.7000 | 0.7143 |
| verb_past | 1.0000 | 0.6977 | 0.6364 | 0.7143 | 0.7500 | 0.7179 | 0.8205 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
