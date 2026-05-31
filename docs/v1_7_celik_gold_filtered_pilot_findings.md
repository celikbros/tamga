# v1.7 CELIK Gold Filtered Pilot Findings

Date: 2026-05-31

## Purpose

This is a historical local SentencePiece pilot trained from the copied raw
`celik_gold_corpus.jsonl` source.

Status:

```text
deprecated
```

Active v1.7 work should use:

```text
docs/v1_7_celik_gold_clean_sweep_findings.md
```

It is still not hidden-eval evidence and not downstream LLM-quality evidence.
The purpose is narrower:

```text
Can a filtered, leakage-checked, local Turkish/English corpus sample train
stronger Turkish SentencePiece baselines without long-line skip noise?
```

## Source

Archived private raw source:

```text
data/train/private/celik_ai/archive/deprecated/celik_gold_corpus.raw.deprecated.jsonl
```

The source text is ignored by git. Only aggregate reports are committed. This
raw source is kept only for historical reproducibility.

## Filtered Sample

Config:

```text
configs/v1_7_celik_gold_filtered_sample.toml
```

Build command:

```powershell
python scripts/prepare_claim_grade_corpus.py configs/v1_7_celik_gold_filtered_sample.toml --max-scan-lines 120000
```

Output:

```text
data/train/claim_grade/celik_gold_filtered_pilot.txt
```

This output is ignored by git.

Aggregate reports:

```text
artifacts/v1_7_celik_gold_filtered_sample_manifest.md
artifacts/v1_7_celik_gold_filtered_sample_leakage_report.md
```

Sample summary:

| Metric | Value |
| --- | ---: |
| scanned rows | 120001 |
| usable text rows | 120000 |
| filtered rows | 7779 |
| duplicate rows | 11 |
| written rows | 100000 |
| visible leakage hits | 0 |

Filter details:

| Filter | Count |
| --- | ---: |
| short text | 4329 |
| long by chars | 2466 |
| long by UTF-8 bytes | 217 |
| control chars | 744 |
| replacement char | 2 |
| mojibake suspects | 21 |
| exact duplicates | 0 |
| normalized duplicates | 11 |

The 4192-byte filter is intentional. It keeps SentencePiece from skipping long
lines during the pilot run, making the training input more explicit.

## SentencePiece Pilot

Config:

```text
configs/v1_7_celik_gold_sentencepiece_pilot_sweep.toml
```

Run command:

```powershell
python scripts/run_sentencepiece_sweep.py configs/v1_7_celik_gold_sentencepiece_pilot_sweep.toml --force
```

Private model/vocab output:

```text
artifacts/private/v1_7_celik_gold_sentencepiece_pilot/
```

Public aggregate reports:

```text
artifacts/v1_7_celik_gold_sentencepiece_pilot_sweep_expanded.md
artifacts/v1_7_celik_gold_sentencepiece_pilot_sweep_challenge.md
```

SentencePiece loaded all 100000 filtered sentences in this pilot run.

## Results

Expanded visible eval:

| Model | Avg tokens/word | Boundary F1 |
| --- | ---: | ---: |
| custom_tr_morph | 2.7438 | 1.0000 |
| sp_bpe_4000_celik_gold_pilot | 3.3058 | 0.6424 |
| sp_unigram_4000_celik_gold_pilot | 3.3719 | 0.7125 |
| sp_bpe_8000_celik_gold_pilot | 2.9669 | 0.6633 |
| sp_unigram_8000_celik_gold_pilot | 2.9669 | 0.7445 |

Challenge visible eval:

| Model | Avg tokens/word | Boundary F1 |
| --- | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 |
| sp_bpe_4000_celik_gold_pilot | 2.9347 | 0.6506 |
| sp_unigram_4000_celik_gold_pilot | 3.0052 | 0.7101 |
| sp_bpe_8000_celik_gold_pilot | 2.5770 | 0.6690 |
| sp_unigram_8000_celik_gold_pilot | 2.5979 | 0.7388 |

## Interpretation

The filtered local corpus gives a cleaner baseline than the earlier mixed-source
pilot because long-line skips are removed and the source is now explicit.

The best visible baseline in this run is still the 8k Unigram model:

```text
challenge F1: 0.7388
```

The custom tokenizer remains ahead on the current visible policy-shaped eval:

```text
challenge F1: 0.9220
```

This is useful evidence for baseline pressure, but it is not final proof. The
visible eval sets are small and policy-shaped. The next serious question is
whether this morphology boundary advantage helps an LM objective or downstream
task.

## Next Step

Recommended next step:

```text
Start the downstream-probe runner skeleton before scaling to 16k/32k/48k/64k.
```

Reason:

```text
More SentencePiece sizes will refine the intrinsic baseline, but the LLM-design
question needs byte-normalized LM/probe evidence.
```

Do not add new Turkish morphology rules based on this pilot.
