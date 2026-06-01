# v1.8 Local LM Probe Split Materialization

Config: `configs/v1_8_local_lm_probe_split.toml`
Corpus: `data/train/claim_grade/celik_gold_clean_pilot.txt`
Seed: `20260601`
Split parts: `8:1:1`
Output dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split`

This report records the raw train/valid/test split for v1.8 fairness
work. Raw split files are private artifacts and must not be committed.

## Split Summary

| Split | Lines | Bytes | Chars | Words | Text path | Manifest path |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| train | 16000 | 21.76 MiB | 20840097 | 2603245 | `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/train.txt` | `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/train.manifest.jsonl` |
| valid | 2000 | 2.72 MiB | 2600563 | 324562 | `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/valid.txt` | `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/valid.manifest.jsonl` |
| test | 2000 | 2.65 MiB | 2540544 | 316529 | `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/test.txt` | `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/test.manifest.jsonl` |

## Next Use

Train-only SentencePiece baselines must use only:

`artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/train.txt`

Validation/test text files must not be used for SP vocabulary training.
