# v2.2 LLM Team Integration README

Date: 2026-06-14

## What This Is

This is the current tokenizer integration candidate under v2.2 hardening.

Tokenizer:

```text
sp64_protected_passthrough_sidecar
```

Shape:

```text
SP64 Unigram model tokens
+ 256 UTF-8 byte fallback ids
+ protected-span sidecar JSONL
```

This is not v3.0 yet. v3.0 will be declared only after all required v2.x
hardening work is complete.

## What It Guarantees

This candidate guarantees:

```text
exact encode/decode roundtrip under the audited path
valid model token ids
protected spans recorded as exact byte offsets in sidecar metadata
low fallback rate on current smoke tests
conservative token-overlap masking policy for protected spans
LM batch-window formation for pretraining smoke
```

It does not guarantee:

```text
protected spans align with token boundaries
exact token-index ranges for protected spans
base-model exact copy of protected spans
constrained decoding over protected spans
```

If those become hard requirements, use route-selective or global pre-split
experiments before handoff.

## Required Smoke Command

Run this before accepting the tokenizer into an LLM integration branch:

```powershell
python scripts\audit_v2_2_llm_handoff_smoke.py `
  --input artifacts\private\v2_1_real_mix\real_mix_60k_sample.txt `
  --max-lines 5000 `
  --progress 1000 `
  --report-out artifacts\v2_2_llm_handoff_smoke_real_mix_5k.md `
  --sidecar-out artifacts\private\v2_2_llm_handoff_smoke_real_mix_5k.sidecar.jsonl `
  --failures-out artifacts\private\v2_2_llm_handoff_smoke_real_mix_5k.failures.jsonl
```

Expected current result:

```text
overall: PASS
exact: 5000/5000
fallback rate: 0.000731
sidecar failures: 0
extra mask bytes/raw byte: 0.003117
LM windows: 1883
```

Also run unit/regression tests:

```powershell
$env:TEMP='C:\tmp'; $env:TMP='C:\tmp'; python -m pytest tests\test_v2_2_llm_handoff_smoke.py tests\test_v2_1_sidecar_operation_simulation.py tests\test_tiny_lm_bpb_probe.py
```

Expected current result:

```text
28 passed
```

## Sidecar Schema

Schema doc:

```text
docs/v2_2_sidecar_jsonl_schema.md
```

Each sidecar record represents one input line:

```text
schema_version
tokenizer
split
line_number
raw_bytes
token_count
fallback_source_tokens
spans[]
```

Each protected span has:

```text
route
byte_start
byte_end
char_start
char_end
surface
```

Offset rule:

```text
raw_line.encode("utf-8")[byte_start:byte_end].decode("utf-8") == surface
raw_line[char_start:char_end] == surface
```

## Training Mask Policy

For protected-span loss masking:

```text
1. Use sidecar byte_start/byte_end.
2. Map each byte span to all overlapping model tokens.
3. Mask the entire overlapping token set.
4. Accept small boundary-token over-mask.
```

Current measured over-mask:

```text
real-mix 5k smoke:
  extra mask bytes/raw byte: 0.003117

full real-mix smoke:
  exact: 40388/40388
  fallback rate: 0.000456
  extra mask bytes/raw byte: 0.003983
  overall: PASS

real-mix 60k operation simulation:
  extra mask bytes/raw byte: 0.003983
```

Do not assume token boundaries are exact protected-span boundaries.

## Tokenizer IDs

Current vocabulary accounting:

```text
64000 SP64 ids
+ 256 UTF-8 byte fallback ids
= 64256 ids
```

The model should reserve exactly this tokenizer id range for this candidate.

## Current Reference Reports

Core v2.1/v2.2 reports:

```text
docs/v2_1_final_handoff_package.md
docs/v2_1_closure_gauntlet_findings.md
docs/v2_2_llm_handoff_hardening_gate.md
docs/v2_2_sidecar_jsonl_schema.md
artifacts/v2_2_llm_handoff_smoke_valid_test_250.md
artifacts/v2_2_llm_handoff_smoke_real_mix_5k.md
artifacts/v2_2_llm_handoff_smoke_real_mix_full.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

20M tiny-LM reference:

```text
test BPB: 1.947129
final valid BPB: 1.935810
```

## Acceptance Rule

Do not accept this tokenizer candidate if:

```text
the v2.2 smoke overall gate is FAIL
exact roundtrip is below 1.000000
sidecar failures are non-zero
fallback rate exceeds 0.001 without explanation
extra mask bytes/raw byte exceeds 0.01 without explanation
percent_encoded or azerbaijani_word is missing from the passthrough route list
```

## Current Recommendation

Use this candidate for LLM integration smoke only after v2.2 closes.

Do not call it v3.0 yet.
