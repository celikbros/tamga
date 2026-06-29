# v2.0 Partial-Boundary SentencePiece Findings

Date: 2026-06-10

## Summary

We tested stock SentencePiece `pretokenization_delimiter` as a low-risk
training-time morphology prior.

The idea was:

```text
insert U+E000 at custom soft morphology boundaries in only part of the
training view
train ordinary SP Unigram
encode normal valid/test text without markers
wrap with finite protected routing for protected spans
```

This kept compression near SP64, but did not materially transfer the Turkish
morphology teacher signal into the learned tokenizer.

## Results

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Bare Challenge F1 | Finite-protected Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | ---: | --- |
| SP64 reference | 0.159020 | 0.159620 | ~0.7351 | n/a | 1/25 |
| repaired finite protected numeric-SP floor | ~0.162866 | ~0.163779 | n/a | 0.6755 | 25/25 |
| partial boundary rho=0.10 | 0.158404 | 0.159029 | 0.7361 | 0.6750 | 25/25 |
| partial boundary rho=0.25 | 0.158458 | 0.159060 | 0.7380 | 0.6782 | 25/25 |
| partial boundary rho=0.50 | 0.158676 | 0.159231 | 0.7361 | 0.6777 | 25/25 |

## Interpretation

The delimiter dose was compression-safe, but the learned vocabulary stayed
effectively SP64-like on the visible Turkish morphology challenge.

Increasing rho from 0.10 to 0.50 did not create a monotonic morphology gain:

```text
bare Challenge F1: 0.7361 -> 0.7380 -> 0.7361
finite-protected Challenge F1: 0.6750 -> 0.6782 -> 0.6777
```

This is too small to justify more stock-delimiter tuning.

## Decision

Close the stock SentencePiece partial-boundary branch.

Do not run tiny-LM BPB on these candidates. They are compression-safe but do
not improve the morphology/protected frontier.

## Next

Move to a real training-time objective:

```text
boundary-weighted Unigram or constrained/MorphBPE-style learning
```

The objective should use teacher boundaries as a soft preference inside
training/decoding, not as an external marker dose that disappears at normal
encode time.
