# v3.1 Sidecar Vocab Candidate Findings

Date: 2026-06-18

## Status

Internal evaluation. Do not hand to the LLM team as final yet.

This compares two newly trained real-mix SentencePiece candidates under the
same protected passthrough sidecar contract:

```text
sp48k_protected_passthrough_sidecar
sp64k_retrained_protected_passthrough_sidecar
```

The old v3.0 handoff model remains a separate pilot-trained 64K baseline.

## 1K Sidecar Smoke

Input:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_0\real_mix_60k_sample.txt
```

Scope:

```text
first 1000 lines
byte-offset sidecar
numeric SP passthrough
same route invariants
```

| Candidate | Vocab size | Tokens/raw byte | Fallback rate | Exact | Sidecar failures | Extra mask bytes/raw byte | Overall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 48K sidecar | 48256 | 0.161095 | 0.000006 | 1000/1000 | 0 | 0.003376 | PASS |
| 64K retrained sidecar | 64256 | 0.157006 | 0.000006 | 1000/1000 | 0 | 0.003418 | PASS |

48K token-pressure delta versus 64K retrained:

```text
0.161095 - 0.157006 = +0.004089 tokens/raw byte
relative: about +2.60%
```

## 250-Line Binary Corpus Smoke

The smoke emits:

```text
tokens.bin      uint32_le
loss_mask.bin   uint8, 1=train, 0=masked protected overlap
index.jsonl
sidecar.jsonl
manifest.json
```

| Candidate | Tokens/raw byte | Fallback rate | Masked token rate | Alignment mismatches | Max token id |
| --- | ---: | ---: | ---: | ---: | ---: |
| 48K sidecar | 0.166403 | 0.000000 | 0.034516 | 0 | 47899 |
| 64K retrained sidecar | 0.162406 | 0.000000 | 0.034013 | 0 | 63837 |

Binary size checks passed:

```text
tokens.bin bytes == token_count * 4
loss_mask.bin bytes == token_count
index.jsonl lines == sidecar.jsonl lines == input lines
```

## Parameter Trade-Off

At hidden size 2048:

```text
64K -> 48K saves 16000 embedding rows
16000 * 2048 = 32.768M parameters
```

The observed cost in the 1K sidecar smoke is about +2.6% token pressure.

## Reading

48K is not a toy compromise; it is a real candidate.

64K still wins compression:

```text
lower tokens/raw byte
slightly lower masked token rate in binary smoke
```

48K wins parameter budget:

```text
about 32.8M embedding params saved at hidden=2048
still passes exact roundtrip, sidecar, fallback, and binary mask gates
```

## Current Recommendation

Keep both 48K and 64K alive.

Do not run main LLM training yet because:

```text
special token registry is not frozen
the candidates are trained on 44 MB real-mix sample, not the full corpus
no BPB comparison for 48K vs 64K retrained yet
no LLM dataloader consumer has accepted the binary format yet
```

Next best internal step:

```text
Run a small fixed-byte tiny-LM BPB comparison:
  48K sidecar vs 64K retrained sidecar

Use the same fixed raw-byte budget and same seed.
```

Decision rule:

```text
If 48K BPB is within noise of 64K and the LLM team values the 32.8M parameter
savings, prefer 48K.

If 64K has a clear BPB win beyond token-pressure expectations, keep 64K.
```

## 2M-Byte Tiny-LM BPB Calibration

Reports:

```text
artifacts/v3_1_tiny_lm_sp48k_sidecar_2mbytes_rerun.md
artifacts/v3_1_tiny_lm_sp64k_retrained_sidecar_2mbytes.md
```

Both rows use the same tiny LM architecture:

```text
seq_len=128
batch_size=4
d_model=256
n_layers=4
n_heads=4
```

Step counts were chosen from each tokenizer's train tokens/raw byte to keep the
raw-byte budget near 2M.

| Candidate | Vocab | Test tokens/raw byte | Steps | Approx bytes seen | Valid BPB | Test BPB | Test bits/token |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 48K sidecar | 48256 | 0.166703 | 646 | 1999973 | 3.297038 | 3.276116 | 19.6524 |
| 64K retrained sidecar | 64256 | 0.162877 | 628 | 1998931 | 3.342602 | 3.321394 | 20.3921 |

Delta:

```text
48K test BPB - 64K test BPB = -0.045278
48K test token pressure delta = +0.003826 tokens/raw byte
```

Reading:

```text
At this early 2M-byte tiny-LM checkpoint, 48K is better on BPB despite higher
token pressure. This is a useful signal for the 48K candidate, but it is not a
converged LM-quality result. Both rows still have bits/token above log2(vocab),
so the smaller vocabulary may be benefiting from early optimization geometry.
```

Updated recommendation:

```text
Keep 48K as the leading v3.1 research candidate for integration smoke.
Keep 64K retrained as the compression reference.
Do not freeze either as production final without:
  - special token registry decision
  - LLM dataloader consumer acceptance
  - at least one longer or second-seed confirmation if the LLM team cares about
    the 48K/64K choice
```
