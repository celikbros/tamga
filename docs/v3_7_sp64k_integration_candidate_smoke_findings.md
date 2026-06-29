# v3.7 SP64K Integration Candidate Smoke Findings

Date: 2026-06-19

## Status

v3.7 promotes the v3.4-trained 64K SentencePiece sidecar tokenizer as the
current v3.x integration candidate.

This promotion is based on:

```text
v3.5 protected sidecar smoke PASS
v3.6 fixed-byte BPB screen: 64K beat 48K
v3.7 larger binary handoff smoke PASS
```

It is still not a full production-final tokenizer. It is the current candidate
for LLM-side integration smoke.

## Candidate

```text
sp64k_stratified_protected_passthrough_sidecar_controls128
```

Model:

```text
C:\CELIK-GARDASH\models\tokenizer_v3_4\sp_unigram_64000_stratified_480mb.model
```

Config:

```text
configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json
```

ID layout:

| Range | Meaning |
| --- | --- |
| 0..63999 | SentencePiece ids |
| 64000..64255 | UTF-8 byte fallback ids |
| 64256..64383 | reserved wrapper control ids |

Assigned wrapper controls:

```text
<pad> = 64256
<system> = 64257
<user> = 64258
<assistant> = 64259
<thinking> = 64260
</thinking> = 64261
<answer> = 64262
</answer> = 64263
<tool_call> = 64264
<tool_result> = 64265
```

SP aliases:

```text
<bos> -> <s> id 1
<eos> -> </s> id 2
<unk> remains id 0
```

## 50K Stratified Fixture

Input:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_4_sample\stratified_480mb.txt
```

Output:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_7_smoke\sp64k_stratified_50k
```

Summary:

| Metric | Value |
| --- | ---: |
| lines | 50000 |
| raw bytes | 48942124 |
| tokens | 9060436 |
| tokens/raw byte | 0.185126 |
| fallback tokens | 5352 |
| fallback rate | 0.000591 |
| masked tokens | 575205 |
| masked token rate | 0.063485 |
| protected spans | 319592 |
| protected bytes | 1432490 |
| SP alignment mismatches | 0 |
| max token id | 64243 |

## Validation Gates

| Gate | Result |
| --- | --- |
| tokenizer config validation | PASS |
| fixture validation | PASS |
| binary dataloader simulation | PASS |

Fixture validation:

```text
lines: 50000
tokens: 9060436
tokens.bin bytes: 36241744
loss_mask.bin bytes: 9060436
index rows: 50000
sidecar rows: 50000
max token id: 64243
effective vocab size: 64384
failures: none
warnings: none
```

Dataloader simulation:

```text
batch_size=4
seq_len=128
full_batches=17696
train label positions=8485153
masked label positions=575199
byte fallback tokens=5352
control tokens in fixture=0
failures: none
warnings: none
```

## Decision

Use v3.7 SP64K as the current candidate for future LLM integration smoke.

Keep v3.2/v3.3 SP48K as an older integration-smoke baseline only. Keep the
v3.4-trained 48K model as a smaller-embedding fallback, but do not prefer it
unless the LLM architecture imposes a hard embedding-size constraint.

## Remaining Gates Before Training Final

```text
1. LLM stack accepts <pad>=64256 and <unk>=0.
2. LLM dataloader reproduces the tokenizer-side binary simulation.
3. The team decides whether the 480MB stratified-trained SP model is enough
   or whether a final full-corpus SP retrain is required.
4. Production tokenizer implementation path is chosen:
   Python reference only vs Rust/C++/offline preprocessing.
5. Final selected corpus slice is revalidated with the same fixture gates.
```

## Reports

```text
artifacts/v3_7_tokenizer_config_validation_sp64k_stratified_integration.md
artifacts/v3_7_tokenized_corpus_smoke_sp64k_stratified_50k.md
artifacts/v3_7_smoke_fixture_validation_sp64k_stratified_50k.md
artifacts/v3_7_binary_dataloader_simulation_sp64k_stratified_50k.md
```
