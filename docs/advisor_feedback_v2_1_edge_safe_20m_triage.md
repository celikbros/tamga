# Advisor Feedback Triage: v2.1 Edge-Safe 20M Result

Date: 2026-06-12

## Fable5 Verdict

Fable5 accepted the safety result:

```text
exact roundtrip: 100%
protected edge alignment: 100%
crossing pieces: 0
```

But rejected promotion of the edge-safe artifact because the comparison was
against the wrong floor. The important omitted ladder was:

```text
bare SP64: 0.159620 test tokens/raw byte
inline all-route passthrough: 0.159668
numeric-SP floor: 0.164497
edge-safe sidecar: 0.169791
```

The edge-safe row proved the contract is implementable, but it pays an avoidable
byte-fallback implementation tax.

## Action Taken

We implemented:

```text
sp64_protected_presplit_sidecar
```

Mechanism:

```text
split at protected span edges before SP encoding
dummy-prefix-safe segment encoding
UTF-8 byte fallback for SP <unk>
no route-token vocab
```

## Result

| Candidate | Vocab | Valid tokens/raw byte | Test tokens/raw byte | Exact roundtrip | Edge alignment |
| --- | ---: | ---: | ---: | --- | --- |
| edge-safe sidecar | 64630 | 0.169341 | 0.169791 | valid/test 100% | valid/test 100% |
| pre-split sidecar | 64256 | 0.165261 | 0.165755 | valid/test 100% | valid/test 100% |

Fallback byte coverage for pre-split:

| Split | Fallback token rate | Fallback byte coverage |
| --- | ---: | ---: |
| valid | 0.021225 | 0.003493 |
| test | 0.021397 | 0.003531 |

Main fallback reason:

```text
dummy_prefix_missing_piece
```

`sp_unk` is tiny:

```text
valid: 28 bytes
test: 144 bytes
```

## Decision

Fable5's critique was correct. Do not consolidate edge-safe as the v2.1
baseline.

Current candidate:

```text
sp64_protected_presplit_sidecar
```

Next required step is a 20M fixed-byte tiny-LM run for pre-split sidecar, then
detector/protected stress.
