# v3.1 Special Token Decision Matrix

Date: 2026-06-18

## Why This Exists

The tokenizer package cannot become training-final until special token ids are
frozen. The current SP model has:

| Piece | Id |
| --- | ---: |
| `<unk>` | 0 |
| `<s>` | 1 |
| `</s>` | 2 |

There is no `<pad>` id in the current SP model.

## Decision Options

### Option A: Keep SP Meta Ids, Add Control Tokens After Byte Fallback

Id layout:

```text
0..63999      SentencePiece ids
64000..64255  UTF-8 byte fallback ids
64256..       LLM control/chat/tool tokens
```

Example:

| Token | Proposed id |
| --- | ---: |
| `<unk>` | 0 |
| `<bos>` alias for `<s>` | 1 |
| `<eos>` alias for `</s>` | 2 |
| `<pad>` | 64256 |
| `<system>` | 64257 |
| `<user>` | 64258 |
| `<assistant>` | 64259 |
| `<thinking>` | 64260 |
| `</thinking>` | 64261 |
| `<answer>` | 64262 |
| `</answer>` | 64263 |
| `<tool_call>` | 64264 |
| `<tool_result>` | 64265 |

Pros:

```text
keeps current SP model valid
no id remapping of existing text tokens
safe for current smoke artifacts
fastest path to integration
```

Cons:

```text
<pad> is not id 0
LLM embedding size grows beyond 64256
requires wrapper/config handling for control tokens
```

Recommendation:

```text
Best for short-term integration smoke.
```

### Option B: Retrain Final SP With Full Special Tokens Embedded

Id layout is decided at SentencePiece training time.

Pros:

```text
single tokenizer artifact
cleaner long-term train/inference parity
can set pad/bos/eos/unk policy deliberately before main training
```

Cons:

```text
requires tokenizer retraining
invalidates current v3.0 smoke ids
must rerun all sidecar/fertility/BPB checks
```

Recommendation:

```text
Best for final training-ready tokenizer, if schedule allows.
```

### Option C: Remap Existing SP Meta Ids In The LLM Wrapper

Example:

```text
pretend <pad> is id 0 and move <unk> elsewhere in wrapper logic
```

Pros:

```text
may match a preferred LLM convention
```

Cons:

```text
high mismatch risk
training/inference bugs likely
breaks the "single source of truth" property
```

Recommendation:

```text
Avoid.
```

## Current Internal Recommendation

Use Option A for continued integration smoke, but do not call it final.

For main Gardaş training, decide between:

```text
Option A if the LLM stack accepts <pad> outside id 0.
Option B if the LLM stack requires pad/unk/bos/eos to be embedded in the tokenizer artifact.
```

Option C should be rejected unless there is an unavoidable compatibility reason.

## Question For LLM Architecture Team Later

When we are ready to ask them, the question should be:

```text
Can Gardaş accept <pad> outside id 0 and keep <unk>=0, <bos>=1, <eos>=2?

If yes, we keep the current SP model id layout and append control tokens after
byte fallback.

If no, we retrain the final tokenizer with a new special-token layout before
main training.
```
