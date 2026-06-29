# v3.8 Detector Reconstruct Crash Fix

Date: 2026-06-22

## Issue

The LLM team reported a deterministic full-corpus tokenization crash:

```text
ValueError: analyze_line surfaces did not reconstruct input
```

Crash path:

```text
scripts/tokenize_corpus.py
scripts/audit_v2_1_sidecar_operation_simulation.py::protected_spans
scripts/materialize_v2_soft_morph_artifacts.py::analyze_line
```

## Root Cause

The internal word-start sentinel is U+2581, also known as
LOWER ONE EIGHTH BLOCK:

```text
WORD_START = U+2581
```

Some frozen corpus web/forum lines contain literal decorative U+2581 characters.
The detector helper treated any token starting with `WORD_START` as an internal
marker and stripped it. For a raw literal `▁`, this made the emitted surface
lossy, so `protected_spans` correctly raised the reconstruct guard.

## Fix

Only strip `WORD_START` when it prefixes a non-empty internal token. Preserve a
standalone raw literal `▁` as ordinary surface text.

Patched files:

```text
scripts/materialize_v2_soft_morph_artifacts.py
src/tr_tokenizer/tokenizer.py
src/tr_tokenizer/boundary_weighted_bpe.py
```

The same patch was copied into:

```text
C:\CELIK-GARDASH\tokenizer_v3_0_repo_snapshot
```

## Validation

Targeted tests:

```text
python -m pytest tests\test_v2_1_sidecar_operation_simulation.py tests\test_tokenizer.py tests\test_boundary_weighted_bpe.py --basetemp .pytest_tmp_v3_8_detector_fix
```

Result:

```text
41 passed
```

The broader tokenization tests also passed when run with a custom pytest
basetemp:

```text
python -m pytest tests\test_v2_1_sidecar_operation_simulation.py tests\test_tokenize_corpus.py --basetemp .pytest_tmp_v3_8_detector_fix
```

Result:

```text
9 passed
```

Corpus checks:

```text
line 2631883: contains literal U+2581, analyze_line reconstructs input, protected_spans passes
line 4124939: contains literal U+2581, analyze_line reconstructs input, protected_spans passes
```

Production encode path checks on the patched snapshot:

```text
line 2631883: ids=1249, mask=1249, spans=129, fallback=12, sp_alignment_mismatch=False
line 4124939: ids=624, mask=624, spans=14, fallback=0, sp_alignment_mismatch=False
```

## LLM Team Action

Re-run full-corpus tokenization with the patched snapshot:

```text
C:\CELIK-GARDASH\tokenizer_v3_0_repo_snapshot
```

No input normalization change is required. The tokenizer contract remains:

```text
identity text normalization
lossless detector surfaces
byte-offset passthrough sidecar
```

After tokenization completes, run the standard full package gates:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_tokenized_package_gates.py `
  --manifest <FULL_TOKENIZED_OUT_DIR>\manifest.json `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --base-dir C:\CELIK-GARDASH `
  --report-dir <FULL_TOKENIZED_OUT_DIR>\tokenized_package_gates `
  --batch-size 4 `
  --seq-len 128
```
