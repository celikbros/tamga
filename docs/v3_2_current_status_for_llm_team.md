# Tokenizer v3.2 Current Status For LLM Team

Date: 2026-06-19

## One-Line Status

Tokenizer v3.2 is ready for LLM integration smoke testing, not main LLM
training.

Current smoke candidate:

```text
sp48k_protected_passthrough_sidecar_controls128
```

## Start Here

Read this first:

```text
docs/TOKENIZER_V3_2_LLM_INTEGRATION_SMOKE_REQUEST.md
```

Then use:

```text
configs/tokenizer_v3_0/tokenizer_config.v3_2.sp48k_integration_smoke.json
datasets/tokenizer_v3_3_smoke/sp48k_real_mix_full/manifest.json
```

## What You Should Test Now

Please test the actual LLM stack against the provided fixture:

```text
datasets/tokenizer_v3_2_smoke/sp48k_real_mix_1000/tokens.bin
datasets/tokenizer_v3_2_smoke/sp48k_real_mix_1000/loss_mask.bin
datasets/tokenizer_v3_2_smoke/sp48k_real_mix_1000/index.jsonl
datasets/tokenizer_v3_2_smoke/sp48k_real_mix_1000/sidecar.jsonl
```

The stronger default fixture is now the full real-mix fixture:

```text
datasets/tokenizer_v3_3_smoke/sp48k_real_mix_full/tokens.bin
datasets/tokenizer_v3_3_smoke/sp48k_real_mix_full/loss_mask.bin
datasets/tokenizer_v3_3_smoke/sp48k_real_mix_full/index.jsonl
datasets/tokenizer_v3_3_smoke/sp48k_real_mix_full/sidecar.jsonl
```

Required checks:

```text
uint32 token loading
uint8 loss-mask loading
batch creation
masked-token zero loss
<pad>=48256 accepted
<unk>=0 retained
<bos>=1 and <eos>=2 alias behavior accepted
sidecar byte-offset metadata does not break the pipeline
```

## What Not To Do Yet

Do not start main LLM training from this tokenizer package yet.

Do not remap `<unk>` to make `<pad>` id 0.

Do not inject chat/control tokens into raw text before SentencePiece
tokenization. Control tokens are wrapper-level ids.

## Current Evidence

The 48K candidate passed tokenizer-side checks:

```text
config validation: PASS
binary fixture validation: PASS
binary dataloader simulation: PASS
full real-mix fixture validation: PASS
full real-mix dataloader simulation: PASS
roundtrip/sidecar smoke: PASS
```

The full real-mix fixture summary:

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| tokens | 7350435 |
| tokens.bin bytes | 29401740 |
| loss_mask.bin bytes | 7350435 |
| max token id | 48244 |
| effective vocab size | 48384 |

Tokenizer-side dataloader simulation:

| Metric | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| full batches | 14356 |
| train label positions | 7071403 |
| masked label positions | 278869 |
| byte fallback tokens | 336 |
| status | PASS |

## Why 48K

48K is the current integration-smoke lead because it saves embedding rows and
showed a better early 2M-byte tiny-LM BPB result than the retrained 64K
reference.

This does not prove 48K is the final production tokenizer.

## Decision Needed From LLM Team

Please report one of:

```text
PASS: v3.2 fixture loads and trains through a smoke batch.
FAIL: exact dtype/id/mask/sidecar assumption that failed.
CHANGE REQUEST: final training requires embedded specials or different pad/unk policy.
```

Only after this response should tokenizer v3.2 move toward a training-final
candidate.
