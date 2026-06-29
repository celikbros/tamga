# v3.0 Tokenizer Quickstart Inside CELIK-GARDASH

Date: 2026-06-14

## Read First

```text
C:\CELIK-GARDASH\docs\tokenizer_v3_0\v3_0_experimental_handoff_package.md
C:\CELIK-GARDASH\docs\tokenizer_v3_0\v3_0_gardash_transfer_manifest.md
```

## Working Directory

Run validation commands from:

```powershell
cd C:\CELIK-GARDASH\tokenizer_v3_0_repo_snapshot
```

The target-adjusted config is:

```text
C:\CELIK-GARDASH\configs\tokenizer_v3_0\v3_0_gardash_sidecar.toml
```

## Key Files

Tokenizer model:

```text
C:\CELIK-GARDASH\models\tokenizer_v3_0\sp_unigram_64000_train_only.model
C:\CELIK-GARDASH\models\tokenizer_v3_0\sp_unigram_64000_train_only.vocab
```

Real-mix validation sample:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_0\real_mix_60k_sample.txt
```

Sidecar sample:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_0\v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl
```

Raw pretraining data:

```text
C:\CELIK-GARDASH\datasets\pretraining_raw\celik_ai
```

## Smoke Audit

```powershell
python scripts\audit_v2_2_llm_handoff_smoke.py `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\v3_0_gardash_sidecar.toml `
  --input C:\CELIK-GARDASH\datasets\tokenizer_v3_0\real_mix_60k_sample.txt `
  --progress 5000 `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_0_smoke_real_mix_full.md `
  --sidecar-out C:\CELIK-GARDASH\datasets\tokenizer_v3_0\v3_0_smoke_real_mix_full.sidecar.jsonl `
  --failures-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_0_smoke_real_mix_full.failures.jsonl
```

Expected:

```text
overall PASS
exact 40388/40388
```

## Schema Audit

```powershell
python scripts\audit_v2_3_sidecar_schema_contract.py `
  --sidecar-in C:\CELIK-GARDASH\datasets\tokenizer_v3_0\v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl `
  --input C:\CELIK-GARDASH\datasets\tokenizer_v3_0\real_mix_60k_sample.txt `
  --closed-route-enum `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_0_schema_contract_real_mix_full.md
```

Expected:

```text
status PASS
total failures 0
```

## Consumer Simulation

```powershell
python scripts\audit_v2_4_llm_consumer_simulation.py `
  --input C:\CELIK-GARDASH\datasets\tokenizer_v3_0\real_mix_60k_sample.txt `
  --sidecar-in C:\CELIK-GARDASH\datasets\tokenizer_v3_0\v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl `
  --sp-model C:\CELIK-GARDASH\models\tokenizer_v3_0\sp_unigram_64000_train_only.model `
  --progress 5000 `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_0_consumer_simulation_real_mix_full.md `
  --samples-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_0_consumer_simulation.samples.jsonl
```

Expected:

```text
status PASS
copy/redaction/token-mask failures 0
```

## Important Contract

This tokenizer uses byte-offset sidecar metadata. It does not guarantee that
protected spans align to model-token boundaries.

If the LLM pipeline requires token-boundary protected spans, open a
route-selective pre-split branch instead of silently changing this contract.
