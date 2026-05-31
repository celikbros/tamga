# v1.7 Downstream Probe Protocol

Date: 2026-05-31

Implementation status:

```text
scripts/prepare_downstream_probe.py now prepares deterministic corpus splits,
private token JSONL files, and public aggregate prep reports.
```

Current prep findings:

```text
docs/v1_7_downstream_probe_prep_findings.md
```

## Purpose

This protocol defines a small, practical downstream probe for the tokenizer.

The key question is:

```text
Does morphology-aware tokenization help a language model, or does it only score
well on boundary F1?
```

Boundary F1 is useful, but it is an intrinsic metric. LLM design needs at least
one extrinsic or near-extrinsic signal before adopting a custom tokenizer.

## Non-Goals

This protocol does not claim:

- production LLM quality
- full pretraining validation
- Turkish tokenizer finality
- multilingual/Turkic readiness

It is a small decision probe, not the final LLM experiment.

## Recommended Probe

Primary probe:

```text
small causal language model trained from scratch on the same Turkish corpus
with multiple tokenizer variants
```

Primary metric:

```text
byte-normalized validation loss / bits-per-byte
```

Why byte-normalized:

```text
Different tokenizers produce different sequence lengths. Token-level perplexity
is not directly comparable across tokenizers. Byte-normalized loss is a cleaner
comparison for tokenizer usefulness.
```

## Tokenizers To Compare

Minimum set:

```text
custom_tr_morph
Turkish-trained SentencePiece BPE
Turkish-trained SentencePiece Unigram
byte/character baseline
```

Optional references:

```text
Qwen tokenizer
LLaMA tokenizer
Mistral tokenizer
BERTurk/XLM-R/mT5 tokenizers for fertility and boundary metrics only
```

Encoder-only tokenizers can be useful references, but the causal LM probe should
use tokenizers that can support the chosen training setup cleanly.

## Corpus

Use one fixed corpus split for every tokenizer:

```text
train
validation
test
```

Minimum practical corpus:

```text
5-20 MB Turkish text
```

Better practical corpus:

```text
50-200 MB mixed-domain Turkish text
```

Corpus mix should include:

- formal prose/news
- user-generated/informal text
- technical/code-mixed text
- names/numbers/dates

All reports must state:

```text
source
license
size in bytes
line count
word count
dedup policy
normalization policy
eval leakage status
```

## Model Size

Use a deliberately small model so the probe is cheap:

```text
parameters: 5M-30M
layers: 4-8
hidden size: 256-512
context length: fixed across tokenizers by tokens, plus byte-normalized reporting
training budget: fixed tokens or fixed bytes, both reported
```

The exact architecture can be chosen later by the LLM team. The tokenizer team
should define the metrics and fairness constraints.

## Fairness Constraints

Every tokenizer run must use:

```text
same raw corpus
same train/validation/test split
same model architecture
same optimizer
same training steps or comparable byte budget
same random seeds when possible
same evaluation script
```

Report both:

```text
tokens processed
bytes processed
wall-clock time
```

If fixed-token training is used, also report bytes seen. If fixed-byte training
is used, also report tokens seen.

## Metrics

Primary metrics:

```text
validation bits-per-byte
test bits-per-byte
validation loss normalized by bytes
training throughput bytes/sec
memory use
```

Secondary tokenizer metrics:

```text
avg tokens/word
avg tokens/byte
protected span break rate
byte/fallback rate
morph boundary F1 on visible and heldout eval
```

Optional downstream probes:

```text
small POS/morph tagging probe
NER offset stability check
classification fine-tune smoke
```

These are optional and should not block the first LM probe.

## Decision Criteria

The custom tokenizer is a stronger LLM candidate if:

```text
bits-per-byte is comparable to or better than Turkish-trained BPE/Unigram
protected span break rate remains 0
token fertility is not much worse
roundtrip is lossless
training/inference throughput is acceptable
```

It is not enough for `custom_tr_morph` to win boundary F1. If bits-per-byte is
substantially worse, morphology-aware segmentation may still be useful for
analysis, but it is not yet justified as the default LLM tokenizer.

## Suggested Report Table

```text
tokenizer | vocab_size | avg_tokens/word | boundary_f1 | protected_break_rate |
bits_per_byte_valid | bits_per_byte_test | bytes/sec | notes
```

## Minimum First Experiment

If resources are tight, run:

```text
custom_tr_morph
SP Unigram 8k
SP BPE 8k
byte/char baseline
```

Corpus:

```text
5-20 MB Turkish mixed-domain sample
```

Model:

```text
5M-10M parameters
short training run
3 seeds if affordable, 1 seed if not
```

This will not settle the final design, but it will reveal whether the tokenizer
is obviously harmful, neutral, or promising.

## Risks

Main risks:

- tiny model may not represent large LLM behavior
- small corpus may amplify tokenizer quirks
- fixed-token vs fixed-byte training can bias results
- custom tokenizer may have higher engineering complexity even if metrics are
  close
- boundary F1 and LM loss may disagree

This is acceptable. The probe is a decision aid, not final proof.

## Implementation Hand-Off

Tokenizer team should provide:

```text
tokenizer encode/decode API
baseline tokenizer list
evaluation scripts
metric definitions
corpus split rules
report template
```

LLM team should provide:

```text
training harness
model architecture
compute budget
training logs
loss curves
throughput measurements
```

## Immediate Next Step

After this protocol, the original RFC step is complete:

```text
docs/v2_0_router_morphbpe_rfc.md
```

The current immediate next step is now:

```text
Run the same prepared splits through a small LM training harness and report
byte-normalized validation/test loss.
```

The RFC connects:

- v1.6b R3 Azerbaijani deferral
- protected span layer
- Turkish deterministic core
- learned MorphBPE/Unigram fallback
- byte fallback

## Success Criteria

This protocol is complete when:

```text
primary metric is fixed as byte-normalized LM loss / bits-per-byte
minimum tokenizer comparison set is fixed
fairness constraints are documented
handoff boundary between tokenizer team and LLM team is documented
```

No tokenizer behavior change is required for this workstream.
