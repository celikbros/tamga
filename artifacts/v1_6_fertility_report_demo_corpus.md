# Natural Corpus Fertility Report

Tokenizer behavior is not changed by this report.

## Summary

| Model | Status | Lines | Words | Tokens | Avg tokens/line | Avg tokens/word | Max line tokens/word | Protected preserved | Break rate | Unknown/byte tokens | Unknown/byte rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 310 | 1326 | 2575 | 8.3065 | 1.9419 | 4.3333 | 16/16 (1.0000) | 0.0000 | 0 | 0.0000 |  |
| unicode_char | ok | 310 | 1326 | 9164 | 29.5613 | 6.9110 | 13.0000 | 0/16 (0.0000) | 1.0000 | 0 | 0.0000 |  |
| toy_bpe_1000 | ok | 310 | 1326 | 2911 | 9.3903 | 2.1953 | 4.0000 | 0/16 (0.0000) | 1.0000 | 0 | 0.0000 |  |
| qwen | ok | 310 | 1326 | 3738 | 12.0581 | 2.8190 | 5.0000 | 0/16 (0.0000) | 1.0000 | 0 | 0.0000 |  |
| mistral | ok | 310 | 1326 | 5212 | 16.8129 | 3.9306 | 7.6667 | 0/16 (0.0000) | 1.0000 | 0 | 0.0000 |  |
| llama | ok | 310 | 1326 | 3382 | 10.9097 | 2.5505 | 4.6667 | 0/16 (0.0000) | 1.0000 | 0 | 0.0000 |  |
| sp_bpe | ok | 310 | 1326 | 2930 | 9.4516 | 2.2097 | 4.0000 | 0/16 (0.0000) | 1.0000 | 0 | 0.0000 |  |
| sp_unigram | ok | 310 | 1326 | 3256 | 10.5032 | 2.4555 | 4.7500 | 0/16 (0.0000) | 1.0000 | 0 | 0.0000 |  |

## Highest Fertility Lines

### custom_tr_morph

- line 12: 4.3333 tokens/word, 13 tokens - `Evlerimizdekilerden birkaçını yeniledik.`
- line 13: 4.0000 tokens/word, 12 tokens - `Kitaplarımızdaki notları karşılaştırdık.`
- line 252: 4.0000 tokens/word, 12 tokens - `Dün evlerimizdekileri listeledik.`
- line 255: 4.0000 tokens/word, 12 tokens - `Akşam masalarımızdakileri temizledik.`
- line 18: 3.7500 tokens/word, 15 tokens - `Kalemlerimizdekilerden mavi olanı seçtik.`

### unicode_char

- line 61: 13.0000 tokens/word, 39 tokens - `OpenAIlaştırılamayan metinler listelendi.`
- line 12: 12.6667 tokens/word, 38 tokens - `Evlerimizdekilerden birkaçını yeniledik.`
- line 13: 12.6667 tokens/word, 38 tokens - `Kitaplarımızdaki notları karşılaştırdık.`
- line 258: 12.0000 tokens/word, 36 tokens - `Projelerimizdakilerden eskisi kapandı.`
- line 16: 11.6667 tokens/word, 35 tokens - `Çantalarımızdakileri masaya bıraktık.`

### toy_bpe_1000

- line 183: 4.0000 tokens/word, 16 tokens - `Kayseri'deki fuar kalabalıktı.`
- line 151: 4.0000 tokens/word, 12 tokens - `Kitabımın kapağı yıpranmıştı.`
- line 223: 3.7500 tokens/word, 15 tokens - `config_test.json ortamı tanımladı.`
- line 12: 3.6667 tokens/word, 11 tokens - `Evlerimizdekilerden birkaçını yeniledik.`
- line 14: 3.6667 tokens/word, 11 tokens - `Defterlerimizden sayfalar kopmadı.`

### qwen

- line 176: 5.0000 tokens/word, 20 tokens - `Hafta sonu klasörlerimizdekileri yedekledik.`
- line 255: 5.0000 tokens/word, 15 tokens - `Akşam masalarımızdakileri temizledik.`
- line 95: 4.7500 tokens/word, 19 tokens - `Akşam klasörlerimizdekilerden eskileri sildik.`
- line 100: 4.7500 tokens/word, 19 tokens - `Kayıtlarımızdakilerden hatalı olanı düzelttik.`
- line 177: 4.7500 tokens/word, 19 tokens - `Toplantıda fikirlerimizden bazıları tartışıldı.`

### mistral

- line 99: 7.6667 tokens/word, 23 tokens - `Çalışmalarımızdan sonuç çıkardık.`
- line 13: 7.3333 tokens/word, 22 tokens - `Kitaplarımızdaki notları karşılaştırdık.`
- line 179: 7.3333 tokens/word, 22 tokens - `Kayıtlarımızdan tarihleri çıkardık.`
- line 141: 7.0000 tokens/word, 21 tokens - `OpenAIlaştırılan başlıklar ayrıldı.`
- line 158: 7.0000 tokens/word, 21 tokens - `Kapağının kenarı kırılmıştı.`

### llama

- line 16: 4.6667 tokens/word, 14 tokens - `Çantalarımızdakileri masaya bıraktık.`
- line 61: 4.6667 tokens/word, 14 tokens - `OpenAIlaştırılamayan metinler listelendi.`
- line 13: 4.3333 tokens/word, 13 tokens - `Kitaplarımızdaki notları karşılaştırdık.`
- line 231: 4.3333 tokens/word, 13 tokens - `Kitabının sayfası yırtılmıştı.`
- line 100: 4.2500 tokens/word, 17 tokens - `Kayıtlarımızdakilerden hatalı olanı düzelttik.`

### sp_bpe

- line 223: 4.0000 tokens/word, 16 tokens - `config_test.json ortamı tanımladı.`
- line 151: 4.0000 tokens/word, 12 tokens - `Kitabımın kapağı yıpranmıştı.`
- line 143: 3.7500 tokens/word, 15 tokens - `config_prod.json değişiklikleri kaydetti.`
- line 148: 3.7500 tokens/word, 15 tokens - `settings_v5.json yapılandırmayı taşıdı.`
- line 183: 3.7500 tokens/word, 15 tokens - `Kayseri'deki fuar kalabalıktı.`

### sp_unigram

- line 65: 4.7500 tokens/word, 19 tokens - `README_new.md içeriği güncellendi.`
- line 143: 4.2500 tokens/word, 17 tokens - `config_prod.json değişiklikleri kaydetti.`
- line 148: 4.2500 tokens/word, 17 tokens - `settings_v5.json yapılandırmayı taşıdı.`
- line 145: 4.0000 tokens/word, 20 tokens - `README_final.md dosyasını gözden geçirdim.`
- line 223: 4.0000 tokens/word, 16 tokens - `config_test.json ortamı tanımladı.`

## Notes

- This is a corpus-level fertility report, not a morphology gold evaluation.
- `data/train/tr_bpe_train.txt` is a small demo corpus and is not a production benchmark.
- Protected candidates are auto-detected URL/file-like/numeric-like spans.
- Unknown/byte tokens are a coarse proxy for explicit fallback markers, not a full coverage proof.
