# v1.7 SentencePiece Sweep: challenge

Dataset: `data/eval/tr_challenge.tsv`
Corpus: `data/train/claim_grade/celik_ai_claim_sample.txt`
Corpus label: `local_celik_ai_75k_line_pilot_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| sp_bpe_4000_celik_pilot | ok | 10.7037 | 3.0183 | 0.6480 | 0/108 |  |
| sp_unigram_4000_celik_pilot | ok | 10.6852 | 3.0131 | 0.6961 | 0/108 |  |
| sp_bpe_8000_celik_pilot | ok | 9.1111 | 2.5692 | 0.6714 | 0/108 |  |
| sp_unigram_8000_celik_pilot | ok | 9.1019 | 2.5666 | 0.7405 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_4000_celik_pilot F1 | sp_unigram_4000_celik_pilot F1 | sp_bpe_8000_celik_pilot F1 | sp_unigram_8000_celik_pilot F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.7143 | 0.7414 | 0.7327 | 0.7647 |
| code_mixed | 0.9315 | 0.5171 | 0.6124 | 0.5591 | 0.6444 |
| informal | 0.8649 | 0.7048 | 0.6239 | 0.7708 | 0.7312 |
| negative_word | 0.8317 | 0.6912 | 0.7391 | 0.7119 | 0.8205 |
| numbers_dates | 0.9649 | 0.5755 | 0.6619 | 0.5846 | 0.7031 |
| proper_name | 1.0000 | 0.7079 | 0.7746 | 0.7848 | 0.8302 |
| punctuation | 0.9921 | 0.6225 | 0.6443 | 0.6383 | 0.6714 |
| question | 0.9500 | 0.6621 | 0.7183 | 0.7121 | 0.8031 |
| softening | 0.8906 | 0.6928 | 0.6709 | 0.6522 | 0.6849 |
| suffix_chain | 0.8958 | 0.6262 | 0.6990 | 0.6051 | 0.7310 |
| verb_future | 0.8246 | 0.6536 | 0.6980 | 0.6901 | 0.7338 |
| verb_past | 0.9554 | 0.6824 | 0.7719 | 0.7105 | 0.8000 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
