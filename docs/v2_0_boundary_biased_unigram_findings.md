# v2.0 Boundary-Biased Unigram Decode Findings

Date: 2026-06-10

## Question

After the morph-vocabulary coverage audit, SP64 appeared to already contain most
high-value Turkish morph surfaces as vocabulary pieces. The remaining question
was therefore:

```text
Are morphology pieces missing, or does the Unigram decoder simply prefer pieces
that cross teacher morphology boundaries?
```

This audit tests the second hypothesis without training a new tokenizer.

## Method

We kept the SP64 Unigram model and vocabulary unchanged. For normal text only,
we ran a diagnostic Viterbi decoder over SP64 vocabulary pieces and subtracted a
lambda penalty when a candidate piece crossed a custom-teacher soft morphology
boundary.

Protected routing stayed hard and finite. Numeric-like protected spans used the
current SP passthrough floor.

This is not a final tokenizer implementation. It is a mechanism probe.

## Key Result

The full valid/test pressure sweep shows a strong morphology gain at low token
cost:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | --- |
| finite protected SP64 numeric-SP floor | 0.171202 | 0.172015 | 0.6913 | 25/25 |
| boundary-biased lambda 0 | 0.162451 | 0.163120 | 0.7422 | 25/25 |
| boundary-biased lambda 2 | 0.162522 | 0.163181 | 0.7606 | 25/25 |
| boundary-biased lambda 4 | 0.163313 | 0.163968 | 0.7701 | 25/25 |
| boundary-biased lambda 8 | 0.178023 | 0.178580 | 0.8225 | 25/25 |

Split token pressure in this audit excludes per-line EOS tokens, so tiny-LM
encoded split reports will be slightly higher.

## Interpretation

This initially supported the H2 diagnosis:

```text
The high-value morphology surfaces are often present in SP64 vocabulary, but
plain Unigram decode does not consistently choose morphology-aligned paths.
```

Advisor review found an attribution problem that changes the interpretation:

```text
boundary-biased lambda 0 is already different from official SentencePiece /
the finite protected floor.
```

So the lambda 4 result currently contains two effects:

```text
decoder/pipeline effect
+ morphology boundary penalty effect
```

The lambda 0 tiny-LM BPB row has now been run. It confirms that the decoder /
pipeline effect is large, while lambda 4 still adds a smaller extra morphology
effect over lambda 0.

The result also explains why seed appendix and broad UDS were weak levers:

```text
more vocabulary availability is not the main bottleneck;
decode/objective preference is.
```

Lambda 4 is the current best diagnostic point:

```text
Challenge F1 improves from 0.6913 to 0.7701 while valid/test token pressure
remains near the SP64/floor band.
```

Lambda 8 proves that much higher visible F1 is possible, but it starts moving
back toward expensive segmentation pressure.

## Decision

Do not return to marker-dose tuning, broad UDS expansion, or seed appendix.

Tiny-LM 300-step calibration:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Valid BPB | Test BPB | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| SP64 | 0.159020 | 0.159620 | 4.827723 | 4.860352 | 0.7351 | 1/25 |
| finite protected numeric-SP floor | 0.171903 | 0.172734 | 4.875198 | 4.911037 | 0.6913 | 25/25 |
| boundary-biased lambda 0 | 0.163153 | 0.163839 | 4.726285 | 4.769027 | 0.7422 | 25/25 |
| boundary-biased lambda 4 | 0.164015 | 0.164686 | 4.686700 | 4.721480 | 0.7701 | 25/25 |
| boundary-biased lambda 8 | 0.178725 | 0.179299 | 4.816592 | 4.850946 | 0.8225 | 25/25 |

Lambda 0 already improves BPB over SP64 and the protected floor, so lambda 4 is
not solely responsible for the headline win. Lambda 4 adds:

```text
test BPB vs lambda 0: -0.047547
Challenge F1 vs lambda 0: +0.0279
test tokens/raw byte vs lambda 0: +0.000847
```

This is promising but narrower than the earlier headline claim.

Lambda 8 is also positive against SP64 and the protected floor on BPB, but it
is much less efficient than lambda 4. It should be treated as a high-F1
reference, not the current balanced candidate.

The next meaningful branch should be one of:

```text
1. boundary-biased decode as an experimental tokenizer wrapper,
2. constrained/MorphBPE-style training objective that internalizes this penalty,
3. boundary-weighted Unigram training if feasible without forking too much code.
```

Lambda 4 is frozen as a promising diagnostic point, not promoted. Lambda 8
establishes the upper-F1 side of the local frontier.

## Follow-Up

Recommended immediate follow-up:

```text
decompose floor -> lambda0 and lambda0 -> lambda4;
audit roundtrip/stateless decode;
separate morphology F1 from protected-span scoring;
only then run longer/seeded lambda0 vs lambda4 confirmation.
```
