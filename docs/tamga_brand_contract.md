# Tamga Brand Contract

Date: 2026-06-28

## Canonical Identity

```text
brand: Tamga
GitHub owner: celikbros
repository: https://github.com/celikbros/tamga
Python distribution: tamga-tokenizer
primary CLI: tamga
Git author/committer name: celikbros
```

Tamga refers to a mark, seal, or identity symbol in Turkic cultural history.
The name reflects the tokenizer's job: transform text into reversible symbols
used by a language model.

## Compatibility

The working Python namespace remains:

```text
tr_tokenizer
```

Legacy CLI entry points remain available:

```text
tr-tokenizer
tr-centric-tokenizer
```

Renaming the internal namespace would create unnecessary breakage across the
research scripts, tests, and the frozen v3.8 handoff. It requires a separate
major-version migration if it is ever pursued.

## Release Scope

Tamga v3.8 is production-final for the Turkish-primary CELIK-GARDAS Faz 4 run.
Future multilingual or code-focused retraining must use a new explicit version;
it must not silently alter the frozen v3.8 model or id contract.
