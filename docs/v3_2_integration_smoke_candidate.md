# v3.2 Integration Smoke Candidate

Date: 2026-06-19

## Status

This is not the production-final tokenizer.

It is the first stricter integration-smoke candidate after the v3.1 48K/64K
comparison:

```text
sp48k_protected_passthrough_sidecar_controls128
```

The candidate exists so the LLM side can test dataloader, masking, sidecar, and
control-token handling before we freeze the final tokenizer for main training.

## Why 48K Leads For This Step

The 48K sidecar candidate passed the same roundtrip, sidecar, fallback, and
binary corpus smoke gates as the 64K retrained reference.

At the 2M-byte tiny-LM calibration point:

| Candidate | Vocab | Test tokens/raw byte | Approx bytes seen | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| 48K sidecar | 48256 | 0.166703 | 1999973 | 3.276116 |
| 64K retrained sidecar | 64256 | 0.162877 | 1998931 | 3.321394 |

This does not prove 48K is final. It does make 48K the best current candidate
for integration smoke because it also saves:

```text
16000 embedding rows
about 32.768M embedding parameters at hidden size 2048
```

## Id Layout

The v3.2 smoke config keeps the SentencePiece ids unchanged:

| Range | Meaning |
| --- | --- |
| `0..47999` | SentencePiece ids |
| `48000..48255` | UTF-8 byte fallback ids |
| `48256..48383` | reserved wrapper control-token ids |

Assigned control ids:

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

The range `48266..48383` stays reserved for future integration smoke tokens.

## Contract

Normal text uses SentencePiece Unigram.

True unknown material uses UTF-8 byte fallback.

Protected spans use byte-offset sidecar metadata. Token-boundary alignment is
not guaranteed.

Training hot path:

```text
tokens.bin      uint32 little-endian
loss_mask.bin   uint8, 1=train, 0=masked protected overlap
index.jsonl
sidecar.jsonl
manifest.json
```

## Required LLM Smoke Before Final Training

Before this becomes anything stronger than an integration-smoke candidate:

```text
1. LLM stack accepts <pad>=48256 and <unk>=0.
2. Dataloader reads uint32 token ids without truncation.
3. Loss mask is consumed as uint8 and aligns with token count.
4. Chat/control-token injection happens outside raw text tokenization.
5. Sidecar metadata is either ignored safely or consumed by byte offsets.
6. A sample batch roundtrips through tokenizer encode/decode fixtures.
```

## Current Decision

Use v3.2 for integration smoke only.

Do not start main LLM training until the LLM architecture team explicitly
accepts this id layout or asks us to retrain a final tokenizer with embedded
special tokens.
