# v2.2 LLM Handoff Smoke Audit

Config: `configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml`
Tokenizer: `sp64_protected_passthrough_sidecar`
Input: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/valid.txt, artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/test.txt`
Vocab size: `64256`
Batch smoke shape: `batch_size=4`, `seq_len=128`
Sidecar JSONL: `artifacts/private/v2_2_llm_handoff_smoke_valid_test_250.sidecar.jsonl`
Private failure samples: `artifacts/private/v2_2_llm_handoff_smoke_valid_test_250.failures.jsonl`

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
| `valid` | 250 | 379239 | 58083 | 0.153157 | 0 | 0.000000 | 250 | 0 | 861 | 0 | 0.002629 | 113 |
| `test` | 250 | 352601 | 54857 | 0.155578 | 2 | 0.000036 | 250 | 0 | 834 | 0 | 0.002706 | 107 |
| `all` | 500 | 731840 | 112940 | 0.154323 | 2 | 0.000018 | 500 | 0 | 1695 | 0 | 0.002666 | 221 |

## Protected Operation Summary

| Metric | Value |
| --- | ---: |
| protected spans | 1695 |
| protected bytes/raw byte | 0.014095 |
| conservative mask bytes | 12266 |
| extra mask bytes | 1951 |
| extra mask bytes/raw byte | 0.002666 |
| extra/protected byte | 0.189142 |
| edge-aligned span rate | 0.065487 |
| crossing span rate | 0.934513 |
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
