# v3.0 Experimental LLM Handoff Package

Date: 2026-06-14

## Status

v3.0 is the first experimental LLM-team handoff candidate.

It is not a final production tokenizer decision.

## Candidate

Tokenizer contract:

```text
sp64_protected_passthrough_sidecar
```

Shape:

```text
SP64 Unigram model tokens
+ 256 UTF-8 byte fallback ids
+ protected-span sidecar JSONL with exact byte offsets
```

Vocabulary accounting:

```text
64000 SentencePiece ids
+ 256 UTF-8 fallback ids
= 64256 ids
```

## What Is Guaranteed

For the current v3.0 experimental package:

```text
decode/roundtrip is exact on the v2.2 full real-mix smoke
sidecar byte and character offsets slice back to protected surfaces
sidecar schema is frozen and independently validated
basic LLM consumer operations pass on real-mix data
protected detector adversarial battery passes
model-token stream can form LM batch windows
fallback and over-mask rates stay below preregistered thresholds
```

## What Is Not Guaranteed

Do not claim:

```text
final production readiness
protected spans align to token boundaries
exact protected-span copy by token ids alone
constrained decoding support
morphology-improved tokenization
throughput readiness for production serving
```

## Required Artifacts

Core contract docs:

```text
docs/v2_1_passthrough_sidecar_handoff_contract.md
docs/v2_1_final_handoff_package.md
docs/v2_2_llm_handoff_hardening_gate.md
docs/v2_2_sidecar_jsonl_schema.md
docs/v2_2_llm_team_integration_readme.md
docs/v2_3_sidecar_schema_freeze.md
docs/v2_4_llm_consumer_simulation_findings.md
docs/v2_5_wider_robustness_closeout.md
```

Config and model:

```text
configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml
artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model
```

Validation reports:

```text
artifacts/v2_2_llm_handoff_smoke_valid_test_250.md
artifacts/v2_2_llm_handoff_smoke_real_mix_5k.md
artifacts/v2_2_llm_handoff_smoke_real_mix_full.md
artifacts/v2_3_sidecar_schema_contract_audit_real_mix_full.md
artifacts/v2_4_llm_consumer_simulation_real_mix_full.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

Private/generated sidecar sample:

```text
artifacts/private/v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl
```

## Gate Results

v2.2 full real-mix handoff smoke:

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| exact | 40388/40388 |
| failures | 0 |
| fallback rate | 0.000456 |
| sidecar failures | 0 |
| extra mask bytes/raw byte | 0.003983 |
| LM windows | 14616 |
| overall | PASS |

v2.3 schema contract:

| Metric | Value |
| --- | ---: |
| records | 40388 |
| spans | 149999 |
| total failures | 0 |
| status | PASS |

v2.4 consumer simulation:

| Metric | Value |
| --- | ---: |
| copy failures | 0 |
| redaction failures | 0 |
| token-mask failures | 0 |
| total failures | 0 |
| extra mask bytes/raw byte | 0.003983 |
| status | PASS |

20M tiny-LM reference:

| Metric | Value |
| --- | ---: |
| valid BPB | 1.935810 |
| test BPB | 1.947129 |

## Repro Commands

Handoff smoke:

```powershell
python scripts\audit_v2_2_llm_handoff_smoke.py `
  --input artifacts\private\v2_1_real_mix\real_mix_60k_sample.txt `
  --progress 5000 `
  --report-out artifacts\v2_2_llm_handoff_smoke_real_mix_full.md `
  --sidecar-out artifacts\private\v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl `
  --failures-out artifacts\private\v2_2_llm_handoff_smoke_real_mix_full.failures.jsonl
```

Schema contract:

```powershell
python scripts\audit_v2_3_sidecar_schema_contract.py `
  --sidecar-in artifacts\private\v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl `
  --input artifacts\private\v2_1_real_mix\real_mix_60k_sample.txt `
  --closed-route-enum `
  --report-out artifacts\v2_3_sidecar_schema_contract_audit_real_mix_full.md
```

Consumer simulation:

```powershell
python scripts\audit_v2_4_llm_consumer_simulation.py `
  --input artifacts\private\v2_1_real_mix\real_mix_60k_sample.txt `
  --sidecar-in artifacts\private\v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl `
  --progress 5000 `
  --report-out artifacts\v2_4_llm_consumer_simulation_real_mix_full.md `
  --samples-out artifacts\private\v2_4_llm_consumer_simulation_real_mix_full.samples.jsonl
```

Targeted unit tests:

```powershell
$env:TEMP='C:\tmp'; $env:TMP='C:\tmp'; python -m pytest `
  tests\test_v2_4_llm_consumer_simulation.py `
  tests\test_v2_3_sidecar_schema_contract.py `
  tests\test_v2_2_llm_handoff_smoke.py `
  tests\test_v2_1_sidecar_operation_simulation.py `
  tests\test_tiny_lm_bpb_probe.py
```

Latest targeted result:

```text
34 passed
```

## Acceptance Rule

The LLM team can treat v3.0 as an experimental tokenizer candidate if:

```text
all three audit reports are PASS
targeted unit tests pass
the downstream task accepts byte-offset sidecar metadata instead of
token-boundary protected spans
```

If exact token-boundary protected spans are required, do not use this package as
the final contract. Open a route-selective pre-split branch.
