# v1.8 Tiny LM BPB Smoke Findings

Date: 2026-06-02

## Status

```text
two single-tokenizer 500-step smoke runs completed
SP 200-step iso-byte follow-up completed
custom 1258-step iso-byte follow-up completed
not full matrix
not final LLM evidence
```

## Runs

The user ran:

```powershell
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml --tokenizer custom_tr_morph_lossless
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml --tokenizer sp_bpe_64000_train_only
```

Both runs used:

```text
seq_len = 128
batch_size = 4
max_steps = 500
tokens_seen = 256000
```

## Results

500-step fixed-token smoke:

| Tokenizer | Train tokens/byte | Approx bytes seen | Best valid BPB | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| custom_tr_morph_lossless | 0.385619 | 663868 | 4.295575 | 4.312877 |
| sp_bpe_64000_train_only | 0.153393 | 1668920 | 3.729064 | 3.745292 |

Iso-byte follow-ups:

| Tokenizer checkpoint | Approx bytes seen | Best valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| custom step 500 | 663868 | 4.295575 | 4.312877 |
| sp_bpe_64000 step 200 | 667568 | 5.960158 | 5.984094 |
| sp_bpe_64000 step 500 | 1668920 | 3.729064 | 3.745292 |
| custom step 1258 | 1670292 | 2.943302 | 2.961183 |

## Fixed-Token View

At the same number of optimization steps and tokens seen, `sp_bpe_64000_train_only`
is better:

```text
valid BPB gap: custom - SP = 0.566511
test BPB gap:  custom - SP = 0.567585
```

This is a real warning for the current pure custom LM encoding.

## Byte-Exposure Caveat

The fixed-token run is not an iso-byte comparison.

Because `custom_tr_morph_lossless` produces many more tokens per byte,
`sp_bpe_64000_train_only` saw about 2.51x more raw text bytes in the same
number of training tokens:

```text
SP approx bytes seen / custom approx bytes seen = 1668920 / 663868 = 2.51x
```

At approximately the custom 500-step byte exposure, the closest SP run is the
200-step follow-up:

| Tokenizer checkpoint | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| custom step 500 | 663868 | 4.295575 | 4.312877 |
| sp_bpe_64000 step 200 | 667568 | 5.960158 | 5.984094 |

Under this byte-exposure view, custom is better at the same approximate raw-text
exposure.

At approximately the SP 500-step byte exposure, the closest custom run is the
1258-step follow-up:

| Tokenizer checkpoint | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| sp_bpe_64000 step 500 | 1668920 | 3.729064 | 3.745292 |
| custom step 1258 | 1670292 | 2.943302 | 2.961183 |

Under this byte-exposure view, custom is again better.

## Interpretation

The smoke result is mixed, not decisive:

```text
fixed-token / fixed-step view: SP wins
approx iso-byte view: custom wins
```

This is exactly the budget-confound advisors warned about. The current result
does not justify killing the morphology-aware path.

It also does not make the pure custom tokenizer LLM-ready. The custom tokenizer
needs about 2.5x more training tokens/steps to see the same raw byte exposure as
`sp_bpe_64000_train_only`, and its fixed-token context window covers much less
text.

## Decision

The v1.8 screening question is answered enough for planning:

```text
1. Pure custom has strong byte-exposure/data-efficiency signal.
2. Pure custom has serious token/context/compute pressure.
3. Full matrix training is not the next best use of time.
4. Move the design effort to v2.0 vocabulary/hybrid work.
```

Recommended v2.0 direction:

```text
morphology-aware tokenizer should not be thrown away
pure deterministic custom should not be handed to the LLM team as default
design a morphology-aware learned vocab / hybrid tokenizer to reduce tokens/byte
```

## Next Step

Stop v1.8 tiny-LM experimentation unless an advisor specifically asks for more.

Open v2.0 design around:

```text
custom morphology as pretokenization prior
learned vocab/merge design
byte fallback without excessive sequence pressure
protected-span preservation
```
