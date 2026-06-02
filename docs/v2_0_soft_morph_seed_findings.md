# v2.0 Soft Morph Seed Findings

Date: 2026-06-02

## Status

```text
soft-morph/protected-hard materialization completed on the 16k train split
seed vocabulary analysis completed
not a tokenizer training result
not final LLM evidence
```

## Materialization Result

Report:

```text
artifacts/v2_0_soft_morph_materialization.md
```

Summary:

| Metric | Value |
| --- | ---: |
| lines | 16000 |
| bytes | 22819852 |
| pieces | 6376173 |
| pieces/byte | 0.279413 |
| seed tokens | 3882002 |
| unique seed tokens | 218981 |
| soft boundaries | 894466 |
| hard boundaries | 5481707 |
| whitespace pieces | 2494171 |
| protected pieces | 96132 |
| suffix pieces | 925856 |

Interpretation:

```text
materialized pieces match the lossless-open custom representation
this is much cheaper than lossless+64k byte fallback
but still much more expensive than SP64
```

## Seed Coverage

Report:

```text
artifacts/v2_0_soft_morph_seed_vocab_analysis.md
```

Coverage:

| Cap | Coverage | Uncovered token count |
| ---: | ---: | ---: |
| 8000 | 0.834791 | 641342 |
| 16000 | 0.882641 | 455586 |
| 32000 | 0.921844 | 303400 |
| 64000 | 0.953441 | 180744 |
| 128000 | 0.976563 | 90981 |

Category summary:

| Category | Unique tokens | Token count | Share |
| --- | ---: | ---: | ---: |
| suffix | 244 | 925856 | 0.238500 |
| word_start | 218485 | 2525477 | 0.650560 |
| punct_or_symbol | 152 | 430085 | 0.110789 |
| other | 100 | 584 | 0.000150 |

At cap 64000:

```text
suffix coverage is effectively complete: 203 suffix seed types cover 925808 occurrences
the remaining uncovered count is almost entirely word-start long-tail
```

## Decision

The pressure source is now clearer:

```text
not suffix inventory size
not protected spans
main pressure = whitespace serialization + rare word-start surface pieces
```

Therefore the first v2.0 candidate should not simply seed all custom pieces and
fallback rare pieces to bytes. It should:

```text
seed high-frequency suffixes and protected punctuation/symbol pieces
seed only high-frequency word_start pieces
let a learned tokenizer/BPE handle the long-tail word_start surface pieces
keep morphology boundaries as soft hints, not hard no-merge boundaries
keep protected spans as hard boundaries
```

## Next Candidate

Define the first learned-vocabulary prototype as:

```text
protected_hard_soft_morph_seeded_sp64
```

Initial policy:

```text
hard boundaries: whitespace/protected/script/punctuation
soft boundaries: custom morphology suffix boundaries
seed vocab: suffix + punctuation/protected + top word_start pieces
learned merges may cross soft morphology boundaries
rare word_start long-tail must not become byte fallback by default
```

This is still a prototype path. It is not ready for LLM-team handoff.
