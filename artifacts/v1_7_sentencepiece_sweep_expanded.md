# v1.7 SentencePiece Sweep: expanded

Dataset: `data/eval/tr_gold_expanded.tsv`
Corpus: `data/train/tr_bpe_train.txt`
Corpus label: `demo_corpus_not_claim_grade`
Status: `demo-only`

This report is a reproducibility and wiring check unless the corpus is
explicitly marked claim-grade. It must not be used as hidden-eval or
downstream LLM-quality evidence.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| sp_bpe_1000_demo | ok | 6.6000 | 2.7273 | 0.6263 | 1/50 |  |
| sp_unigram_1000_demo | ok | 7.4400 | 3.0744 | 0.6325 | 0/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | sp_bpe_1000_demo F1 | sp_unigram_1000_demo F1 |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.6667 | 0.5882 |
| informal | 1.0000 | 0.7200 | 0.5882 |
| negative_word | 1.0000 | 0.7407 | 0.7333 |
| proper_name | 1.0000 | 0.6535 | 0.6600 |
| question | 1.0000 | 0.7333 | 0.7667 |
| softening | 1.0000 | 0.5915 | 0.5333 |
| suffix_chain | 1.0000 | 0.5057 | 0.5618 |
| verb_future | 1.0000 | 0.4815 | 0.6429 |
| verb_past | 1.0000 | 0.6341 | 0.6667 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
