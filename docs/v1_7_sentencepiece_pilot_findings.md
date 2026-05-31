# v1.7 SentencePiece Pilot Findings

Date: 2026-05-31

Update:

```text
The cleaner filtered pilot from `celik_gold_corpus.jsonl` is documented in:
docs/v1_7_celik_gold_filtered_pilot_findings.md
```

## Purpose

This is a local pilot, not a claim-grade baseline.

The goal is to verify that a larger leakage-checked local corpus sample can train
stronger Turkish SentencePiece baselines than the tiny 310-line demo corpus.

## Corpus

Config:

```text
configs/v1_7_claim_grade_corpus.toml
```

Local output:

```text
data/train/claim_grade/celik_ai_claim_sample.txt
```

This file is ignored by git.

Pilot build command:

```powershell
python scripts/prepare_claim_grade_corpus.py configs/v1_7_claim_grade_corpus.toml --max-scan-lines 15000
```

Current manifest:

```text
artifacts/v1_7_claim_grade_corpus_manifest.md
```

The pilot sample contains 75,388 written lines across the local CELIK_AI source
pool. The sample is approximately 132 MB on disk. Exact, normalized, and 8-gram
leakage checks against the visible expanded/challenge eval sets found no hits.

SentencePiece reported 69,459 loaded sentences and 5,929 skipped too-long lines
during training. This is acceptable for a pilot, but a claim-grade run should
either pre-filter long lines explicitly or document the skip count.

## Models

Config:

```text
configs/v1_7_sentencepiece_pilot_sweep.toml
```

Trained local models:

```text
artifacts/private/v1_7_sentencepiece_pilot/
```

These model/vocab files are ignored by git because they were trained from local
private corpus text. Public commits include only aggregate reports.

Pilot models:

```text
sp_bpe_4000_celik_pilot
sp_unigram_4000_celik_pilot
sp_bpe_8000_celik_pilot
sp_unigram_8000_celik_pilot
```

## Results

Expanded visible eval:

| Model | Avg tokens/word | Boundary F1 |
| --- | ---: | ---: |
| custom_tr_morph | 2.7438 | 1.0000 |
| sp_bpe_4000_celik_pilot | 3.3058 | 0.6614 |
| sp_unigram_4000_celik_pilot | 3.2810 | 0.7091 |
| sp_bpe_8000_celik_pilot | 2.9008 | 0.6792 |
| sp_unigram_8000_celik_pilot | 2.9917 | 0.7441 |

Challenge visible eval:

| Model | Avg tokens/word | Boundary F1 |
| --- | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 |
| sp_bpe_4000_celik_pilot | 3.0183 | 0.6480 |
| sp_unigram_4000_celik_pilot | 3.0131 | 0.6961 |
| sp_bpe_8000_celik_pilot | 2.5692 | 0.6714 |
| sp_unigram_8000_celik_pilot | 2.5666 | 0.7405 |

Reports:

```text
artifacts/v1_7_sentencepiece_pilot_sweep_expanded.md
artifacts/v1_7_sentencepiece_pilot_sweep_challenge.md
```

## Interpretation

The local 8k Unigram pilot is meaningfully stronger than the tiny 1k demo
SentencePiece baseline, especially on challenge F1.

This does not prove the final tokenizer claim. The visible eval sets are still
policy-shaped and small. The result only says:

```text
A larger Turkish-trained SentencePiece pilot narrows the gap, but does not erase
the morphology-boundary advantage on the current visible evals.
```

## Next Step

Before enabling 16k/32k/48k/64k, decide whether to:

1. build a larger leakage-checked local sample, with explicit long-line
   filtering and source proportions; or
2. pause baseline scaling and implement the downstream-probe runner skeleton.

Do not add new Turkish morphology rules based on these visible results.
