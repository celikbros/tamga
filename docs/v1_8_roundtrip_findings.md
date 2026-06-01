# v1.8 Roundtrip Findings

Date: 2026-06-01

## Status

```text
roundtrip check completed
filtered split used
all checked tokenizers have zero encode/decode failures
```

## Scope

Checked the filtered v1.8 local LM probe split:

```text
artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/
```

Public report:

```text
artifacts/v1_8_local_lm_probe_roundtrip.md
```

The public report does not include private corpus text snippets.

## Key Result

All checked tokenizers reconstruct every filtered split line exactly:

| Tokenizer family | Train failures | Valid failures | Test failures |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 0 | 0 | 0 |
| train-only SentencePiece BPE | 0 | 0 | 0 |
| train-only SentencePiece Unigram | 0 | 0 | 0 |

## Custom Tokenizer Change

The custom tokenizer now has an opt-in lossless mode:

```text
TurkishTokenizer(preserve_whitespace=True)
```

Default visible-eval behavior remains unchanged. The lossless mode preserves
whitespace spans explicitly and keeps suffix surface casing intact.

The roundtrip report uses this lossless mode for `custom_tr_morph`.

## Important Caveat

Lossless custom tokenization increases token pressure because whitespace spans
are explicit tokens:

| Tokenizer | Valid avg tokens/line |
| --- | ---: |
| custom_tr_morph | 398.3942 |
| sp_bpe_32000_train_only | 239.6540 |
| sp_unigram_32000_train_only | 240.4443 |
| sp_bpe_64000_train_only | 222.2578 |
| sp_unigram_64000_train_only | 225.7513 |

This does not invalidate the morphology-aware path, but it means the tiny LM
probe must report:

```text
bits-per-byte
tokens seen
bytes seen
effective context in bytes
throughput
parameter allocation
```

Token-level perplexity alone would be misleading.

## Current Decision

```text
P4 is cleared for v1.8 screening.
Use lossless custom mode for any generation-oriented LM probe.
Do not treat the older non-lossless default decode as LLM-ready.
```
