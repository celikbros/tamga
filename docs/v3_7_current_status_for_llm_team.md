# v3.7 Current Tokenizer Status For LLM Team

Date: 2026-06-19

## Short Answer

The current tokenizer-side integration candidate is:

```text
sp64k_stratified_protected_passthrough_sidecar_controls128
```

This is suitable for LLM-side integration smoke testing. It is not yet declared
production-final.

## Why This Candidate

The older v3.2/v3.3 48K candidate passed integration smoke, but it was trained
on a narrower real-mix sample.

The v3.4/v3.5/v3.6 path tested broader stratified data and found that the
64K stratified model is stronger:

```text
v3.5: sidecar smoke PASS for both 48K and 64K
v3.6: 64K beat 48K in fixed-byte tiny-LM BPB
v3.7: 64K binary handoff fixture PASS on 50K stratified lines
```

Key v3.6 comparison:

| Candidate | Test tokens/raw byte | Test BPB |
| --- | ---: | ---: |
| v3.4-trained 48K sidecar | 0.192455 | 2.386732 |
| v3.4-trained 64K sidecar | 0.185791 | 2.340260 |

## ID Contract

| Range | Meaning |
| --- | --- |
| 0..63999 | SentencePiece ids |
| 64000..64255 | UTF-8 byte fallback ids |
| 64256..64383 | reserved wrapper control ids |

Important ids:

```text
<unk> = 0
<bos> alias <s> = 1
<eos> alias </s> = 2
<pad> = 64256
<system> = 64257
<user> = 64258
<assistant> = 64259
```

## Files In CELIK-GARDASH

Model:

```text
C:\CELIK-GARDASH\models\tokenizer_v3_4\sp_unigram_64000_stratified_480mb.model
C:\CELIK-GARDASH\models\tokenizer_v3_4\sp_unigram_64000_stratified_480mb.vocab
```

Config:

```text
C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json
```

50K binary fixture:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_7_smoke\sp64k_stratified_50k
```

Reports:

```text
C:\CELIK-GARDASH\docs\TOKENIZER_V3_7_SP64K_INTEGRATION_CANDIDATE_SMOKE_FINDINGS.md
C:\CELIK-GARDASH\docs\TOKENIZER_V3_6_STRATIFIED_FIXED_BYTE_BPB_FINDINGS.md
```

## What Passed

The v3.7 50K fixture passed:

```text
tokenizer config validation
fixture validation
binary dataloader simulation
```

Fixture summary:

```text
lines: 50000
raw bytes: 48942124
tokens: 9060436
tokens/raw byte: 0.185126
fallback rate: 0.000591
masked token rate: 0.063485
protected spans: 319592
SP alignment mismatches: 0
max token id: 64243
effective vocab size: 64384
```

## What Is Still Not Final

Before main LLM pretraining, we still need one project-level decision:

```text
Use this 480MB-stratified-trained SP64K model as the experimental training
tokenizer, or retrain SentencePiece on a larger/final corpus slice.
```

The Python implementation is the reference path. A Rust/C++/offline production
preprocessing implementation can be built after the contract is frozen.

## Recommendation

Use v3.7 SP64K for LLM-side smoke/integration planning.

Do not start irreversible main training until the LLM stack confirms:

```text
<pad>=64256 is acceptable
<unk>=0 remains acceptable
uint32 token stream + uint8 loss mask format works
sidecar byte-offset contract is sufficient for protected spans
```
