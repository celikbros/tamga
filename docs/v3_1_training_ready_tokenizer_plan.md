# v3.1 Training-Ready Tokenizer Plan

Date: 2026-06-14

## Goal

Turn the v3.0 experimental sidecar handoff into a training-ready Gardaş
tokenizer package.

v3.0 proved the sidecar contract. v3.1 must close the LLM integration decisions.

## Non-Negotiable Gates

Before main LLM training:

| Gate | Required result |
| --- | --- |
| exact roundtrip | PASS on representative corpus smoke |
| sidecar schema | frozen and audited |
| special tokens | frozen id registry |
| vocab size | 32K/48K/64K decision documented |
| fertility | official report for selected vocab |
| fallback | below accepted threshold |
| corpus tokenization | binary token/mask format produced |
| dataloader smoke | LLM side can read tokens and masks |

## Work Items

### 1. Fertility Benchmark

Current preliminary result:

```text
full real-mix tokens/word: ~1.4985
```

Need:

```text
official 100-line Turkish sample
requested sentence table
real-mix corpus summary
English/noisy/code-mixed canary
```

### 2. Vocab Ablation

Train comparable Unigram models:

```text
32K
48K
64K
```

Use the same normalizer/training corpus selection and the same special-token
policy. Compare:

```text
tokens/raw byte
tokens/word
fallback rate
20M tiny-LM BPB if needed
embedding parameter cost
```

### 3. Special Token Registry

Produce:

```text
docs/v3_1_special_token_registry.md
configs/tokenizer_config.json
```

Must resolve:

```text
<unk>/<pad>/<bos>/<eos>
chat role tokens
thinking/answer tokens
tool tokens
```

### 4. Corpus Tokenization Pipeline

Build or agree on:

```text
tokenize_corpus.py
```

Output:

```text
tokens.bin
tokens.idx
sidecar.jsonl
loss_mask.bin
manifest.json
```

The training loop should not parse sidecar JSONL on every batch.

### 5. Runtime / Rust Decision

Current implementation is Python reference plus SentencePiece binding.

Production options:

```text
offline tokenized corpus only for training
Rust/C++ sidecar detector and tokenizer wrapper for serving
Python reference retained for parity tests
```

Rust work should start after the tokenization contract is frozen.

## Stop Criteria

Do not promote a tokenizer package to training-ready if:

```text
special token ids are still undecided
48K/64K decision is untested
roundtrip fails
sidecar schema audit fails
fallback rate exceeds threshold without explanation
dataloader cannot consume binary token/mask artifacts
```

## Success Criteria

v3.1 is successful when the LLM team can start a training smoke using only:

```text
tokenizer_config.json
SP model/vocab
tokens.bin/tokens.idx
optional loss_mask.bin
sidecar.jsonl for audit/debug
manifest/checksums
```

and the tokenizer team can reproduce the same ids from raw text.
