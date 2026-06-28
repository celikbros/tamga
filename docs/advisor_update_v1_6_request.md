# Danisman Degerlendirme Istegi: v1.5 Sonuclari ve v1.6 Plani

Tarih: 2026-05-30

Repo:

```text
https://github.com/celikbros/tamga
```

## 1. Kisa Ozet

`Tamga`, Turkce merkezli morphology-aware tokenizer arastirma
prototipidir.

Ana hedefimiz:

```text
Turkce gibi eklemeli dillerde morfolojik sinirlari, standart subword
tokenizerlara gore daha bilincli koruyan bir tokenizer cekirdegi kurmak.
```

Proje su anda production tokenizer degildir. Su anki asama:

```text
olculebilir arastirma prototipi
+ baseline karsilastirma
+ multilingual do-no-harm smoke testleri
+ v1.6 routing guard plani
```

Danismanlardan beklentimiz:

```text
Bu yolda metodolojik veya mimari bir hata yapiyor muyuz?
Hangi alanlara dokunmali, hangilerine dokunmamaliyiz?
v1.6 do-no-harm plani dogru mu?
```

## 2. Su Ana Kadar Ne Yaptik?

### Deterministik Turkce Cekirdek

Mevcut tokenizer:

- kelime baslangici marker'i kullanir: `▁`
- Turkce ek zincirlerini deterministik olarak ayirir
- apostrof sonrasi Turkce ekleri ayirir
- surface-stem yaklasimi kullanir
- informal yuzey bicimleri normalize etmeden parcalar
- code/file/date/number benzeri spanlari korumaya calisir

Ornek:

```text
Geldim. -> ▁Gel +di +m .
Türkiye'den -> ▁Türkiye ' +den
Gelicem -> ▁Gel +icem
README.md'yi -> ▁README.md ' +yi
```

Onemli prensip:

```text
Tokenizer normalizer degildir. Yuzey metni korumaya calisir.
```

### Frozen Regression

Frozen cekirdek eval:

```text
data/eval/tr_gold_expanded.tsv
```

Guncel sonuc:

```text
50/50 exact match
f1 = 1.0000
```

Bu set artik cekirdek regression olarak korunuyor.

### Challenge Eval

Challenge/dev set:

```text
data/eval/tr_challenge.tsv
```

Guncel sonuc:

```text
44/108 exact match
boundary_f1 = 0.9220
```

Bu seti final benchmark olarak degil, hata analizi ve karar seti olarak
kullaniyoruz.

## 3. v1.5 Baseline Karsilastirmalari

v1.5'te tokenizerimizi su referanslarla karsilastirdik:

- toy BPE
- SentencePiece BPE
- SentencePiece Unigram
- Qwen tokenizer
- Mistral tokenizer
- Meta LLaMA tokenizer
- Unicode character baseline

### Expanded Regression Sonuclari

Dataset:

```text
data/eval/tr_gold_expanded.tsv
```

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.7438 | 1.0000 | 50/50 |
| toy_bpe_1000 | 2.7438 | 0.6277 | 1/50 |
| sp_bpe | 2.7273 | 0.6263 | 1/50 |
| sp_unigram | 3.0744 | 0.6325 | 0/50 |
| qwen | 3.0661 | 0.3317 | 0/50 |
| llama | 2.9008 | 0.3259 | 0/50 |
| mistral | 4.3306 | 0.5423 | 0/50 |
| unicode_char | 7.5041 | 0.4947 | 0/50 |

Yorumumuz:

```text
Ayni veya benzer token maliyetinde, Turkce morfolojik boundary korumasi
bizim tokenizerda cok daha yuksek.
```

Ancak bu sonuc kucuk ve kontrollu eval uzerinde.

### Challenge Sonuclari

Dataset:

```text
data/eval/tr_challenge.tsv
```

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 | 44/108 |
| toy_bpe_1000 | 2.7572 | 0.6610 | 0/108 |
| sp_bpe | 2.7807 | 0.6497 | 0/108 |
| sp_unigram | 2.9321 | 0.6225 | 0/108 |
| qwen | 2.8590 | 0.3511 | 0/108 |
| llama | 2.5744 | 0.3501 | 0/108 |
| mistral | 3.9426 | 0.5463 | 0/108 |
| unicode_char | 6.6214 | 0.4949 | 0/108 |

Yorumumuz:

```text
Custom tokenizer challenge sette mukemmel degil, ama boundary F1 acisindan
referans tokenizerlardan belirgin sekilde yuksek.
```

Bu bulgu bizi cesaretlendiriyor, ama production iddiasi icin yeterli degil.

## 4. Ingilizce ve Multilingual Smoke Testleri

Turkce merkezli tokenizerin baska dilleri bozup bozmadigini gormek icin smoke
testler ekledik.

### English Smoke

Dataset:

```text
data/eval/en_smoke.tsv
```

Sonuc:

```text
exact_match = 5/10
boundary_f1 = 0.7949
avg_tokens/word = 1.2692
```

Iyi:

- duz Ingilizce buyuk olcude geciyor
- basit code-like ornekler iyi korunuyor

Sorunlu:

```text
Don't -> ▁Don ' +t
John's -> ▁John ' +s
We're -> ▁We ' +re
transformers>=4.40 -> ▁transformers > = ▁4.40
data -> ▁da +ta
code -> ▁co +de
```

### Multilingual Smoke

Dataset:

```text
data/eval/multilingual_smoke.tsv
```

Sonuc:

```text
exact_match = 8/20
boundary_f1 = 0.6775
avg_tokens/word = 2.8493
```

Iyi:

```text
kazakh_cyrillic = 1.0000
kyrgyz_cyrillic = 1.0000
russian = 1.0000
tatar_cyrillic = 1.0000
uzbek_latin = 1.0000
```

Sorunlu:

```text
Azerice: adım -> ad +ım, Bakıda -> Bak +ı +da
Fransizca/Italyanca: d'Istanbul, L'amico apostrof hatalari
Almanca/Ispanyolca: Straße, niño, Bogotá gibi non-Turkish Latin harfler bolunuyor
Arapca/Yunanca: karakter karakter fallback oluyor
```

## 5. Su Anki Ana Riskler

### R1: Turkce Kurallarin Baska Dillere Sizmasi

En buyuk risk bu.

Ornek:

```text
Azerice Bakıda -> Bak +ı +da
Ingilizce data -> da +ta
Fransizca d'Istanbul -> d ' +Istanbul
```

Bu, Turkce icin yararli olan kurallarin multilingual ortamda zararli hale
gelebilecegini gosteriyor.

### R2: Kucuk Eval Setlerine Overfit

Expanded set 50/50 guzel ama kucuk ve kontrollu.

Challenge ve smoke setler daha cok hata gosteriyor. Bu iyi; ancak production
iddiasi icin daha buyuk, daha dogal ve tercihen heldout eval gerekiyor.

### R3: Boundary F1 Tek Basina Yeterli Degil

Boundary F1 morfolojik sinir uyumunu olcuyor. Ama LLM kalitesi icin:

- token fertility
- protected span break rate
- byte/fallback rate
- downstream veya small-LM deneyi
- hidden/heldout eval

gerekir.

### R4: Surface Stem vs Lemma

Mevcut sistem surface-stem koruyor:

```text
kitabımdan -> ▁Kitab +ım +dan
kitaplarımdan -> ▁Kitap +lar +ım +dan
```

Bu tokenizer icin lossless ve pratik, ama lemma-level paylasimi azaltabilir.
Bu karar v2.0 MorphBPE veya metadata tasariminda tekrar tartisilmali.

## 6. v1.6 Plani

v1.6'da hedefimiz yeni Turkce morfoloji kurali yazmak degil.

Hedef:

```text
do-no-harm routing fixes
```

Yani baska dil veya teknik span geldiyse Turkce morfolojiye zorla sokmayalim.

Plan dosyasi:

```text
docs/v1_6_do_no_harm_routing_plan.md
```

Onerilen sira:

1. English/French/Italian apostrophe guard
2. Non-Turkish Latin word guard
3. Arabic/Greek script-span fallback
4. Technical comparator span guard
5. Azerbaijani routing guard

Basari kriteri:

```text
tr_gold_expanded.tsv 50/50 kalmali
English smoke 5/10 ustune cikmali
Multilingual smoke 8/20 ustune cikmali
Smoke testlerde Turkce disi hasar azalmali
```

## 7. Danismanlardan Istedigimiz Geri Bildirim

Lutfen sadece onaylamayin. Katilmadiginiz yerlerde acikca itiraz edin.

### Soru 1: Ana Hipotez

Su hipotez metodolojik olarak makul mu?

```text
Turkce merkezli morphology-aware tokenizer, genel subword tokenizerlara gore
Turkce morfolojik sinirlari benzer token maliyetinde daha iyi koruyabilir.
```

Bu hipotezi desteklemek icin hangi ek metrik veya deney gerekir?

### Soru 2: Baseline Karsilastirmalari

Qwen, Mistral, LLaMA, SentencePiece BPE/Unigram karsilastirmalari dogru
yorumlanmis mi?

Eksik baseline var mi?

Ozellikle:

```text
LLaMA/Qwen genel tokenizerdir; morfolojik boundary icin optimize edilmemistir.
```

Bu ayrimi raporda yeterince net tutuyor muyuz?

### Soru 3: v1.6 Do-No-Harm Plani

v1.6'da yeni Turkce morfoloji kurali eklemeyip sadece routing guard eklemek
dogru mu?

Onerilen sira dogru mu?

```text
apostrophe guard
non-Turkish Latin guard
Arabic/Greek span fallback
technical comparator guard
Azerbaijani routing guard
```

Hangi adim riskli?

### Soru 4: Turkic / Multilingual Yol Haritasi

Turk dilleri icin nasil ilerlemeliyiz?

Secenekler:

- v1.x: sadece do-no-harm pass-through
- v2.0: script/language router + Turkic-aware layer
- v2.0: sadece MorphBPE fallback, deterministic Turkic morphology yok

Hangisi daha saglam?

### Soru 5: Surface Stem Karari

Tokenizer icin surface-stem yaklasimi savunulabilir mi?

```text
kitabımdan -> ▁Kitab +ım +dan
```

Yoksa lemma/canonical stem veya metadata tabakasi simdiden tasarlanmali mi?

### Soru 6: Hidden/Heldout Eval

Bu noktada insan etiketli hidden/heldout eval zorunlu hale geldi mi?

Eger evetse:

- kac ornek?
- hangi domainler?
- kac etiketleyici?
- policy gold ve independent gold ayrimi gerekli mi?

### Soru 7: En Buyuk Risk

Sizce bu projenin su an en buyuk teknik veya metodolojik riski nedir?

Lutfen ilk 3 riski sirasiyla yazin.

## 8. Incelenmesi Onerilen Dosyalar

Kisa bakis:

```text
README.md
docs/current_resume_point.md
docs/v1_5_baseline_findings.md
docs/v1_5_english_smoke_findings.md
docs/v1_5_multilingual_smoke_findings.md
docs/v1_6_do_no_harm_routing_plan.md
```

Raporlar:

```text
artifacts/v1_5_real_tokenizer_report_all_expanded.md
artifacts/v1_5_real_tokenizer_report_all_challenge.md
artifacts/v1_5_real_tokenizer_report_english_smoke.md
artifacts/v1_5_real_tokenizer_report_multilingual_smoke.md
```

Eval setleri:

```text
data/eval/tr_gold_expanded.tsv
data/eval/tr_challenge.tsv
data/eval/en_smoke.tsv
data/eval/multilingual_smoke.tsv
data/eval/tr_stress_public.tsv
```

## 9. Kapanis

Bizim mevcut yorumumuz:

```text
Proje iyi yolda, ama production seviyesinde degil.
Turkce morfolojik boundary konusunda guclu sinyal var.
Asil risk, Turkce kurallarin non-Turkish inputlara sizmasi.
v1.6 bu riski azaltmali.
```

Danismanlardan bekledigimiz:

```text
Bu yorum dogru mu?
Yanlis veya eksik yorumladigimiz yer var mi?
v1.6 plani bizi dogru yonde mi tutar?
```
