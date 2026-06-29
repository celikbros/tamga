# v3.1 Special Token Registry Draft

Date: 2026-06-14

## Status

Draft. Do not use for main LLM training until frozen.

## Current SentencePiece Meta Tokens

The current v3.0 integration model is:

```text
sp_unigram_64000_train_only.model
```

Current SP meta-token assumption:

| Token | Current id | Notes |
| --- | ---: | --- |
| `<unk>` | 0 | SentencePiece unknown id |
| `<s>` | 1 | SentencePiece BOS id |
| `</s>` | 2 | SentencePiece EOS id |

This means `<pad> id 0` is not compatible with the current artifact unless the
tokenizer is retrained or a wrapper-level id remap is explicitly introduced.

## Open Decision

Choose one policy before LLM training:

### Option A: Embed Special Tokens In The Tokenizer Artifact

Retrain or patch the SentencePiece model with final special symbols.

Benefits:

```text
single artifact
less training/inference mismatch risk
standard tokenizer loading path
```

Costs:

```text
requires final token list before training
requires model regeneration if chat/tool protocol changes
```

### Option B: Manage Chat/Tool Tokens In Wrapper Config

Keep the SP model as lexical text tokenizer and reserve ids outside the SP range.

Benefits:

```text
chat/tool protocol can evolve without SP retraining
clear separation between lexical text and control tokens
```

Costs:

```text
requires strict tokenizer_config.json
training and inference must share exactly the same id map
more implementation responsibility on the LLM stack
```

## Recommended Direction

For Gardaş, prefer a frozen `tokenizer_config.json` that explicitly records:

```text
sp_model_path
sp_vocab_size
byte_fallback_offset
byte_fallback_size
special_tokens
sidecar_schema_version
```

The special token policy can still be Option A or B, but it must be expressed
in one canonical config file consumed by both training and inference.

## Candidate Special Tokens To Decide

LLM team requested:

```text
<pad>
<eos>
<bos>
<system>
<user>
<assistant>
<thinking>
</thinking>
<answer>
</answer>
<tool_call>
<tool_result>
```

Tokenizer team note:

```text
Do not silently alias <eos> and </s> unless the LLM team explicitly accepts it.
Do not assign <pad> to id 0 while <unk> is id 0.
Do not start training with one special-token map and serve with another.
```

## Freeze Gate

Special token registry is frozen only after:

```text
LLM architecture accepts ids
tokenizer package includes tokenizer_config.json
unit test verifies encode/decode/control-token ids
dataloader smoke reads the same config
generation/inference code reads the same config
```
