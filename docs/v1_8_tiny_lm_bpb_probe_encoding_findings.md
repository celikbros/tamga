# v1.8 Tiny LM BPB Encoding Findings

Date: 2026-06-02

## Status

```text
full encoding dry-run completed
no LM training run yet
screening only
not final LLM tokenizer evidence
```

## Artifacts

```text
artifacts/v1_8_tiny_lm_bpb_probe.md
artifacts/private/v1_8_tiny_lm_bpb_probe/encoded_stats.jsonl
```

## Key Result

The dry-run succeeded for all configured tokenizers.

The custom tokenizer now uses UTF-8 byte fallback for source tokens outside the
temporary train-only custom vocabulary. This avoids destructive `<unk>` loss,
but it increases token count substantially.

## Encoding Summary

Validation split:

| Tokenizer | Vocab | Valid tokens/byte | Fallback source rate |
| --- | ---: | ---: | ---: |
| custom_tr_morph_lossless | 64000 | 0.416206 | 0.026071 |
| sp_bpe_32000_train_only | 32000 | 0.168770 | 0.000000 |
| sp_unigram_32000_train_only | 32000 | 0.169325 | 0.000000 |
| sp_bpe_64000_train_only | 64000 | 0.156571 | 0.000000 |
| sp_unigram_64000_train_only | 64000 | 0.159020 | 0.000000 |
| hybrid_morph_pretok_unigram_64000_train_only | 64000 | 0.186428 | 0.000000 |
| utf8_byte | 257 | 1.000701 | 0.000000 |

Test split:

| Tokenizer | Vocab | Test tokens/byte | Fallback source rate |
| --- | ---: | ---: | ---: |
| custom_tr_morph_lossless | 64000 | 0.419445 | 0.026279 |
| sp_bpe_32000_train_only | 32000 | 0.169422 | 0.000000 |
| sp_unigram_32000_train_only | 32000 | 0.169875 | 0.000000 |
| sp_bpe_64000_train_only | 64000 | 0.157028 | 0.000000 |
| sp_unigram_64000_train_only | 64000 | 0.159620 | 0.000000 |
| hybrid_morph_pretok_unigram_64000_train_only | 64000 | 0.186270 | 0.000000 |
| utf8_byte | 257 | 1.000718 | 0.000000 |

## Interpretation

This dry-run is a serious warning for LM use of the current pure custom
encoding.

`custom_tr_morph_lossless` preserves morphology/protected-span behavior, but its
temporary vocabulary plus byte fallback creates much higher sequence pressure
than the strongest SP baselines:

```text
valid custom / sp_bpe_64000 tokens-per-byte ratio: about 2.66x
test custom / sp_bpe_64000 tokens-per-byte ratio: about 2.67x
```

With a fixed token context, this means the custom tokenizer sees much less raw
text context per training example. A tiny LM BPB result must be interpreted with
that context-pressure penalty in mind.

## Decision

Do not run the full tokenizer training matrix first.

Run a narrow training smoke instead:

```text
custom_tr_morph_lossless
sp_bpe_64000_train_only
```

If the custom run is clearly unstable, too slow, or far worse in BPB, stop and
move the next design effort toward v2.0 hybrid/vocabulary design instead of
spending time on the full matrix.

## Next Commands

Custom smoke:

```powershell
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml --tokenizer custom_tr_morph_lossless
```

Strong SP smoke:

```powershell
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml --tokenizer sp_bpe_64000_train_only
```

After those two outputs, compare validation/test bits-per-byte and decide
whether a full matrix is worth running.
