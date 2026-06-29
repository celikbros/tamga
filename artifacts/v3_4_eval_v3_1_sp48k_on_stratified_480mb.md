# v2.0 Candidate SentencePiece Probe

Candidate: `v3_1_sp_unigram_48000_real_mix_eval_on_v3_4_stratified_480mb`
Config: `configs/v3_4_eval_v3_1_sp48k_on_stratified_480mb.toml`
Model: `artifacts/private/v3_1_vocab_ablation_sentencepiece/sp_unigram_48000_real_mix.model`

This is an intrinsic learned-tokenizer probe, not an LLM result.
SentencePiece trains on the configured train view.
Candidate metadata, when present, is diagnostic and is not enforced as SentencePiece user-defined symbols.

## Model Settings

| Setting | Value |
| --- | ---: |
| model_type | unigram |
| vocab_size | 48000 |
| split_by_whitespace | True |
| remove_extra_whitespaces | False |
| max_sentence_length | 16384 |
| user_defined_symbols | 0 |
| pretokenization_delimiter | '' |

## Token Pressure

| Split | Lines | Raw bytes | View bytes | View/raw bytes | SP tokens | SP tokens/view byte | SP tokens/raw byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 398469 | 396217280 | 396217280 | 1.000000 | 81756489 | 0.206343 | 0.206343 |
| valid | 49809 | 49279753 | 49279753 | 1.000000 | 10123874 | 0.205437 | 0.205437 |
| test | 49808 | 50024285 | 50024285 | 1.000000 | 10419025 | 0.208279 | 0.208279 |

## Gate

Compare valid/test `SP tokens/raw byte` against:

```text
SP64 baseline valid/test: ~0.1566 / ~0.1570 tokens/raw byte
custom lossless+64k byte fallback valid/test: ~0.4162 / ~0.4194 tokens/raw byte
candidate hard segment floor valid/test: ~0.1307 / ~0.1306 segments/raw byte
```

The candidate is worth intrinsic evaluation only if it is much closer
to SP64 than to pure custom lossless pressure.
