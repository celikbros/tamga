# v2.1 Passthrough Sidecar Operation Simulation

Input: `artifacts/private/v2_1_real_mix/real_mix_smoke.txt`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Max lines per split/file: `all`
Private worst-case samples: `artifacts/private/v2_1_sidecar_operation_simulation_real_mix_smoke.samples.jsonl`

This audit simulates a downstream training-mask operation for the
`sp64_protected_passthrough_sidecar` contract. Protected spans are exact
byte ranges in the sidecar, while model tokens may straddle span edges.
The safe token-index policy maps each protected byte span to every
overlapping SP token, conservatively over-masking boundary tokens.

## Split Summary

| Split | Lines | Raw bytes | Protected spans | Protected bytes | Protected bytes/raw byte | Conservative mask bytes | Extra mask bytes | Extra mask bytes/raw byte | Extra/protected byte | Edge-aligned span rate | Crossing span rate | Avg tokens/span | Max extra bytes/span |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `real_mix_smoke` | 100 | 295821 | 995 | 2665 | 0.009009 | 3703 | 1038 | 0.003509 | 0.389493 | 0.049246 | 0.950754 | 1.428141 | 4 |

## Route Summary

| Route | Spans | Protected bytes | Summed extra bytes | Extra/protected byte | Edge-aligned span rate | Crossing span rate | Avg tokens/span | Max extra bytes/span | Top surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `numeric_like` | 962 | 2393 | 1009 | 0.421646 | 0.050936 | 0.949064 | 1.347193 | 4 | `5G`:51, `2`:44, `1`:44, `30`:32, `3`:27, `2026`:25, `20`:20, `4`:20 |
| `file_like` | 21 | 154 | 21 | 0.136364 | 0.000000 | 1.000000 | 3.904762 | 1 | `pic.twitter.com`:4, `E.A`:4, `A.Ş`:3, `T.T`:2, `çıkarıldı.Yapılan`:1, `M.Ç`:1, `A.C`:1, `S.K`:1 |
| `apostrophe_surface` | 12 | 118 | 12 | 0.101695 | 0.000000 | 1.000000 | 3.583333 | 1 | `İran'la`:3, `Hatemu'l`:2, `Cumhurbaşkanı'mızın`:1, `İHA'larla`:1, `Hürmüz'le`:1, `6'ncı`:1, `Merkezi'mize`:1, `Guterres'le`:1 |

## Gate

Use this audit to decide whether byte-span metadata is operationally
safe enough for training-time masking/redaction workflows.

- `Extra mask bytes/raw byte` estimates the global data lost by
  conservative token over-masking.
- High route-specific `Extra/protected byte` suggests selective
  pre-splitting for that route class before considering global
  pre-splitting.
- This does not test exact constrained decoding/copy. If that becomes a
  base-model requirement, use a pre-split or route-selective aligned
  variant.
