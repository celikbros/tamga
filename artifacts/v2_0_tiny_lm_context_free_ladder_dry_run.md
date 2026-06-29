# Tiny LM Bits-Per-Byte Probe

Config: `configs/v2_0_tiny_lm_context_free_ladder.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Dry run: `True`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 300 |
| eval_interval | 100 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| finite_protected_sp64_numeric_sp_floor | ok | 64630 | train | 16000 | 22819852 | 3630926 | 0.159113 | 1597 | 0.000440 |  |
| finite_protected_sp64_numeric_sp_floor | ok | 64630 | valid | 1994 | 2843294 | 465069 | 0.163567 | 208 | 0.000447 |  |
| finite_protected_sp64_numeric_sp_floor | ok | 64630 | test | 1998 | 2781995 | 457630 | 0.164497 | 357 | 0.000780 |  |
| finite_protected_pruned_ge070_nonword | ok | 64630 | train | 16000 | 22819852 | 3676752 | 0.161121 | 1597 | 0.000434 |  |
| finite_protected_pruned_ge070_nonword | ok | 64630 | valid | 1994 | 2843294 | 471456 | 0.165813 | 208 | 0.000441 |  |
| finite_protected_pruned_ge070_nonword | ok | 64630 | test | 1998 | 2781995 | 463752 | 0.166698 | 357 | 0.000770 |  |
| finite_protected_teacher_distilled_16000 | ok | 64630 | train | 16000 | 22819852 | 3938786 | 0.172603 | 1597 | 0.000405 |  |
| finite_protected_teacher_distilled_16000 | ok | 64630 | valid | 1994 | 2843294 | 503472 | 0.177073 | 208 | 0.000413 |  |
| finite_protected_teacher_distilled_16000 | ok | 64630 | test | 1998 | 2781995 | 494802 | 0.177859 | 357 | 0.000722 |  |
| finite_protected_teacher_distilled_2000 | ok | 64630 | train | 16000 | 22819852 | 4262250 | 0.186778 | 1597 | 0.000375 |  |
| finite_protected_teacher_distilled_2000 | ok | 64630 | valid | 1994 | 2843294 | 541646 | 0.190499 | 208 | 0.000384 |  |
| finite_protected_teacher_distilled_2000 | ok | 64630 | test | 1998 | 2781995 | 531939 | 0.191208 | 357 | 0.000671 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| dry_run | skipped | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  | no training run |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- Finite protected candidates use finite protected pieces plus UTF-8 byte fallback for protected spans.
- Marker-stripped finite protected candidates do not insert morphology markers at normal encode time.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the protocol caveats for the active experiment.
