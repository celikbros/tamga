# v1.7 Downstream Probe Prep Findings

Date: 2026-05-31

## Purpose

This step prepares tokenizer inputs for a later small-LM downstream probe.

It does not train a model and does not report bits-per-byte yet. The goal is to
make the LLM-team handoff concrete:

```text
same raw split
same corpus bytes
multiple tokenizer variants
private token JSONL outputs
public aggregate prep report
```

## Script

```text
scripts/prepare_downstream_probe.py
```

The script:

- reads a plain-text corpus
- creates deterministic train/valid/test splits
- tokenizes the same split with each configured tokenizer
- writes private token JSONL files
- writes a public aggregate report without raw corpus text

## Demo Config

```text
configs/v1_7_downstream_probe_demo.toml
```

Command:

```powershell
python scripts/prepare_downstream_probe.py configs/v1_7_downstream_probe_demo.toml
```

Report:

```text
artifacts/v1_7_downstream_probe_prep_demo.md
```

This uses the tiny public demo corpus and exists mostly as a wiring check.

## CELIK Gold Pilot Config

```text
configs/v1_7_downstream_probe_celik_gold_pilot.toml
```

Command:

```powershell
python scripts/prepare_downstream_probe.py configs/v1_7_downstream_probe_celik_gold_pilot.toml
```

Report:

```text
artifacts/v1_7_downstream_probe_prep_celik_gold_pilot.md
```

Private token outputs:

```text
artifacts/private/v1_7_downstream_probe/celik_gold_filtered_pilot_20k/
```

The public report contains only aggregate counts.

## Pilot Split

The CELIK gold pilot uses the first 20,000 lines from the filtered local sample:

| Split | Lines | Bytes | Words |
| --- | ---: | ---: | ---: |
| train | 16000 | 21.68 MiB | 2592338 |
| valid | 2000 | 2.73 MiB | 325698 |
| test | 2000 | 2.71 MiB | 324637 |

## Tokenizer Prep Metrics

Validation split:

| Tokenizer | Avg tokens/word | Tokens/byte | Bytes/token |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 1.4922 | 0.170041 | 5.8809 |
| unicode_char | 7.0537 | 0.803788 | 1.2441 |
| sp_bpe_8000_celik_gold_pilot | 1.9342 | 0.220405 | 4.5371 |
| sp_unigram_8000_celik_gold_pilot | 1.8876 | 0.215099 | 4.6490 |

Test split:

| Tokenizer | Avg tokens/word | Tokens/byte | Bytes/token |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 1.4935 | 0.170326 | 5.8711 |
| unicode_char | 7.0491 | 0.803907 | 1.2439 |
| sp_bpe_8000_celik_gold_pilot | 1.9292 | 0.220017 | 4.5451 |
| sp_unigram_8000_celik_gold_pilot | 1.8824 | 0.214672 | 4.6583 |

## Interpretation

On this natural-ish local pilot split, the custom tokenizer is not obviously
token-expensive. It produces fewer tokens per word and per byte than the 8k
SentencePiece pilot baselines.

That is useful, but it is still not the downstream answer. The important next
metric is:

```text
byte-normalized validation/test loss from the same small LM training harness
```

If the custom tokenizer has lower fertility but worse bits-per-byte, morphology
boundary quality alone is not enough. If it is comparable or better in
bits-per-byte, it becomes a credible LLM-tokenizer candidate.

## Next Step

Hand this prep output to the LLM training side, or add a minimal training harness
only if tokenizer-team ownership expands.

Recommended LLM-team first run:

```text
custom_tr_morph
sp_unigram_8000_celik_gold_pilot
sp_bpe_8000_celik_gold_pilot
unicode_char baseline
```

Metric:

```text
validation bits-per-byte
test bits-per-byte
bytes/sec
tokens/sec
```

Do not add new Turkish morphology rules based on this prep result.

## CELIK Gold Clean Pilot Config

The active LLM handoff prep now uses the clean corpus pilot, not the older
filtered raw-source pilot.

Config:

```text
configs/v1_7_downstream_probe_celik_gold_clean_pilot.toml
```

Command:

```powershell
python scripts/prepare_downstream_probe.py configs/v1_7_downstream_probe_celik_gold_clean_pilot.toml
```

Report:

```text
artifacts/v1_7_downstream_probe_prep_celik_gold_clean_pilot.md
```

Private token outputs:

```text
artifacts/private/v1_7_downstream_probe/celik_gold_clean_pilot_20k/
```

Prepared split:

| Split | Lines | Bytes | Words |
| --- | ---: | ---: | ---: |
| train | 16000 | 21.76 MiB | 2603245 |
| valid | 2000 | 2.72 MiB | 324562 |
| test | 2000 | 2.65 MiB | 316529 |

Validation prep metrics:

| Tokenizer | Avg tokens/word | Tokens/byte | Bytes/token |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 1.4931 | 0.170166 | 5.8766 |
| unicode_char | 7.0540 | 0.803931 | 1.2439 |
| sp_bpe_8000_celik_gold_clean | 1.9272 | 0.219642 | 4.5529 |
| sp_unigram_8000_celik_gold_clean | 1.8791 | 0.214160 | 4.6694 |
| sp_bpe_16000_celik_gold_clean | 1.6775 | 0.191180 | 5.2307 |
| sp_unigram_16000_celik_gold_clean | 1.6464 | 0.187635 | 5.3295 |

Handoff docs:

```text
docs/llm_handoff_packet.md
docs/v1_7_downstream_probe_handoff.md
```

After the clean SentencePiece sweep, the downstream probe config was expanded
to include 32k and 64k SP baselines. The clean downstream prep was re-run with:

```powershell
python scripts/prepare_downstream_probe.py configs/v1_7_downstream_probe_celik_gold_clean_pilot.toml
```

The public aggregate report is:

```text
artifacts/v1_7_downstream_probe_prep_celik_gold_clean_pilot.md
```

The clean handoff is ready for a controlled small-LM probe, but it is not a
production tokenizer handoff.
