# v2.0 Candidate SentencePiece Probe

Candidate: `morph_seed_bias_unigram_64000`
Config: `configs/v2_0_morph_seed_bias_sentencepiece.toml`
Model: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_bias_unigram_64000.model`

This is an intrinsic learned-tokenizer probe, not an LLM result.
SentencePiece trains on the serialized train view. Candidate metadata,
when present, is diagnostic and is not enforced as SentencePiece
user-defined symbols in this first probe.

## Model Settings

| Setting | Value |
| --- | ---: |
| model_type | unigram |
| vocab_size | 64000 |
| split_by_whitespace | True |
| remove_extra_whitespaces | False |
| max_sentence_length | 16384 |

## Token Pressure

| Split | Lines | Raw bytes | View bytes | View/raw bytes | SP tokens | SP tokens/view byte | SP tokens/raw byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16100 | 22820344 | 22820344 | 1.000000 | 3513990 | 0.153985 | 0.153985 |
| valid | 1994 | 2843294 | 2843294 | 1.000000 | 450128 | 0.158312 | 0.158312 |
| test | 1998 | 2781995 | 2781995 | 1.000000 | 442062 | 0.158901 | 0.158901 |

## Gate

Compare valid/test `SP tokens/raw byte` against:

```text
SP64 baseline valid/test: ~0.1566 / ~0.1570 tokens/raw byte
custom lossless+64k byte fallback valid/test: ~0.4162 / ~0.4194 tokens/raw byte
candidate hard segment floor valid/test: ~0.1307 / ~0.1306 segments/raw byte
```

The candidate is worth intrinsic evaluation only if it is much closer
to SP64 than to pure custom lossless pressure.
