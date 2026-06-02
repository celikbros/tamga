# v2.0 Candidate SentencePiece Probe

Candidate: `protected_hard_soft_morph_seeded_sp64`
Config: `configs/v2_0_candidate_sentencepiece.toml`
Model: `artifacts/private/v2_0_candidate_sentencepiece/protected_hard_soft_morph_seeded_sp64_unigram_64000.model`

This is an intrinsic learned-tokenizer probe, not an LLM result.
The selected seed policy is recorded in candidate JSONL; this first
SentencePiece probe trains on the serialized train view and does not
force every selected seed as a user-defined symbol.

## Model Settings

| Setting | Value |
| --- | ---: |
| model_type | unigram |
| vocab_size | 64000 |
| split_by_whitespace | True |
| remove_extra_whitespaces | False |

## Token Pressure

| Split | Lines | Raw bytes | View bytes | View/raw bytes | SP tokens | SP tokens/view byte | SP tokens/raw byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 34482902 | 1.511092 | 8999966 | 0.260998 | 0.394392 |
| valid | 1994 | 2843294 | 4297686 | 1.511517 | 1132982 | 0.263626 | 0.398475 |
| test | 1998 | 2781995 | 4201532 | 1.510259 | 1106101 | 0.263261 | 0.397593 |

## Gate

Compare valid/test `SP tokens/raw byte` against:

```text
SP64 baseline valid/test: ~0.1566 / ~0.1570 tokens/raw byte
custom lossless+64k byte fallback valid/test: ~0.4162 / ~0.4194 tokens/raw byte
candidate hard segment floor valid/test: ~0.1307 / ~0.1306 segments/raw byte
```

The candidate is worth intrinsic evaluation only if it is much closer
to SP64 than to pure custom lossless pressure.
