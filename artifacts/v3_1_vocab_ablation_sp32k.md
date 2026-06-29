# v2.0 Candidate SentencePiece Probe

Candidate: `v3_1_sp_unigram_32000_real_mix`
Config: `configs/v3_1_vocab_ablation_sp32k.toml`
Model: `artifacts/private/v3_1_vocab_ablation_sentencepiece/sp_unigram_32000_real_mix.model`

This is an intrinsic learned-tokenizer probe, not an LLM result.
SentencePiece trains on the configured train view.
Candidate metadata, when present, is diagnostic and is not enforced as SentencePiece user-defined symbols.

## Model Settings

| Setting | Value |
| --- | ---: |
| model_type | unigram |
| vocab_size | 32000 |
| split_by_whitespace | True |
| remove_extra_whitespaces | False |
| max_sentence_length | 16384 |
| user_defined_symbols | 0 |
| pretokenization_delimiter | '' |

## Token Pressure

| Split | Lines | Raw bytes | View bytes | View/raw bytes | SP tokens | SP tokens/view byte | SP tokens/raw byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 32311 | 35511533 | 35511533 | 1.000000 | 6123376 | 0.172433 | 0.172433 |
| valid | 4039 | 4404796 | 4404796 | 1.000000 | 766385 | 0.173989 | 0.173989 |
| test | 4038 | 4435472 | 4435472 | 1.000000 | 766665 | 0.172849 | 0.172849 |

## Gate

Compare valid/test `SP tokens/raw byte` against:

```text
SP64 baseline valid/test: ~0.1566 / ~0.1570 tokens/raw byte
custom lossless+64k byte fallback valid/test: ~0.4162 / ~0.4194 tokens/raw byte
candidate hard segment floor valid/test: ~0.1307 / ~0.1306 segments/raw byte
```

The candidate is worth intrinsic evaluation only if it is much closer
to SP64 than to pure custom lossless pressure.
