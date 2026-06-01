# v1.8 Hybrid Baseline Plan

Date: 2026-06-02

## Status

```text
hybrid pretokenized train corpus materialized
SentencePiece hybrid sweep config prepared
not a final LM serialization
```

## Purpose

The advisor reviews requested at least one hybrid baseline:

```text
morphology/protection-aware pretokenization + learned BPE/Unigram
```

The v1.8 hybrid baseline tests whether the custom tokenizer's boundary signal
is useful as a hard pretokenization prior for a learned tokenizer.

## Materialized Corpus

Private corpus:

```text
artifacts/private/v1_8_hybrid_morph_pretok/train.morph_pretok.txt
```

Public aggregate report:

```text
artifacts/v1_8_hybrid_morph_pretok_corpus.md
```

Input split:

```text
artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/train.txt
```

Summary:

| Lines | Input bytes | Output bytes | Output/Input bytes | Morph tokens | Avg morph tokens/line |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16000 | 22819852 | 32693579 | 1.4327 | 3881827 | 242.6142 |

## Sweep Config

```text
configs/v1_8_hybrid_sentencepiece_sweep.toml
```

Models:

```text
hybrid_morph_pretok_bpe_32000_train_only
hybrid_morph_pretok_unigram_32000_train_only
hybrid_morph_pretok_bpe_64000_train_only
hybrid_morph_pretok_unigram_64000_train_only
```

Command:

```powershell
python scripts/run_sentencepiece_sweep.py configs\v1_8_hybrid_sentencepiece_sweep.toml --force
```

The `--force` flag is required when rerunning after an earlier hybrid sweep,
because existing private SentencePiece model files would otherwise be reused.

The config sets:

```text
max_sentence_length = 20000
```

This avoids SentencePiece skipping long morph-pretokenized training lines.

## Caveat

This is a hard-boundary intrinsic baseline, not a final generation-oriented LM
serialization. The pretokenized corpus inserts visible spaces between custom
tokens, so it is larger than the raw train split.

Before using a hybrid design in actual LM training, v2.0 still needs:

```text
roundtrip-safe hybrid serialization
decoder path
tokens/byte and throughput accounting
comparison against raw train-only SP and pure custom lossless mode
```

## Current Decision

```text
P3 is prepared but not complete until the hybrid SP sweep is run and reported.
```
