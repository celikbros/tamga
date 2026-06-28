# Danismanlara Soru Paketi: v1.6b Batch 5 / R3 Azerbaijani Routing Guard

Tarih: 2026-05-30  
Repo: `https://github.com/celikbros/tamga`
Son commit: `b8d9ab1 Add non-Turkish Latin word guard`

## Kisa Durum

Proje su anda Turkce merkezli morphology-aware tokenizer arastirma prototipi.
v1.6b hattinda yeni Turkce morfoloji kurali eklemiyoruz; sadece "do-no-harm"
routing/guard iyilestirmeleri yapiyoruz.

Tamamlanan v1.6b batch'leri:

1. Technical comparator guard:
   - `transformers>=4.40`
   - `tokenizers>=0.19`
2. Arabic/Greek script word fallback:
   - Arapca/Yunanca kelimeler karakter karakter bolunmuyor.
3. English/European apostrophe guard:
   - `Don't`, `John's`, `L'amico`, `d'Istanbul` yuzey token kaliyor.
   - Turkce `Türkiye'den`, `README.md'yi`, `2026'da` akisi korunuyor.
4. Non-Turkish Latin word guard:
   - `Straße`, `niño`, `Bogotá`, `università` yuzey token kaliyor.
   - Bu guard yalnizca Turkce alfabesi disinda Latin harf tasiyan kelimelerde
     calisiyor; genel dil tespiti yapmiyor.

Guncel dogrulama:

```text
python -m pytest --basetemp C:\tmp\pytest-basetemp
116 passed

tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

tr_challenge.tsv
exact_match: 44/108
f1: 0.8255

en_smoke.tsv
exact_match: 8/10
f1: 0.8889

multilingual_smoke.tsv
exact_match: 17/20
f1: 0.9404

protected span stress
protected_preserved: 25/25
break_rate: 0.0000
```

## Kalan Gorunur Hatalar

`multilingual_smoke.tsv` icinde kalan ana hatalar:

```text
Azerbaijani:
Mənim adım Əli, Bakıda yaşayıram.

Beklenen:
▁Mənim ▁adım ▁Əli , ▁Bakıda ▁yaşayıram .

Guncel:
▁Mənim ▁ad +ım ▁Əli , ▁Bak +ı +da ▁yaşayıram .
```

```text
Azerbaijani:
Xəbər: qız məktəbə gedir, dağ yolu uzundur.

Beklenen:
▁Xəbər : ▁qız ▁məktəbə ▁gedir , ▁dağ ▁yolu ▁uzundur .

Guncel:
▁Xəbər : ▁qız ▁məktəbə ▁ge +dir , ▁dağ ▁yolu ▁uzun +dur .
```

Bir de multilingual mixed satirinda hyphen sorunu var:

```text
Turkic-speaking -> ▁Turkic - ▁speaking
```

Bu R3 kapsaminda degil; ayri bir hyphen/code-mixed guard konusu.

## Neden R3 Riskli?

R3, onceki guard'lardan daha riskli; cunku Azerice ile Turkiye Turkcesi Latin
yazida yuzey olarak cok yakin. Turkce suffix kurallari Azerice kelimelerde
"yanlis ama makul gorunen" bolmeler uretebilir:

```text
adım   -> ad +ım
Bakıda -> Bak +ı +da
gedir  -> ge +dir
uzundur -> uzun +dur
```

Bu bir "sessiz hata" riski. Sistem hata vermiyor; ama Turkce morfoloji Azerice
kelimeye sizmis oluyor.

Ayrica R3 ters yonde de riskli:

- Azerice sanip Turkce metni pass-through yaparsak Turkce morfoloji recall'u
  duser.
- Token-level dil tespiti kisa kelimelerde guvenilir degil.
- Cok genis bir `q/x/ə` guard'i, ileride Turkic-aware v2.0 tasarimini yanlis
  yonde dondurebilir.

## Su Anki Aday Yaklasimlar

### Secenek A: R3'u v1.6b'de Uygulama, Sadece Dokumante Et

Davranis degisikligi yok. Azerice over-splitting known limitation olarak kalir.

Artisi:

- En guvenli secenek.
- Turkce regression riski yok.
- v2.0 router/MorphBPE kararini erken dondurmez.

Eksisi:

- Multilingual smoke `17/20` seviyesinde kalir.
- Azerice "do-no-harm" hedefi eksik kalir.

### Secenek B: Sadece Guclu Azerice Karakter Iceren Kelimeyi Koru

Ornek cue:

```text
ə / Ə
```

Bu durumda:

```text
Mənim -> ▁Mənim
Əli -> ▁Əli
Xəbər -> ▁Xəbər
məktəbə -> ▁məktəbə
```

Ama su kelimeler yine Turkce morfolojiye dusebilir:

```text
adım
Bakıda
gedir
uzundur
```

Artisi:

- Dar ve dusuk riskli.
- Zaten kismen mevcut davranisa yakin.

Eksisi:

- Iki Azerice smoke satirini tam duzeltmez.
- Token-level guard oldugu icin cumle icindeki Turkce-benzeri Azerice kelimeleri
  kacirir.

### Secenek C: Cumle/Span Bazli Azerice Cue Varsa Satirdaki Latin Kelimeleri Koru

Eger bir cumlede guclu Azerice cue varsa (`ə/Ə`, belki `q`, `x`) o cumledeki
Latin kelimeleri Turkce morfolojiye sokmadan yuzey token olarak koru.

Ornek:

```text
Mənim adım Əli, Bakıda yaşayıram.
-> ▁Mənim ▁adım ▁Əli , ▁Bakıda ▁yaşayıram .
```

Artisi:

- Mevcut Azerice smoke hatalarini cozer.
- "Azerice metne Turkce kurallar sizmasin" hedefine daha uygun.

Eksisi:

- Tokenizer simdilik token-level akisa yakin; cumle/span-level routing mimari
  yuzeyi buyutur.
- Code-mixed Turkce + Azerice veya Turkce metinde tek Azerice ad gecerse fazla
  koruyabilir.
- Turkce metinde `q/x` gibi yabanci/code karakterleri false positive yaratabilir.

### Secenek D: R3'u v2.0'a Ertele, v1.6b'yi Batch 4'te Dondur

v1.6b burada kapanir. Sonraki is:

- v1.7 heldout/independent eval protokolu
- missing baselines
- downstream/tokenizer usefulness protokolu
- v2.0 router/MorphBPE RFC

Artisi:

- R3'te acele etmeyiz.
- Danismanlarin "eval once, yeni kural sonra" uyarilarina uyar.

Eksisi:

- Azerice smoke bilinen hata olarak kalir.

## Bizim Varsayilan Egilimimiz

Varsayilan egilimimiz:

> Secenek C'yi hemen kodlamamak; once R3 icin kisa bir design review yapmak.

Eger uygulanacaksa da su kisitlarla uygulanmali:

- Turkce `tr_gold_expanded.tsv` 50/50 kalmali.
- `tr_challenge.tsv` gerilememeli.
- English smoke `8/10` altina dusmemeli.
- Multilingual smoke sadece net skorla degil, kategori bazinda incelenmeli.
- Azerice guard Turkce apostrof, code/file, number/date korumalarini bozmamali.
- Herhangi bir Turkce regression gorulurse revert edilmeli.

## Danismanlara Sorular

### Soru 1

R3'u v1.6b icinde uygulamali miyiz, yoksa Batch 4'te v1.6b'yi dondurup
Azerice/Turkic routing'i v2.0'a mi ertelemeliyiz?

### Soru 2

Uygulanacaksa hangi scope dogru?

- A: hic uygulama, sadece known limitation
- B: sadece `ə/Ə` gibi guclu Azerice harf tasiyan kelimeyi koru
- C: cumlede guclu Azerice cue varsa Latin kelimeleri yuzey token olarak koru
- D: baska bir daha guvenli ara cozum

### Soru 3

Azerice routing icin guvenli cue seti ne olmali?

Dusundugumuz adaylar:

```text
Strong cue: ə / Ə
Possible cue: q, x
Risky cue: ı, ş, ç, ğ
```

`q/x` tek basina yeterli sayilmali mi, yoksa `ə/Ə` olmadan Azerice route
tetiklenmemeli mi?

### Soru 4

Token-level guard yeterli mi, yoksa Azerice icin cumle/span-level routing
kacinilmaz mi?

Ornek problem:

```text
Mənim adım Əli, Bakıda yaşayıram.
```

`Mənim` ve `Əli` guclu cue tasiyor; ama `adım`, `Bakıda`, `yaşayıram`
Turkce-benzeri gorunebiliyor.

### Soru 5

R3 icin revert kriterleri ne olmali?

Bizim onerimiz:

```text
Revert if:
- tr_gold_expanded < 50/50
- protected span break rate > 0
- English smoke < 8/10
- multilingual smoke improves only by breaking Turkish/code-mixed behavior
- Turkish proper-name/apostrophe examples regress
```

Bunlar yeterli mi? Eklememiz gereken kritik regression ornekleri var mi?

### Soru 6

R3'u implement etmeden once public stress setine hangi Azerice/Turkic regression
orneklerini eklemeliyiz?

Ornek adaylar:

```text
Mənim adım Əli, Bakıda yaşayıram.
Xəbər: qız məktəbə gedir, dağ yolu uzundur.
API'den data aldım.  # Turkce/code-mixed bozulmamali
Türkiye'den geldim. # Turkce apostrof bozulmamali
```

### Soru 7

Bu noktada R3'u uygulamak yerine v1.7'ye gecmek daha mi akillica?

v1.7 icin planlanan hat:

- independent/heldout eval planini somutlastirma
- missing baseline protokolu: Morfessor, Turkish-trained BPE/Unigram,
  BERTurk/XLM-R/mT5
- downstream usefulness protokolu: kucuk LM bpc veya byte-normalized perplexity
- v2.0 router/MorphBPE RFC

## Danismandan Beklenen Cikti

Lutfen su formatta yanit verin:

```text
1. R3 v1.6b'de uygulanmali mi? Evet/Hayir/Kosullu
2. Onerilen scope: A/B/C/D
3. Guvenli cue seti:
4. Token-level mi, span-level mi?
5. Revert kriterleri:
6. Eklenmesi gereken regression ornekleri:
7. v1.7'ye gecis hakkinda yorum:
8. En kritik uyariniz:
```

## Kisa Ozet

v1.6b Batch 1-4 iyi gitti:

```text
tr_gold_expanded: 50/50
multilingual_smoke: 8/20 -> 17/20
protected span break rate: 0.0000
```

Ancak R3 Azerice guard onceki guard'lardan daha riskli. Karar vermeden once
danisman gorusu istiyoruz:

> Dar bir Azerice do-no-harm guard yazalim mi, yoksa v1.6b'yi burada dondurup
> Turkic routing'i v2.0 tasarimina mi birakalim?
