# v2.2 LLM Handoff Smoke Audit

Config: `configs/v3_5_sidecar_sp64k_stratified_480mb.toml`
Tokenizer: `sp64k_stratified_480mb_protected_passthrough_sidecar`
Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_4_sample/stratified_480mb.txt`
Vocab size: `64256`
Batch smoke shape: `batch_size=4`, `seq_len=128`
Sidecar JSONL: `artifacts/private/v3_5_sidecar_sp64k_stratified_480mb_5k.sidecar.jsonl`
Private failure samples: `artifacts/private/v3_5_sidecar_sp64k_stratified_480mb_5k.failures.jsonl`

This audit is a handoff-hardening smoke test for the future v3.0
experimental tokenizer candidate. It checks exact decode, sidecar byte offsets, token id ranges,
fallback pressure, conservative protected-span masking overhead, and
whether the emitted token stream can form at least one LM batch window.

## Gate Summary

| Gate | Status |
| --- | --- |
| `exact_roundtrip` | PASS |
| `valid_token_ids` | PASS |
| `sidecar_offsets` | PASS |
| `passthrough_route_invariants` | PASS |
| `fallback_rate` | PASS |
| `extra_mask_bytes_per_byte` | PASS |
| `lm_batch_windows` | PASS |
| `overall` | PASS |

## Split Summary

| Split | Lines | Raw bytes | Tokens | Tokens/raw byte | Fallback source tokens | Fallback rate | Exact | Failures | Sidecar spans | Sidecar failures | Extra mask bytes/raw byte | LM windows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `stratified_480mb` | 5000 | 4910147 | 899120 | 0.183115 | 17 | 0.000019 | 5000 | 0 | 32556 | 0 | 0.006876 | 1765 |

## Protected Operation Summary

| Metric | Value |
| --- | ---: |
| protected spans | 32556 |
| protected bytes/raw byte | 0.030048 |
| conservative mask bytes | 181303 |
| extra mask bytes | 33764 |
| extra mask bytes/raw byte | 0.006876 |
| extra/protected byte | 0.228848 |
| edge-aligned span rate | 0.078972 |
| crossing span rate | 0.921028 |
| max extra bytes/span | 5 |

## Sidecar Schema Smoke

The sidecar JSONL emitted by this smoke contains one record per audited
line. Each record contains:

```text
schema_version
tokenizer
split
line_number
raw_bytes
token_count
fallback_source_tokens
spans[]: route, byte_start, byte_end, char_start, char_end, surface
```

For each span, this audit verifies that byte and character offsets slice
back to the recorded surface.

## Thresholds

| Threshold | Value |
| --- | ---: |
| max fallback rate | 0.001000 |
| max extra mask bytes/raw byte | 0.010000 |

## Interpretation

The v2.2 handoff smoke passed for this input. This does not make
the tokenizer a v3.0 release yet, but it is strong enough for
LLM-team integration smoke testing preparation.
