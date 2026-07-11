# v3.8 PII-Clean Re-Tokenize Readiness

Date: 2026-07-05
Status: READY / WAITING ON DERLEM RELEASE

## Trigger

LLM team (Gardash) field feedback, received 2026-07-05, three items:

```text
1. field validation: v3.8 package proven in a real training run
2. incoming job: re-tokenize the Derlem PII-clean corpus with the v3.8 chain
3. archive note: v3.1-v3.8 reports/configs merged on the Gardash side
```

Item 3 is Gardash-side record keeping; no tokenizer-side action. Items 1 and 2
are recorded below.

## Field Validation Record

First field proof of the frozen v3.8 Faz 2 contract:

```text
consumer run: 132M-param recipe-proof pretraining (~0.2B tokens consumed)
binary loader / loss_mask / single label-shift chain: no defects reported
tokenizer-side conclusion: frozen contract validated in production use
```

## Incoming Job: Re-Tokenize On The Derlem Clean Candidate

### What does not change (frozen v3.8 invariants)

```text
SP model: sp64k_final_protected_passthrough_sidecar_controls128
model sha256: 5f54645a76c8cc6346f4283884b2adb219eb44118e6024b765d965239f62e77a
vocab sha256: 18b951bf201a8f5fc6bed15965263ebde13ee85ec36b4594eb42cf3636ef10a2
id contract: SP 0..63999, byte fallback 64000..64255, controls 64256..64383
effective vocab: 64,384 · <pad>=64256 · normalizer identity
sidecar schema: v2.2-sidecar-jsonl-1
tokenizer version: stays v3.8 (NO SP retrain, NO registry/config change)
```

This is a new tokenized package of the same tokenizer version, produced from a
new frozen input corpus. It is not a tokenizer version change.

### What changes

```text
input corpus: Derlem clean candidate
  quoted lines: 5,922,891
  removed: 104,853 verified-PII lines (TCKN/IBAN/card/phone/email)
  sha256 prefix quoted so far: ebe292...
new final corpus manifest instance (schema v3.8-final-corpus-manifest-1)
new package outputs: tokens.bin / loss_mask.bin / index.jsonl / sidecar.jsonl
suggested output dir name: tokenized_v3_8_pii_clean (distinct from tokenized_v3_8)
```

### Preconditions required from the Derlem/LLM side

```text
1. frozen release handoff: full sha256, exact line count, exact byte count
2. line-ending policy confirmed (v3.8 chain canonicalizes to LF before SP work;
   the raw Faz 2 .txt was CRLF and needed LF materialization)
3. line-count reconciliation: 6,027,968 - 104,853 = 5,923,115, but the quoted
   clean candidate is 5,922,891 (224-line delta). The release manifest must
   account for the delta (e.g. additional non-PII removals). Do not assume.
4. output naming/location decision confirmed by the LLM team
```

### Execution checklist (v3.8 chain, unchanged order)

```text
1. preflight: scripts/run_v3_8_final_corpus_preflight.py
   (LF canonicalization if needed, line/byte counts, sha vs manifest)
2. manifest: instantiate docs/v3_8_final_corpus_manifest_template.json,
   validate with scripts/validate_v3_8_final_corpus_manifest.py
3. tokenize: scripts/tokenize_corpus.py with the frozen v3.8 tokenizer entry
   (worker determinism was verified in v3.8: workers=1 vs 2 checksum-identical)
   config template: configs/v3_8_pii_clean_retokenize_sp64k.toml (fill the
   <GARDASH_ROOT> placeholders; --config/--tokenizer are now required args)
   environment: v3.8-era tools resolve consumer paths via the GARDASH_ROOT
   environment variable (fallback: the historical C:/CELIK-GARDASH literal)
4. package gates: scripts/run_v3_8_tokenized_package_gates.py
   (checksum PASS, fixture PASS, dataloader sampled 4,096 batches PASS)
5. handoff smoke: scripts/audit_v2_2_llm_handoff_smoke.py
   (NOT the older SentencePiece-sweep canary helper)
6. publish aggregate evidence only: lines, tokens, tokens/raw byte, fallback
   rate, masked token rate, SP alignment mismatches, max token id, sha prefixes
```

### Acceptance criteria

```text
SP alignment mismatches: 0
handoff smoke exact roundtrip: 100%
max token id < 64,384; raw text never activates wrapper control tokens
tokens/raw byte expected near the v3.8 full-corpus value (0.184311); the
removed PII lines are ~1.7% of lines, so a large shift is a red flag
```

### Explicit non-actions

```text
no SP retrain: PII-line removal does not reopen vocabulary or ids
  (v3.8 SP was trained on a 1M shuffled sample of the raw corpus; the model
  stays frozen per the v3.8 closure contract)
optional extra evidence, only if requested: aggregate vocab scan for
  PII-shaped pieces (long digit-heavy tokens); expectation: none beyond
  generic number pieces
```

## Ownership

```text
Derlem: frozen clean release + manifest
LLM team (Gardash): runs the chain in its environment, owns Spark v1 schedule
tokenizer team (this repo): provides chain/runbook/validators, reviews the
  aggregate gate evidence, answers contract questions
```

This job is the only chain blocking the Spark v1 schedule on the LLM side.
Tokenizer-side readiness is complete; nothing to run until the Derlem release
lands.
