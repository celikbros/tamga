# LLM Handoff Packet

Date: 2026-06-01

Status:

```text
pilot-ready for LLM-team evaluation
not production-ready
not final tokenizer selection
```

## Purpose

This packet summarizes what the tokenizer team can hand to the LLM team now.

The immediate goal is not to claim that `Tamga` is the final LLM
tokenizer. The immediate goal is:

```text
run a small controlled LM probe and test whether morphology-aware Turkish
tokenization helps or hurts byte-normalized LM loss
```

## Current Tokenizer Status

The tokenizer is a Turkish-centered morphology-aware research prototype.

Current visible eval status:

| Eval | Role | Result |
| --- | --- | ---: |
| `data/eval/tr_gold_expanded.tsv` | frozen regression | 50/50 exact, F1 1.0000 |
| `data/eval/tr_challenge.tsv` | challenge/dev | 44/108 exact, F1 0.8255 |

The frozen regression result checks policy fidelity. It is not hidden-eval or
downstream proof.

## Baseline Evidence

Clean local corpus source:

```text
data/train/private/celik_ai/celik_gold_corpus.clean.jsonl
```

Actual clean pilot text used for current SentencePiece and downstream prep:

```text
data/train/claim_grade/celik_gold_clean_pilot.txt
```

This text file is ignored by git. Public reports contain only aggregate metrics.

Clean SentencePiece sweep:

```text
docs/v1_7_sentencepiece_sweep_findings.md
artifacts/v1_7_celik_gold_clean_sentencepiece_sweep_expanded.md
artifacts/v1_7_celik_gold_clean_sentencepiece_sweep_challenge.md
```

Key visible baseline result:

| Eval | Custom boundary F1 | Best clean SP boundary F1 | Closest-fertility SP boundary F1 |
| --- | ---: | ---: | ---: |
| expanded | 1.0000 | 0.7425 | 0.7290 |
| challenge | 0.9220 | 0.7369 | 0.7353 |

Interpretation:

```text
The custom tokenizer is stronger on visible morphology-policy boundary metrics.
This does not yet prove LLM training benefit. It means the LLM team should run
byte-normalized LM probes rather than choose from boundary F1 alone.
```

## Leakage Status

Direct eval leakage was checked on the actual 100k clean pilot text used for the
current SentencePiece baseline.

Report:

```text
artifacts/v1_7_celik_gold_clean_pilot_eval_leakage_report.md
```

Summary:

| Eval set | Raw exact | Strict normalized full | Partial 8-gram | Notes |
| --- | ---: | ---: | ---: | --- |
| gold | 0 | 0 | 0 | 9 one-word `short_full` hits |
| challenge | 0 | 0 | 0 | no hits |

The one-word `short_full` hits are not treated as sentence leakage.

## Downstream Probe Prep

Clean downstream prep config:

```text
configs/v1_7_downstream_probe_celik_gold_clean_pilot.toml
```

Public aggregate report:

```text
artifacts/v1_7_downstream_probe_prep_celik_gold_clean_pilot.md
```

Private tokenized outputs:

```text
artifacts/private/v1_7_downstream_probe/celik_gold_clean_pilot_20k/
```

These private token JSONL files must not be committed or shared publicly because
tokens can reconstruct private corpus text.

Prepared split:

| Split | Lines | Bytes | Words |
| --- | ---: | ---: | ---: |
| train | 16000 | 21.76 MiB | 2603245 |
| valid | 2000 | 2.72 MiB | 324562 |
| test | 2000 | 2.65 MiB | 316529 |

Prepared tokenizer variants:

```text
custom_tr_morph
unicode_char
sp_bpe_8000_celik_gold_clean
sp_unigram_8000_celik_gold_clean
sp_bpe_16000_celik_gold_clean
sp_unigram_16000_celik_gold_clean
sp_bpe_32000_celik_gold_clean
sp_unigram_32000_celik_gold_clean
sp_bpe_64000_celik_gold_clean
sp_unigram_64000_celik_gold_clean
```

Validation split prep metrics:

| Tokenizer | Avg tokens/word | Tokens/byte | Bytes/token |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 1.4931 | 0.170166 | 5.8766 |
| unicode_char | 7.0540 | 0.803931 | 1.2439 |
| sp_bpe_8000_celik_gold_clean | 1.9272 | 0.219642 | 4.5529 |
| sp_unigram_8000_celik_gold_clean | 1.8791 | 0.214160 | 4.6694 |
| sp_bpe_16000_celik_gold_clean | 1.6775 | 0.191180 | 5.2307 |
| sp_unigram_16000_celik_gold_clean | 1.6464 | 0.187635 | 5.3295 |
| sp_bpe_32000_celik_gold_clean | 1.5014 | 0.171116 | 5.8440 |
| sp_unigram_32000_celik_gold_clean | 1.4844 | 0.169170 | 5.9112 |
| sp_bpe_64000_celik_gold_clean | 1.3776 | 0.156997 | 6.3696 |
| sp_unigram_64000_celik_gold_clean | 1.3703 | 0.156169 | 6.4033 |

Interpretation:

```text
On this pilot split, custom_tr_morph is not token-expensive. It is close to the
32k clean SP baselines, while the 64k SP baselines use fewer tokens per byte.
The important question is whether the morphology-aware boundary advantage
improves byte-normalized LM loss enough to justify the tokenizer design.
```

This is still only preparation. It does not report LM loss.

## What The LLM Team Should Run

Use the same raw split and train the same small causal LM for each tokenizer.

Minimum first comparison:

```text
custom_tr_morph
sp_unigram_32000_celik_gold_clean
sp_bpe_32000_celik_gold_clean
sp_unigram_64000_celik_gold_clean
sp_unigram_16000_celik_gold_clean
unicode_char
```

Primary metric:

```text
validation bits-per-byte
test bits-per-byte
```

Secondary metrics:

```text
tokens/sec
bytes/sec
GPU memory
max sequence pressure
decode/roundtrip failures if any
```

Do not compare token-level perplexity by itself across tokenizers.

## Acceptance Criteria For Pilot Use

The custom tokenizer becomes a credible LLM pilot candidate if:

```text
bits-per-byte is comparable to or better than clean SP baselines
protected span behavior remains stable
roundtrip remains lossless
sequence length and throughput are acceptable
```

The custom tokenizer should not become the default LLM tokenizer if:

```text
bits-per-byte is clearly worse than SP baselines
training throughput or sequence pressure is unacceptable
decode/roundtrip behavior breaks
```

## Known Limits

Current known limits:

- visible evals are policy-shaped; they are not hidden eval
- no independent human heldout eval yet
- no LM bits-per-byte result yet
- no production vocabulary allocation yet
- v1.x is Turkish-centered and multilingual-aware, not full Turkic morphology

## Recommendation

Do not send this as a final tokenizer handoff.

Send it as:

```text
controlled pilot package for small-LM tokenizer comparison
```

The tokenizer team should wait for the LLM team's byte-normalized probe result
before making a final tokenizer recommendation for the larger LLM project.
