# v2.2 LLM Handoff Hardening Gate

Date: 2026-06-13

## Target

v2.2 is the handoff-hardening phase before any v3.0 release. It proves that
the v2.1 tokenizer baseline can survive LLM-style integration smoke tests.

The candidate is:

```text
sp64_protected_passthrough_sidecar
```

Tokenizer shape:

```text
SP64 Unigram model tokens
+ 256 UTF-8 byte fallback ids
+ protected-span sidecar metadata with exact byte offsets
```

This is not a final production tokenizer and not yet v3.0. It is the current
integration candidate under hardening.

## Hardening Gate

Before v2.2 can close, the candidate must pass:

| Gate | Required |
| --- | --- |
| exact roundtrip | PASS |
| token id range validity | PASS |
| sidecar byte/char offset slicing | PASS |
| required passthrough route invariants | PASS |
| fallback source rate | <= 0.001 on handoff smoke |
| extra mask bytes/raw byte | <= 0.01 on handoff smoke |
| LM batch window formation | PASS |
| detector adversarial battery | F1 1.000000 |
| v2.1 regression checklist | PASS |

## Handoff Smoke Script

Canonical script:

```text
scripts/audit_v2_2_llm_handoff_smoke.py
```

The script emits:

```text
public markdown report
private sidecar JSONL
private failure JSONL
```

It checks:

```text
exact encode/decode reconstruction
valid token-id ranges
sidecar byte and character offsets
protected-span conservative masking overhead
fallback source token rate
minimal dataloader-style LM batch windows
```

## Current Smoke Results

### Valid/Test 250-Line Smoke

Report:

```text
artifacts/v2_2_llm_handoff_smoke_valid_test_250.md
```

Result:

| Metric | Value |
| --- | ---: |
| lines | 500 |
| exact | 500/500 |
| fallback rate | 0.000018 |
| sidecar failures | 0 |
| extra mask bytes/raw byte | 0.002666 |
| LM windows | 221 |
| overall | PASS |

### Real-Mix 5k Smoke

Report:

```text
artifacts/v2_2_llm_handoff_smoke_real_mix_5k.md
```

Result:

| Metric | Value |
| --- | ---: |
| lines | 5000 |
| exact | 5000/5000 |
| fallback source tokens | 701 |
| fallback rate | 0.000731 |
| protected spans | 16683 |
| sidecar failures | 0 |
| extra mask bytes/raw byte | 0.003117 |
| LM windows | 1883 |
| overall | PASS |

### Full Real-Mix Smoke

Report:

```text
artifacts/v2_2_llm_handoff_smoke_real_mix_full.md
```

Result:

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| exact | 40388/40388 |
| fallback source tokens | 3395 |
| fallback rate | 0.000456 |
| protected spans | 149999 |
| sidecar failures | 0 |
| extra mask bytes/raw byte | 0.003983 |
| LM windows | 14616 |
| overall | PASS |

This full smoke caught and then closed the missing `azerbaijani_word`
passthrough-route regression. `percent_encoded` and `azerbaijani_word` must
both remain in the sidecar passthrough route lists.

## Commands

Valid/test smoke:

```powershell
python scripts\audit_v2_2_llm_handoff_smoke.py `
  --split valid --split test `
  --max-lines 250 `
  --progress 100 `
  --report-out artifacts\v2_2_llm_handoff_smoke_valid_test_250.md `
  --sidecar-out artifacts\private\v2_2_llm_handoff_smoke_valid_test_250.sidecar.jsonl `
  --failures-out artifacts\private\v2_2_llm_handoff_smoke_valid_test_250.failures.jsonl
```

Real-mix smoke:

```powershell
python scripts\audit_v2_2_llm_handoff_smoke.py `
  --input artifacts\private\v2_1_real_mix\real_mix_60k_sample.txt `
  --max-lines 5000 `
  --progress 1000 `
  --report-out artifacts\v2_2_llm_handoff_smoke_real_mix_5k.md `
  --sidecar-out artifacts\private\v2_2_llm_handoff_smoke_real_mix_5k.sidecar.jsonl `
  --failures-out artifacts\private\v2_2_llm_handoff_smoke_real_mix_5k.failures.jsonl
```

Unit tests:

```powershell
$env:TEMP='C:\tmp'; $env:TMP='C:\tmp'; python -m pytest tests\test_v2_2_llm_handoff_smoke.py tests\test_v2_1_sidecar_operation_simulation.py tests\test_tiny_lm_bpb_probe.py
```

Current result:

```text
28 passed
```

## Sidecar Schema

Schema candidate:

```text
docs/v2_2_sidecar_jsonl_schema.md
```

Current schema version candidate:

```text
v2.2-sidecar-jsonl-1
```

The schema defines:

```text
one JSONL record per input line
UTF-8 byte offsets
Python-style character offsets
route labels
fallback source token accounting
```

## LLM Integration README

Consumer-facing draft:

```text
docs/v2_2_llm_team_integration_readme.md
```

This README states:

```text
what is guaranteed
what is not guaranteed
required smoke commands
sidecar schema summary
training-mask policy
acceptance rule
```

## v2.2 Status

Current status:

```text
v2.2 hardening gate prototype is implemented
valid/test smoke passes
real-mix 5k smoke passes
full real-mix smoke passes
v2.1 closure gauntlet passes
20M BPB reference row exists
sidecar JSONL schema is emitted with schema_version and tokenizer fields
```

Remaining before declaring v2.2 complete:

```text
1. Review/freeze the sidecar JSONL schema.
2. Review/finalize the concise LLM-team integration README.
3. Package the exact command set and expected artifacts.
4. Keep v3.0 reserved until the remaining v2.x phases are closed.
```
