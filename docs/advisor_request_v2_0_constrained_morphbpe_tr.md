# Danışman Değerlendirme Talebi: v2.0 Morfoloji-Duyarlı Öğrenilmiş Tokenizer Yönü

Tarih: 2026-06-10

Bu notu yeni bir uzmana gönderiyoruz. Uzman projeyi daha önce bilmiyor; bu
yüzden durumu baştan, açık ve eleştiriye açık şekilde anlatıyoruz.

## Projenin Amacı

Türkçe öncelikli, ileride çok dilli LLM projesinde kullanılabilecek bir
tokenizer araştırıyoruz.

Amacımız hazır bir tokenizer'ı aynen kullanmak değil. Türkçenin eklemeli ve
düzenli morfolojik yapısını bir **öğrenilmiş tokenizer'a matematiksel/ yapısal
öncül** olarak verebilir miyiz, bunu araştırıyoruz.

Şu anki sistem üretim tokenizer'ı değildir. Araştırma prototipidir.

Ana fikir:

```text
kayıpsız tokenization
+ Türkçe morfoloji öğretmeni
+ URL / dosya / kod / sayı / tarih gibi protected span routing
+ normal metin için learned vocabulary
+ gereken yerde byte / finite fallback
```

Şimdiye kadar öğrendiğimiz temel ayrım:

```text
Pure custom deterministic morphology:
  Morfoloji öğretmeni ve tanılama referansı olarak değerli.
  Ama doğrudan LLM tokenizer'ı olarak şu an fazla riskli ve token-heavy.

Plain SentencePiece / Unigram:
  Sıkıştırma açısından verimli.
  Ama Türkçe morfolojik boundary koruması zayıf ve protected span'leri kırıyor.

En umutlu yön:
  Custom morfolojiyi hard segmentation olarak değil, learned tokenizer'a soft
  prior olarak kullanan hibrit bir sistem.
```

Sizden istediğimiz şey onay değil; hatalı düşünüyorsak net itiraz etmeniz.

## Değişmez Gereksinimler

1. Tokenization LLM pretraining için kayıpsız veya fiilen kayıpsız olmalı.
2. Protected span'ler kırılmamalı:

```text
URL
dosya adı
kod-benzeri token
package/version string
sayı
tarih
```

3. Türkçe morfoloji ancak token-pressure ve language-modeling maliyetini
haklı çıkarıyorsa learned tokenizer'a taşınmalı.
4. Visible challenge set'e sonsuz ayar yapmak istemiyoruz.
5. Regex/istisna yığınına dönüşen, bakımı imkansız bir sistem istemiyoruz.

## Eval Setleri ve Metrikler

Kullandığımız görünür eval setleri:

| Eval set | Rol | Not |
| --- | --- | --- |
| `tr_gold_expanded.tsv` | frozen policy/spec regression | Kalite kanıtı değil, conformance/regression |
| `tr_challenge.tsv` | visible challenge/dev | Morfoloji stress testi; hidden değil |
| `multilingual_smoke.tsv` | do-no-harm smoke | Küçük çok dilli sanity |
| `tr_stress_public.tsv` | protected span stress | Protected span korunuyor mu |

Kullandığımız metrikler:

```text
boundary F1
exact match
tokens/raw byte
protected span preserved count
seçilmiş dallarda tiny-LM bits-per-byte
```

Boundary F1'in tek başına LLM kanıtı olmadığını biliyoruz. Biz bunu tanılama
metriği olarak kullanıyoruz. LLM tarafına daha yakın metrik bits-per-byte, ama
onu sadece temel intrinsic/token-pressure kapısını geçen adaylarda çalıştırmak
istiyoruz.

## Önemli Referanslar

| Aday | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | --- |
| custom deterministic morphology | n/a | n/a | 0.9220 | 25/25 |
| SP64 Unigram reference | 0.159020 | 0.159620 | ~0.735 | 1/25 |
| finite protected SP64 floor | 0.182112 | 0.183362 | ~0.691 | 25/25 |

Yorum:

```text
Bare SP64 final baseline olamaz; protected span'leri kırıyor.
Gerçek protected null baseline: finite_protected_sp64_floor.
```

Custom deterministic tokenizer güçlü morphology F1 veriyor ama şu an doğrudan
üretim LLM tokenizer'ı değil. Onu öğretmen/reference olarak görüyoruz.

## Denediğimiz Dallar

### 1. Train-Only Marker Shaping

Fikir:

```text
Morfolojik boundary marker'larını sadece SentencePiece training view içine koy.
Normal encode-time metinde marker olmasın.
```

Sonuç:

| Aday | Test tokens/raw byte | Challenge F1 | Protected stress |
| --- | ---: | ---: | --- |
| suffix_chain2 marker-stripped | ~0.185337 | 0.7632 | 25/25 |
| all-soft marker-stripped | ~0.196954 | 0.7703 | 25/25 |

Tiny-LM 300-step BPB:

| Aday | Test BPB |
| --- | ---: |
| SP64 | 4.860352 |
| finite protected SP64 floor | 4.976850 |
| suffix_chain2 | 5.094965 |
| all-soft | 5.157444 |

Karar:

```text
Marker-dose tuning durduruldu.
Marker'lar visible F1'i artırdı ama token-pressure maliyeti tiny-LM BPB'de
kendini ödemedi.
```

### 2. Morph Seed Bias Appendix

Fikir:

```text
Seçilmiş suffix/morph yüzeylerini train-only küçük bir appendix olarak ekle.
Marker yok. UDS yok. Sadece frekans bias.
```

Weak appendix:

```text
augmentation bytes/base byte: 0.000022
valid/test tokens/raw byte: 0.158312 / 0.158901
finite-protected Challenge F1: 0.6913
```

Strong appendix:

```text
augmentation bytes/base byte: 0.011047
valid/test tokens/raw byte: 0.158315 / 0.158913
finite-protected Challenge F1: 0.6918
```

Karar:

```text
Seed appendix durduruldu.
Compression-safe ama custom morphology teacher sinyalini Unigram vocabulary'ye
taşımadı.
```

### 3. Safe UDS7

Fikir:

```text
Sadece çok küçük ve denetlenmiş bir suffix yüzey havuzunu SentencePiece
user_defined_symbols olarak zorla.
```

Seçilen 7 sembol:

```text
ecek
acak
ümüz
ımız
imiz
yecek
umuz
```

Seçim train-only istatistiklerden geldi:

```text
uzun suffix yüzeyi
düşük hard-boundary share
sıfır veya çok düşük exact collision
```

Sonuç:

| Aday | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| SP64 reference | 0.159020 | 0.159620 |
| safe UDS7 | 0.159109 | 0.159684 |

Intrinsic:

| Model | Challenge F1 | Protected stress |
| --- | ---: | --- |
| safe UDS7, bare | 0.7556 | 1/25 |
| finite protected + safe UDS7 | 0.7081 | 25/25 |

Karar:

```text
Safe UDS7 şimdiye kadarki en iyi ucuz/yapısal morfoloji prior'ı.
Neredeyse token-pressure maliyeti yok ve gerçek morphology sinyali veriyor.
Ama hâlâ tiny-LM veya LLM handoff için yeterince güçlü değil.
```

### 4. Expanded UDS22

Fikir:

```text
UDS havuzunu train-only eşiklerle konservatif biçimde 7'den 22'ye çıkar.
```

Seçim:

```text
recommendation == uds_or_seed_candidate
min_count >= 100
surface_len >= 3
hard_share <= 0.01
exact_collision_rate <= 0.001
```

Sonuç:

| Aday | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| safe UDS7 | 0.159109 | 0.159684 |
| expanded UDS22 | 0.183675 | 0.184059 |
| finite protected SP64 floor | 0.182112 | 0.183362 |
| suffix_chain2 marker branch | 0.184500 | 0.185337 |

Karar:

```text
UDS expansion durduruldu.
UDS7 faydalı; fakat UDS'yi genişletmek hızlıca hard segmentation gibi
davranıyor ve token-pressure'ı marker/floor bandına çıkarıyor.
```

## Şu Anki İç Yorumumuz

Bizim mevcut yorumumuz:

```text
1. Finite protected routing kalmalı.
2. Safe UDS7 küçük ama değerli bir prior olarak kalmalı.
3. Marker-dose tuning kapalı.
4. Seed appendix kapalı.
5. Broad UDS expansion kapalı.
6. Sıradaki gerçek yön constrained/MorphBPE tarzı öğrenilmiş objective olmalı.
```

Ana tasarım problemi:

```text
Türkçe morfoloji öğretmeninden faydalanalım, ama çok sayıda suffix'i hard
boundary veya UDS olarak zorlayıp token count'u patlatmayalım.
```

## Düşündüğümüz Sonraki Yön: Constrained / MorphBPE

Custom deterministic morphology engine boundary hint üretecek; learned tokenizer
bu hint'leri kullanacak ama gerektiğinde override edebilecek.

Olası mekanizmalar:

```text
1. Morphology-aware BPE merge scoring:
   high-confidence morphology boundary geçen merge'lere ceza ver ama tamamen
   yasaklama.

2. Boundary-weighted Unigram:
   morph surface'lerle hizalı parçaları zayıf prior ile ödüllendir.

3. Protected-aware pretokenization:
   hard boundary sadece protected span / whitespace / script transition için.
   morphology boundary soft olsun.

4. Safe UDS7 kalsın:
   Sadece kanıtlanmış küçük havuz hard user_defined_symbol olarak tutulabilir.

5. Byte / finite fallback:
   Kayıpsızlık için korunmalı.
```

## Sizden İstediğimiz Eleştiri

Lütfen sadece onaylamayın. Yanlış yorumluyorsak net söyleyin.

### Sorular

1. Şu anki sonucumuz doğru mu?

```text
Safe UDS7 işe yarıyor.
UDS22 fazla maliyetli.
Marker-dose tuning ve seed appendix doğru sonraki lever değil.
```

2. Sizce sıradaki anlamlı dal constrained/MorphBPE tarzı öğrenilmiş objective
mi olmalı, yoksa hâlâ UDS/marker tarafında denememiz gereken daha basit bir şey
var mı?

3. Constrained objective kuracaksak, en küçük uygulanabilir deney ne olmalı?

Seçenekler:

```text
A. BPE merge selection sırasında morphology boundary geçen merge'lere soft ceza.
B. High-confidence morph surface'leri ödüllendir, ama UDS gibi zorunlu yapma.
C. Hard protected pretokenization + soft morph metadata.
D. Önce normal SP/Unigram eğit, sonra vocab'ı morph-aware prune/replace et.
E. Başka bir yöntem.
```

4. Compression ve morphology arasında trade-off nasıl kurulmalı?

Örnek:

```text
score(pair) = frequency(pair) - lambda * boundary_crossing_penalty
```

Boundary crossing cezası hangi durumlarda farklı olmalı?

```text
derivational suffix
inflectional suffix
case / possessive suffix
negative suffix
tense/aspect suffix
protected-tail suffix
```

5. Safe UDS7 bir sonraki dalda hard UDS olarak kalmalı mı, yoksa onlar bile
soft hint'e mi dönmeli?

6. Boundary F1'i fazla mı önemsiyoruz?

LLM kanıtı olmadığını biliyoruz. Ama morphology sinyalinin learned tokenizer'a
geçip geçmediğini tanılamada işe yaradı. Tiny-LM öncesi hangi intrinsic metriği
eklerdiniz?

7. Tiny-LM BPB ne zaman tekrar açılmalı?

Bizim düşündüğümüz gate:

```text
finite protected stress: 25/25
tokens/raw byte: tercihen <= 0.17
0.184 bandına ancak çok büyük F1 kazancı varsa izin
Challenge F1: finite_protected_sp64_floor ve safe UDS7 üstünde anlamlı iyileşme
```

Bu gate fazla katı mı, fazla zayıf mı, yanlış mı?

8. Finite protected routing'in kendisi yeniden tasarlanmalı mı?

Gözlem:

```text
Bare learned model bazen daha yüksek visible boundary F1 veriyor.
Ama bare model protected span'leri kırıyor.
Finite protected wrapper protected stress'i çözüyor ama visible F1'i düşürüyor.
```

Bu düşüşü doğru protected behavior maliyeti olarak mı kabul edelim, yoksa wrapper
segmentation/scoring tarafını mı iyileştirelim?

9. Mevcut akıl yürütmemizde en büyük gizli hata ne olabilir?

Örnek riskler:

```text
visible challenge overfitting
token-pressure proxy fazla katı
custom morphology teacher fazla kırılgan
20k pilot corpus temsil gücü düşük
protected routing morphology metric'i bozuyor
SentencePiece UDS davranışı custom objective ile karşılaştırılamaz
```

10. Bu proje sizde olsaydı, bir haftada hangi en küçük deneyi kurardınız?

Lütfen şunları verin:

```text
en küçük yararlı deney
stop criteria
success criteria
LLM ekibine deneysel paket olarak gitmeden önce görmek isteyeceğiniz artifact/result
```

## Bizim Önerdiğimiz Sonraki Adım

Şu an önerimiz:

```text
20k pilot split üzerinde küçük bir MorphBPE / constrained-BPE prototipi kur.

Kullan:
  hard boundaries: protected spans, whitespace, script transitions
  soft boundaries: custom teacher'dan high-confidence morphology boundaries
  safe hard symbols: belki sadece UDS7

Karşılaştır:
  SP64
  finite_protected_sp64_floor
  safe_uds_unigram_64000

Raporla:
  tokens/raw byte
  Challenge F1
  protected stress
  category F1
  sonra gerekirse tiny-LM BPB
```

Bu planı lütfen eleştirin. Constrained/MorphBPE erken veya yanlışsa, hangi yolu
önerirsiniz?
