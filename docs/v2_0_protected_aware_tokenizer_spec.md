# v2.0 Protected-Aware Tokenizer Spec

Date: 2026-06-02

## Status

```text
design spec
not an implementation
blocks further candidate probing until accepted
```

This spec turns the advisor decision into an implementation contract. The
v2.0 tokenizer must be a finite-vocabulary, protected-aware learned tokenizer.
It should preserve the useful Turkish morphology/protection signal without
returning to pure-custom lossless token pressure.

## Core Principle

```text
LLM-safe means stateless decode(ids)
```

Every token ID used by the model must have a deterministic decode payload known
from the vocabulary itself. Decoding cannot depend on:

```text
side-channel payload maps
runtime placeholder tables
bracket matching
the original input string
hidden span metadata unavailable to the model
```

Therefore:

```text
placeholder + payload designs are rejected
open-vocabulary protected surface tokens are diagnostic only
soft morphology markers cannot become arbitrary non-decodable model tokens
```

## Architecture

The v2.0 candidate uses an Option 1 + Option 3 hybrid:

```text
raw input
-> deterministic protected-span pretokenizer
-> route each span to a finite encoder family
-> learned normal-text BPE/Unigram for ordinary text
-> finite protected-subword encoder for protected spans
-> universal UTF-8 byte fallback
-> stateless decode from token payloads
```

The target is not a Turkish-only rule engine. The target is a learned tokenizer
with hard safety boundaries and optional morphology priors.

## Token Families

The final vocabulary should be partitioned conceptually:

```text
NORMAL_TEXT pieces
PROTECTED_TEXT pieces
BYTE_00 through BYTE_FF fallback pieces
SPECIAL control tokens
optional USER_DEFINED protected literals/patterns
```

Rules:

```text
NORMAL_TEXT pieces decode to ordinary UTF-8 text fragments
PROTECTED_TEXT pieces decode to ordinary UTF-8 text fragments
BYTE pieces decode to their exact byte value
SPECIAL control tokens are reserved and never used for source text fallback
```

No source-text token may decode to an empty string. If a marker is needed during
training, it must either be removed before final vocabulary export or be kept as
a non-generatable training artifact outside the LLM tokenizer vocabulary.

## Protected Categories

The protected-span pretokenizer must identify at least:

```text
URL
email
file name and file path
code-like identifier
package/version/comparator expression
number
date
time
hash/commit-like string
inline code literal where detectable
non-target script word span
```

Turkish suffix tails attached to protected bases must be handled explicitly:

```text
README.md'yi
Node.js'in
transformers>=4.40
2026'da
https://example.com'da
```

The protected base should remain protected. A valid Turkish suffix tail may be
routed back to the normal text/morphology path after the protected base.

## Protected Encoding

Protected spans cannot be represented as one arbitrary token per observed
surface form. That would recreate open vocabulary and fail stateless generation.

Protected spans must be encoded with finite pieces:

```text
frequent protected literals/patterns as optional user-defined symbols
learned protected-subword pieces for common protected substrings
UTF-8 byte fallback for all remaining protected bytes
```

Examples of likely useful protected pieces:

```text
http
https
://
.com
.org
.md
.py
.json
>=
<=
==
v
_
-
/
.
```

These examples are not a fixed list. The actual list must be learned or selected
from train-only data and then validated on held-out protected stress tests.

## Normal Text Encoding

Normal Turkish/text spans use a learned BPE or Unigram model.

Morphology can influence this model through:

```text
seed vocabulary
merge constraints
soft-boundary training views
feature/metadata diagnostics
```

Morphology should not force every suffix boundary to become a hard model-token
boundary. Frequent surface forms must be allowed to compress when the learned
model supports it.

## Soft Morphology Policy

Soft morphology is a prior, not a payload.

Allowed:

```text
seed high-confidence suffix pieces
weight or mark candidate morphology boundaries during tokenizer training
forbid merges only at hard protected/script/whitespace boundaries
report morphology alignment as diagnostics
```

Not allowed:

```text
turn every custom morphology piece into a mandatory model token
emit hidden morphology markers that decode to nothing
depend on morphology metadata to reconstruct the text
apply Turkish morphology to protected, code, URL, or non-target script spans
```

## User-Defined Symbol Policy

User-defined symbols are optional accelerators, not the main protected solution.

Promote a protected literal/pattern only if:

```text
it is frequent in train-only data
it is stable across domains
it does not encode private payload content
it improves protected token pressure or span preservation
it does not replace byte fallback
```

Do not promote:

```text
rare full URLs
rare full file paths
one-off identifiers
private-looking strings
eval-only artifacts
```

## Byte Fallback

Byte fallback is mandatory.

Requirements:

```text
all UTF-8 bytes 0x00 through 0xFF are representable
unknown normal text can fall back to bytes
unknown protected text can fall back to bytes
decode(encode(x)) == x for valid input strings
no <unk> is emitted for source text
```

Byte fallback is a losslessness guarantee, not a quality target. Frequent
Turkish/Turkic letters, common punctuation, and common protected substrings
should not routinely fall to bytes.

## Training Data Rules

Learned vocabularies and selected UDS entries must be trained only on the train
split for controlled probes.

For claim-grade comparisons:

```text
train-only tokenizer vocabulary
valid/test never used for tokenizer training
SP64 remains the compression null hypothesis
custom lossless remains the high-F1 high-pressure reference
```

## Decode Invariants

The final tokenizer must satisfy:

```text
decode(encode(x)) == x
decode(ids) is a pure function of ids
source text fallback never needs <unk>
protected spans do not require external payload maps
generated arbitrary ids decode deterministically
```

The implementation should test:

```text
raw roundtrip
Unicode roundtrip
protected-span roundtrip
byte fallback roundtrip
random token-id decode sanity
```

## Evaluation Gates

Before any tiny-LM BPB run, a candidate must pass intrinsic gates:

```text
roundtrip exact: 100% on public stress and probe splits
protected span preservation: near 25/25 on current stress set
challenge boundary F1: materially above SP64, target 0.80+
token pressure: much closer to SP64 than pure custom lossless
byte fallback rate: reported separately for normal and protected spans
no Turkish morphology leakage into non-target/protected spans
```

Only after these pass:

```text
run controlled tiny-LM BPB screening
compare against SP64 null baseline
report fixed-token and approximate iso-byte views
report tokens/sec, bytes/sec, and effective context bytes
```

## First Prototype Scope

The first implementation should be intentionally small:

```text
1. implement protected-span route labels
2. train/select finite protected pieces from train-only data
3. keep normal SP64-compatible learned text model
4. add universal byte fallback
5. export a single stateless vocabulary map
6. run intrinsic gates before tiny-LM
```

Do not start by:

```text
writing full Turkic morphology
adding another raw-soft-marker SP candidate
building a placeholder side-channel decoder
running tiny-LM before protected intrinsic gates pass
```

## Open Questions

These must be answered during prototype design:

```text
Should protected pieces share the normal learned vocabulary or use a separate
protected vocabulary range?

Should Turkish suffix tails after protected bases be segmented before or after
protected encoding?

What is the maximum protected UDS budget?

What fallback-rate threshold is acceptable for URL/file/code spans?

Which public tokenizer format can represent the final vocabulary without custom
stateful decoding?
```

## Decision

This spec is the next gate.

```text
If the smallest finite protected-aware prototype cannot beat SP64 intrinsic
behavior while staying near SP64 token pressure, plain SP64 remains the null
hypothesis and morphology should move to analysis/metadata or a later learned
hybrid.
```
