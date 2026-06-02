# v1.8 Tiny LM BPB Smoke Findings

Date: 2026-06-02

## Status

```text
two single-tokenizer 500-step smoke runs completed
SP 200-step iso-byte follow-up completed
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

| Tokenizer | Train tokens/byte | Approx bytes seen | Best valid BPB | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| custom_tr_morph_lossless | 0.385619 | 663868 | 4.295575 | 4.312877 |
| sp_bpe_64000_train_only | 0.153393 | 1668920 | 3.729064 | 3.745292 |

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

At approximately the custom 500-step byte exposure, the closest SP run is
the 200-step follow-up:

| Tokenizer checkpoint | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| custom step 500 | 663868 | 4.295575 | 4.312877 |
| sp_bpe_64000 step 200 | 667568 | 5.960158 | 5.984094 |

Under this byte-exposure view, custom is better at the same approximate raw-text
exposure.

## Interpretation

The smoke result is mixed, not decisive:

```text
fixed-token / fixed-step view: SP wins
approx iso-byte view: custom wins
```

This is exactly the budget-confound advisors warned about. The current result
does not justify running the full matrix yet, and it does not justify killing
the morphology-aware path.

## Decision

Use a narrower iso-byte follow-up before any full matrix:

```text
1. Completed: run SP at 200 steps near custom 500-step byte exposure.
2. Next optional check: run custom longer, around 1258 steps, to match SP 500-step byte exposure.
```

Do not run the full matrix yet. The mixed result says the tokenizer question is
mostly budget-sensitive and should inform v2.0 vocabulary/hybrid design.

## Next Command

```powershell
python scripts/run_tiny_lm_bpb_probe.py configs\v1_8_tiny_lm_bpb_probe.toml `
  --tokenizer custom_tr_morph_lossless `
  --max-steps 1258 `
  --report-out artifacts\v1_8_tiny_lm_bpb_probe_custom_1258steps.md `
  --output-dir artifacts\private\v1_8_tiny_lm_bpb_probe_custom_1258steps
```

This is longer than the first custom smoke. Run it only if the extra local time
is acceptable.
