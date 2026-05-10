# Danismanlar Icin Proje Durum Raporu

Tarih: 2026-05-08  
Repo: `https://github.com/alicelik77/tr-centric-tokenizer`  
Guncel surum: `v1.2.0`

## 1. Kisa Ozet

`tr-centric-tokenizer`, Turkce merkezli morphology-aware tokenizer arastirma
prototipidir. Projenin ilk hedefi, Turkce gibi eklemeli dillerde standart
subword tokenization yaklasimlarinin kacirdigi morfolojik sinirlari daha bilincli
koruyan deterministik bir cekirdek kurmaktir.

Su an proje production tokenizer degildir. Ancak arastirma prototipi olarak
olculebilir, test edilebilir ve genisletilebilir bir seviyeye gelmistir.

Mevcut durum:

- Deterministik Turkce tokenizer cekirdegi var.
- Kelime baslangici marker'i kullaniliyor: `▁`.
- Apostrof sonrasi ekler ayriliyor:
  `Türkiye'den -> ▁Türkiye ' +den`.
- Yuzey govde yaklasimi kullaniliyor:
  `kitaplarımdan -> ▁Kitap +lar +ım +dan`,
  `kitabımdan -> ▁Kitab +ım +dan`.
- Informal yuzey bicimleri standart dile cevrilmeden parcalaniyor:
  `Gelicem -> ▁Gel +icem`.
- Code/file-like ve sayi/date tokenlari icin temel guard'lar var:
  `README.md`, `config_v2.json`, `3.14`, `34-ABC-1907`.
- Evaluation, BPE baseline karsilastirmasi, challenge error analysis ve
  challenge taxonomy altyapilari var.

Ana sonuc:

> Secili cekirdek regression setinde sistem 50/50 exact match veriyor. Daha zor
> challenge setinde v1.1 sonrasi 40/108 exact match seviyesinde; kalan hatalar
> artik etiketlenmis ve hangi teknik yola ait olduklari gorunur durumda.

## 2. Proje Ne Degil?

Bu proje su anda:

- production tokenizer degil
- genel Turkce morfolojik cozumleyici degil
- baglamli disambiguation sistemi degil
- egitilmis LLM tokenizer'i degil
- akademik olarak tamamlanmis bir benchmark sonucu degil

Bu proje su anda:

- Turkce merkezli deterministic morphology tokenizer cekirdegi
- evaluation ve hata analizi altyapisi
- toy BPE baseline karsilastirmasi
- MorphBPE/hybrid yaklasima hazirlik zemini

## 3. Neden Bu Proje?

Standart BPE/Unigram tokenizers sikca kelimeleri frekans ve karakter dizisi
temelli parcalar. Turkce gibi eklemeli dillerde bu, su sinirlarin kaybolmasina
yol acabilir:

```text
Geldim -> gel +di +m
Arabalarımızdakilerdenmişsiniz -> araba +lar +ımız +da +ki +ler +den +miş +siniz
```

BPE bu kelimeleri daha az tokenla temsil edebilir. Ancak daha az token her zaman
daha iyi temsil anlamina gelmez. Turkcede morfolojik bilgi, ek zincirlerinin
duzenli ve uretken olmasi nedeniyle modelleme acisindan degerlidir.

v0.9 BPE sweep bulgusu ozellikle onemliydi:

| Model | Avg tokens/word | Boundary F1 |
| --- | ---: | ---: |
| custom tokenizer | 2.7438 | 1.0000 |
| bpe_1000 | 2.7438 | 0.6277 |

Bu sonuc kucuk ve kontrollu eval setine aittir; kesin genelleme degildir. Ama
sunlari gosterir:

- Ayni token/kelime maliyetinde bile morfoloji-duyarli tokenizer daha iyi
  boundary uyumu verebilir.
- Token sayisi tek basina kalite metrigi degildir.
- Turkce icin boundary-aware evaluation anlamli sinyal veriyor.

## 4. Mevcut Veri Setleri

### 4.1 Frozen Regression Set

Dosya:

```text
data/eval/tr_gold_expanded.tsv
```

Amac:

- Cekirdek davranisin bozulmadigini garanti etmek.
- Her surumde exact match beklemek.

Guncel sonuc:

```text
50/50 exact match
precision: 1.0000
recall:    1.0000
f1:        1.0000
```

Bu set artik "frozen regression" olarak kabul ediliyor.

### 4.2 Challenge / Dev Set

Dosya:

```text
data/eval/tr_challenge.tsv
```

Amac:

- Sistemin nerelerde kirildigini gormek.
- Her hatayi hemen duzeltmek degil, hatalari siniflandirmak.

Guncel sonuc:

```text
40/108 exact match
precision: 0.8600
recall:    0.7807
f1:        0.8184
```

Bu set regression set degildir; hata analizi ve arastirma yonlendirmesi icin
kullanilir.

### 4.3 Labeled Challenge Taxonomy

Dosya:

```text
data/eval/tr_challenge_labeled.tsv
```

v1.2 ile challenge mismatches etiketlendi.

Etiketler:

| Label | Anlam |
| --- | --- |
| `exact_match` | Beklenen ve uretilen tokenlar ayni. |
| `safe_rule_candidate` | Izole, dusuk riskli kural adayi. |
| `needs_lexicon` | Yuzey govde / lexicon genisletmesi gerekebilir. |
| `needs_context` | Baglam olmadan karar verilmemeli. |
| `hybrid_candidate` | MorphBPE/hybrid fallback icin aday. |
| `do_not_fix_yet` | Simdilik duzeltilmemeli; false-positive riski yuksek. |

Guncel taxonomy ozeti:

| Label | Count |
| --- | ---: |
| exact_match | 40 |
| needs_lexicon | 28 |
| hybrid_candidate | 17 |
| do_not_fix_yet | 9 |
| needs_context | 7 |
| safe_rule_candidate | 7 |

Bu tablo v1.3 ve sonrasinda hangi hatalara once dokunulacagini belirlemek icin
kullanilacak.

## 5. Surum Gecmisi

### v0.1 - Minimal Proje Iskeleti

- `src/tr_tokenizer/`
- `tests/`
- `data/eval/`
- `scripts/`
- `pyproject.toml`
- `README.md`

Ilk normalizer, pre-tokenizer, apostrof ayirici ve encode/decode prototipi
olusturuldu.

### v0.2 - Kelime Baslangici ve Fiil Gecmis Zaman

- `▁` kelime baslangici marker'i eklendi.
- `geldim -> ▁gel +di +m`
- `gittim -> ▁git +ti +m`
- Apostrof ve ek ayrimi test edildi.

### v0.3 - Evaluation Sistemi

- `data/eval/tr_gold_segmented.tsv`
- `scripts/evaluate_tokenizer.py`
- exact match, precision, recall, F1
- mismatch raporu

Bu asamada evaluation sistemi bir gold hatasini yakaladi:

```text
Kitaplarımdan -> ▁Kitap +lar +ım +dan
```

Bu karar yuzey govde yaklasiminin temelini olusturdu.

### v0.4 - Lexicon-aware Surface Stem Splitter

Kisa ekleri genel greedy splitter'a koymadan, bilinen yuzey govdelerde guvenli
ayrim yapildi.

Ornek:

```text
Ağacın -> ▁Ağac +ın
Rengini -> ▁Reng +i +ni
```

Ama:

```text
kadın -> ▁kadın
yakın -> ▁yakın
altın -> ▁altın
kedi  -> ▁kedi
```

Bu kritik bir tasarim karariydi: basari sadece ek ayirmak degil, yanlis yerde ek
ayirmamaktir.

### v0.5 - Expanded Gold Set

- `data/eval/tr_gold_expanded.tsv`
- kategori bazli evaluation
- en az 40 ornek, sonra 50 orneklik cekirdek set

Kategoriler:

- suffix_chain
- proper_name
- softening
- negative_word
- verb_past
- verb_future
- question
- informal
- code_mixed

### v0.6 - Proper Name, Softening, Code-mixed

Iyilestirilen alanlar:

- `Ali'nin`
- `API'den`
- `README.md`
- `OpenAIlaştırılamayanlardanmış`
- yuzey govde yumusama ornekleri

### v0.7 - Informal Turkish Layer

Konusma dili yuzey bicimi korunarak parcalandi:

```text
Gelicem -> ▁Gel +icem
Gidiyom -> ▁Gid +iyom
Napıyorsun -> ▁Napı +yor +sun
```

Onemli prensip:

> Tokenizer normalizer gibi davranmaz. `Gelicem` metnini `geleceğim`e
> cevirmeyiz.

### v0.8 - Toy BPE Baseline

- `src/tr_tokenizer/baseline_bpe.py`
- `scripts/train_baseline_bpe.py`
- `scripts/compare_tokenizers.py`

Minimal pure-Python toy BPE baseline eklendi.

### v0.9 - BPE Sweep ve Leakage Kontrol

- `data/train/tr_bpe_train.txt`
- `scripts/check_eval_leakage.py`
- `scripts/compare_bpe_sweep.py`
- `docs/evaluation.md`

Eval leakage kontrolu ve multi-vocab BPE karsilastirmasi eklendi.

### v1.0-rc1 / v1.0-rc2 - Freeze ve Challenge Analysis

- `data/eval/tr_challenge.tsv`
- `scripts/write_eval_report.py`
- `scripts/analyze_mismatches.py`
- challenge mismatch raporu

Bu asamada proje "korunabilir arastirma prototipi" haline geldi.

### v1.1 - Low-risk Pretokenizer Fixes

Hedef:

- proper_name apostrophe suffix gap
- numbers_dates
- punctuation

Sonuc:

| Metric | Before v1.1 | After v1.1 |
| --- | ---: | ---: |
| challenge exact match | 21/108 | 40/108 |
| challenge F1 | 0.7570 | 0.8184 |
| numbers_dates F1 | 0.5693 | 0.9091 |
| proper_name F1 | 0.8409 | 0.9785 |
| punctuation F1 | 0.8392 | 0.9388 |
| expanded exact match | 50/50 | 50/50 |

Guard kategoriler bilerek degistirilmedi:

| Category | Before F1 | After F1 |
| --- | ---: | ---: |
| negative_word | 0.6387 | 0.6387 |
| ambiguity | 0.7304 | 0.7304 |

### v1.2 - Challenge Error Taxonomy

Tokenizer davranisi degistirilmedi. Kalan hatalar etiketlendi.

Komut:

```powershell
python scripts/label_challenge_mismatches.py data/eval/tr_challenge.tsv data/eval/tr_challenge_labeled.tsv --markdown-out artifacts/v1_2_error_taxonomy_report.md
```

Sonuc:

```text
exact_match: 40
needs_lexicon: 28
hybrid_candidate: 17
do_not_fix_yet: 9
needs_context: 7
safe_rule_candidate: 7
```

## 6. Temel Tasarim Kararlari

### 6.1 Kelime Baslangici Marker'i

Kelime baslangici `▁` ile gosterilir:

```text
Türkiye'den geldim.
-> ▁Türkiye ' +den ▁gel +di +m .
```

Bu, subword tokenization gelenegine yakin durur ve word boundary bilgisini
korur.

### 6.2 Yuzey Govde Yaklasimi

Tokenlar lemma olmak zorunda degildir; yuzeyde gorunen govdeyi koruruz.

```text
kitaplarımdan -> ▁Kitap +lar +ım +dan
kitabımdan    -> ▁Kitab +ım +dan
```

Bu karar tokenizer'i morfolojik cozumleyiciye donusturmeden, yuzey metne sadik
kalmasini saglar.

### 6.3 Kisa Ekler Genel Greedy Splitter'a Konmaz

`+ı`, `+i`, `+ın`, `+in` gibi kisa ekler tehlikelidir.

Yanlis ornekler:

```text
kadın -> kad +ın
yakın -> yak +ın
altın -> alt +ın
kedi  -> ked +i
```

Bu nedenle kisa ekler sadece guarded flow icinde kullanilir:

- surface stem lexicon
- apostrof suffix flow
- mixed-case/code flow
- informal-only flow

### 6.4 Informal Normalization Yok

Tokenizer yuzey bicimi korur:

```text
Gelicem -> ▁Gel +icem
```

Sunlar yapilmaz:

```text
Gelicem -> geleceğim
```

### 6.5 Challenge Set 100% Hedef Degil

Challenge seti, sistemi zorlamak ve hata tiplerini gormek icindir.

`tr_gold_expanded.tsv` = frozen regression  
`tr_challenge.tsv` = dev/error analysis  
`tr_challenge_labeled.tsv` = taxonomy data

## 7. Su Anki Ana Riskler

### 7.1 Ambiguity

Ornekler:

```text
Yazın
Yazarım
Gül
Yüz
At
Ocak
```

Bu kelimeler baglamsiz olarak birden fazla analiz tasiyabilir. Context-free
tokenizer'in bunlari kesin sekilde bolmesi risklidir.

Mevcut policy:

- `needs_context`
- broad rule ekleme
- MorphBPE/hybrid veya baglamli analiz dusun

### 7.2 Negative Words

Ornekler:

```text
kadın
yakın
altın
alın
odun
```

Bu sinifta yanlis pozitif bolme riski yuksektir. Mevcut policy:

- `do_not_fix_yet`
- daha fazla negative regression ekle
- genel suffix splitter'i agresiflestirme

### 7.3 Lexicon Buyutme Riski

`needs_lexicon` 28 ornek var. Bunlar cozulebilir gibi gorunse de rastgele stem
eklemek sistemi kisa vadede yukseltip uzun vadede kirilganlastirabilir.

Gereken yaklasim:

- batch halinde kucuk stem eklemeleri
- her batch icin negative-word regression
- expanded set 50/50 kontrolu
- challenge taxonomy tekrar calistirma

### 7.4 Toy BPE Baseline Siniri

BPE baseline minimal pure-Python toy baseline'dir. Production SentencePiece,
tiktoken veya HuggingFace tokenizers karsilastirmasi degildir.

Bu nedenle BPE karsilastirmasi:

- guclu bir sinyal verir
- ama kesin akademik iddia degildir

## 8. Danismanlardan Beklenen Geri Bildirimler

### 8.1 Ambiguity Policy

Soru:

> Context-free tokenizer `Yazın`, `Gül`, `Yüz`, `Yazarım` gibi formlari bolmeli mi,
> yoksa baglam olmadigi icin korumali mi?

Secenekler:

- Conservative: bilinen guvenli stem yoksa bolme.
- Aggressive: olasi morfolojik sinirlari daha cok ac.
- Hybrid: deterministic core conservative kalsin, MorphBPE fallback devreye girsin.

Mevcut onerimiz:

> Conservative deterministic core + MorphBPE fallback.

### 8.2 Gold Set Stratejisi

Soru:

> `expanded = frozen regression`, `challenge = dev/error analysis` ayrimi yeterli
> mi?

Onerilen ek:

- `data/eval/private/tr_hidden_eval.tsv`
- danisman/uzman tarafindan gorulmemis 40 ornek
- v1.3 safe-rule veya lexicon calismasindan once tarafsiz test
- protokol: `docs/hidden_eval_protocol.md`
- etiketleme kilavuzu: `docs/hidden_eval_labeling_guideline.md`
- etiketleyici paketi: `docs/hidden_eval_labeler_packet.md`
- etiketleyici bulma plani: `docs/labeler_recruitment_plan.md`
- iki gold sutunu: independent morphology ve project policy
- hidden setten ayri 5 orneklik private kalibrasyon adimi
- public raporlarda sadece aggregate metrikler
- divergence varsa `divergence_note` zorunlu
- aggregate-only rapor komutu:
  `python scripts/evaluate_hidden_eval.py data/eval/private/tr_hidden_eval.tsv --markdown-out artifacts/v1_3_hidden_eval_report.md`

Guncel karar:

> Hidden/heldout eval v1.5'e birakilmamali. v1.3'ten once kurulacak. Aksi halde
> v1.3 ve v1.4'teki kural/lexicon artislari challenge setine overfit etme riski
> tasir.

### 8.3 Surface Stem Lexicon

Soru:

> Surface stem lexicon nasil buyumeli?

Secenekler:

- elle kontrollu
- corpus frekansi ile aday cikarimi
- TDK/lexicon tabanli
- MorphBPE ile birlikte yarı-otomatik

Mevcut onerimiz:

> Once elle kontrollu kucuk batch'ler, sonra corpus adaylari.

### 8.4 Boundary F1 Yeterli mi?

Soru:

> Boundary F1, morfolojik basariyi olcmek icin yeterli mi?

Ek metrik adaylari:

- morpheme boundary precision/recall
- token/word ratio
- unknown/over-split rate
- false-positive split rate
- category-specific risk score
- downstream LM experiment

### 8.5 MorphBPE'ye Ne Zaman Gecilmeli?

Soru:

> Daha fazla deterministik kural mi yazilmali, yoksa MorphBPE/hybrid trainer'a mi
> gecilmeli?

Mevcut taxonomy sunu gosteriyor:

- 7 safe_rule_candidate var
- 28 needs_lexicon var
- 17 hybrid_candidate var
- 7 needs_context var
- 9 do_not_fix_yet var

Bu tabloya gore deterministik kural eklemeye devam etmek mumkun ama dikkatli
olmaliyiz. Uzun vadede MorphBPE/hybrid yonu daha dogru gorunuyor.

## 9. Onerilen Yol Haritasi

### v1.3 - Hidden/Heldout Eval Protocol

Hedef:

- Danismanlardan veya dogal corpus'tan 40 yeni ornek
- gelistirici tarafindan onceden gorulmemis test
- `data/eval/private/tr_hidden_eval.tsv` gibi Git tarafindan ignore edilen dosya
- hidden setten ayri 5 kalibrasyon ornegi uzerinden danisman/ikinci gozlemci
  kontrolu
- expanded/challenge/hidden uc katmanli raporlama
- v1.4 oncesi overfitting kontrolu
- public raporda hidden ornek metni paylasmama
- hidden eval icin aggregate-only rapor script'i

Bu adim tokenizer davranisi degistirmez.

### v1.4 - Safe Rule Candidates

Sadece `safe_rule_candidate` etiketli 7 ornege bak.

Hedef:

- `docs/v1_4_decision_framework.md` icindeki karar agacina uy
- hidden eval aggregate sonucu gelmeden implementation karari alma
- 2-3 dusuk riskli fixture sec
- testleri once yaz
- genel suffix splitter'a dokunma
- expanded 50/50 kalsin
- hidden eval gerilemesin

### v1.5 - Lexicon Batch Discipline

Hedef:

- `needs_lexicon` orneklerinden kucuk batch sec
- negative regression ekle
- surface stem eklemelerinin yan etkisini olc
- methodological strengthening: independent morphological reference integration
  hattini baslat veya netlestir

### v2.0 - MorphBPE Hybrid Prototype

Hedef:

- deterministic morphology layer
- morfem sinirina saygili BPE merge
- code/file/English cluster
- byte fallback
- Turkce/Turk dilleri vocabulary allocation fikrine hazirlik

## 10. Danismanlara Sunulacak Ana Mesaj

Proje su anda "genel tokenizer hazir" seviyesinde degil. Ama iyi bir arastirma
prototipi seviyesinde.

En onemli kazanimlar:

- Morfolojiye duyarli deterministic cekirdek calisiyor.
- Hatalar gorunur ve olculebilir hale geldi.
- BPE baseline ile ilk sinyal alindi.
- Challenge hatalari artik taxonomy ile siniflandiriliyor.
- Riskli alanlara rastgele kural yazmama disiplini olustu.

Ana arastirma sorusu:

> Turkce merkezli deterministic morphology layer + MorphBPE fallback, standart
> subword tokenization'a gore Turkce morfolojik boundary kalitesini ayni veya
> benzer token maliyetinde daha iyi koruyabilir mi?

Su anki cevap:

> Kucuk ve kontrollu eval setlerinde evet yonunde guclu sinyal var. Daha buyuk,
> dogal ve heldout setlerle test edilmesi gerekiyor.

## 11. Incelenmesi Onerilen Dosyalar

Baslangic:

```text
README.md
RELEASE_NOTES.md
docs/design.md
docs/evaluation.md
docs/ambiguity_policy.md
docs/hidden_eval_protocol.md
docs/hidden_eval_labeling_guideline.md
docs/v1_2_error_taxonomy.md
```

Raporlar:

```text
artifacts/v1_1_report.md
artifacts/v1_2_error_taxonomy_report.md
artifacts/bpe_sweep_report.md
```

Veri:

```text
data/eval/tr_gold_expanded.tsv
data/eval/tr_challenge.tsv
data/eval/tr_challenge_labeled.tsv
```

Scriptler:

```text
scripts/evaluate_tokenizer.py
scripts/analyze_mismatches.py
scripts/label_challenge_mismatches.py
scripts/prepare_hidden_eval_views.py
scripts/compare_bpe_sweep.py
```

## 12. Kapanis

Bu proje artik "calisiyor mu?" asamasini gecmistir. Su an soru sudur:

> Hangi morfolojik olaylari deterministic olarak cozecegiz, hangilerini
> lexicon'a, hangilerini context'e, hangilerini MorphBPE fallback'e birakacagiz?

v1.2'nin amaci tam olarak bu karar zeminini olusturmaktir.
