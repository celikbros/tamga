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
| sp_bpe_1000_celik_gold_clean | ok | 19.1759 | 5.4073 | 0.5159 | 0/108 |  |
| sp_unigram_1000_celik_gold_clean | ok | 19.7778 | 5.5770 | 0.5287 | 0/108 |  |
| sp_bpe_4000_celik_gold_clean | ok | 10.4074 | 2.9347 | 0.6506 | 0/108 |  |
| sp_unigram_4000_celik_gold_clean | ok | 10.6574 | 3.0052 | 0.7101 | 0/108 |  |
| sp_bpe_8000_celik_gold_clean | ok | 9.1389 | 2.5770 | 0.6690 | 0/108 |  |
| sp_unigram_8000_celik_gold_clean | ok | 9.2037 | 2.5953 | 0.7369 | 0/108 |  |
| sp_bpe_16000_celik_gold_clean | ok | 8.3148 | 2.3446 | 0.6837 | 0/108 |  |
| sp_unigram_16000_celik_gold_clean | ok | 8.5093 | 2.3995 | 0.7340 | 0/108 |  |
| sp_bpe_32000_celik_gold_clean | ok | 7.6759 | 2.1645 | 0.6819 | 0/108 |  |
| sp_unigram_32000_celik_gold_clean | ok | 7.7778 | 2.1932 | 0.7353 | 0/108 |  |
| sp_bpe_64000_celik_gold_clean | ok | 7.0278 | 1.9817 | 0.6926 | 0/108 |  |
| sp_unigram_64000_celik_gold_clean | ok | 7.1204 | 2.0078 | 0.7327 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_1000_celik_gold_clean F1 | sp_unigram_1000_celik_gold_clean F1 | sp_bpe_4000_celik_gold_clean F1 | sp_unigram_4000_celik_gold_clean F1 | sp_bpe_8000_celik_gold_clean F1 | sp_unigram_8000_celik_gold_clean F1 | sp_bpe_16000_celik_gold_clean F1 | sp_unigram_16000_celik_gold_clean F1 | sp_bpe_32000_celik_gold_clean F1 | sp_unigram_32000_celik_gold_clean F1 | sp_bpe_64000_celik_gold_clean F1 | sp_unigram_64000_celik_gold_clean F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.5380 | 0.5355 | 0.7143 | 0.7692 | 0.7327 | 0.7885 | 0.7423 | 0.8081 | 0.7292 | 0.7789 | 0.7333 | 0.8132 |
| code_mixed | 0.9315 | 0.4820 | 0.4948 | 0.5200 | 0.6502 | 0.5426 | 0.6339 | 0.5682 | 0.6477 | 0.5783 | 0.6316 | 0.5987 | 0.6460 |
| informal | 0.8649 | 0.4875 | 0.4756 | 0.7184 | 0.6931 | 0.7629 | 0.7368 | 0.7912 | 0.7097 | 0.7674 | 0.7333 | 0.8148 | 0.7317 |
| negative_word | 0.8317 | 0.4955 | 0.4758 | 0.7101 | 0.7286 | 0.7438 | 0.8136 | 0.7679 | 0.8393 | 0.7778 | 0.8381 | 0.7921 | 0.8485 |
| numbers_dates | 0.9649 | 0.4636 | 0.4821 | 0.5882 | 0.6618 | 0.6047 | 0.6822 | 0.5785 | 0.6777 | 0.5983 | 0.7009 | 0.6071 | 0.6786 |
| proper_name | 1.0000 | 0.5692 | 0.5865 | 0.7314 | 0.8023 | 0.7702 | 0.7901 | 0.7922 | 0.8077 | 0.7785 | 0.7947 | 0.7724 | 0.7945 |
| punctuation | 0.9921 | 0.5000 | 0.5421 | 0.6267 | 0.6533 | 0.6383 | 0.6667 | 0.6466 | 0.6815 | 0.6562 | 0.7023 | 0.6667 | 0.7087 |
| question | 0.9500 | 0.5050 | 0.5258 | 0.6621 | 0.6897 | 0.7068 | 0.7786 | 0.7520 | 0.8130 | 0.7705 | 0.8403 | 0.7863 | 0.8319 |
| softening | 0.8906 | 0.5368 | 0.5410 | 0.6711 | 0.6543 | 0.6569 | 0.6939 | 0.6565 | 0.6383 | 0.6240 | 0.6457 | 0.6281 | 0.6281 |
| suffix_chain | 0.8958 | 0.5380 | 0.5460 | 0.5837 | 0.6761 | 0.5960 | 0.7461 | 0.6105 | 0.7351 | 0.5955 | 0.6667 | 0.6220 | 0.6303 |
| verb_future | 0.8246 | 0.4854 | 0.4790 | 0.6849 | 0.7273 | 0.6667 | 0.7206 | 0.6822 | 0.7176 | 0.6780 | 0.7642 | 0.6783 | 0.7692 |
| verb_past | 0.9554 | 0.5679 | 0.6295 | 0.6871 | 0.8276 | 0.7152 | 0.8250 | 0.7222 | 0.7763 | 0.7234 | 0.8000 | 0.7101 | 0.8000 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
