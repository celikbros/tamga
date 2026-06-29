# v3.8 Production Corpus Tokenization Runbook

Date: 2026-06-20

## Status

Production corpus tokenization path is now available as a deterministic offline
Python preprocessing script.

Script:

```text
scripts/tokenize_corpus.py
```

This is intended for full-corpus preprocessing after the LLM team freezes the
final corpus manifest/path.

## Outputs

The script writes:

```text
tokens.bin       uint32 little-endian token ids
loss_mask.bin    uint8; 1=train, 0=protected-span mask
index.jsonl      per-line token offsets
sidecar.jsonl    protected byte/char spans
manifest.json    machine-readable summary
checksums.json   SHA-256 checksums
```

## Determinism

The writer preserves input line order. Parallel workers cannot reorder output.

Payload determinism smoke:

```text
same 20-line input
workers=1 vs workers=2
tokens.bin checksum: identical
loss_mask.bin checksum: identical
index.jsonl checksum: identical
sidecar.jsonl checksum: identical
```

`manifest.json` may differ across output directories because it records output
paths and run configuration. The token/mask/index/sidecar payload is the
deterministic training artifact.

## Small Smoke Result

Command shape:

```powershell
python scripts\tokenize_corpus.py `
  --config configs\v3_5_sidecar_sp64k_stratified_480mb.toml `
  --tokenizer sp64k_stratified_480mb_protected_passthrough_sidecar `
  --input C:\CELIK-GARDASH\datasets\tokenizer_v3_4_sample\stratified_480mb.txt `
  --out-dir artifacts\private\v3_8_tokenize_corpus_smoke_w2 `
  --report-out artifacts\v3_8_tokenize_corpus_smoke_w2.md `
  --max-lines 20 `
  --workers 2 `
  --chunk-lines 7 `
  --progress 10
```

Result:

```text
lines: 20
raw bytes: 12396
tokens: 2088
tokens/raw byte: 0.168441
fallback tokens: 0
masked tokens: 100
protected spans: 53
SP alignment mismatches: 0
max token id: 59180
```

Validation:

```text
fixture validation: PASS
binary dataloader simulation: PASS
checksum package validation: PASS
```

## Full-Corpus Command Template

After final corpus freeze:

First run the final-corpus preflight. It validates the freeze manifest and
materializes the canonical plain-text view:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_final_corpus_preflight.py `
  --manifest C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_manifest.json `
  --base-dir C:\CELIK-GARDASH `
  --out-text C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --report-dir C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_corpus_preflight
```

Then tokenize the plain text view:

```powershell
python scripts\tokenize_corpus.py `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\v3_5_sidecar_sp64k_stratified_480mb.toml `
  --tokenizer sp64k_stratified_480mb_protected_passthrough_sidecar `
  --input C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --out-dir <TOKENIZED_OUTPUT_DIR> `
  --report-out <TOKENIZATION_REPORT_PATH> `
  --max-lines 0 `
  --workers 8 `
  --chunk-lines 256 `
  --progress 10000
```

Use `--workers 1` to disable multiprocessing for debugging.

## Gates

Before using a full-corpus output for training:

```text
1. sp_alignment_mismatches == 0
2. checksums.json exists and travels with the fixture
3. validate_v3_8_tokenized_package.py passes
4. validate_v3_2_smoke_fixture.py passes
5. simulate_v3_2_binary_dataloader.py passes
6. route/fallback/fertility summary is reviewed
```

## Standard Validation Commands

Run these from the same repository root used to create the package. For
CELIK-GARDASH, that is usually:

```text
C:\CELIK-GARDASH
```

Preferred one-command gate:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_tokenized_package_gates.py `
  --manifest <TOKENIZED_OUTPUT_DIR>\manifest.json `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --base-dir C:\CELIK-GARDASH `
  --report-dir <REPORT_DIR>\v3_8_tokenized_package_gates `
  --batch-size 4 `
  --seq-len 128 `
  --dataloader-max-batches 4096
```

This writes:

```text
gate_summary.md
checksum_validation.md
fixture_validation.md
dataloader_simulation.md
```

The process exits non-zero if any gate fails.

Checksum package validation:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\validate_v3_8_tokenized_package.py `
  --manifest <TOKENIZED_OUTPUT_DIR>\manifest.json `
  --base-dir C:\CELIK-GARDASH `
  --report-out <REPORT_DIR>\v3_8_tokenized_package_checksum_validation.md
```

Fixture validation:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\validate_v3_2_smoke_fixture.py `
  --manifest <TOKENIZED_OUTPUT_DIR>\manifest.json `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --report-out <REPORT_DIR>\v3_8_tokenized_package_fixture_validation.md
```

Binary dataloader simulation:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\simulate_v3_2_binary_dataloader.py `
  --manifest <TOKENIZED_OUTPUT_DIR>\manifest.json `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --batch-size 4 `
  --seq-len 128 `
  --max-batches 4096 `
  --report-out <REPORT_DIR>\v3_8_tokenized_package_dataloader_simulation.md
```

For full-corpus packages, the dataloader simulation reads evenly spaced batches
directly from the binary files. `--max-batches 0` requests the legacy exhaustive
scan and should normally be reserved for small fixtures. Checksum and fixture
validation remain full-package gates.

## Notes

This script is for offline preprocessing. The LLM training hot path should read
binary `tokens.bin` and `loss_mask.bin`, not parse sidecar JSONL per batch.

Rust/C++ serving tokenizer can be deferred until final freeze.
