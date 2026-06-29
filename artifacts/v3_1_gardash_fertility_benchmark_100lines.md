# v3.1 Gardaş Fertility Benchmark

Config: `C:/CELIK-GARDASH/configs/tokenizer_v3_0/v3_0_gardash_sidecar.toml`
Tokenizer: `sp64_protected_passthrough_sidecar`
Corpus: `C:/CELIK-GARDASH/datasets/tokenizer_v3_0/real_mix_60k_sample.txt`

This report measures the actual v3 handoff encode path, including the
finite protected passthrough sidecar configuration and UTF-8 byte fallback.
EOS is not counted in fertility.

## Requested Sentences

| Text | Words | Tokens | Tokens/word | Tokens/byte | Fallback tokens | Pieces |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Türkiye'nin başkenti Ankara'dır. | 3 | 8 | 2.6667 | 0.228571 | 0 | `▁Türkiye` `'` `nin` `▁başkenti` `▁Ankara` `'` `dır` `.` |
| Mercimek çorbası Türk mutfağının vazgeçilmezidir. | 5 | 9 | 1.8000 | 0.160714 | 0 | `▁Mercimek` `▁çorba` `sı` `▁Türk` `▁mutfağı` `nın` `▁vazgeçilmez` `idir` `.` |
| görüşebileceklerimizdenmisiniz | 1 | 5 | 5.0000 | 0.151515 | 0 | `▁görüş` `ebilecekleri` `mizden` `mi` `siniz` |
| güneşli | 1 | 2 | 2.0000 | 0.222222 | 0 | `▁güneş` `li` |
| The quick brown fox jumps over the lazy dog. | 9 | 15 | 1.6667 | 0.340909 | 0 | `▁The` `▁quick` `▁br` `own` `▁fo` `x` `▁jump` `s` `▁over` `▁the` `▁l` `az` `y` `▁dog` `.` |

## Corpus Summary

| Lines | Words | Bytes | Tokens | Tokens/word | Tokens/byte | Fallback tokens | Fallback rate | Max line tokens/word |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 33904 | 295821 | 51745 | 1.526221 | 0.174920 | 27 | 0.000522 | 2.166667 |

## Highest-Fertility Lines

| Tokens/word | Tokens | Words | Text prefix |
| ---: | ---: | ---: | --- |
| 2.166667 | 104 | 48 | Dışişleri Bakanı Hakan Fidan, Türkiye-Mısır-Pakistan-Suudi Arabistan Dışişleri Bakanları Toplantısı'na katılmak üzere bulunduğu Pakistan'da temaslarını sürdürüyor. Bakan Fidan, "Türkiye-Mısır-Pakistan-Suudi Arabistan Dış |
| 1.960432 | 545 | 278 | Tüpraş Stadı'nda oynanan maçta taraftar desteğini arkasına alan milli takım, mücadelenin ilk yarısında rakibine karşı baskın bir oyun ortaya koysa da hücumda etkili olamadı. İlk 45 dakikada gol sesi çıkmazken ay-yıldızlı |
| 1.875000 | 30 | 16 | Dışişleri Bakanlığının Nsosyal hesabından yapılan paylaşıma göre Bakan Fidan, başkent İslamabad'da Mısırlı mevkidaşı Abdulati ile görüştü. |
| 1.803030 | 119 | 66 | İstanbul Cumhuriyet Başsavcılığınca, İBB'ye yönelik "suç örgütü yöneticisi olmak", "suç örgütüne üye olmak", "irtikap", "rüşvet", "nitelikli dolandırıcılık", "kişisel verileri hukuka aykırı ele geçirmek" ve "ihaleye fesa |
| 1.789474 | 204 | 114 | Çevre, Şehircilik ve İklim Değişikliği Bakanı Murat Kurum, sosyal medya hesabından, Uluslararası Sıfır Atık Günü'ne ilişkin paylaşım yaptı. Bakan Kurum, şunları kaydetti: "Azalt, paylaş, dönüştür. Gıda israfı sadece bugü |
| 1.788462 | 186 | 104 | NATO'nun sosyal medya hesabından yapılan paylaşımda, "Ankara'da düzenlenecek 2026 NATO Zirvesi'ne 100 gün kaldı." denildi. ????️ 100 days to go until the 2026 #NATOsummit in Ankara, Türkiye ??? This is the second time Tü |
| 1.787330 | 395 | 221 | Türkiye Yüzme Federasyonunun açıklamasına göre Çekya'nın başkenti Prag'da düzenlenen Multinations Gençler Yüzme Şampiyonası'nda Emre Onuş, 200 metre karışık erkeklerde 2:00.55'lik derecesi ile altın madalya elde etti. De |
| 1.779310 | 516 | 290 | Ankara Cumhuriyet Başsavcılığınca hazırlanan iddianamede, Yenimahalle ilçesinde, 2 Şubat'ta aracını muayene ettirmek için TÜVTÜRK'ün Yenimahalle ilçesi İvedik Araç Muayene İstasyonu'na giden polis memuru Melih Okan Keski |
| 1.759615 | 183 | 104 | Başsavcılıktan yapılan açıklamaya göre, Sayıştay Başkanlığı tarafından Etimesgut Belediye Başkanlığında gerçekleştirilen 2025 yılı hesap ve işlemleri olağan denetimleri sırasında, aşevi, yemek alımı ve dağıtımı işlemleri |
| 1.758621 | 204 | 116 | Emine Erdoğan, 30 Mart Uluslararası Sıfır Atık Günü dolayısıyla sosyal medya hesabından paylaşımda bulundu. Bu sene "Gıda İsrafı" temasıyla 4'üncü yılını kutladığımız 30 Mart #UluslararasıSıfırAtıkGünü, görünmeyen bir ka |

## Reading

- Corpus-level fertility should be read together with BPB and fallback rate.
- Very high line fertility is mostly caused by corpus formatting issues such as glued text without spaces.
- Morphological stress words can still have high fertility even when corpus-level average is acceptable.
- This report does not decide the final vocab size; it is an input to the 32K/48K/64K ablation.
