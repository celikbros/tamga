# v2.2 Sidecar JSONL Schema

Date: 2026-06-14

## Status

This was the v2.2 schema candidate for protected-span sidecar records. It is
frozen by v2.3 for the current experimental sidecar contract.

It is not yet a v3.0 release artifact.

## Purpose

The tokenizer model-token stream remains close to ordinary SP64 tokenization.
Protected spans are represented in sidecar metadata using exact UTF-8 byte
offsets and route labels.

This lets downstream consumers reconstruct, mask, redact, or inspect protected
spans without paying the global token-boundary pre-split tax.

## File Format

Format:

```text
JSON Lines
one record per input line
UTF-8 encoded
newline-delimited
```

The sidecar file must preserve line order with the encoded text stream.

## Top-Level Record

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | string | Sidecar schema version. Current candidate: `v2.2-sidecar-jsonl-1`. |
| `tokenizer` | string | Tokenizer name, currently `sp64_protected_passthrough_sidecar`. |
| `split` | string | Input split or source label. |
| `line_number` | integer | 1-based line number within `split`. |
| `raw_bytes` | integer | UTF-8 byte length of the raw input line without trailing newline. |
| `token_count` | integer | Number of model tokens emitted for this line, excluding EOS. |
| `fallback_source_tokens` | integer | Number of UTF-8 byte fallback ids emitted for this line. |
| `spans` | array | Protected-span metadata records. |

Optional fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `source_id` | string | Stable corpus/source id if available. |
| `document_id` | string | Stable document id if available. |
| `byte_start_in_document` | integer | Absolute document byte offset if line-level input is derived from larger documents. |

## Span Record

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `route` | string | Protected route class. |
| `byte_start` | integer | Inclusive UTF-8 byte offset within the raw line. |
| `byte_end` | integer | Exclusive UTF-8 byte offset within the raw line. |
| `char_start` | integer | Inclusive Python-style character offset within the raw line. |
| `char_end` | integer | Exclusive Python-style character offset within the raw line. |
| `surface` | string | Exact protected substring. |

Offset invariants:

```text
raw_line.encode("utf-8")[byte_start:byte_end].decode("utf-8") == surface
raw_line[char_start:char_end] == surface
0 <= byte_start <= byte_end <= raw_bytes
0 <= char_start <= char_end <= len(raw_line)
```

Span ordering:

```text
spans are sorted by byte_start, then byte_end
overlapping spans are not allowed in v2.2
adjacent spans are allowed
```

## Current Route Labels

Current route labels observed in v2.1/v2.2:

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

Compatibility rule:

```text
Consumers must ignore unknown route labels unless their application requires a
closed route enum.
```

Reason:

```text
The detector may gain new protected route classes in later v2.x phases without
changing the model-token stream.
```

## Example

Input line:

```text
README.md'yi %20'si ile aç.
```

Example record:

```json
{
  "schema_version": "v2.2-sidecar-jsonl-1",
  "tokenizer": "sp64_protected_passthrough_sidecar",
  "split": "valid",
  "line_number": 1,
  "raw_bytes": 29,
  "token_count": 8,
  "fallback_source_tokens": 0,
  "spans": [
    {
      "route": "file_like",
      "byte_start": 0,
      "byte_end": 9,
      "char_start": 0,
      "char_end": 9,
      "surface": "README.md"
    },
    {
      "route": "percent_encoded",
      "byte_start": 13,
      "byte_end": 16,
      "char_start": 13,
      "char_end": 16,
      "surface": "%20"
    }
  ]
}
```

## Consumer Policy

Recommended use:

```text
raw-text redaction before tokenization when possible
byte-offset redaction after reconstruction when needed
training-loss masking by mapping protected byte spans to all overlapping tokens
```

Do not assume:

```text
protected spans start/end at model-token boundaries
token-index spans are exact without byte-offset reconciliation
base model can copy protected spans exactly by token ids alone
```

## Current Smoke Evidence

The v2.2 handoff smoke validates this schema shape:

```text
script: scripts/audit_v2_2_llm_handoff_smoke.py
valid/test report: artifacts/v2_2_llm_handoff_smoke_valid_test_250.md
real-mix report: artifacts/v2_2_llm_handoff_smoke_real_mix_5k.md
full real-mix report: artifacts/v2_2_llm_handoff_smoke_real_mix_full.md
```

Smoke results:

| Scope | Exact | Sidecar failures | Fallback rate | Extra mask bytes/raw byte | Overall |
| --- | ---: | ---: | ---: | ---: | --- |
| valid/test 250 each | 500/500 | 0 | 0.000018 | 0.002666 | PASS |
| real-mix 5k | 5000/5000 | 0 | 0.000731 | 0.003117 | PASS |
| full real-mix | 40388/40388 | 0 | 0.000456 | 0.003983 | PASS |

## Freeze Criteria

This schema is frozen for v2.3 after:

```text
v2.2 smoke stays PASS on valid/test and full real-mix
LLM-team README is written
no consumer requires token-boundary protected spans
```

Freeze evidence:

```text
docs/v2_3_sidecar_schema_freeze.md
artifacts/v2_3_sidecar_schema_contract_audit_real_mix_full.md
```
