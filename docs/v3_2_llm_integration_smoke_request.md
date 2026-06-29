# v3.2 LLM Integration Smoke Request

Date: 2026-06-19

## Status

This is an integration-smoke request, not approval to start main LLM training.

Tokenizer candidate:

```text
sp48k_protected_passthrough_sidecar_controls128
```

The tokenizer team has validated the candidate package on the tokenizer side.
We now need the LLM stack to prove that it can consume the files and id layout
without hidden dataloader, masking, or special-token bugs.

## Files To Use

Config:

```text
C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.v3_2.sp48k_integration_smoke.json
```

SentencePiece model:

```text
C:\CELIK-GARDASH\models\tokenizer_v3_1\sp_unigram_48000_real_mix.model
C:\CELIK-GARDASH\models\tokenizer_v3_1\sp_unigram_48000_real_mix.vocab
```

Binary fixture:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_3_smoke\sp48k_real_mix_full\tokens.bin
C:\CELIK-GARDASH\datasets\tokenizer_v3_3_smoke\sp48k_real_mix_full\loss_mask.bin
C:\CELIK-GARDASH\datasets\tokenizer_v3_3_smoke\sp48k_real_mix_full\index.jsonl
C:\CELIK-GARDASH\datasets\tokenizer_v3_3_smoke\sp48k_real_mix_full\sidecar.jsonl
C:\CELIK-GARDASH\datasets\tokenizer_v3_3_smoke\sp48k_real_mix_full\manifest.json
```

Tokenizer-side validation reports:

```text
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_2_tokenizer_config_validation_sp48k_integration_smoke_gardash.md
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_3_tokenized_corpus_smoke_sp48k_real_mix_full.md
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_3_smoke_fixture_validation_sp48k_real_mix_full.md
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_3_binary_dataloader_simulation_sp48k_real_mix_full.md
```

## Id Layout

| Range | Meaning |
| --- | --- |
| `0..47999` | SentencePiece ids |
| `48000..48255` | UTF-8 byte fallback ids |
| `48256..48383` | wrapper control-token reserved range |

Important assigned ids:

| Token | Id |
| --- | ---: |
| `<unk>` | 0 |
| `<bos>` alias for `<s>` | 1 |
| `<eos>` alias for `</s>` | 2 |
| `<pad>` | 48256 |
| `<system>` | 48257 |
| `<user>` | 48258 |
| `<assistant>` | 48259 |
| `<thinking>` | 48260 |
| `</thinking>` | 48261 |
| `<answer>` | 48262 |
| `</answer>` | 48263 |
| `<tool_call>` | 48264 |
| `<tool_result>` | 48265 |

Do not remap `<unk>` to make `<pad>` id 0.

## Fixture Format

The tokenizer team produced:

```text
tokens.bin      uint32 little-endian
loss_mask.bin   uint8; 1=train, 0=masked protected overlap
index.jsonl     per-line token_start/token_end offsets
sidecar.jsonl   protected span byte/char offsets
manifest.json   machine-readable summary
```

Tokenizer-side fixture validation:

| Check | Result |
| --- | --- |
| token count | 7350435 |
| `tokens.bin` size | 29401740 bytes |
| `loss_mask.bin` size | 7350435 bytes |
| index rows | 40388 |
| sidecar rows | 40388 |
| max token id | 48244 |
| effective vocab size | 48384 |
| validation status | PASS |

Tokenizer-side packed dataloader simulation:

| Check | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| full batches | 14356 |
| train label positions | 7071403 |
| masked label positions | 278869 |
| status | PASS |

## LLM-Side Smoke Tests Requested

Please run these checks in the actual LLM dataloader/training stack:

```text
1. Read tokens.bin as uint32 little-endian without truncation.
2. Read loss_mask.bin as uint8 and confirm it has exactly one byte per token.
3. Build at least one real training batch from tokens.bin.
4. Apply loss_mask.bin so masked tokens produce zero loss.
5. Accept vocab/effective embedding size 48384.
6. Accept <pad>=48256 while keeping <unk>=0.
7. Confirm <bos>=1 and <eos>=2 alias behavior is acceptable.
8. Inject chat/control tokens outside raw text tokenization.
9. Either ignore sidecar.jsonl safely or load its byte offsets without assuming token-boundary alignment.
10. Report any dtype, id-range, padding, EOS, masking, or sidecar assumption failures.
```

## Pass Criteria

The LLM smoke passes if:

```text
tokens.bin and loss_mask.bin load successfully
batch construction works
loss masking works
no token id is rejected by embedding/id-range checks
<pad>=48256 is accepted
sidecar metadata does not break the pipeline
```

## Decision After Smoke

If this passes:

```text
v3.2 can be treated as the integration-smoke baseline.
```

If this fails:

```text
do not start main training
return the exact failing assumption to the tokenizer team
```

This package is still not the final production tokenizer. The final training
tokenizer requires a separate decision on full-corpus tokenizer retraining and
whether wrapper control tokens are acceptable long term.
