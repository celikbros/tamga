# v3.7 Sidecar Schema Freeze And Boundary Branch

Date: 2026-06-20

## Status

For v3.7 pretraining smoke, the protected-span sidecar schema is frozen as:

```text
v2.2-sidecar-jsonl-1
```

The contract is:

```text
byte_offset_passthrough_sidecar
```

Token-boundary alignment is not required for v3.7 pretraining.

## Frozen Required Fields

Top-level sidecar record:

```text
schema_version
tokenizer
line_number
raw_bytes
token_start
token_end
token_count
fallback_source_tokens
spans
```

Span record:

```text
route
byte_start
byte_end
char_start
char_end
surface
```

Offset invariant:

```text
raw_line.encode("utf-8")[byte_start:byte_end].decode("utf-8") == surface
raw_line[char_start:char_end] == surface
```

## v3.7 Route Set

Current known protected route labels:

```text
numeric_like
url
technical_comparator
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

Consumers should ignore unknown route labels unless they explicitly require a
closed route enum.

If the detector gains a new route before production-final, rerun:

```text
sidecar schema audit
fixture validation
binary dataloader simulation
```

## Pretraining Policy

Pretraining hot path should use:

```text
tokens.bin
loss_mask.bin
```

The sidecar JSONL remains offline metadata.

For protected-span loss masking, the recommended pretraining artifact is the
precomputed `loss_mask.bin`; do not parse JSONL per batch.

## Token-Boundary Branch

A token-boundary-aligned branch remains available for future SFT,
constrained-decoding, copy, redaction, or tool-routing needs.

Its status:

```text
documented and prototyped
not selected for v3.7 pretraining
kept as a future branch
```

Use token-boundary alignment only if downstream needs exact token-index spans.
It has a permanent token-pressure cost and couples detector decisions to the
model-token stream.

## Answer To LLM Team

For v3.7 pretraining:

```text
byte-offset passthrough sidecar is frozen and sufficient
```

For later SFT/inference:

```text
token-boundary branch is available but not yet production-selected
```
