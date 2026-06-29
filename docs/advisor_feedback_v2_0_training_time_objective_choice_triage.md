# Advisor Feedback Triage: v2.0 Training-Time Objective Choice

Date: 2026-06-10

## Short Verdict

The advisor feedback changes the immediate order of work.

The direction is still alive:

```text
finite protected routing
+ learned tokenizer
+ Turkish morphology teacher as a soft/training-time prior
```

But the next step is not a full custom trainer yet. The active protected
baseline and wrapper path are not valid enough to anchor new objective results.

## Consensus

All advisors agreed on the important structural points:

1. Runtime boundary-biased decode should stay demoted.
2. Roundtrip / stateless decode / normalization must be fixed before more BPB
   claims.
3. `finite_protected_sp64_numeric_sp_floor` is not a reliable active null
   baseline while it fails roundtrip and adds wrapper tax on clean text.
4. Protected routing should remain a hard route outside the learned morphology
   objective, but it must be exact and nearly invisible when no protected spans
   are present.
5. The toy boundary-weighted BPE probe is useful as a mechanical sanity check,
   not as strategic evidence.
6. The next serious morphology objective should use the custom morphology
   teacher as a soft prior, not as hard marker dose, broad UDS, or runtime-only
   decode trick.

## Main Disagreement

The advisors diverged on which learned objective should come first:

| Option | Support | Triage |
| --- | --- | --- |
| Boundary-weighted Unigram | Strong support from most advisors | Best main direction, but not before wrapper/normalization is fixed |
| Boundary-weighted BPE | Supported as lower implementation risk by one advisor | Keep as fallback/control; do not make it the main branch yet |
| Full custom posterior-regularized Unigram EM | High-upside but invasive | Too early |
| Runtime boundary-biased decoder | Useful diagnostic only | Not a tokenizer candidate until exact roundtrip is solved |

## New Immediate Blocker

The current protected wrapper fails exact reconstruction:

```text
finite_protected_sp64_numeric_sp_floor: 17/1994 exact on valid
boundary-biased lambda0/lambda4: 0/1994 exact on valid smoke
SP64 bare: not perfect either under the current audit
```

This means we cannot treat the current protected floor as a clean LLM-tokenizer
baseline. It may still be useful diagnostically, but not as the anchor for
handoff-quality claims.

The likely cause is wrapper/normalization behavior around:

```text
dummy prefix
spaces
punctuation
apostrophes
segment seams
protected-span boundaries
```

## Decision

Pause new trainer implementation until these are handled:

1. Define the normalization contract.
2. Repair or redesign the protected wrapper so roundtrip is exact under that
   contract.
3. Re-emit the baseline table after the wrapper repair.
4. Only then run training-time morphology objective experiments.

Do not return to:

```text
marker-dose tuning
broad UDS expansion
seed appendix tuning
runtime lambda promotion
```

## Recommended Next Technical Sequence

### Phase 0: Contract And Wrapper Repair

Decide which contract the tokenizer will claim:

```text
Option A: byte-exact lossless
Option B: exact after a documented normalizer
```

Then require:

```text
SP64 bare roundtrip: explain or eliminate failures
finite protected floor roundtrip: 100% under the contract
zero-protected wrapper no-op: tokenization should match official SP as closely
as possible, or every difference must be explained
protected stress: 25/25
```

### Phase 1: Rung-0 Diagnostic

Before training a new tokenizer, measure whether the existing SP64 vocabulary
already contains morphology-compliant paths.

For each word or span:

```text
unconstrained SP64 Viterbi path
best path that avoids crossing high-confidence teacher boundaries
delta score
delta tokens
whether compliant path exists
```

Interpretation:

```text
small delta -> decode/objective nudges may be enough
large delta / missing pieces -> vocabulary training must be reshaped
```

### Phase 2: Stock SentencePiece Soft Prior

If Phase 1 is promising, test a zero-custom-trainer soft prior:

```text
use stock SentencePiece Unigram
insert pretokenization delimiters at high-confidence morphology boundaries
only for a fraction rho of training examples
rho sweep: 0.0, 0.05, 0.10, 0.25, 0.50
inference text remains delimiter-free
```

This gives a soft training-time morphology prior while preserving stock runtime.

### Phase 3: Custom Objective Only If Needed

Only if the stock-rho experiment plateaus:

```text
boundary-weighted Unigram pruning / posterior regularization
or constrained MorphBPE/BPE fallback
```

## Gates Before Tiny-LM Again

Tiny-LM BPB should be unblocked only after:

```text
roundtrip contract passes
protected stress = 25/25
rho=0 / lambda=0 null reproduces the intended baseline
tokens/raw byte is near the repaired protected floor
hidden or fresh intrinsic morphology eval is at least directionally positive
multilingual/code token bloat is bounded
```

When run, the tiny-LM comparison should be byte-matched or at least report
bytes seen clearly, not interpreted from fixed-step results alone.

## Updated Project Interpretation

This is not a failure of the project. It is a useful correction:

```text
The morphology prior may be real.
The runtime decoder result was not yet a valid tokenizer result.
The wrapper layer is now the engineering bottleneck.
The next good research move is to make the baseline exact, then test whether
SP64 already has morphology-compliant paths before writing a heavier trainer.
```
