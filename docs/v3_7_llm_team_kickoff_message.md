# v3.7 Tokenizer Integration Kickoff Message To LLM Team

Date: 2026-06-19

LLM ekibine merhaba,

Tokenizer tarafında v3.x hattını yeni bir entegrasyon adayına kadar getirdik.
Su an size onerdigimiz aday:

```text
sp64k_stratified_protected_passthrough_sidecar_controls128
```

Bu aday production-final degil. Ama LLM motoru ve dataloader entegrasyon smoke
testleri icin hazir.

## Neyi Kullanacaksiniz

Model:

```text
C:\CELIK-GARDASH\models\tokenizer_v3_4\sp_unigram_64000_stratified_480mb.model
C:\CELIK-GARDASH\models\tokenizer_v3_4\sp_unigram_64000_stratified_480mb.vocab
```

Ana config:

```text
C:\CELIK-GARDASH\configs\tokenizer_v3_0\tokenizer_config.v3_7.sp64k_stratified_integration_candidate.json
```

Hazir 50K binary fixture:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_7_smoke\sp64k_stratified_50k
```

Bu fixture icinde:

```text
tokens.bin      uint32 little-endian token ids
loss_mask.bin   uint8; 1=train, 0=protected-span mask
index.jsonl     line -> token offset index
sidecar.jsonl   protected byte/char spans
manifest.json   machine-readable summary
```

## ID Sozlesmesi

```text
0..63999       SentencePiece ids
64000..64255   UTF-8 byte fallback ids
64256..64383   wrapper-level control-token reserve
```

Onemli id'ler:

```text
<unk> = 0
<bos> alias <s> = 1
<eos> alias </s> = 2
<pad> = 64256
<system> = 64257
<user> = 64258
<assistant> = 64259
<thinking> = 64260
</thinking> = 64261
<answer> = 64262
</answer> = 64263
<tool_call> = 64264
<tool_result> = 64265
```

Lutfen ozellikle su varsayimi dogrulayin:

```text
<pad> id 64256 olabilir mi?
<unk> id 0 olarak kalabilir mi?
```

Biz <pad>'i 0 yapmadik, cunku SentencePiece modelinde id 0 zaten <unk>.

## Neden 64K Aday

48K entegrasyon smoke daha once basariliydi, fakat daha dar bir real-mix ornegi
uzerinden geliyordu. Daha genis v3.4 stratified orneginde 64K daha iyi cikti.

v3.6 fixed-byte tiny-LM sonucu:

| Candidate | Test tokens/raw byte | Test BPB |
| --- | ---: | ---: |
| v3.4-trained 48K sidecar | 0.192455 | 2.386732 |
| v3.4-trained 64K sidecar | 0.185791 | 2.340260 |

64K hem daha az token uretti hem de byte-normalized BPB'de kazandi.

## Tokenizer Tarafinda Gecen Testler

v3.7 50K fixture:

```text
lines: 50000
raw bytes: 48942124
tokens: 9060436
tokens/raw byte: 0.185126
fallback rate: 0.000591
masked token rate: 0.063485
protected spans: 319592
SP alignment mismatches: 0
max token id: 64243
effective vocab size: 64384
```

Gecen kapilar:

```text
tokenizer config validation: PASS
fixture validation: PASS
binary dataloader simulation: PASS
```

Tokenizer tarafindaki dataloader simulasyonu:

```text
batch_size=4
seq_len=128
full_batches=17696
train label positions=8485153
masked label positions=575199
byte fallback tokens=5352
control tokens in fixture=0
failures: none
warnings: none
```

## Sizden Beklenen Smoke Testleri

Lutfen kendi LLM motorunuzda su testleri calistirin:

1. `tokens.bin` dosyasini `uint32 little-endian` olarak okuyun.
2. `loss_mask.bin` dosyasini `uint8` olarak okuyun.
3. Token ve mask uzunluklarinin esit oldugunu dogrulayin.
4. Tum token id'lerinin `0 <= id < 64384` araliginda oldugunu dogrulayin.
5. Packed causal-LM batch olusturun:

```text
batch_size=4
seq_len=128
```

6. Label shift ve loss mask hizalamasini kontrol edin.
7. `<pad>=64256` ile tail padding yapin.
8. `sidecar.jsonl` dosyasini hot path'e sokmadan, metadata olarak okuyabildiginizi dogrulayin.
9. Protected-span maskleme operasyonunda byte-offset sidecar sozlesmesinin sizin icin yeterli olup olmadigini kontrol edin.

## Karar Bekledigimiz Noktalar

Ana egitime basmadan once sizden net cevap bekledigimiz noktalar:

```text
1. <pad>=64256 kabul mu?
2. <unk>=0 kabul mu?
3. uint32 tokens + uint8 loss_mask formatiniz icin uygun mu?
4. byte-offset passthrough sidecar protected-span ihtiyaclariniz icin yeterli mi?
5. 64K embedding tablosu mimariniz icin kabul edilebilir mi?
6. Bu 480MB stratified-trained SP model ile experimental training smoke'a
   gecelim mi, yoksa once daha buyuk/final corpus slice uzerinde SP retrain mi
   istiyorsunuz?
```

## Bizim Onerimiz

LLM-side integration smoke icin v3.7 SP64K adayini kullanin.

Irreversible ana pretraining'e henuz basmayin. Once yukaridaki engine/dataloader
smoke testlerini gecirelim. Eger sizin motor tarafinda da temiz gecerse,
sonraki karar:

```text
v3.7 SP64K ile experimental LLM training smoke
veya
final corpus slice uzerinde SP64K retrain
```

olacak.

## Referans Dosyalar

```text
C:\CELIK-GARDASH\docs\TOKENIZER_V3_7_CURRENT_STATUS.md
C:\CELIK-GARDASH\docs\TOKENIZER_V3_7_SP64K_INTEGRATION_CANDIDATE_SMOKE_FINDINGS.md
C:\CELIK-GARDASH\docs\TOKENIZER_V3_6_STRATIFIED_FIXED_BYTE_BPB_FINDINGS.md
```
