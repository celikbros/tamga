# Protected Span Baseline Report

Tokenizer behavior is not changed by this report.

## Summary

| Model | Status | Examples | Protected preserved | Broken | Break rate | Avg tokens/example | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 29 | 25/25 (1.0000) | 0 | 0.0000 | 7.8621 | 1.4805 |  |
| unicode_char | ok | 29 | 0/25 (0.0000) | 25 | 1.0000 | 29.7241 | 5.5974 |  |
| toy_bpe_1000 | ok | 29 | 1/25 (0.0400) | 24 | 0.9600 | 20.4828 | 3.8571 |  |
| qwen | ok | 29 | 1/25 (0.0400) | 24 | 0.9600 | 15.3448 | 2.8896 |  |
| mistral | ok | 29 | 1/25 (0.0400) | 24 | 0.9600 | 18.6897 | 3.5195 |  |
| llama | ok | 29 | 1/25 (0.0400) | 24 | 0.9600 | 14.2414 | 2.6818 |  |
| sp_bpe | ok | 29 | 1/25 (0.0400) | 24 | 0.9600 | 18.4483 | 3.4740 |  |
| sp_unigram | ok | 29 | 0/25 (0.0000) | 25 | 1.0000 | 19.7241 | 3.7143 |  |

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
| technical_comparator | 2/2 (1.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) | 0/2 (0.0000) |
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
- `technical_comparator` span `transformers>=4.40` in `Install transformers>=4.40 and tokenizers>=0.19.`
- `technical_comparator` span `tokenizers>=0.19` in `Install transformers>=4.40 and tokenizers>=0.19.`
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
- `technical_comparator` span `transformers>=4.40` in `Install transformers>=4.40 and tokenizers>=0.19.`
- `technical_comparator` span `tokenizers>=0.19` in `Install transformers>=4.40 and tokenizers>=0.19.`
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
- `technical_comparator` span `transformers>=4.40` in `Install transformers>=4.40 and tokenizers>=0.19.`
- `technical_comparator` span `tokenizers>=0.19` in `Install transformers>=4.40 and tokenizers>=0.19.`
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
- `technical_comparator` span `transformers>=4.40` in `Install transformers>=4.40 and tokenizers>=0.19.`
- `technical_comparator` span `tokenizers>=0.19` in `Install transformers>=4.40 and tokenizers>=0.19.`
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
- `technical_comparator` span `transformers>=4.40` in `Install transformers>=4.40 and tokenizers>=0.19.`
- `technical_comparator` span `tokenizers>=0.19` in `Install transformers>=4.40 and tokenizers>=0.19.`
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
- `technical_comparator` span `transformers>=4.40` in `Install transformers>=4.40 and tokenizers>=0.19.`
- `technical_comparator` span `tokenizers>=0.19` in `Install transformers>=4.40 and tokenizers>=0.19.`
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
- `technical_comparator` span `transformers>=4.40` in `Install transformers>=4.40 and tokenizers>=0.19.`
- `technical_comparator` span `tokenizers>=0.19` in `Install transformers>=4.40 and tokenizers>=0.19.`
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
