# v3.0 Tokenizer Transfer Manifest For CELIK-GARDASH

Date: 2026-06-14

## Destination

Target project:

```text
C:\CELIK-GARDASH
```

This transfer places the tokenizer handoff package under:

```text
C:\CELIK-GARDASH\docs\tokenizer_v3_0
C:\CELIK-GARDASH\models\tokenizer_v3_0
C:\CELIK-GARDASH\configs\tokenizer_v3_0
C:\CELIK-GARDASH\scripts\tokenizer_v3_0
C:\CELIK-GARDASH\datasets\tokenizer_v3_0
C:\CELIK-GARDASH\datasets\pretraining_raw\celik_ai
```

## Primary File To Read First

```text
C:\CELIK-GARDASH\docs\tokenizer_v3_0\v3_0_experimental_handoff_package.md
```

## Tokenizer Candidate

```text
sp64_protected_passthrough_sidecar
```

Contract:

```text
SP64 Unigram model tokens
+ 256 UTF-8 byte fallback ids
+ protected-span sidecar JSONL with exact byte offsets
```

Vocabulary size:

```text
64256
```

## What Was Transferred

Docs:

```text
v3_0_experimental_handoff_package.md
v2_2_llm_team_integration_readme.md
v2_2_sidecar_jsonl_schema.md
v2_1_passthrough_sidecar_handoff_contract.md
v2_3_sidecar_schema_freeze.md
v2_4_llm_consumer_simulation_findings.md
v2_5_wider_robustness_closeout.md
v3_0_gardash_transfer_manifest.md
```

Validation reports:

```text
v2_2_llm_handoff_smoke_real_mix_full.md
v2_3_sidecar_schema_contract_audit_real_mix_full.md
v2_4_llm_consumer_simulation_real_mix_full.md
v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

Tokenizer files:

```text
sp_unigram_64000_train_only.model
sp_unigram_64000_train_only.vocab
```

Scripts/configs:

```text
v2_1_tiny_lm_edge_safe_route_passthrough.toml
audit_v2_2_llm_handoff_smoke.py
audit_v2_3_sidecar_schema_contract.py
audit_v2_4_llm_consumer_simulation.py
```

Tokenizer validation data:

```text
real_mix_60k_sample.txt
v2_2_llm_handoff_smoke_real_mix_full.sidecar.jsonl
v1_8 filtered pilot train/valid/test split
```

Raw pretraining data copied from:

```text
C:\TÜRKÇE-TOKENIZER\data\train\private\celik_ai
```

to:

```text
C:\CELIK-GARDASH\datasets\pretraining_raw\celik_ai
```

## Critical Warning For LLM Team

This is an experimental tokenizer handoff package, not a final production
tokenizer.

The contract is byte-offset sidecar protection. It does not guarantee that
protected spans align with model-token boundaries.

If token-boundary protected spans are required, open a route-selective pre-split
branch instead of silently changing this tokenizer.
