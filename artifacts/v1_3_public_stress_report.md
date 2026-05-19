# Public Stress Report

Tokenizer behavior is not changed by this report.

## SUMMARY

- examples: 28
- roundtrip_exact: 21/28 (0.7500)
- protected_spans_preserved: 18/23 (0.7826)

## CATEGORY SUMMARY

| category | examples | roundtrip_exact | protected_preserved | avg_tokens |
| --- | ---: | ---: | ---: | ---: |
| ambiguity | 1 | 1/1 (1.0000) | n/a | 7.00 |
| azerbaijani | 2 | 0/2 (0.0000) | n/a | 17.00 |
| code_like | 1 | 1/1 (1.0000) | 2/2 (1.0000) | 13.00 |
| code_mixed | 1 | 1/1 (1.0000) | 1/1 (1.0000) | 9.00 |
| english_apostrophe | 1 | 1/1 (1.0000) | n/a | 9.00 |
| english_passthrough | 1 | 1/1 (1.0000) | 2/2 (1.0000) | 9.00 |
| european_apostrophe | 1 | 1/1 (1.0000) | n/a | 6.00 |
| informal | 2 | 2/2 (1.0000) | n/a | 4.50 |
| kazakh_cyrillic | 1 | 0/1 (0.0000) | n/a | 35.00 |
| kyrgyz_cyrillic | 1 | 0/1 (0.0000) | n/a | 31.00 |
| negative_word | 1 | 1/1 (1.0000) | n/a | 5.00 |
| numbers_dates | 3 | 3/3 (1.0000) | 4/4 (1.0000) | 7.67 |
| protected_file | 2 | 2/2 (1.0000) | 2/2 (1.0000) | 8.00 |
| protected_file_date | 1 | 1/1 (1.0000) | 2/2 (1.0000) | 6.00 |
| protected_url | 1 | 1/1 (1.0000) | 1/1 (1.0000) | 7.00 |
| punctuation_mixed | 1 | 1/1 (1.0000) | n/a | 7.00 |
| punctuation_unicode | 1 | 1/1 (1.0000) | n/a | 7.00 |
| tatar_cyrillic | 1 | 0/1 (0.0000) | n/a | 36.00 |
| turkish_apostrophe | 1 | 1/1 (1.0000) | 1/1 (1.0000) | 9.00 |
| turkish_i_case | 1 | 1/1 (1.0000) | n/a | 10.00 |
| url_code_mixed | 1 | 1/1 (1.0000) | 3/3 (1.0000) | 4.00 |
| uzbek_apostrophe | 2 | 0/2 (0.0000) | 0/5 (0.0000) | 11.00 |

## BROKEN PROTECTED SPANS

- category: `uzbek_apostrophe`
  text: `Oʻzbekistonning poytaxti Toshkent.`
  broken_span: `Oʻzbekistonning`
  tokens: `["▁O","ʻ","▁zbekistonning","▁poytaxti","▁Toshkent","."]`
- category: `uzbek_apostrophe`
  text: `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
  broken_span: `Oʻzbekcha`
  tokens: `["▁O","ʻ","▁zbekcha",":","▁g","ʻ","▁isht",",","▁san","'","+at",",","▁ma","'","+no","."]`
- category: `uzbek_apostrophe`
  text: `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
  broken_span: `gʻisht`
  tokens: `["▁O","ʻ","▁zbekcha",":","▁g","ʻ","▁isht",",","▁san","'","+at",",","▁ma","'","+no","."]`
- category: `uzbek_apostrophe`
  text: `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
  broken_span: `sanʼat`
  tokens: `["▁O","ʻ","▁zbekcha",":","▁g","ʻ","▁isht",",","▁san","'","+at",",","▁ma","'","+no","."]`
- category: `uzbek_apostrophe`
  text: `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
  broken_span: `maʼno`
  tokens: `["▁O","ʻ","▁zbekcha",":","▁g","ʻ","▁isht",",","▁san","'","+at",",","▁ma","'","+no","."]`

## SAMPLE TOKENIZATIONS

### turkish_apostrophe

Text: `İstanbul'da 2026'da yaşıyorum.`

Tokens:

```json
["▁İstanbul","'","+da","▁2026","'","+da","▁yaşıyor","+um","."]
```

Decoded: `İstanbul'da 2026'da yaşıyorum.`

Roundtrip exact: `True`

### turkish_i_case

Text: `Iğdır'ın ışığı ile İzmir'in inciri.`

Tokens:

```json
["▁Iğdır","'","+ın","▁ışığı","▁ile","▁İzmir","'","+in","▁inciri","."]
```

Decoded: `Iğdır'ın ışığı ile İzmir'in inciri.`

Roundtrip exact: `True`

### numbers_dates

Text: `Toplantı 19.05.2026 saat 14:30'da başlayacak.`

Tokens:

```json
["▁Toplantı","▁19.05.2026","▁saat","▁14:30","'","+da","▁başla","+yacak","."]
```

Decoded: `Toplantı 19.05.2026 saat 14:30'da başlayacak.`

Roundtrip exact: `True`

### numbers_dates

Text: `3.14 değerini yazdım.`

Tokens:

```json
["▁3.14","▁değer","+i","+ni","▁yaz","+dı","+m","."]
```

Decoded: `3.14 değerini yazdım.`

Roundtrip exact: `True`

### numbers_dates

Text: `34-ABC-1907 plakası vardı.`

Tokens:

```json
["▁34-ABC-1907","▁plaka","+sı","▁var","+dı","."]
```

Decoded: `34-ABC-1907 plakası vardı.`

Roundtrip exact: `True`

### protected_file

Text: `README.md'yi açtın mı?`

Tokens:

```json
["▁README.md","'","+yi","▁aç","+tı","+n","▁mı","?"]
```

Decoded: `README.md'yi açtın mı?`

Roundtrip exact: `True`

### protected_file

Text: `config_v2.json dosyasını açtım.`

Tokens:

```json
["▁config_v2.json","▁dosya","+sı","+nı","▁aç","+tı","+m","."]
```

Decoded: `config_v2.json dosyasını açtım.`

Roundtrip exact: `True`

### protected_url

Text: `Bilgi için https://example.com/tr/sayfa adresine bakın.`

Tokens:

```json
["▁Bilgi","▁için","▁https://example.com/tr/sayfa","▁adresine","▁bak","+ın","."]
```

Decoded: `Bilgi için https://example.com/tr/sayfa adresine bakın.`

Roundtrip exact: `True`

### protected_file_date

Text: `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`

Tokens:

```json
["▁file_v2.0.txt","▁2026-05-19","▁tarihin","+de","▁güncellendi","."]
```

Decoded: `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`

Roundtrip exact: `True`

### code_like

Text: `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`

Tokens:

```json
["▁def","▁kullanici_adi","(","▁ad",")",":","▁return","▁ad.strip","(",")","#","▁Türkçe","▁örnek"]
```

Decoded: `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`

Roundtrip exact: `True`

### english_passthrough

Text: `The quick brown fox updates file_v2.0.txt on 2026-05-19.`

Tokens:

```json
["▁The","▁quick","▁brown","▁fox","▁updates","▁file_v2.0.txt","▁on","▁2026-05-19","."]
```

Decoded: `The quick brown fox updates file_v2.0.txt on 2026-05-19.`

Roundtrip exact: `True`

### english_apostrophe

Text: `Don't split John's book.`

Tokens:

```json
["▁Don","'","+t","▁split","▁John","'","+s","▁book","."]
```

Decoded: `Don't split John's book.`

Roundtrip exact: `True`

### european_apostrophe

Text: `Je viens d'Istanbul.`

Tokens:

```json
["▁Je","▁viens","▁d","'","+Istanbul","."]
```

Decoded: `Je viens d'Istanbul.`

Roundtrip exact: `True`

### uzbek_apostrophe

Text: `Oʻzbekistonning poytaxti Toshkent.`

Tokens:

```json
["▁O","ʻ","▁zbekistonning","▁poytaxti","▁Toshkent","."]
```

Decoded: `O ʻ zbekistonning poytaxti Toshkent.`

Roundtrip exact: `False`

### uzbek_apostrophe

Text: `Oʻzbekcha: gʻisht, sanʼat, maʼno.`

Tokens:

```json
["▁O","ʻ","▁zbekcha",":","▁g","ʻ","▁isht",",","▁san","'","+at",",","▁ma","'","+no","."]
```

Decoded: `O ʻ zbekcha: g ʻ isht, san'at, ma'no.`

Roundtrip exact: `False`

### azerbaijani

Text: `Mənim adım Əli, Bakıda yaşayıram.`

Tokens:

```json
["▁M","ə","▁nim","▁ad","+ım","Ə","▁li",",","▁Bak","+ı","+da","▁yaşayıram","."]
```

Decoded: `M ə nim adım Ə li, Bakıda yaşayıram.`

Roundtrip exact: `False`

### azerbaijani

Text: `Xəbər: qız məktəbə gedir, dağ yolu uzundur.`

Tokens:

```json
["▁X","ə","▁b","ə","▁r",":","▁qız","▁m","ə","▁kt","ə","▁b","ə","▁ge","+dir",",","▁dağ","▁yolu","▁uzun","+dur","."]
```

Decoded: `X ə b ə r: qız m ə kt ə b ə gedir, dağ yolu uzundur.`

Roundtrip exact: `False`

### kazakh_cyrillic

Text: `Қазақстан Республикасы — Алматы қаласы.`

Tokens:

```json
["Қ","а","з","а","қ","с","т","а","н","Р","е","с","п","у","б","л","и","к","а","с","ы","-","А","л","м","а","т","ы","қ","а","л","а","с","ы","."]
```

Decoded: `Қ а з а қ с т а н Р е с п у б л и к а с ы - А л м а т ы қ а л а с ы.`

Roundtrip exact: `False`

### kyrgyz_cyrillic

Text: `Кыргызча: тоо, суу, өң, үн, жаңы күн.`

Tokens:

```json
["К","ы","р","г","ы","з","ч","а",":","т","о","о",",","с","у","у",",","ө","ң",",","ү","н",",","ж","а","ң","ы","к","ү","н","."]
```

Decoded: `К ы р г ы з ч а: т о о, с у у, ө ң, ү н, ж а ң ы к ү н.`

Roundtrip exact: `False`

### tatar_cyrillic

Text: `Татарча: әни, җил, күңел, өч, үрдәк, һава.`

Tokens:

```json
["Т","а","т","а","р","ч","а",":","ә","н","и",",","җ","и","л",",","к","ү","ң","е","л",",","ө","ч",",","ү","р","д","ә","к",",","һ","а","в","а","."]
```

Decoded: `Т а т а р ч а: ә н и, җ и л, к ү ң е л, ө ч, ү р д ә к, һ а в а.`

Roundtrip exact: `False`

### punctuation_unicode

Text: `“Merhaba,” dedi.`

Tokens:

```json
["“","▁Merhaba",",","”","▁de","+di","."]
```

Decoded: `“Merhaba,” dedi.`

Roundtrip exact: `True`

### punctuation_mixed

Text: `Evet; ama sonra döndü.`

Tokens:

```json
["▁Evet",";","▁ama","▁sonra","▁dön","+dü","."]
```

Decoded: `Evet; ama sonra döndü.`

Roundtrip exact: `True`

### negative_word

Text: `Kadın yakın altın kedi.`

Tokens:

```json
["▁Kadın","▁yakın","▁altın","▁kedi","."]
```

Decoded: `Kadın yakın altın kedi.`

Roundtrip exact: `True`

### ambiguity

Text: `Yazın tatile gittik.`

Tokens:

```json
["▁Yaz","+ın","▁tatile","▁git","+ti","+k","."]
```

Decoded: `Yazın tatile gittik.`

Roundtrip exact: `True`

### informal

Text: `Gelicem birazdan.`

Tokens:

```json
["▁Gel","+icem","▁biraz","+dan","."]
```

Decoded: `Gelicem birazdan.`

Roundtrip exact: `True`

### informal

Text: `Napıyorsun?`

Tokens:

```json
["▁Napı","+yor","+sun","?"]
```

Decoded: `Napıyorsun?`

Roundtrip exact: `True`

### code_mixed

Text: `API'den data aldım.`

Tokens:

```json
["▁API","'","+den","▁da","+ta","▁al","+dı","+m","."]
```

Decoded: `API'den data aldım.`

Roundtrip exact: `True`

### url_code_mixed

Text: `https://example.com/2024-05-19 dosya.py 1234.56 TL`

Tokens:

```json
["▁https://example.com/2024-05-19","▁dosya.py","▁1234.56","▁TL"]
```

Decoded: `https://example.com/2024-05-19 dosya.py 1234.56 TL`

Roundtrip exact: `True`

