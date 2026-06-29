# v3.7 Control-Token Wrapper Spec

Date: 2026-06-20

## Status

This is the reference contract for v3.7 control-token handling.

It answers the LLM team's request:

```text
SP only knows ids 0..64255.
Control ids 64256+ are wrapper-managed.
Training and inference must use the same mapping.
```

Reference implementation:

```text
scripts/reference_v3_7_control_wrapper.py
```

Canonical config:

```text
configs/tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json
```

## ID Layout

```text
0..63999       SentencePiece ids
64000..64255   UTF-8 byte fallback ids
64256..64383   wrapper control-token reserve
```

Current effective vocab size:

```text
64384
```

## Assigned Tokens

| Token | Id |
| --- | ---: |
| `<unk>` | 0 |
| `<bos>` alias `<s>` | 1 |
| `<eos>` alias `</s>` | 2 |
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

Reserved but unassigned:

```text
64266..64383
```

## Encode Contract

There are two modes.

### Raw Text Encode

Raw user text must not activate wrapper control strings.

Example:

```text
raw text: "<user>"
```

is encoded as ordinary text pieces, not as id `64258`.

Use this path for:

```text
pretraining raw text
user-provided content
documents
corpus text
```

### Trusted Template Encode

Trusted chat/template code may inject control ids.

Example:

```text
<user>Merhaba<assistant>
```

is encoded as:

```text
64258 + SP("Merhaba") + 64259
```

Only trusted formatting code should call this mode.

## Decode Contract

Decoding ids must:

```text
1. decode SP id runs through SentencePiece
2. decode byte fallback ids by subtracting byte_fallback_start
3. emit wrapper control strings for assigned control ids
4. reject ids outside [0, 64384)
```

The reference wrapper decodes a mixed stream such as:

```text
64258 SP("A") 64033 64259
```

as:

```text
<user>A!<assistant>
```

## EOS And Padding

`<eos>` is an alias for SP `</s>` id `2`.

`<pad>` is wrapper id `64256`.

Do not remap:

```text
<unk> remains 0
```

## Reference Commands

Trusted template roundtrip:

```powershell
python scripts\reference_v3_7_control_wrapper.py `
  --config configs\tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json `
  --text "<user>Merhaba<assistant>" `
  --roundtrip
```

Raw text path:

```powershell
python scripts\reference_v3_7_control_wrapper.py `
  --config configs\tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json `
  --raw-text "<user>" `
  --roundtrip
```

The raw-text command must not collapse `"<user>"` to id `64258`.

## Production Guidance

The Python wrapper is the behavior reference, not the final serving
implementation.

Production may port this to Rust/C++/the LLM engine, but the id mapping and
raw-vs-template distinction must remain identical.
