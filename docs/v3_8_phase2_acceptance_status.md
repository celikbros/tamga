# v3.8 Phase 2 Tokenization Acceptance Status

Date: 2026-06-24

## Status

LLM architecture team accepted the v3.8 production tokenization delivery.

They independently verified:

```text
scripts/tokenize_corpus.py shim resolves to the real snapshot implementation
workers=1 vs workers=2 produce identical payload checksums
tokens.bin / loss_mask.bin / index.jsonl / sidecar.jsonl are deterministic
the three written contracts and production runbook are present
```

Consumer-side contract is also closed:

```text
uint32_le tokens
uint8 loss_mask
single label shift
loss_mask -> -100
GardashForCausalLM smoke passed with real v3.7 ids
```

LLM-side v3.8 smoke is also closed:

```text
LLM-side tests: 57/57 PASS
v3.8 model sha verified: 5f54645a...
config points to v3.8 model
tokenization invocation smoke: sp_alignment_mismatches = 0
```

## Current Ownership

Tokenizer-side pipeline contract:

```text
CLOSED / ACCEPTED
```

The previous critical path was:

```text
LLM team final corpus decision
Turkish-primary corpus freeze
MinHash dedup result
frozen corpus manifest/path
```

That dependency is now closed. The LLM team handed off the frozen Faz 2
Turkish-primary corpus on 2026-06-21:

```text
C:\CELIK-GARDASH\datasets\faz2_corpus\gardash_tr_dedup.jsonl
C:\CELIK-GARDASH\datasets\faz2_corpus\gardash_tr_dedup.txt
C:\CELIK-GARDASH\datasets\faz2_corpus\gardash_tr_dedup.lf.txt
```

The tokenizer-facing canonical input is the LF text file:

```text
C:\CELIK-GARDASH\datasets\faz2_corpus\gardash_tr_dedup.lf.txt
lines: 6,027,968
bytes: 13,569,773,056
sha256: 9826d58e8e11713ab99fb3690fff75bbfa2d533490c81b1b78f5ebdd83aa07b5
```

Manifest/preflight:

```text
docs/v3_8_final_corpus_manifest_template.json
schema_version = v3.8-final-corpus-manifest-1
docs/v3_8_final_corpus_manifest_faz2.json
C:\CELIK-GARDASH\datasets\faz2_corpus\final_corpus_manifest.v3_8.json
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_faz2_final_corpus_preflight_lf
```

The original `.txt` contained CRLF line endings. A canonical LF copy was
materialized before SentencePiece retraining. The LF preflight passed.

## v3.8 Final SP Retrain Outcome

The first full-corpus SentencePiece attempt did not produce a model. It loaded
5,959,029 trainable sentences and completed preprocessing, then exited during
the memory-heavy unigram seed/EM path.

The LLM team correctly recommended SentencePiece sampling with
`input_sentence_size` and `shuffle_input_sentence`. A 3M shuffled-sentence
attempt also exited during the memory-heavy path on this machine.

The successful retrain used a 1M shuffled sample from the frozen corpus:

```text
model: C:\CELIK-GARDASH\models\tokenizer_v3_8\sp_unigram_64000_faz2_tr.model
vocab: C:\CELIK-GARDASH\models\tokenizer_v3_8\sp_unigram_64000_faz2_tr.vocab
vocab size: 64,000
normalizer: identity
input_sentence_size: 1,000,000
shuffle_input_sentence: true
train_extremely_large_corpus: true
skipped too-long sentences: 68,933
```

Hashes:

```text
model sha256: 5f54645a76c8cc6346f4283884b2adb219eb44118e6024b765d965239f62e77a
vocab sha256: 18b951bf201a8f5fc6bed15965263ebde13ee85ec36b4594eb42cf3636ef10a2
```

Retrain report:

```text
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_faz2_sp_retrain_train_sample1m.md
```

The canonical config now points to the v3.8 model and validates:

```text
C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.json
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_final_config_validation.md
status: PASS
```

## Release Gate Sample

The v3.8 final tokenizer candidate passed the 10K release-gate sample:

```text
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_faz2_release_gate_sample10k\release_gate_summary.md
status: PASS
```

Passed gates:

```text
config_validation
route_density
fertility
handoff_smoke
tokenize_corpus
tokenized_package
```

Tokenization sample metrics:

```text
lines: 10,000
raw bytes: 12,125,857
tokens: 2,045,848
tokens/raw byte: 0.168718
fallback tokens: 136
fallback rate: 0.000066
masked token rate: 0.032526
protected spans: 32,939
SP alignment mismatches: 0
max token id: 64,244
```

Handoff smoke:

```text
exact roundtrip: 10,000/10,000
sidecar failures: 0
fallback rate: 0.000067
extra mask bytes/raw byte: 0.002881
LM windows: 3,996
overall: PASS
```

Tokenized package gates:

```text
checksum: PASS
fixture: PASS
dataloader: PASS
warnings: 0
failures: 0
```

## Current Status

Tokenizer-side v3.8 status:

```text
SP64K final-corpus candidate: TRAINED on 1M shuffled final-corpus sample
10K release gate sample: PASS
LLM-side v3.8 engine smoke: PASS
full-corpus tokenization: COMPLETE after detector reconstruct fix
full-corpus package consistency check: PASS on LLM side
checksum validation: PASS
fixture validation: PASS
LLM production binary_loader validation: PASS
production-final for Faz 4: ACCEPTED / FROZEN
```

This candidate is stronger than v3.7 because it is trained from the frozen Faz 2
corpus instead of the older v3.4 stratified 480MB sample. It is not a full
6.0M-line SP retrain because that path exceeded the practical memory envelope
on the current machine.

## Full-Corpus Tokenization Crash Fix

The first LLM-side full-corpus tokenization run crashed in the protected-span
detector path:

```text
ValueError: analyze_line surfaces did not reconstruct input
```

Root cause:

```text
Some web/forum lines contain literal U+2581 decorative characters.
The detector used U+2581 as an internal word-start sentinel and stripped a
standalone literal U+2581 as if it were an internal marker.
```

Fix:

```text
Only strip U+2581 when it prefixes a non-empty internal token.
Preserve a standalone literal U+2581 as ordinary surface text.
```

Patched files:

```text
scripts/materialize_v2_soft_morph_artifacts.py
src/tr_tokenizer/tokenizer.py
src/tr_tokenizer/boundary_weighted_bpe.py
C:\CELIK-GARDASH\tokenizer_v3_0_repo_snapshot\...
```

Validation:

```text
tests/test_v2_1_sidecar_operation_simulation.py + tests/test_tokenizer.py + tests/test_boundary_weighted_bpe.py: 41 passed
tests/test_v2_1_sidecar_operation_simulation.py + tests/test_tokenize_corpus.py: 9 passed
actual corpus line 2631883: encode_task passes
actual corpus line 4124939: encode_task passes
```

Dedicated fix note:

```text
docs/v3_8_detector_reconstruct_crash_fix.md
C:\CELIK-GARDASH\docs\TOKENIZER_V3_8_DETECTOR_RECONSTRUCT_CRASH_FIX.md
```

## Full-Corpus Tokenization Completed

The LLM team reran full-corpus tokenization with the patched snapshot. The run
passed the former crash point near line 2.6M and completed all lines:

```text
input lines: 6,027,968
tokens.bin bytes: 9,999,798,408
token count: 2,499,949,602
loss_mask.bin bytes: 2,499,949,602
SP alignment mismatches: 0
fallback rate: 0.0056%
max token id: 64,244 (< 64,384)
```

The LLM-side quick package consistency check passed:

```text
tokens.bin size == token_count * 4
loss_mask.bin size == token_count
expected 6 output files present
token count is consistent with the expected ~2.5B-token Faz 2 corpus scale
```

## Full-Corpus Package Acceptance

The LLM team completed end-to-end validation and accepted the v3.8 package as
production-final for Faz 4 on 2026-06-23.

Final package metrics:

```text
input lines: 6,027,968
tokens: 2,499,949,602
tokens/raw byte: 0.184311
fallback rate: 0.000056
masked token rate: 0.066567
SP alignment mismatches: 0
max token id: 64,244 (< 64,384)
tokens.bin sha256 prefix: e1697aeb
loss_mask.bin sha256 prefix: 3490629e
```

Acceptance gates:

| Gate | Result |
| --- | --- |
| checksum validation | PASS; all five manifest payloads matched |
| fixture validation | PASS; lines, tokens, index, sidecar, and id range consistent |
| LLM production binary_loader | PASS; 1,220,678 sequences at seq_len 2048 |
| label contract | PASS; single shift and loss_mask -> -100 verified |

The tokenizer-side Python dataloader simulation was not used as final evidence
for the 2.5B-token package. Its original implementation loaded and iterated the
entire stream and did not complete after approximately six hours. The production
`binary_loader` is memory-mapped and validated the actual training path.

The local gate tooling was subsequently hardened:

```text
simulate_v3_2_binary_dataloader.py: --max-batches
run_v3_8_tokenized_package_gates.py: --dataloader-max-batches
default package-gate sample: 4,096 evenly spaced batches
```

This scaling fix is maintenance work. It is not a condition on the already
accepted Faz 4 package.

Final decision:

```text
v3.8 tokenizer package: PRODUCTION-FINAL FOR FAZ 4
tokenizer-side Faz 2 blocker: CLOSED
SP model, id registry, config, and tokenized binaries: FROZEN FOR THIS RUN
next owner: LLM team / Faz 4 pretraining
```

Future multilingual or code expansion may require a later tokenizer retrain and
new version. It does not reopen the v3.8 Turkish-primary Faz 4 package.

## Prepared Since Acceptance

Added:

```text
scripts/run_v3_8_final_sp_retrain.py
scripts/run_v3_8_final_release_gates.py
```

Purpose:

```text
plan or run final SP64K retrain
write v3_8_final_sidecar_sp64k.toml
write canonical tokenizer_config.json
write retrain plan/report
plan or execute final release gates after retrain
```

Default behavior is dry-run/config materialization only. Actual SentencePiece
training requires explicit `--train`.

Snapshot smoke:

```text
C:\CELIK-GARDASH\tokenizer_v3_0_repo_snapshot\scripts\run_v3_8_final_sp_retrain.py
dry-run on the existing preflight smoke corpus: PASS
generated TOML parser load: PASS
release gate dry-run tests: PASS
release gate execute on real-mix 1K: PASS
```

Important correction:

```text
final sidecar canary/smoke should use audit_v2_2_llm_handoff_smoke.py
not the older SentencePiece-sweep canary helper
```

Execute-smoke report:

```text
docs/v3_8_release_gate_execute_smoke_findings.md
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_release_gate_execute_real_mix_1k\release_gate_summary.md
```
