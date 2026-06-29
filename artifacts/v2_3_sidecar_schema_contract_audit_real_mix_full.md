# v2.3 Sidecar Schema Contract Audit

Sidecar: `artifacts/private/v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl`
Raw input: `artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt`
Expected schema version: `v2.2-sidecar-jsonl-1`
Expected tokenizer: `sp64_protected_passthrough_sidecar`
Closed route enum: `True`

## Summary

| Metric | Value |
| --- | ---: |
| records | 40388 |
| spans | 149999 |
| total failures | 0 |
| status | PASS |

## Failure Counts

| Check | Failures |
| --- | ---: |
| json | 0 |
| missing fields | 0 |
| field types | 0 |
| schema version | 0 |
| tokenizer | 0 |
| line order | 0 |
| raw line | 0 |
| offsets | 0 |
| surfaces | 0 |
| span order | 0 |
| span overlap | 0 |
| unknown route | 0 |

## Interpretation

The sidecar JSONL satisfies the v2.3 schema contract.
