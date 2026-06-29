# Tokenizer Team Response: LLM Phase 2 Direction

Date: 2026-06-20

LLM mimari ekibine merhaba,

Faz 2 yonlendirmenizi kabul ediyoruz.

## Durum

v3.7 SP64K pretraining contract:

```text
CLOSED / PASS
```

Sizin tarafta `GardashForCausalLM` smoke'unun gecmis olmasi sonraki adimi net
yapti:

```text
production offline corpus tokenization path
```

## 1. Production tokenize_corpus.py

Eklendi:

```text
scripts/tokenize_corpus.py
```

Ozellikler:

```text
tokens.bin uint32_le
loss_mask.bin uint8
index.jsonl
sidecar.jsonl
manifest.json
checksums.json
deterministic ordered writer
multiprocessing support
```

Smoke:

```text
workers=1 vs workers=2 payload checksums identical
fixture validation PASS
binary dataloader simulation PASS
```

Runbook:

```text
docs/v3_8_production_tokenize_corpus_runbook.md
```

## 2. Rust/C++ Direction

Katiliyoruz:

```text
Rust/C++ port'a simdi kosmuyoruz.
```

Offline tokenization tek seferlik maliyet. Python multiprocessing yolu Faz 2
icin yeterli olgunluga getiriliyor. Rust/C++ serving/inference tarafina ve
final freeze sonrasina ayrilmali.

## 3. SP Retrain Siralamasi

Katiliyoruz:

```text
Final corpus donmadan SP retrain yapmayacagiz.
```

Sizden bekledigimiz final-corpus girdileri:

```text
donmus corpus path/manifest
dedup durumu
dil/domain karisimi
normalizasyon karari
v3.7 registry degismedi teyidi
```

Retrain protokolu:

```text
docs/v3_8_final_sp_retrain_protocol.md
```

## 4. Eksik Denen Dokumanlar

Bu dokumanlar ana repoda ve CELIK-GARDASH tarafinda mevcut:

```text
docs/v3_8_final_sp_retrain_protocol.md
docs/v3_7_sidecar_schema_freeze_and_boundary_branch.md
docs/v3_7_control_token_wrapper_spec.md
```

CELIK-GARDASH kopyalari:

```text
C:\CELIK-GARDASH\docs\TOKENIZER_V3_8_FINAL_SP_RETRAIN_PROTOCOL.md
C:\CELIK-GARDASH\docs\TOKENIZER_V3_7_SIDECAR_SCHEMA_FREEZE_AND_BOUNDARY_BRANCH.md
C:\CELIK-GARDASH\docs\TOKENIZER_V3_7_CONTROL_TOKEN_WRAPPER_SPEC.md
```

## 5. Final Corpus Mixed-Corpus Hazirligi

Turkish-only varsaymayacagiz.

Final corpus EN/kod icerirse:

```text
SP training mix buna gore kurulacak
identity normalization korunacak, aksi birlikte kararlastirilmazsa
EN/code fertility + fallback ayri raporlanacak
file/package/version/code-like route density ayrica izlenecek
```

## Tokenizer Tarafinda Sonraki Is

Final corpus manifest gelene kadar tokenizer tarafinda:

```text
1. tokenize_corpus.py full-corpus hazirligini sertlestirme
2. checksum/manifest/validation raporlarini standardize etme
3. fertility/canary rapor komutlarini final retrain protokolune baglama
```

Final corpus geldikten sonra:

```text
v3.8 final SP64K retrain
fertility report
sidecar smoke
fixture validation
binary dataloader simulation
LLM engine smoke
freeze decision
```
