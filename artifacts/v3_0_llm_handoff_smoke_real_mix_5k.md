# v3.0 LLM Handoff Smoke Audit

Config: `configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml`
Tokenizer: `sp64_protected_passthrough_sidecar`
Input: `artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt`
Vocab size: `64256`
Batch smoke shape: `batch_size=4`, `seq_len=128`
Sidecar JSONL: `artifacts/private/v3_0_llm_handoff_smoke_real_mix_5k.sidecar.jsonl`
Private failure samples: `artifacts/private/v3_0_llm_handoff_smoke_real_mix_5k.failures.jsonl`

This audit is a handoff smoke test for the v3.0 experimental tokenizer
candidate. It checks exact decode, sidecar byte offsets, token id ranges,
fallback pressure, conservative protected-span masking overhead, and
whether the emitted token stream can form at least one LM batch window.

## Gate Summary

| Gate | Status |
| --- | --- |
| `exact_roundtrip` | PASS |
| `valid_token_ids` | PASS |
| `sidecar_offsets` | PASS |
| `percent_encoded_route_invariant` | PASS |
| `fallback_rate` | PASS |
| `extra_mask_bytes_per_byte` | PASS |
| `lm_batch_windows` | PASS |
| `overall` | PASS |

## Split Summary

| Split | Lines | Raw bytes | Tokens | Tokens/raw byte | Fallback source tokens | Fallback rate | Exact | Failures | Sidecar spans | Sidecar failures | Extra mask bytes/raw byte | LM windows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `real_mix_60k_sample` | 5000 | 6119247 | 959396 | 0.156783 | 701 | 0.000731 | 5000 | 0 | 16683 | 0 | 0.003117 | 1883 |

## Protected Operation Summary

| Metric | Value |
| --- | ---: |
| protected spans | 16683 |
| protected bytes/raw byte | 0.013371 |
| conservative mask bytes | 100894 |
| extra mask bytes | 19072 |
| extra mask bytes/raw byte | 0.003117 |
| extra/protected byte | 0.233091 |
| edge-aligned span rate | 0.056884 |
| crossing span rate | 0.943116 |
| max extra bytes/span | 8 |

## Sidecar Schema Smoke

The sidecar JSONL emitted by this smoke contains one record per audited
line. Each record contains:

```text
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

The v3.0 handoff smoke passed for this input. This does not make
the tokenizer final production-ready, but it is strong enough for
LLM-team integration smoke testing.
