# LLM Team Review Request: v2.1 Protected Sidecar Contract

Date: 2026-06-13

## Why We Are Asking

We are building a Turkish-primary tokenizer research prototype for future LLM
work. At this stage the tokenizer decision is no longer mainly about Turkish
morphology. The immediate v2.1 question is the protected-span contract:

```text
How should URLs, file names, code-ish spans, package/version strings, numbers,
dates, and similar protected spans be represented during LLM training and later
tooling?
```

We have two lossless sidecar designs. Both can reconstruct the original text.
They differ in whether protected spans are guaranteed to align with token
boundaries.

We need your consumer-side decision before spending another 20M-byte tiny-LM
probe or consolidating the v2.1 baseline.

## What Protected Means Here

Protected spans include cases such as:

```text
https://example.com/a?b=1
github.com'daki
README.md'yi
config_v2.json
tokenizers>=0.19
3'uncu
14:30'da
%20'si
```

The protected-span detector writes sidecar metadata with byte offsets and route
type. The model-token stream may or may not be forced to split at those byte
offsets, depending on the option below.

## Current Options

Both options:

```text
use normal SP64 pieces for normal text
use a 256-token UTF-8 fallback for true unknowns
roundtrip exactly on the v1.8 valid/test split
store protected-span metadata in a sidecar
do not reserve finite route-token ids
```

Vocabulary accounting for both sidecar options:

```text
64000 SP pieces + 256 UTF-8 byte fallback ids = 64256 vocab
```

| Option | Test tokens/raw byte | Roundtrip | Protected edge alignment | Detector coupling | Meaning |
| --- | ---: | --- | ---: | --- | --- |
| `sp64_protected_passthrough_sidecar` | 0.159660 | 1998/1998 | 0.463721 | Low | Cheapest; protected spans are byte-logical metadata, but SP tokens may cross protected edges |
| `sp64_protected_presplit_sidecar` | 0.165755 | 1998/1998 | 1.000000 | High | More expensive; protected span start/end always align with token boundaries |

Measured alignment tax:

```text
0.165755 - 0.159660 = +0.006095 tokens/raw byte
about +3.8%
```

## What The Difference Means

### Option B: Passthrough Sidecar

The model sees nearly ordinary SP64 tokenization. Protected spans are tracked in
metadata by byte offsets.

Benefits:

```text
almost no token-pressure tax versus bare SP64
detector improvements can often be patched in sidecar logic later
model-token stream is less coupled to protected-span detector decisions
```

Cost:

```text
some SP tokens can straddle a protected-span boundary
token-level operations may need byte-offset reconciliation
```

### Option A: Pre-Split Sidecar

The detector runs before SP encoding. Text is split at protected-span edges, so
no SP token can cross a protected edge.

Benefits:

```text
protected spans are token-boundary aligned
span-level token masking/copy/redaction is simpler and safer
```

Cost:

```text
about +3.8% tokens/raw byte
the token stream is coupled to detector decisions
if detector behavior changes materially, retraining may be required
```

## Safety Status

Pre-split safety checks:

```text
valid exact roundtrip: 1994/1994
test exact roundtrip: 1998/1998
protected edge alignment: 1.000000
crossing pieces: 0
```

Detector adversarial battery:

```text
61 cases
62 expected protected spans
precision/recall/F1 = 1.000000
```

The battery covers:

```text
protected suffix attachment
percent-encoded suffixes
numeric suffix attachment
span-adjacent punctuation
line-edge spans
nested/comparator spans
```

## What We Are Not Asking

We are not asking you to choose the final production tokenizer.

We are not asking whether Turkish morphology should be used in the model. That
is a separate v2.x research question.

We are asking which protected-span contract is useful enough for LLM training
and downstream tooling to justify the permanent +3.8% token tax.

## Questions For The LLM/Downstream Team

Please answer concretely. We prefer a conservative answer if any of these
features are planned.

1. During pretraining or SFT, will you mask, weight, redact, copy, or route
   protected spans using token indices rather than byte offsets?

2. Do you require that no model token straddles a protected-span boundary for
   PII/security/privacy reasons?

3. Will generation or constrained decoding need to copy protected spans exactly
   from token-boundary-aligned spans?

4. Is a one-token edge fuzz acceptable if the sidecar still records exact byte
   offsets and exact text reconstruction is guaranteed?

5. If the protected-span detector improves later, is it acceptable for the
   model-token stream to remain unchanged while sidecar metadata changes?

6. Is a permanent +3.8% token/raw-byte tax acceptable for simpler protected-span
   token operations?

7. Which contract should be treated as the v2.1 baseline for the next tiny-LM
   row and handoff docs?

## Requested Answer

Please choose one:

```text
A. Token-boundary alignment is required.
   Use `sp64_protected_presplit_sidecar` despite the +3.8% token tax.

B. Logical byte-span metadata is sufficient.
   Use `sp64_protected_passthrough_sidecar` and avoid the token tax.

C. Unsure.
   Run a small downstream masking/copy/redaction simulation before choosing.
```

If you choose A:

```text
we will run the 20M fixed-byte tiny-LM row for
`sp64_protected_presplit_sidecar`
```

If you choose B:

```text
we will consolidate the cheaper passthrough sidecar as the practical v2.1
baseline and avoid training on detector-coupled token boundaries
```

If you choose C:

```text
we will build a tiny simulation with representative protected-span operations
and decide from actual downstream behavior instead of tokenization metrics alone
```
