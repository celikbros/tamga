# Example Scenario: Professor Outreach and Reply

This is a fictional scenario. Names and institutions are placeholders.

## Message Sent To Professor

```text
Konu: Turkce merkezli tokenizer projesi icin kisa multilingual/Turk dilleri review istegi

Merhaba Hocam,

tr-centric-tokenizer adli Turkce merkezli, morfoloji-duyarli bir tokenizer
arastirma prototipi uzerinde calisiyoruz.

Mevcut v1.x sistem Turkce deterministic morfoloji cekirdegine odaklaniyor.
Ancak uzun vadede sistemi multilingual/Turk dilleri farkindaligi olan bir v2.0
tasarima tasimak istiyoruz. Bu asamaya gecmeden once Unicode normalization,
script handling, apostrof kullanimi, fallback ve vocabulary allocation gibi
ileride degistirmesi pahali olabilecek mimari kararlar konusunda dis review
almak istiyoruz.

Bu bir kod yazma veya buyuk veri etiketleme istegi degildir. Beklentimiz kisa
bir mimari risk degerlendirmesi.

Tahmini sure: 30-60 dakika.

Ilgili dosyalar:

- docs/multilingual_strategy.md
- docs/multilingual_observations.md
- docs/multilingual_reviewer_packet.md
- docs/multilingual_reviewer_response_form.md

Eger bu konuda calisabilecek bir lisansustu ogrenciniz veya Turkish/Turkic NLP
alanina asina bir meslektasiniz varsa yonlendirmeniz de cok degerli olur.

Tesekkurler,
[Adiniz]
```

## Fictional Professor Reply

```text
Merhaba,

Dosyalari inceledim. Genel strateji dogru yonde gorunuyor: Turkce morfoloji
katmanini ayri tutmaniz ve vocabulary allocation'i script/fallback kararlari
netlesmeden dondurmemeniz onemli.

Benim hizli notlarim:

1. Cross-language protection katmani dogru yerde, yani Turkce morfoloji
   katmanindan once gelmeli. Dosya adlari, URL'ler, API isimleri ve sayilar
   tum diller icin once korunmali.

2. Turk dilleri icin apostrof konusunda genelleme yapmayin. Turkiye Turkcesinde
   ozel ad eki gibi calisan apostrof mantigi diger Turk dillerine dogrudan
   tasinmamali.

3. Kiril tabanli diller icin char-by-char fallback uzun vadede kabul edilemez.
   v1.x'te regression saymayabilirsiniz ama v2.0 vocabulary oncesi script-aware
   pretokenizer ve byte fallback netlesmeli.

4. Azerbaycanca icin e/ə, x/kh, q/g ayrimlari ve Latin/Kiril gecisleri goz
   onunde bulundurulmali. Bu noktada bir doktora ogrencim [Student Name] size
   daha somut ornekler verebilir.

5. Normalization kararlarini acele dondurmayin. Ozellikle dotted/dotless i
   sadece Turkiye Turkcesi icin dusunulmemeli.

Bu haliyle strategy doc v2.0 icin makul bir baslangic. Ancak vocabulary
egitiminden once Turkic Latin ve Turkic Cyrillic icin ayri smoke set kurulmasini
oneririm.

Isterseniz [Student Name]'i bu review icin yonlendirebilirim.

Selamlar,
[Professor Name]
```

## What This Reply Gives Us

Useful signals:

- Confirms cross-language protection before morphology.
- Confirms apostrophe must stay Turkish-scoped.
- Flags Cyrillic char-level fallback as v2.0-critical.
- Flags Azerbaijani `ə` and Latin/Kiril variation.
- Suggests a PhD student for detailed examples.

Not enough yet:

- No filled response form.
- No concrete smoke examples.
- No detailed language-specific normalization proposal.

Next action:

```text
Ask the referred PhD student to fill docs/multilingual_reviewer_response_form.md.
```
