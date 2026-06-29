# v2.2 LLM Handoff Smoke Audit

Config: `configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml`
Tokenizer: `sp64_protected_passthrough_sidecar`
Input: `artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt`
Vocab size: `64256`
Batch smoke shape: `batch_size=4`, `seq_len=128`
Sidecar JSONL: `artifacts/private/v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl`
Private failure samples: `artifacts/private/v2_2_llm_handoff_smoke_real_mix_full.failures.jsonl`

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
| `real_mix_60k_sample` | 40388 | 44351801 | 7443139 | 0.167820 | 3395 | 0.000456 | 40388 | 0 | 149999 | 0 | 0.003983 | 14616 |

## Protected Operation Summary

| Metric | Value |
| --- | ---: |
| protected spans | 149999 |
| protected bytes/raw byte | 0.015398 |
| conservative mask bytes | 859592 |
| extra mask bytes | 176661 |
| extra mask bytes/raw byte | 0.003983 |
| extra/protected byte | 0.258681 |
| edge-aligned span rate | 0.077861 |
| crossing span rate | 0.922139 |
| max extra bytes/span | 9 |

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
