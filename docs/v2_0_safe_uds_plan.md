# v2.0 Safe UDS Probe Plan

Date: 2026-06-10

## Purpose

The simple morph-seed appendix branch was compression-safe but did not transfer
the custom morphology teacher signal into the learned Unigram vocabulary.

This probe tests the next cheapest structural mechanism:

```text
SentencePiece user_defined_symbols for only the seven safe_uds_candidate_later
suffix surfaces selected from train-only policy statistics.
```

This is not a broad morphology rule and not a production tokenizer.

## Inputs

```text
policy TSV: artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv
symbol materializer: scripts/materialize_v2_safe_uds_symbols.py
SP config: configs/v2_0_safe_uds_sentencepiece.toml
```

The expected safe pool is:

```text
ecek
acak
ümüz
ımız
imiz
yecek
umuz
```

These were selected because they are long, low-collision, low-hard-share
suffix surfaces. Short/ambiguous suffixes stay out.

## Commands

Materialize the safe UDS symbol list:

```powershell
python scripts\materialize_v2_safe_uds_symbols.py
```

Train/evaluate the UDS Unigram candidate:

```powershell
python scripts\run_v2_candidate_sentencepiece_probe.py configs\v2_0_safe_uds_sentencepiece.toml --force
```

If token pressure is acceptable, run intrinsic eval:

```powershell
python scripts\evaluate_v2_finite_protected_sp64_intrinsic.py `
  --sp64-model artifacts\private\v2_0_safe_uds\safe_uds_unigram_64000.model `
  --reference-label safe_uds_unigram_64000 `
  --finite-label finite_protected_safe_uds `
  --report-out artifacts\v2_0_safe_uds_finite_protected_intrinsic_eval.md
```

## Gates

Continue only if:

```text
protected stress remains 25/25 with finite protected routing
valid/test tokens/raw byte stays close to SP64 and far below marker branches
visible Challenge F1 improves over finite_protected_sp64_floor
```

Stop this cheap UDS branch if it preserves protection but does not materially
improve morphology F1.
