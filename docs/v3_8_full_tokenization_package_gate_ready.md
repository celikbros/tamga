# v3.8 Full Tokenization Package Gate Ready Note

Date: 2026-06-24

## Closure Update

The LLM team completed the full-corpus acceptance on 2026-06-23:

```text
checksum validation: PASS
fixture validation: PASS
LLM production binary_loader: PASS
production-final for Faz 4: ACCEPTED
```

This note is retained as the pre-acceptance runbook. There is no remaining v3.8
package blocker.

## Current State

The v3.8 tokenizer candidate is trained and integration-smoke clean.

```text
tokenizer: sp64k_final_protected_passthrough_sidecar_controls128
SP model: C:\CELIK-GARDASH\models\tokenizer_v3_8\sp_unigram_64000_faz2_tr.model
model sha256: 5f54645a76c8cc6346f4283884b2adb219eb44118e6024b765d965239f62e77a
config: C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json
corpus text: C:\CELIK-GARDASH\datasets\faz2_corpus\gardash_tr_dedup.lf.txt
corpus sha256: 9826d58e8e11713ab99fb3690fff75bbfa2d533490c81b1b78f5ebdd83aa07b5
```

Already passed:

```text
Tokenizer-side 10K release gate: PASS
LLM-side v3.8 smoke: 57/57 PASS
LLM-side tokenization invocation smoke: sp_alignment_mismatches = 0
```

The LLM team completed full-corpus tokenization with the patched detector
snapshot. Do not duplicate that run from the tokenizer side.

Quick LLM-side package consistency check:

```text
input lines: 6,027,968
tokens.bin bytes: 9,999,798,408
token count: 2,499,949,602
loss_mask.bin bytes: 2,499,949,602
SP alignment mismatches: 0
fallback rate: 0.0056%
max token id: 64,244 (< 64,384)
```

## Expected Full Tokenization Output

The output directory must contain:

```text
tokens.bin
loss_mask.bin
index.jsonl
sidecar.jsonl
manifest.json
checksums.json
```

The only required input from the LLM team is:

```text
<FULL_TOKENIZED_OUT_DIR>\manifest.json
```

## Final Package Gate Command

Run this after the full-corpus `manifest.json` exists:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_tokenized_package_gates.py `
  --manifest <FULL_TOKENIZED_OUT_DIR>\manifest.json `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --base-dir C:\CELIK-GARDASH `
  --report-dir <FULL_TOKENIZED_OUT_DIR>\tokenized_package_gates `
  --batch-size 4 `
  --seq-len 128 `
  --dataloader-max-batches 4096
```

The bounded simulation samples evenly across the token stream. Use
`--dataloader-max-batches 0` only when an exhaustive tokenizer-side simulation
is explicitly required and the package is small enough.

## Pass Criteria

Production-final tokenizer packaging can be accepted only if:

```text
overall status: PASS
checksum: PASS
fixture: PASS
dataloader: PASS
failures: 0
warnings: 0 preferred; any warning must be explicitly reviewed
```

Also verify from the generated reports:

```text
token ids are in [0, 64384)
loss_mask length == tokens length
loss_mask values are only {0, 1}
pad id 64256 is accepted by the dataloader simulation
single label shift + ignore_index=-100 masking is clean
```

## Decision Wording

If the final package gates pass:

```text
v3.8 tokenizer package is accepted for Faz 4 pretraining input.
The tokenizer-side blocker is closed.
Production-final means the tokenizer package is frozen for this Faz 4 run,
not that future multilingual/code expansion cannot trigger a later retrain.
```

If any gate fails:

```text
Do not start Faz 4.
Treat the failure as a packaging/tokenization bug unless checksum evidence
shows the full tokenization run was interrupted or corrupted.
```

## Do Not Do

```text
Do not retrain SP again unless the LLM team changes the corpus.
Do not rerun full tokenization from the tokenizer side.
Do not switch back to v3.7 unless v3.8 package gates fail and cannot be fixed.
```
