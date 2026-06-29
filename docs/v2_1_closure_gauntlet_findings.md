# v2.1 Closure Gauntlet Findings

Date: 2026-06-13

## Decision

The v2.1 protected-span baseline can be closed around:

```text
sp64_protected_passthrough_sidecar
```

This remains an experimental tokenizer contract, not a final production
tokenizer. The closed decision is narrower:

```text
Use byte-offset protected sidecar metadata with normal SP64 model tokens.
Do not make global protected-span token-boundary alignment the default.
```

## Gauntlet Summary

| Check | Result | Reading |
| --- | ---: | --- |
| unit/regression tests | 44 passed | helper behavior still coherent |
| detector battery | F1 1.000000 | no synthetic protected-span misses |
| valid roundtrip | 1994/1994 | lossless on valid split |
| test roundtrip | 1998/1998 | lossless on test split |
| real-mix conservative masking overhead | 0.003983 extra bytes/raw byte | passthrough over-mask cost is low |
| real-mix global pre-split tax | +0.006088 tokens/raw byte | global alignment costs ~3.63% |
| 20M tiny-LM test BPB | 1.947129 | selected baseline now has a fixed-byte LM row |

## Regression Lock

Report:

```text
docs/v2_1_regression_checklist.md
```

Latest locked values:

| Check | Result |
| --- | ---: |
| detector battery | 61 cases, 62 expected spans, F1 1.000000 |
| valid roundtrip | 1994/1994 |
| test roundtrip | 1998/1998 |
| dry-run train tokens/raw byte | 0.154684 |
| dry-run valid tokens/raw byte | 0.159026 |
| dry-run test tokens/raw byte | 0.159660 |

Important invariant:

```text
percent_encoded and azerbaijani_word must remain in the sidecar passthrough
route lists.
```

This invariant was added after the regression suite caught a real integration
bug where percent-encoded protected spans could fall back to byte ids and
decode with an extra SP dummy-prefix space.

## Real-Mix Token Pressure Audit

Report:

```text
artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
```

Input:

```text
artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt
```

Result:

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| raw bytes | 44351801 |
| protected spans | 149999 |
| protected bytes/raw byte | 0.015398 |
| protected line share | 0.680053 |
| SP tokens/raw byte | 0.167769 |
| passthrough tokens/raw byte | 0.167822 |
| pre-split tokens/raw byte | 0.173911 |
| pre-split tax tokens/raw byte | 0.006088 |
| pre-split relative tax | 0.036279 |

Dominant protected routes:

| Route | Occurrences | Bytes/raw byte |
| --- | ---: | ---: |
| numeric_like | 127588 | 0.009805 |
| file_like | 10309 | 0.003169 |
| apostrophe_surface | 7579 | 0.001574 |
| non_turkish_latin_word | 3228 | 0.000682 |
| percent_encoded | 171 | 0.000012 |

Interpretation:

```text
The real-mix sample reproduces the earlier pilot conclusion.
Global pre-split costs about +3.6% tokens/raw byte.
Route-selective alignment should be tested before any future global pre-split.
```

## 20M Tiny-LM Row

Report:

```text
artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

Setup:

```text
seq_len=128
batch_size=4
d_model=256
n_layers=4
n_heads=4
max_steps=6042
eval_interval=500
```

Encoding:

| Split | Lines | Bytes | Tokens | Tokens/raw byte | Fallback source tokens | Fallback source rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 3529856 | 0.154684 | 98 | 0.000028 |
| valid | 1994 | 2843294 | 452157 | 0.159026 | 28 | 0.000062 |
| test | 1998 | 2781995 | 444173 | 0.159660 | 144 | 0.000324 |

Training result:

| Metric | Value |
| --- | ---: |
| steps | 6042 |
| tokens seen | 3093504 |
| approx bytes seen | 19998919 |
| best valid BPB | 1.935810 |
| final valid BPB | 1.935810 |
| test BPB | 1.947129 |
| valid bits/token | 12.1730 |
| test bits/token | 12.1955 |

Interpretation:

```text
This row is a baseline reference for the selected v2.1 contract.
It is not evidence that passthrough is a final production tokenizer.
It is enough to close v2.1 sidecar selection unless downstream consumers
require exact token-boundary protected spans.
```

## Closed Branches

Closed as default:

```text
global pre-split sidecar
edge-safe byte-fallbacking whole crossing pieces
finite route-token protected wrapper as the main v2.1 contract
more morphology-tokenizer sweeps inside v2.1
```

Still available under explicit downstream requirement:

```text
sp64_protected_presplit_sidecar
route-selective pre-split, especially numeric_like
```

## Final v2.1 Reading

Close v2.1 as:

```text
SP64-family model token stream
+ UTF-8 byte fallback for true unknowns
+ protected-span sidecar with exact byte offsets and route labels
+ conservative byte-span-to-token overlap policy for masking/redaction
```

Do not claim:

```text
token-boundary protected spans
exact token-index protected ranges
base-model exact copy of protected spans
constrained decoding support over protected spans
```

## Reopen Criteria

Reopen v2.1 only if:

```text
LLM/SFT pipeline requires exact token-index protected spans
security policy rejects conservative boundary-token over-mask
constrained decoding or exact-copy requires protected token spans
future real pretraining mix has much higher protected density or mask overhead
one route class dominates enough to justify selective pre-splitting
```
