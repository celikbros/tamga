# v3.8 Release Gate Execute Smoke Findings

Date: 2026-06-21

## Purpose

`scripts/run_v3_8_final_release_gates.py` was added as the post-retrain gate
orchestrator for the final tokenizer candidate.

Default mode is dry-run. This smoke verifies that `--execute` can run the
actual gate sequence end to end.

## First Execute Smoke: Tiny Preflight Corpus

Input:

```text
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_preflight_snapshot_smoke\final_corpus_text.txt
```

Result:

```text
config_validation: PASS
route_density: PASS
fertility: PASS
handoff_smoke: FAIL
```

Failure reason:

```text
lm_batch_windows: FAIL
```

The input had only two lines and five tokens, so it could not form a
`batch_size=4, seq_len=128` LM smoke window. This is a correct gate failure,
not a tokenizer failure.

The run also exposed and fixed a Windows subprocess output decoding issue in
the runner. The runner now captures child-process output with UTF-8 and
replacement fallback.

## Second Execute Smoke: Real-Mix 1K

Input:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_0\real_mix_60k_sample.txt
```

Limits:

```text
max_lines: 1000
smoke_max_lines: 1000
tokenization_max_lines: 1000
workers: 2
chunk_lines: 64
batch_size: 4
seq_len: 128
```

Report:

```text
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_release_gate_execute_real_mix_1k\release_gate_summary.md
```

Gate result:

| Gate | Status |
| --- | --- |
| config_validation | PASS |
| route_density | PASS |
| fertility | PASS |
| handoff_smoke | PASS |
| tokenize_corpus | PASS |
| tokenized_package | PASS |

## Current Reading

The final release gate runner is now tested in both modes:

```text
dry-run command planning: PASS
execute on realistic 1K sample: PASS
```

Use the runner after final SP retrain. Do not use the tiny two-line preflight
corpus as an execute smoke input because it is too small to satisfy the LM
window gate.
