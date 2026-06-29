# v3.3 Full Real-Mix Smoke Closeout

Date: 2026-06-19

## Status

The v3.2 48K integration-smoke candidate has now passed the full real-mix
fixture gate.

Candidate:

```text
sp48k_protected_passthrough_sidecar_controls128
```

Input:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_0\real_mix_60k_sample.txt
```

Output fixture:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_3_smoke\sp48k_real_mix_full
```

## Fixture Summary

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| raw bytes | 44351801 |
| tokens | 7350435 |
| tokens/raw byte | 0.165730 |
| eos tokens | 40388 |
| fallback tokens | 336 |
| fallback rate | 0.000046 |
| masked tokens | 278873 |
| masked token rate | 0.037940 |
| protected spans | 149999 |
| protected bytes | 682931 |
| SP alignment mismatches | 0 |
| max token id | 48244 |
| effective vocab size | 48384 |

## Route Coverage

| Route | Spans |
| --- | ---: |
| `numeric_like` | 127588 |
| `file_like` | 10309 |
| `apostrophe_surface` | 7579 |
| `non_turkish_latin_word` | 3228 |
| `greek_word` | 606 |
| `arabic_word` | 391 |
| `percent_encoded` | 171 |
| `uzbek_apostrophe_word` | 69 |
| `cyrillic_word` | 50 |
| `azerbaijani_word` | 8 |

## Validation

Fixture validation:

```text
PASS
```

Key checks:

| Check | Value |
| --- | ---: |
| `tokens.bin` bytes | 29401740 |
| `loss_mask.bin` bytes | 7350435 |
| index rows | 40388 |
| sidecar rows | 40388 |
| max token id | 48244 |
| effective vocab size | 48384 |

Packed dataloader simulation:

```text
PASS
```

| Metric | Value |
| --- | ---: |
| seq_len | 128 |
| batch_size | 4 |
| windows | 57425 |
| full batches | 14356 |
| train label positions | 7071403 |
| masked label positions | 278869 |
| byte fallback tokens | 336 |
| control tokens in raw fixture | 0 |

## Reports

```text
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_3_tokenized_corpus_smoke_sp48k_real_mix_full.md
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_3_smoke_fixture_validation_sp48k_real_mix_full.md
C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_3_binary_dataloader_simulation_sp48k_real_mix_full.md
```

## Interpretation

This closes the v3.3 full real-mix smoke gate for the current 48K integration
candidate.

The package is stronger than the earlier 1K/5K fixtures because it covers the
entire real-mix sample and all route classes observed in that sample.

This still does not make the tokenizer production-final. It means the tokenizer
side has a robust integration candidate ready for future LLM-engine smoke.

## Remaining Before Training-Final

```text
1. LLM engine consumes the fixture successfully.
2. Special-token policy is accepted or changed.
3. Final decision: keep 48K sample-trained model or retrain on a larger/full corpus.
4. If retrained, rerun this full smoke gate.
5. If final, freeze config status as training_final.
```
