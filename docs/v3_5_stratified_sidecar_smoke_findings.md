# v3.5 Stratified Sidecar Smoke Findings

Date: 2026-06-19

## Status

The v3.4-trained 48K and 64K tokenizer models both passed a 5K protected
sidecar handoff smoke on the broader stratified sample.

Input:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_4_sample\stratified_480mb.txt
```

Models:

```text
C:\CELIK-GARDASH\models\tokenizer_v3_4\sp_unigram_48000_stratified_480mb.model
C:\CELIK-GARDASH\models\tokenizer_v3_4\sp_unigram_64000_stratified_480mb.model
```

## Gate Result

| Candidate | Exact | Sidecar failures | Fallback rate | Extra mask bytes/raw byte | Overall |
| --- | ---: | ---: | ---: | ---: | --- |
| v3.4 48K sidecar | 5000/5000 | 0 | 0.000018 | 0.006715 | PASS |
| v3.4 64K sidecar | 5000/5000 | 0 | 0.000019 | 0.006876 | PASS |

Both candidates passed:

```text
exact_roundtrip
valid_token_ids
sidecar_offsets
passthrough_route_invariants
fallback_rate
extra_mask_bytes_per_byte
lm_batch_windows
```

## Token Pressure

| Candidate | Tokens/raw byte | LM windows |
| --- | ---: | ---: |
| v3.4 48K sidecar | 0.190048 | 1832 |
| v3.4 64K sidecar | 0.183115 | 1765 |

On this broader/noisier stratified window, 64K is about:

```text
0.190048 - 0.183115 = 0.006933 tokens/raw byte lower
about 3.65% lower token pressure
```

## Protected Density

Both rows were evaluated on the same first 5K lines:

| Metric | Value |
| --- | ---: |
| raw bytes | 4910147 |
| protected spans | 32556 |
| protected bytes/raw byte | 0.030048 |

This is denser than the v3.3 real-mix fixture and is therefore a useful stress
smoke for sidecar/masking behavior.

## Reports

```text
artifacts/v3_5_sidecar_sp48k_stratified_480mb_5k_smoke.md
artifacts/v3_5_sidecar_sp64k_stratified_480mb_5k_smoke.md
```

## Interpretation

The protected sidecar contract survives the broader v3.4 models.

The v3.4 64K model is the stronger broad-corpus compression candidate.

The v3.4 48K model remains viable if the LLM architecture strongly prefers the
smaller embedding table, but the earlier v3.2 48K lead should be treated as an
integration-smoke result, not a final tokenizer result.

## Next

Before final selection:

```text
1. run fixed-byte tiny-LM BPB on v3.4 48K vs v3.4 64K
2. decide whether 64K's lower token pressure beats 48K's parameter saving
3. if one candidate is selected, build a v3.6 training-final candidate config
4. rerun full fixture validation and binary dataloader simulation for that candidate
```
