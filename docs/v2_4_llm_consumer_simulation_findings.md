# v2.4 LLM Consumer Simulation Findings

Date: 2026-06-14

## Status

v2.4 validates that the frozen sidecar schema can support basic downstream LLM
consumer operations without requiring token-boundary protected spans.

This is still not a v3.0 handoff release. It is a v2.x hardening result.

## Simulation

Input:

```text
artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt
```

Sidecar:

```text
artifacts/private/v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl
```

Script:

```text
scripts/audit_v2_4_llm_consumer_simulation.py
```

The audit simulates:

```text
copy protected bytes by sidecar offsets
redact protected spans in raw text
map protected byte spans to conservative overlapping SP tokens for masking
```

## Result

Report:

```text
artifacts/v2_4_llm_consumer_simulation_real_mix_full.md
```

Summary:

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| raw bytes | 44351801 |
| protected spans | 149999 |
| protected bytes/raw byte | 0.015398 |
| copy failures | 0 |
| redaction failures | 0 |
| token-mask failures | 0 |
| total failures | 0 |
| conservative mask bytes | 859592 |
| extra mask bytes | 176661 |
| extra mask bytes/raw byte | 0.003983 |
| extra/protected byte | 0.258681 |
| edge-aligned span rate | 0.077861 |
| crossing span rate | 0.922139 |
| avg tokens/span | 1.865539 |
| max extra bytes/span | 9 |
| status | PASS |

## Interpretation

The passthrough sidecar contract is operationally usable for conservative
training-time masking/redaction workflows:

```text
sidecar byte offsets copy exact protected text
raw-text redaction is deterministic
token masking can safely over-mask overlapping SP tokens
global over-mask cost remains about 0.4% of raw bytes
```

This does not prove token-boundary copy/constrained decoding. If that becomes a
base-model requirement, route-selective pre-splitting should be tested before
global pre-splitting.

## Decision

v2.4 can be treated as closed for the current consumer simulation scope.

Recommended next step:

```text
v2.5 wider robustness / throughput only if needed
then package v3.0 experimental handoff candidate
```
