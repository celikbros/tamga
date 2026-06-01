# v1.7 SentencePiece Sweep: expanded

Dataset: `data/eval/tr_gold_expanded.tsv`
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
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| hybrid_morph_pretok_bpe_32000_train_only | ok | 7.1200 | 2.9421 | 0.7177 | 0/50 |  |
| hybrid_morph_pretok_unigram_32000_train_only | ok | 7.5000 | 3.0992 | 0.8270 | 0/50 |  |
| hybrid_morph_pretok_bpe_64000_train_only | ok | 6.5400 | 2.7025 | 0.7478 | 1/50 |  |
| hybrid_morph_pretok_unigram_64000_train_only | ok | 7.1600 | 2.9587 | 0.8441 | 1/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | hybrid_morph_pretok_bpe_32000_train_only F1 | hybrid_morph_pretok_unigram_32000_train_only F1 | hybrid_morph_pretok_bpe_64000_train_only F1 | hybrid_morph_pretok_unigram_64000_train_only F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.5618 | 0.6742 | 0.5581 | 0.6977 |
| informal | 1.0000 | 0.6286 | 0.7222 | 0.6471 | 0.7222 |
| negative_word | 1.0000 | 0.8302 | 0.8214 | 0.8980 | 0.9020 |
| proper_name | 1.0000 | 0.8966 | 0.9556 | 0.9157 | 0.9318 |
| question | 1.0000 | 0.7931 | 0.8438 | 0.8070 | 0.9000 |
| softening | 1.0000 | 0.6027 | 0.7733 | 0.6197 | 0.7945 |
| suffix_chain | 1.0000 | 0.7059 | 0.9333 | 0.7500 | 0.9333 |
| verb_future | 1.0000 | 0.7500 | 0.8163 | 0.8000 | 0.8333 |
| verb_past | 1.0000 | 0.6977 | 0.7907 | 0.7895 | 0.7907 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
