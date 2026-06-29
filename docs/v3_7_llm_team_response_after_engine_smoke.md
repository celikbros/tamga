# Tokenizer Team Response To v3.7 LLM Engine Smoke

Date: 2026-06-20

LLM ekibine merhaba,

v3.7 SP64K adayini gercek `GardashForCausalLM` motorundan gecirdiginiz icin
tesekkurler. Yaniti tokenizer tarafi acisindan net kabul ediyoruz:

```text
LLM-side pretraining smoke contract: CLOSED / PASS
```

## Kabul Ettigimiz Kararlar

Sizin 6 karariniz tokenizer tarafinda da onaylandi:

```text
<pad>=64256 accepted
<unk>=0 accepted
uint32 tokens + uint8 loss_mask accepted
byte-offset passthrough sidecar accepted for pretraining
64K embedding accepted for integration smoke
v3.7 SP64K experimental training smoke can proceed
```

Ana pretraining'e henuz basmama konusunda da ayni fikirdeyiz:

```text
production-final = final corpus + final retrain/freeze + final gates
```

## Size Verdiklerimiz

### 1. Control-token wrapper spec

Spec:

```text
docs/v3_7_control_token_wrapper_spec.md
```

Reference implementation:

```text
scripts/reference_v3_7_control_wrapper.py
```

Key rule:

```text
raw user text does not activate control strings
trusted template text may inject control ids
```

Example:

```text
raw text "<user>" != id 64258
trusted template "<user>" == id 64258
```

### 2. Final SP retrain protocol

Protocol:

```text
docs/v3_8_final_sp_retrain_protocol.md
```

From you we need:

```text
frozen corpus path or manifest
dedup status
language/domain mixture
normalization decision
confirmation that v3.7 special-token registry remains unchanged
```

### 3. Canonical tokenizer config

Current canonical integration config:

```text
configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json
```

In CELIK-GARDASH it is also copied as:

```text
C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json
```

This is not production-final yet, but it is the canonical v3.7 integration
config.

### 4. Fertility report plan

Final fertility requirements are included in:

```text
docs/v3_8_final_sp_retrain_protocol.md
```

Required slices:

```text
Turkish clean
Turkish noisy/web
English
code/config/package strings
multilingual/script canary
```

### 5. Sidecar schema freeze + token-boundary branch

Schema/status:

```text
docs/v3_7_sidecar_schema_freeze_and_boundary_branch.md
```

For pretraining:

```text
byte-offset passthrough sidecar is frozen and sufficient
```

For later SFT/inference:

```text
token-boundary branch remains available but is not selected for v3.7 pretraining
```

### 6. EN/code handling

If EN/code becomes a meaningful share of final corpus:

```text
include EN/code in SP training mixture
keep identity normalization unless jointly changed
audit code/package/file-like fertility and fallback separately
do not assume Turkish-only training remains optimal
```

## Next Joint Step

Tokenizer team agrees with:

```text
v3.7 SP64K experimental LLM training smoke can proceed
```

Parallel track:

```text
LLM team freezes final corpus and mixture
Tokenizer team prepares final SP64K retrain + gates
```

Once final corpus is frozen, send us:

```text
corpus manifest/path
mixing policy
normalization policy
dedup status
EN/code target share
```

Then we will run v3.8 final retrain protocol.
