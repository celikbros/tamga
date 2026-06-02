# v1.8 Tiny LM Bits-Per-Byte Probe

Config: `configs/v1_8_tiny_lm_bpb_probe.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Dry run: `True`

This is an early screening probe, not final LLM tokenizer evidence.

## Model Config

| Setting | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| max_steps | 500 |
| eval_interval | 100 |
| d_model | 256 |
| n_layers | 4 |
| n_heads | 4 |

## Encoding Summary

| Tokenizer | Status | Vocab | Split | Lines | Bytes | Tokens | Tokens/byte | Fallback source tokens | Fallback source rate | Notes |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph_lossless | ok | 64000 | train | 16000 | 22819852 | 8799765 | 0.385619 | 181264 | 0.020599 |  |
| custom_tr_morph_lossless | ok | 64000 | valid | 1994 | 2843294 | 1183395 | 0.416206 | 30852 | 0.026071 |  |
| custom_tr_morph_lossless | ok | 64000 | test | 1998 | 2781995 | 1166895 | 0.419445 | 30665 | 0.026279 |  |
| sp_bpe_32000_train_only | ok | 32000 | train | 16000 | 22819852 | 3817078 | 0.167270 | 0 | 0.000000 |  |
| sp_bpe_32000_train_only | ok | 32000 | valid | 1994 | 2843294 | 479864 | 0.168770 | 0 | 0.000000 |  |
| sp_bpe_32000_train_only | ok | 32000 | test | 1998 | 2781995 | 471331 | 0.169422 | 0 | 0.000000 |  |
| sp_unigram_32000_train_only | ok | 32000 | train | 16000 | 22819852 | 3801974 | 0.166608 | 0 | 0.000000 |  |
| sp_unigram_32000_train_only | ok | 32000 | valid | 1994 | 2843294 | 481440 | 0.169325 | 0 | 0.000000 |  |
| sp_unigram_32000_train_only | ok | 32000 | test | 1998 | 2781995 | 472592 | 0.169875 | 0 | 0.000000 |  |
| sp_bpe_64000_train_only | ok | 64000 | train | 16000 | 22819852 | 3500397 | 0.153393 | 0 | 0.000000 |  |
| sp_bpe_64000_train_only | ok | 64000 | valid | 1994 | 2843294 | 445176 | 0.156571 | 0 | 0.000000 |  |
| sp_bpe_64000_train_only | ok | 64000 | test | 1998 | 2781995 | 436852 | 0.157028 | 0 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 64000 | train | 16000 | 22819852 | 3529781 | 0.154680 | 0 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 64000 | valid | 1994 | 2843294 | 452142 | 0.159020 | 0 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 64000 | test | 1998 | 2781995 | 444063 | 0.159620 | 0 | 0.000000 |  |
| hybrid_morph_pretok_unigram_64000_train_only | ok | 64000 | train | 16000 | 22819852 | 4175154 | 0.182961 | 0 | 0.000000 |  |
| hybrid_morph_pretok_unigram_64000_train_only | ok | 64000 | valid | 1994 | 2843294 | 530071 | 0.186428 | 0 | 0.000000 |  |
| hybrid_morph_pretok_unigram_64000_train_only | ok | 64000 | test | 1998 | 2781995 | 518201 | 0.186270 | 0 | 0.000000 |  |
| utf8_byte | ok | 257 | train | 16000 | 22819852 | 22835852 | 1.000701 | 0 | 0.000000 |  |
| utf8_byte | ok | 257 | valid | 1994 | 2843294 | 2845288 | 1.000701 | 0 | 0.000000 |  |
| utf8_byte | ok | 257 | test | 1998 | 2781995 | 2783993 | 1.000718 | 0 | 0.000000 |  |

## Training Results

| Tokenizer | Status | Vocab | Total params | Embedding params | Non-embedding params | Steps | Tokens seen | Approx bytes seen | Best valid BPB | Final valid BPB | Test BPB | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| dry_run | skipped | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |  |  | no training run |

## Interpretation Guardrails

- Compare only byte-normalized validation/test loss, not token perplexity.
- Custom uses a temporary train-only vocabulary plus UTF-8 byte fallback for unseen source tokens.
- This script does not make the tokenizer LLM-ready.
- A negative result should be read with the v1.8 protocol caveats.
