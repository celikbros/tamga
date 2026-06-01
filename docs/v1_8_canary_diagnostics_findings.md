# v1.8 Canary Diagnostics Findings

Date: 2026-06-02

## Status

```text
P6 canary diagnostics completed
public/synthetic diagnostic only
not hidden eval
not downstream LM evidence
```

## Purpose

This canary checks whether the tokenizer setup shows obvious robustness
failures before any tiny LM bits-per-byte probe.

Covered slices:

```text
clean Turkish
noisy / ASCII-folded Turkish
code-mixed Turkish-English
technical / URL / file-like spans
English apostrophes
Azerbaijani, Uzbek Latin, Kazakh/Kyrgyz/Tatar Cyrillic
Arabic, Russian, Greek
emoji / symbol text
```

## Artifacts

```text
data/eval/v1_8_canary.tsv
artifacts/v1_8_canary_diagnostics.md
scripts/report_v1_8_canary_diagnostics.py
```

## Summary

| Model | Avg tokens/word | Tokens/byte | Roundtrip failures | Protected broken |
| --- | ---: | ---: | ---: | ---: |
| custom_tr_morph_lossless | 2.2137 | 0.274882 | 0 | 0/7 |
| sp_bpe_32000_train_only | 3.5344 | 0.438863 | 0 | 7/7 |
| sp_unigram_32000_train_only | 3.6489 | 0.453081 | 0 | 7/7 |
| sp_bpe_64000_train_only | 3.3740 | 0.418957 | 0 | 7/7 |
| sp_unigram_64000_train_only | 3.4733 | 0.431280 | 0 | 7/7 |
| hybrid_morph_pretok_bpe_64000_train_only | 3.4733 | 0.431280 | 0 | 7/7 |
| hybrid_morph_pretok_unigram_64000_train_only | 3.5725 | 0.443602 | 0 | 7/7 |
| unicode_char | 5.9695 | 0.741232 | 23 | 7/7 |

## Interpretation

The canary did not find a generation-blocking lossless failure for
`custom_tr_morph_lossless`.

The custom tokenizer also preserved all auto-detected protected spans on the
canary set. The SP and hybrid SP baselines roundtrip successfully, but they
split all auto-detected protected spans in this diagnostic view.

The `unicode_char` row is retained as a fragmentation sanity check. Its
roundtrip failures are expected because the current Unicode-char helper is not
a whitespace-preserving generation tokenizer.

## Decision

```text
P6 is complete.
No canary result blocks proceeding to tiny LM bits-per-byte implementation.
The result is diagnostic only and must not be presented as LLM quality evidence.
```
