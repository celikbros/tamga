# v2.0 Candidate SentencePiece Probe

Candidate: `safe_uds_unigram_64000`
Config: `configs/v2_0_safe_uds_sentencepiece.toml`
Model: `artifacts/private/v2_0_safe_uds/safe_uds_unigram_64000.model`

This is an intrinsic learned-tokenizer probe, not an LLM result.
SentencePiece trains on the configured train view.
Configured user-defined symbols are enforced by SentencePiece during training and encode.

## Model Settings

| Setting | Value |
| --- | ---: |
| model_type | unigram |
| vocab_size | 64000 |
| split_by_whitespace | True |
| remove_extra_whitespaces | False |
| max_sentence_length | 16384 |
| user_defined_symbols | 7 |

## Token Pressure

| Split | Lines | Raw bytes | View bytes | View/raw bytes | SP tokens | SP tokens/view byte | SP tokens/raw byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 22819852 | 1.000000 | 3531092 | 0.154738 | 0.154738 |
| valid | 1994 | 2843294 | 2843294 | 1.000000 | 452393 | 0.159109 | 0.159109 |
| test | 1998 | 2781995 | 2781995 | 1.000000 | 444239 | 0.159684 | 0.159684 |

## Gate

Compare valid/test `SP tokens/raw byte` against:

```text
SP64 baseline valid/test: ~0.1566 / ~0.1570 tokens/raw byte
custom lossless+64k byte fallback valid/test: ~0.4162 / ~0.4194 tokens/raw byte
candidate hard segment floor valid/test: ~0.1307 / ~0.1306 segments/raw byte
```

The candidate is worth intrinsic evaluation only if it is much closer
to SP64 than to pure custom lossless pressure.
