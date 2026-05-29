# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| unicode_char | ok | 18.1600 | 7.5041 | 0.4947 | 0/50 |  |
| llama | skipped | 0.0000 | 0.0000 | 0.0000 | 0/0 | could not load 'meta-llama/Llama-3.2-1B' from remote download: You are trying to access a gated repo.
Make sure to have access to it at https://huggingface.co/meta-llama/Llama-3.2-1B.
401 Client Error. (Request ID: Root=1-6a1a1963-0a54d3013d17f0e13f0e41f3;be1b026a-ea44-4520-9c74-46306b02deb7)

Cannot access gated repo for url https://huggingface.co/meta-llama/Llama-3.2-1B/resolve/main/config.json.
Access to model meta-llama/Llama-3.2-1B is restricted. You must have access to it and be authenticated to access it. Please log in. |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | llama F1 |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.4768 | 0.0000 |
| informal | 1.0000 | 0.4478 | 0.0000 |
| negative_word | 1.0000 | 0.4167 | 0.0000 |
| proper_name | 1.0000 | 0.5087 | 0.0000 |
| question | 1.0000 | 0.5455 | 0.0000 |
| softening | 1.0000 | 0.5248 | 0.0000 |
| suffix_chain | 1.0000 | 0.4951 | 0.0000 |
| verb_future | 1.0000 | 0.4466 | 0.0000 |
| verb_past | 1.0000 | 0.6087 | 0.0000 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
