# v2.3 Sidecar Schema Freeze

Date: 2026-06-14

## Status

v2.3 freezes the current protected-sidecar JSONL schema for the
`sp64_protected_passthrough_sidecar` integration candidate.

This is still not v3.0. It is a v2.x contract freeze that later v3.0 handoff
can reference.

## Frozen Schema

Schema version:

```text
v2.2-sidecar-jsonl-1
```

Tokenizer:

```text
sp64_protected_passthrough_sidecar
```

Required top-level fields:

```text
schema_version
tokenizer
split
line_number
raw_bytes
token_count
fallback_source_tokens
spans
```

Required span fields:

```text
route
byte_start
byte_end
char_start
char_end
surface
```

Offset contract:

```text
raw_line.encode("utf-8")[byte_start:byte_end].decode("utf-8") == surface
raw_line[char_start:char_end] == surface
```

## Route Policy

For v2.3 validation we use a closed route enum over the currently known route
labels:

```text
numeric_like
file_like
apostrophe_surface
non_turkish_latin_word
greek_word
arabic_word
percent_encoded
cyrillic_word
uzbek_apostrophe_word
azerbaijani_word
```

Future v2.x detector changes may add routes, but that must be treated as a
schema-contract change and must rerun this audit.

## Validator

Canonical validator:

```text
scripts/audit_v2_3_sidecar_schema_contract.py
```

Unit tests:

```text
tests/test_v2_3_sidecar_schema_contract.py
```

## Full Real-Mix Result

Command:

```powershell
python scripts\audit_v2_3_sidecar_schema_contract.py `
  --sidecar-in artifacts\private\v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl `
  --input artifacts\private\v2_1_real_mix\real_mix_60k_sample.txt `
  --closed-route-enum `
  --report-out artifacts\v2_3_sidecar_schema_contract_audit_real_mix_full.md
```

Result:

| Metric | Value |
| --- | ---: |
| records | 40388 |
| spans | 149999 |
| total failures | 0 |
| status | PASS |

Failure counts:

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

## Decision

v2.3 can be treated as closed for the current sidecar schema.

Next v2.x work should move to consumer behavior:

```text
v2.4 LLM consumer simulation
```
