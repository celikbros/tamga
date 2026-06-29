# v3.1 Response To LLM Architecture Team

Date: 2026-06-14

## Summary

Thank you for the review. The questions are exactly the right integration
questions: fertility, vocab size, special token ids, sidecar overhead, and the
runtime shape of the tokenizer must be closed before a main Gardaş training run.

The most important clarification is:

```text
v3.0 is an experimental integration handoff, not the final production tokenizer.
```

Current v3.0 handoff contract:

```text
SP64 Unigram model tokens
+ 256 UTF-8 byte fallback ids
+ protected-span sidecar JSONL with exact byte offsets
```

The repo contains morphology, pretokenization, normalization, and teacher
components, but the handed-off model-token path is not a runtime morphology
segmentation pipeline for every normal Turkish word.

The copied 26 GB under:

```text
C:\CELIK-GARDASH\datasets\pretraining_raw\celik_ai
```

is LLM pretraining data. The current `sp_unigram_64000_train_only.model` was
not retrained on that full corpus. Therefore 64K should be treated as the
current integration baseline, not as a proven final vocab size.

## Q1: Can We Reduce Vocab To 48K?

Yes, this should be tested. We cannot currently claim that 64K is required.

Proposed v3.1 ablation:

```text
32K / 48K / 64K Unigram, trained on the same representative Gardaş corpus view
```

Required metrics:

```text
tokens/raw byte
tokens/word fertility
fallback rate
protected sidecar smoke
special-token compatibility
tiny-LM BPB if 48K remains competitive on intrinsic metrics
```

Decision rule:

```text
Prefer 48K if it stays close to 64K in fertility/BPB and lowers embedding cost.
Keep 64K only if it shows a material quality or compression advantage.
```

## Q2: Fertility Benchmark

Preliminary exact v3 handoff-path sentence results:

| Text | Words | Tokens | Tokens/word |
| --- | ---: | ---: | ---: |
| `Türkiye'nin başkenti Ankara'dır.` | 3 | 8 | 2.6667 |
| `Mercimek çorbası Türk mutfağının vazgeçilmezidir.` | 5 | 9 | 1.8000 |
| `görüşebileceklerimizdenmisiniz` | 1 | 5 | 5.0000 |
| `güneşli` | 1 | 2 | 2.0000 |
| `The quick brown fox jumps over the lazy dog.` | 9 | 15 | 1.6667 |

Full real-mix estimate from the existing v2.2 handoff smoke token count plus
word counting:

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| words | 4967044 |
| model tokens | 7443139 |
| tokens/word | 1.498505 |
| tokens/raw byte | 0.167820 |
| fallback rate | 0.000456 |

Reading:

```text
The corpus-level fertility is near the requested <=1.5 target.
However, morphologically dense single words can still be high-fertility.
This is acceptable for an integration baseline but must be compared in 48K/64K ablation.
```

Current artifact:

```text
artifacts/v3_1_gardash_fertility_benchmark_100lines.md
```

The exact full real-mix v3 fertility path is too slow in the current Python
reference implementation. That is itself an integration finding: production
corpus tokenization should be precomputed and/or ported to optimized Rust/C++.

## Q3: Special Tokens

This is not closed yet and must be frozen before training.

Current SentencePiece meta ids:

```text
<unk>  id 0
<s>    id 1
</s>   id 2
```

Therefore a request such as:

```text
<pad> id 0
```

would conflict with the current model. We need a single frozen id registry used
by both training and inference.

Recommended next artifact:

```text
tokenizer_config.json
special_token_registry.md
```

Recommended policy:

```text
Do not start main LLM training until special token ids are frozen.
```

## Q4: Sidecar Overhead

We do not recommend parsing JSONL sidecar metadata in the training hot path.

Recommended corpus-tokenization output:

```text
tokens.bin
tokens.idx
sidecar.jsonl
loss_mask.bin      optional, precomputed from sidecar byte offsets
manifest.json
```

Training should consume binary token and mask files. The sidecar JSONL remains
an audit/debug/metadata artifact.

## Q5: Does SP Re-Split Morphology Pieces?

The premise needs correction. The v3.0 handoff path does not run a deterministic
morphology segmenter over every normal word and then force those pieces through
SP.

Earlier v2.x morphology-forcing attempts improved visible morphology F1 but did
not pay for their token-pressure/BPB cost. Current v3.0 keeps normal text close
to SP64 and uses the sidecar for protected span metadata.

Morphology remains useful as:

```text
teacher signal
diagnostic evaluation
possible auxiliary LM objective
future selective tokenizer branch
```

It is not currently a production runtime segmentation layer.

## Rust / Production Runtime Clarification

The current package is not Rust-native.

Current implementation shape:

```text
Python reference scripts
SentencePiece runtime via Python binding
sidecar detector in Python
```

This was intentional for research iteration. Production tokenization should be
handled by either:

```text
offline pretokenized binary corpus artifacts
or an optimized Rust/C++ implementation with parity tests
```

## Proposed v3.1 Closeout

Before main Gardaş training:

```text
1. Freeze special-token id registry.
2. Run 32K/48K/64K vocab ablation on a representative Gardaş corpus view.
3. Produce official fertility report for candidate vocabs.
4. Implement corpus tokenization pipeline that emits tokens.bin/tokens.idx/sidecar/mask.
5. Validate Python reference output against the LLM dataloader consumer.
```

After those pass, we can declare a training-ready tokenizer package.
