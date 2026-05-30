# Protected Span Baseline Report

Tokenizer behavior is not changed by this report.

## Summary

| Model | Status | Examples | Protected preserved | Broken | Break rate | Avg tokens/example | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 28 | 23/23 (1.0000) | 0 | 0.0000 | 7.9643 | 1.5274 |  |
| unicode_char | ok | 28 | 0/23 (0.0000) | 23 | 1.0000 | 29.1786 | 5.5959 |  |
| toy_bpe_1000 | ok | 28 | 1/23 (0.0435) | 22 | 0.9565 | 20.0000 | 3.8356 |  |
| qwen | ok | 28 | 1/23 (0.0435) | 22 | 0.9565 | 15.3214 | 2.9384 |  |
| mistral | ok | 28 | 1/23 (0.0435) | 22 | 0.9565 | 18.7500 | 3.5959 |  |
| llama | ok | 28 | 1/23 (0.0435) | 22 | 0.9565 | 14.2500 | 2.7329 |  |
| sp_bpe | ok | 28 | 1/23 (0.0435) | 22 | 0.9565 | 18.0714 | 3.4658 |  |
| sp_unigram | ok | 28 | 0/23 (0.0000) | 23 | 1.0000 | 19.3214 | 3.7055 |  |

## Category Summary

| Category | custom_tr_morph | unicode_char | toy_bpe_1000 | qwen | mistral | llama | sp_bpe | sp_unigram |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| code_like | 2/2 (1.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) |
| code_mixed | 1/1 (1.0000) | 0/1 (0.0000) | 1/1 (1.0000) | 1/1 (1.0000) | 1/1 (1.0000) | 1/1 (1.0000) | 1/1 (1.0000) | 0/1 (0.0000) |
| english_passthrough | 2/2 (1.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) |
| numbers_dates | 4/4 (1.0000) | 0/4 (0.0000) | 0/4 (0.0000) | 0/4 (0.0000) | 0/4 (0.0000) | 0/4 (0.0000) | 0/4 (0.0000) | 0/4 (0.0000) |
| protected_file | 2/2 (1.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) |
| protected_file_date | 2/2 (1.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) |
| protected_url | 1/1 (1.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) |
| turkish_apostrophe | 1/1 (1.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) | 0/1 (0.0000) |
| url_code_mixed | 3/3 (1.0000) | 0/3 (0.0000) | 0/3 (0.0000) | 0/3 (0.0000) | 0/3 (0.0000) | 0/3 (0.0000) | 0/3 (0.0000) | 0/3 (0.0000) |
| uzbek_apostrophe | 5/5 (1.0000) | 0/5 (0.0000) | 0/5 (0.0000) | 0/5 (0.0000) | 0/5 (0.0000) | 0/5 (0.0000) | 0/5 (0.0000) | 0/5 (0.0000) |

## Broken Protected Spans

### unicode_char

- `turkish_apostrophe` span `2026` in `İstanbul'da 2026'da yaşıyorum.`
- `numbers_dates` span `19.05.2026` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `14:30` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `3.14` in `3.14 değerini yazdım.`
- `numbers_dates` span `34-ABC-1907` in `34-ABC-1907 plakası vardı.`
- `protected_file` span `README.md` in `README.md'yi açtın mı?`
- `protected_file` span `config_v2.json` in `config_v2.json dosyasını açtım.`
- `protected_url` span `https://example.com/tr/sayfa` in `Bilgi için https://example.com/tr/sayfa adresine bakın.`
- `protected_file_date` span `file_v2.0.txt` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `protected_file_date` span `2026-05-19` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `code_like` span `kullanici_adi` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `code_like` span `ad.strip` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `english_passthrough` span `file_v2.0.txt` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `english_passthrough` span `2026-05-19` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `uzbek_apostrophe` span `Oʻzbekistonning` in `Oʻzbekistonning poytaxti Toshkent.`
- `uzbek_apostrophe` span `Oʻzbekcha` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `gʻisht` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `sanʼat` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `maʼno` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `code_mixed` span `API` in `API'den data aldım.`
- `url_code_mixed` span `https://example.com/2024-05-19` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `dosya.py` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `1234.56` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`

### toy_bpe_1000

- `turkish_apostrophe` span `2026` in `İstanbul'da 2026'da yaşıyorum.`
- `numbers_dates` span `19.05.2026` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `14:30` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `3.14` in `3.14 değerini yazdım.`
- `numbers_dates` span `34-ABC-1907` in `34-ABC-1907 plakası vardı.`
- `protected_file` span `README.md` in `README.md'yi açtın mı?`
- `protected_file` span `config_v2.json` in `config_v2.json dosyasını açtım.`
- `protected_url` span `https://example.com/tr/sayfa` in `Bilgi için https://example.com/tr/sayfa adresine bakın.`
- `protected_file_date` span `file_v2.0.txt` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `protected_file_date` span `2026-05-19` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `code_like` span `kullanici_adi` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `code_like` span `ad.strip` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `english_passthrough` span `file_v2.0.txt` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `english_passthrough` span `2026-05-19` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `uzbek_apostrophe` span `Oʻzbekistonning` in `Oʻzbekistonning poytaxti Toshkent.`
- `uzbek_apostrophe` span `Oʻzbekcha` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `gʻisht` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `sanʼat` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `maʼno` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `url_code_mixed` span `https://example.com/2024-05-19` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `dosya.py` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `1234.56` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`

### qwen

- `turkish_apostrophe` span `2026` in `İstanbul'da 2026'da yaşıyorum.`
- `numbers_dates` span `19.05.2026` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `14:30` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `3.14` in `3.14 değerini yazdım.`
- `numbers_dates` span `34-ABC-1907` in `34-ABC-1907 plakası vardı.`
- `protected_file` span `README.md` in `README.md'yi açtın mı?`
- `protected_file` span `config_v2.json` in `config_v2.json dosyasını açtım.`
- `protected_url` span `https://example.com/tr/sayfa` in `Bilgi için https://example.com/tr/sayfa adresine bakın.`
- `protected_file_date` span `file_v2.0.txt` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `protected_file_date` span `2026-05-19` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `code_like` span `kullanici_adi` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `code_like` span `ad.strip` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `english_passthrough` span `file_v2.0.txt` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `english_passthrough` span `2026-05-19` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `uzbek_apostrophe` span `Oʻzbekistonning` in `Oʻzbekistonning poytaxti Toshkent.`
- `uzbek_apostrophe` span `Oʻzbekcha` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `gʻisht` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `sanʼat` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `maʼno` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `url_code_mixed` span `https://example.com/2024-05-19` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `dosya.py` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `1234.56` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`

### mistral

- `turkish_apostrophe` span `2026` in `İstanbul'da 2026'da yaşıyorum.`
- `numbers_dates` span `19.05.2026` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `14:30` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `3.14` in `3.14 değerini yazdım.`
- `numbers_dates` span `34-ABC-1907` in `34-ABC-1907 plakası vardı.`
- `protected_file` span `README.md` in `README.md'yi açtın mı?`
- `protected_file` span `config_v2.json` in `config_v2.json dosyasını açtım.`
- `protected_url` span `https://example.com/tr/sayfa` in `Bilgi için https://example.com/tr/sayfa adresine bakın.`
- `protected_file_date` span `file_v2.0.txt` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `protected_file_date` span `2026-05-19` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `code_like` span `kullanici_adi` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `code_like` span `ad.strip` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `english_passthrough` span `file_v2.0.txt` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `english_passthrough` span `2026-05-19` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `uzbek_apostrophe` span `Oʻzbekistonning` in `Oʻzbekistonning poytaxti Toshkent.`
- `uzbek_apostrophe` span `Oʻzbekcha` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `gʻisht` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `sanʼat` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `maʼno` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `url_code_mixed` span `https://example.com/2024-05-19` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `dosya.py` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `1234.56` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`

### llama

- `turkish_apostrophe` span `2026` in `İstanbul'da 2026'da yaşıyorum.`
- `numbers_dates` span `19.05.2026` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `14:30` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `3.14` in `3.14 değerini yazdım.`
- `numbers_dates` span `34-ABC-1907` in `34-ABC-1907 plakası vardı.`
- `protected_file` span `README.md` in `README.md'yi açtın mı?`
- `protected_file` span `config_v2.json` in `config_v2.json dosyasını açtım.`
- `protected_url` span `https://example.com/tr/sayfa` in `Bilgi için https://example.com/tr/sayfa adresine bakın.`
- `protected_file_date` span `file_v2.0.txt` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `protected_file_date` span `2026-05-19` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `code_like` span `kullanici_adi` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `code_like` span `ad.strip` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `english_passthrough` span `file_v2.0.txt` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `english_passthrough` span `2026-05-19` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `uzbek_apostrophe` span `Oʻzbekistonning` in `Oʻzbekistonning poytaxti Toshkent.`
- `uzbek_apostrophe` span `Oʻzbekcha` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `gʻisht` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `sanʼat` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `maʼno` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `url_code_mixed` span `https://example.com/2024-05-19` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `dosya.py` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `1234.56` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`

### sp_bpe

- `turkish_apostrophe` span `2026` in `İstanbul'da 2026'da yaşıyorum.`
- `numbers_dates` span `19.05.2026` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `14:30` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `3.14` in `3.14 değerini yazdım.`
- `numbers_dates` span `34-ABC-1907` in `34-ABC-1907 plakası vardı.`
- `protected_file` span `README.md` in `README.md'yi açtın mı?`
- `protected_file` span `config_v2.json` in `config_v2.json dosyasını açtım.`
- `protected_url` span `https://example.com/tr/sayfa` in `Bilgi için https://example.com/tr/sayfa adresine bakın.`
- `protected_file_date` span `file_v2.0.txt` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `protected_file_date` span `2026-05-19` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `code_like` span `kullanici_adi` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `code_like` span `ad.strip` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `english_passthrough` span `file_v2.0.txt` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `english_passthrough` span `2026-05-19` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `uzbek_apostrophe` span `Oʻzbekistonning` in `Oʻzbekistonning poytaxti Toshkent.`
- `uzbek_apostrophe` span `Oʻzbekcha` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `gʻisht` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `sanʼat` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `maʼno` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `url_code_mixed` span `https://example.com/2024-05-19` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `dosya.py` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `1234.56` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`

### sp_unigram

- `turkish_apostrophe` span `2026` in `İstanbul'da 2026'da yaşıyorum.`
- `numbers_dates` span `19.05.2026` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `14:30` in `Toplantı 19.05.2026 saat 14:30'da başlayacak.`
- `numbers_dates` span `3.14` in `3.14 değerini yazdım.`
- `numbers_dates` span `34-ABC-1907` in `34-ABC-1907 plakası vardı.`
- `protected_file` span `README.md` in `README.md'yi açtın mı?`
- `protected_file` span `config_v2.json` in `config_v2.json dosyasını açtım.`
- `protected_url` span `https://example.com/tr/sayfa` in `Bilgi için https://example.com/tr/sayfa adresine bakın.`
- `protected_file_date` span `file_v2.0.txt` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `protected_file_date` span `2026-05-19` in `file_v2.0.txt 2026-05-19 tarihinde güncellendi.`
- `code_like` span `kullanici_adi` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `code_like` span `ad.strip` in `def kullanici_adi(ad): return ad.strip() # Türkçe örnek`
- `english_passthrough` span `file_v2.0.txt` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `english_passthrough` span `2026-05-19` in `The quick brown fox updates file_v2.0.txt on 2026-05-19.`
- `uzbek_apostrophe` span `Oʻzbekistonning` in `Oʻzbekistonning poytaxti Toshkent.`
- `uzbek_apostrophe` span `Oʻzbekcha` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `gʻisht` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `sanʼat` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `uzbek_apostrophe` span `maʼno` in `Oʻzbekcha: gʻisht, sanʼat, maʼno.`
- `code_mixed` span `API` in `API'den data aldım.`
- `url_code_mixed` span `https://example.com/2024-05-19` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `dosya.py` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`
- `url_code_mixed` span `1234.56` in `https://example.com/2024-05-19 dosya.py 1234.56 TL`


## Notes

- A span is preserved when it appears as a single tokenizer token after removing common word-start markers.
- This is stricter than boundary F1 and is intended for code/file/URL/number and explicitly protected smoke spans.
- It should not be read as a general word-level quality metric.
