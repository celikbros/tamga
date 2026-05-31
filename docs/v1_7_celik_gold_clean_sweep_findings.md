# v1.7 CELIK Gold Clean Sweep Findings

Date: 2026-06-01

## Purpose

This note records the first SentencePiece baseline sweep using the cleaned local
corpus:

```text
celik_gold_corpus.clean.jsonl
```

The clean source was copied into the repo's ignored private area:

```text
data/train/private/celik_ai/celik_gold_corpus.clean.jsonl
```

The original `C:\CELIK_AI` file was not modified.

## Scope

This is the point where corpus polishing stops for v1.7.

Remaining corpus work is limited to:

```text
visible eval leakage checks
explicit source/corpus policy for larger claim-grade runs
```

No extra adult/SEO/keyword-specific filtering is introduced here because it can
create topic bias and unnecessary data loss. The current result is a baseline
training sample, not a final pretraining corpus policy.

## Sample And Leakage

Config:

```text
configs/v1_7_celik_gold_clean_sample.toml
```

Command:

```powershell
python scripts/prepare_claim_grade_corpus.py configs/v1_7_celik_gold_clean_sample.toml --max-scan-lines 120000
```

Output:

```text
data/train/claim_grade/celik_gold_clean_pilot.txt
```

The output text is ignored by git.

Aggregate reports:

```text
artifacts/v1_7_celik_gold_clean_sample_manifest.md
artifacts/v1_7_celik_gold_clean_sample_leakage_report.md
```

Sample summary:

| Metric | Value |
| --- | ---: |
| scanned rows | 120001 |
| usable text rows | 120000 |
| filtered rows | 7737 |
| duplicate rows | 11 |
| written rows | 100000 |
| exact leakage hits | 0 |
| normalized leakage hits | 0 |
| 8-gram leakage hits | 0 |

Filter details:

| Filter | Count |
| --- | ---: |
| short text | 4326 |
| long by chars | 2466 |
| long by UTF-8 bytes | 217 |
| control chars | 705 |
| replacement char | 2 |
| mojibake suspects | 21 |
| exact duplicates | 0 |
| normalized duplicates | 11 |

## SentencePiece Sweep

Config:

```text
configs/v1_7_celik_gold_clean_sentencepiece_sweep.toml
```

Command:

```powershell
python scripts/run_sentencepiece_sweep.py configs/v1_7_celik_gold_clean_sentencepiece_sweep.toml --force
```

Private model/vocab output:

```text
artifacts/private/v1_7_celik_gold_clean_sentencepiece/
```

Public reports:

```text
artifacts/v1_7_celik_gold_clean_sentencepiece_sweep_expanded.md
artifacts/v1_7_celik_gold_clean_sentencepiece_sweep_challenge.md
```

SentencePiece loaded all 100000 filtered sentences.

## Results

Expanded visible eval:

| Model | Avg tokens/word | Boundary F1 |
| --- | ---: | ---: |
| custom_tr_morph | 2.7438 | 1.0000 |
| sp_bpe_8000_celik_gold_clean | 2.9669 | 0.6633 |
| sp_unigram_8000_celik_gold_clean | 2.9669 | 0.7377 |
| sp_bpe_16000_celik_gold_clean | 2.6694 | 0.6919 |
| sp_unigram_16000_celik_gold_clean | 2.7355 | 0.7425 |

Challenge visible eval:

| Model | Avg tokens/word | Boundary F1 |
| --- | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 |
| sp_bpe_8000_celik_gold_clean | 2.5770 | 0.6690 |
| sp_unigram_8000_celik_gold_clean | 2.5953 | 0.7369 |
| sp_bpe_16000_celik_gold_clean | 2.3446 | 0.6837 |
| sp_unigram_16000_celik_gold_clean | 2.3995 | 0.7340 |

## Interpretation

The clean 16k BPE baseline narrows the token-budget gap on visible eval:

```text
expanded avg tokens/word:
custom: 2.7438
16k BPE: 2.6694
16k Unigram: 2.7355
```

However, boundary F1 remains much lower than the custom morphology-aware
tokenizer on these visible policy-shaped evals:

```text
challenge boundary F1:
custom: 0.9220
best clean SP baseline: 0.7369
```

This is a useful baseline-pressure result. It is not hidden-eval evidence and
not downstream LLM evidence.

## Decision

Stop corpus polishing for now.

Next useful work is either:

```text
small LM bits-per-byte probe
```

or, if baseline scaling continues:

```text
32k/48k/64k SP sweep on the same clean source with explicit corpus policy
```

Do not add new Turkish morphology rules based on this visible sweep.
