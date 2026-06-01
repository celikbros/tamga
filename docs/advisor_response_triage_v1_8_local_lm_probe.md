# Advisor Response Triage: v1.8 Local LM Probe

Date: 2026-06-01

## Verdict

The advisors agree that a local bits-per-byte LM probe can be useful, but the
current plan must not be run as-is.

The revised stance is:

```text
Do not run v1.8 as a confirmation probe.
Run it only after fairness fixes, as an adversarial screening probe designed to
falsify the morphology-aware tokenizer path.
```

## Consensus Points

Both advisors support:

- v1.8 as a cheap screening step, not final LLM evidence.
- no final LLM tokenizer handoff before v2.0.
- bits-per-byte as the primary cross-tokenizer metric.
- explicit reporting of tokens seen, bytes seen, throughput, and memory.
- keeping the result small-scope and not over-interpreting it.

## Blockers Before Running

### 1. Retrain SP Vocabularies On Train Split Only

Current SP baselines were trained on the full 100k pilot, while the LM probe
split uses 20k lines from that same pilot. This means SP vocabularies have seen
validation/test distribution.

Fix:

```text
For v1.8 LM loss probing, train every SP baseline on the 16k train split only.
Do not reuse the full-pilot SP vocabularies as primary LM-loss baselines.
```

The existing full-pilot SP sweep remains useful as intrinsic baseline pressure,
but it is not fair enough for LM-loss comparison.

### 2. Add A Hybrid Baseline

The current comparison is pure deterministic custom vs pure SP. Advisors agree
that the practical winner may be hybrid:

```text
morphology/protection-aware pretokenization + learned BPE/Unigram
```

Fix:

```text
Add at least one hybrid baseline before treating v1.8 as actionable.
```

If implementation is too costly, mark v1.8 as incomplete and defer the LM probe
until the hybrid baseline exists.

### 3. Use A Symmetric Baseline Matrix

The proposed run set was asymmetric. It included some 32k/64k models but not a
complete enough matrix.

Minimum fair matrix:

```text
custom_tr_morph
utf8_byte or byte-level baseline
unicode_char
sp_bpe_16000_train_only
sp_unigram_16000_train_only
sp_bpe_32000_train_only
sp_unigram_32000_train_only
sp_bpe_64000_train_only
sp_unigram_64000_train_only
hybrid_bpe_or_unigram_train_only
```

8k baselines are optional and can be treated as weak lower anchors.

### 4. Check Split Near-Duplicates

Before LM probing, check train/valid/test near-duplicate leakage inside the 20k
split. Full eval leakage is not enough for LM validation hygiene.

Fix:

```text
Run n-gram or MinHash-style split dedup / overlap checks between train, valid,
and test.
```

### 5. Prove Lossless Roundtrip

Bits-per-byte comparison is meaningful only if every tokenizer can represent and
decode the same raw text without loss.

Fix:

```text
Add encode/decode roundtrip checks on train/valid/test for each tokenizer.
Roundtrip failure > 0 disqualifies that tokenizer from generation use.
```

## Design Changes

### Budget

Primary reporting should use:

```text
bytes seen
bits-per-byte vs bytes seen
```

Also report:

```text
tokens seen
steps
wall-clock
approximate compute if available
```

Fixed-token-only training would bias the comparison.

### Model Size

Avoid tiny models where vocabulary embeddings dominate the whole parameter
budget.

Recommended first model:

```text
fixed transformer body
tied embeddings
roughly 10M-30M non-embedding parameters if feasible
report total parameters and embedding parameters per tokenizer
```

Large vocabularies change parameter allocation, especially at small scale. This
must be reported.

### Canary Slice

Keep the primary v1.8 probe Turkish-primary, but add a small diagnostic canary:

```text
noisy Turkish
code-mixed Turkish/English
non-Turkish multilingual snippets
```

The canary is not the primary score. It exists to catch catastrophic rule-based
failure modes.

## Pre-Registered Interpretation

### Strong Positive

Custom tokenizer is worth deeper v2.0 investment if:

```text
custom_tr_morph is comparable or better than the strongest SP/hybrid baselines
on validation/test bits-per-byte, while keeping stable training, lossless
roundtrip, and acceptable throughput/context pressure.
```

### Weak Or Inconclusive Negative

If SP wins or ties in the current small setup:

```text
Do not kill the morphology direction automatically.
Treat the result as weak/inconclusive unless train-only SP, hybrid baselines,
roundtrip checks, duplicate checks, and canary diagnostics are all in place.
```

### Strong Negative

Deprioritize pure deterministic custom as a default LLM tokenizer if, after the
fairness fixes:

```text
custom_tr_morph is consistently worse than the strongest comparable SP/hybrid
baseline by more than 0.15-0.25 bits/byte on both validation and test, without
offsetting throughput/context/robustness benefits.
```

Even then, keep morphology as a v2.0 hybrid prior rather than abandoning it.

## Updated Internal Decision

```text
Do not start LM training immediately.
First implement the v1.8 fairness fixes:
1. train-split-only SP baselines,
2. hybrid baseline,
3. symmetric baseline matrix,
4. split near-duplicate checks,
5. lossless roundtrip checks,
6. noisy/code-mixed canary diagnostics.
```

After those are in place, run the local LM probe as adversarial screening.
