# v1.8 Hybrid Morph Pretokenized Corpus

Input: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/train.txt`
Output: `artifacts/private/v1_8_hybrid_morph_pretok/train.morph_pretok.txt`

This private corpus applies the deterministic morphology/protection
tokenizer to the train split and separates its pieces with spaces.
It is used only to train morphology-aware SentencePiece baselines.

## Summary

| Lines | Input bytes | Output bytes | Output/Input bytes | Morph tokens | Avg morph tokens/line | Max morph tokens/line |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16000 | 22819852 | 32693579 | 1.4327 | 3881827 | 242.6142 | 978 |

## Caveat

This is a hard-boundary intrinsic baseline corpus, not a final LM
serialization format. Generation-oriented hybrid use still needs an
explicit roundtrip-safe serialization/decoder.
