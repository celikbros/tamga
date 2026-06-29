# Tamga v3.8 Release And Maintenance Roadmap

Date: 2026-06-28

## Current State

Tamga v3.8 is production-final for the Turkish-primary CELIK-GARDAS Faz 4
pretraining run. The tokenizer model, id contract, sidecar schema, tokenized
package, and LLM consumer contract are accepted and frozen.

This repository release archives the public implementation, reproducible
research history, tests, configs, and aggregate evidence. Private corpora,
private trained models, and full token binaries are not part of the public Git
release.

## v3.8 Release Closeout

The repository closeout requires:

```text
release-relevant source, scripts, configs, tests, docs, and aggregate reports
temporary pytest output excluded
private data and model artifacts excluded
project version set to 3.8.0
test suite passing
secret and large-file scan passing
Git author and committer identity equal to celikbros
v3.8.0 tag published from a clean tree
```

## Frozen Invariants

The following must not change within v3.8:

```text
SentencePiece vocabulary ids: 0..63999
UTF-8 byte fallback ids: 64000..64255
wrapper control reserve: 64256..64383
effective vocabulary size: 64384
<unk>: 0
<bos>/<s>: 1
<eos>/</s>: 2
<pad>: 64256
sidecar schema: v2.2-sidecar-jsonl-1
raw text must never activate wrapper control tokens
```

## Maintenance Mode

After the v3.8.0 repository release, tokenizer work is reactive. Reopen this
line only for a reproduced tokenizer regression, corpus reconstruction defect,
security issue, or an integration mismatch found during Faz 4.

Any fix that changes token ids, model vocabulary, normalizer behavior, sidecar
semantics, or existing corpus tokenization requires a new explicit version and
an LLM compatibility decision.

## Next Research Version

A multilingual or code-heavy corpus is a new scope, not a silent v3.8 update.
Start that work on a new major research line after the corpus mix and consumer
requirements are frozen. Re-run vocabulary-size selection, fertility and
fallback canaries, fixed-byte LM comparison, roundtrip and sidecar gates, and
LLM integration smoke before adoption.

Until such a scope exists, the tokenizer team has no open algorithmic critical
path. Faz 4 pretraining belongs to the LLM team.
