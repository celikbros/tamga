# v3.8 Final SP64K Retrain Protocol

Date: 2026-06-20

## Purpose

This is the proposed protocol for moving from v3.7 integration candidate to a
production-final tokenizer candidate.

v3.7 uses:

```text
SP64K trained on the v3.4 480MB stratified sample
```

The LLM team correctly notes that irreversible main pretraining should use a
final/frozen tokenizer. If the final corpus differs materially, retrain SP64K
on the frozen corpus slice before Phase 4.

## Inputs Needed From LLM Team

Tokenizer team needs:

```text
1. frozen corpus path or manifest
2. exact corpus mixture policy
3. dedup status and whether text is already normalized
4. language/domain proportions, especially Turkish / English / code / noisy web
5. max bytes or max lines for tokenizer training sample, if not full corpus
6. whether document boundaries matter for sampling
7. confirmation that v3.7 special-token registry remains unchanged
```

Minimum path shape:

```text
C:\CELIK-GARDASH\datasets\pretraining_final\...
```

or a manifest:

```text
source_path<TAB>source_name<TAB>target_bytes_or_weight
```

Preferred final corpus manifest:

```text
docs/v3_8_final_corpus_manifest_template.json
schema_version = v3.8-final-corpus-manifest-1
```

Validate it before any SP retrain:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\validate_v3_8_final_corpus_manifest.py `
  --manifest C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_manifest.json `
  --base-dir C:\CELIK-GARDASH `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_corpus_manifest_validation.md
```

Use `--allow-missing-paths` only while drafting. It must not be used for the
actual final freeze gate.

Preferred one-command final corpus preflight:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_final_corpus_preflight.py `
  --manifest C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_manifest.json `
  --base-dir C:\CELIK-GARDASH `
  --out-text C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --report-dir C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_corpus_preflight
```

This writes:

```text
preflight_summary.md
manifest_validation.md
text_materialization.md
```

The process exits non-zero if manifest validation or text materialization
fails. Run the individual commands below only when debugging a failed preflight.

Individual materialization command:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\materialize_v3_8_final_corpus_text.py `
  --manifest C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_manifest.json `
  --base-dir C:\CELIK-GARDASH `
  --out C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_corpus_text_materialization.md
```

If `corpus.format` is `text`, this rewrites the file into the canonical LF
line view. If it is `jsonl`, it extracts `corpus.text_field`. The output file is
the input for SentencePiece retrain, route-density/fertility reports, and
`tokenize_corpus.py`.

## Frozen ID Policy

Keep the v3.7 id layout:

```text
0..63999       SP ids
64000..64255   UTF-8 byte fallback ids
64256..64383   control-token reserve
```

Changing SP training data will change SP piece ids and embeddings. Therefore:

```text
final retrain must happen before irreversible main pretraining
```

The wrapper control ids should stay fixed.

## Training Settings

Default proposed SP settings:

```text
model_type = unigram
vocab_size = 64000
character_coverage = 1.0
normalizer = identity
split_by_whitespace = true
remove_extra_whitespaces = false
max_sentence_length = 16384
byte_fallback = false
```

UTF-8 byte fallback remains wrapper-managed at ids `64000..64255`.

## Final Retrain Launcher

After final corpus preflight writes the canonical text view, use the retrain
launcher to train SP64K and materialize both downstream configs:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_final_sp_retrain.py `
  --corpus-text C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --model-prefix C:\CELIK-GARDASH\models\tokenizer_v3_8\sp_unigram_64000_final `
  --toml-out C:\CELIK-GARDASH\configs\tokenizer_v3_0\v3_8_final_sidecar_sp64k.toml `
  --tokenizer-config-out C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_sp_retrain_plan.md `
  --train
```

Without `--train`, the same command is a safe dry run: it writes the planned
sidecar TOML, canonical tokenizer config JSON, and report, but does not train a
SentencePiece model. Use dry run while reviewing paths; use `--train` only
after the final corpus manifest is frozen and preflight is `PASS`.

The launcher writes:

```text
C:\CELIK-GARDASH\models\tokenizer_v3_8\sp_unigram_64000_final.model
C:\CELIK-GARDASH\models\tokenizer_v3_8\sp_unigram_64000_final.vocab
C:\CELIK-GARDASH\configs\tokenizer_v3_0\v3_8_final_sidecar_sp64k.toml
C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_sp_retrain_plan.md
```

If the model already exists, add `--force` only when intentionally replacing a
known previous retrain.

## Required Gates After Retrain

Run these before declaring production-final:

```text
1. final corpus preflight: manifest validation + text materialization
2. tokenizer config validation
3. route-density audit on final sample
4. fertility report: Turkish, English, code/noisy, multilingual canary
5. protected sidecar smoke
6. exact fixture validation
7. binary dataloader simulation
8. fixed-byte tiny-LM BPB screen against v3.7 candidate, if budget allows
9. LLM-engine smoke with real GardashForCausalLM
```

Preferred one-command final release gate:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_final_release_gates.py `
  --base-dir C:\CELIK-GARDASH `
  --corpus-text C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --tokenizer-config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --sidecar-config C:\CELIK-GARDASH\configs\tokenizer_v3_0\v3_8_final_sidecar_sp64k.toml `
  --tokenizer-name sp64k_final_protected_passthrough_sidecar_controls128 `
  --tokenized-out-dir C:\CELIK-GARDASH\datasets\tokenizer_v3_8_final_full `
  --report-dir C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_release_gates
```

By default this is a dry-run planner. It writes the release-gate command report
but does not execute heavy corpus tokenization. Add `--execute` only after final
SP retrain is complete and the generated configs have been reviewed.

The runner performs:

```text
config validation
route-density audit
fertility report
sidecar handoff smoke
production tokenize_corpus
tokenized package gates
```

For sidecar tokenizer canary/smoke, use `audit_v2_2_llm_handoff_smoke.py`.
The older `report_v1_8_canary_diagnostics.py` is SentencePiece-sweep oriented
and is not the authoritative final sidecar gate.

## Standard Gate Commands

Use these command shapes after the final corpus and, where applicable, final
SP64K model and canonical `tokenizer_config.json` are written into
`C:\CELIK-GARDASH`.

Preferred final corpus preflight:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_final_corpus_preflight.py `
  --manifest C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_manifest.json `
  --base-dir C:\CELIK-GARDASH `
  --out-text C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --report-dir C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_corpus_preflight
```

Run the individual materialization command below only when debugging a failed
preflight.

Final corpus text materialization:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\materialize_v3_8_final_corpus_text.py `
  --manifest C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_manifest.json `
  --base-dir C:\CELIK-GARDASH `
  --out C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_corpus_text_materialization.md
```

Tokenizer config validation:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\validate_v3_1_tokenizer_config.py `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_config_validation.md
```

Route density on the frozen corpus sample:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\audit_v2_1_sidecar_route_density.py `
  --input C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --max-lines 100000 `
  --progress 10000 `
  --with-token-pressure `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_route_density.md
```

Fertility report:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\report_v3_1_gardash_fertility.py `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\v3_8_final_sidecar_sp64k.toml `
  --tokenizer <FINAL_TOKENIZER_NAME> `
  --input C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --max-lines 100000 `
  --progress 10000 `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_fertility.md `
  --json-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_fertility.json
```

Sidecar handoff smoke:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\audit_v2_2_llm_handoff_smoke.py `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\v3_8_final_sidecar_sp64k.toml `
  --tokenizer sp64k_final_protected_passthrough_sidecar_controls128 `
  --input C:\CELIK-GARDASH\datasets\pretraining_final\final_corpus_text.txt `
  --max-lines 5000 `
  --progress 10000 `
  --batch-size 4 `
  --seq-len 128 `
  --sidecar-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_release_gates\private\handoff_smoke.sidecar.jsonl `
  --failures-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_release_gates\private\handoff_smoke.failures.jsonl `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_release_gates\handoff_smoke.md
```

Preferred one-command tokenized package gate:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_tokenized_package_gates.py `
  --manifest <TOKENIZED_OUTPUT_DIR>\manifest.json `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --base-dir C:\CELIK-GARDASH `
  --report-dir C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_tokenized_package_gates `
  --batch-size 4 `
  --seq-len 128
```

Run the individual commands below only when debugging a failed package gate.

Tokenized package checksum validation:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\validate_v3_8_tokenized_package.py `
  --manifest <TOKENIZED_OUTPUT_DIR>\manifest.json `
  --base-dir C:\CELIK-GARDASH `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_tokenized_package_checksum_validation.md
```

Fixture validation:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\validate_v3_2_smoke_fixture.py `
  --manifest <TOKENIZED_OUTPUT_DIR>\manifest.json `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_fixture_validation.md
```

Binary dataloader simulation:

```powershell
python tokenizer_v3_0_repo_snapshot\scripts\simulate_v3_2_binary_dataloader.py `
  --manifest <TOKENIZED_OUTPUT_DIR>\manifest.json `
  --config C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json `
  --batch-size 4 `
  --seq-len 128 `
  --report-out C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_dataloader_simulation.md
```

## Fertility Report Requirements

Report at least:

```text
tokens/raw byte
tokens/word
fallback rate
protected span density
masked token rate
route distribution
max token id
roundtrip failures
```

Evaluate by slice:

```text
Turkish clean
Turkish noisy/web
English
code/config/package strings
multilingual/script canary
```

## EN / Code Handling

If English and code share rises materially in the final corpus:

```text
include them in the SP training mixture
do not train only on Turkish
keep identity normalization unless the LLM team explicitly freezes another policy
audit code/package/version/file-like routes separately
watch fallback rate and route density
```

Expected risk if EN/code is underrepresented:

```text
higher token pressure
higher fallback rate
worse code/package fertility
more sidecar masking pressure
```

## Stop Criteria

Stop or revise the retrain if:

```text
roundtrip fails
config validation fails
fallback rate jumps materially versus v3.7
64K no longer beats 48K or an accepted baseline on broad fertility
LLM engine smoke rejects id layout
sidecar route schema changes without a corresponding schema freeze
```

## Success Criteria

Production-final candidate can be declared only after:

```text
final corpus is frozen
SP64K is retrained or retrain is explicitly waived
canonical tokenizer_config.json is frozen
control wrapper spec is accepted
sidecar schema is accepted
LLM engine smoke passes
binary fixture/dataloader gates pass
```
