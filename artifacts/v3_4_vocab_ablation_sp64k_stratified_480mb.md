# v2.0 Candidate SentencePiece Probe

Candidate: `v3_4_sp_unigram_64000_stratified_480mb`
Config: `configs/v3_4_vocab_ablation_sp64k_stratified_480mb.toml`
Model: `artifacts/private/v3_4_vocab_ablation_sentencepiece/sp_unigram_64000_stratified_480mb.model`

This is an intrinsic learned-tokenizer probe, not an LLM result.
SentencePiece trains on the configured train view.
Candidate metadata, when present, is diagnostic and is not enforced as SentencePiece user-defined symbols.

## Model Settings

| Setting | Value |
| --- | ---: |
| model_type | unigram |
| vocab_size | 64000 |
| split_by_whitespace | True |
| remove_extra_whitespaces | False |
| max_sentence_length | 16384 |
| user_defined_symbols | 0 |
| pretokenization_delimiter | '' |

## Token Pressure

| Split | Lines | Raw bytes | View bytes | View/raw bytes | SP tokens | SP tokens/view byte | SP tokens/raw byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 398469 | 396217280 | 396217280 | 1.000000 | 72632895 | 0.183316 | 0.183316 |
| valid | 49809 | 49279753 | 49279753 | 1.000000 | 9022707 | 0.183092 | 0.183092 |
| test | 49808 | 50024285 | 50024285 | 1.000000 | 9242860 | 0.184767 | 0.184767 |

## Gate

Compare valid/test `SP tokens/raw byte` against:

```text
SP64 baseline valid/test: ~0.1566 / ~0.1570 tokens/raw byte
custom lossless+64k byte fallback valid/test: ~0.4162 / ~0.4194 tokens/raw byte
candidate hard segment floor valid/test: ~0.1307 / ~0.1306 segments/raw byte
```

The candidate is worth intrinsic evaluation only if it is much closer
to SP64 than to pure custom lossless pressure.
