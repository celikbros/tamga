# v3.1 Gardaş Fertility Benchmark

Config: `configs/v3_1_sidecar_sp64k_retrained.toml`
Tokenizer: `sp64k_retrained_protected_passthrough_sidecar`
Corpus: `C:/CELIK-GARDASH/datasets/tokenizer_v3_4_sample/stratified_480mb.txt`

This report measures the actual v3 handoff encode path, including the
finite protected passthrough sidecar configuration and UTF-8 byte fallback.
EOS is not counted in fertility.

## Requested Sentences

| Text | Words | Tokens | Tokens/word | Tokens/byte | Fallback tokens | Pieces |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Türkiye'nin başkenti Ankara'dır. | 3 | 8 | 2.6667 | 0.228571 | 0 | `▁Türkiye` `'` `nin` `▁başkenti` `▁Ankara` `'` `dır` `.` |
| Mercimek çorbası Türk mutfağının vazgeçilmezidir. | 5 | 8 | 1.6000 | 0.142857 | 0 | `▁Mercimek` `▁çorbası` `▁Türk` `▁mutfağı` `nın` `▁vazgeçilmez` `idir` `.` |
| görüşebileceklerimizdenmisiniz | 1 | 5 | 5.0000 | 0.151515 | 0 | `▁görüş` `ebilecek` `lerimizden` `mi` `siniz` |
| güneşli | 1 | 2 | 2.0000 | 0.222222 | 0 | `▁güneş` `li` |
| The quick brown fox jumps over the lazy dog. | 9 | 18 | 2.0000 | 0.409091 | 0 | `▁The` `▁quick` `▁b` `r` `ow` `n` `▁fo` `x` `▁jump` `s` `▁over` `▁the` `▁la` `z` `y` `▁do` `g` `.` |

## Corpus Summary

| Lines | Words | Bytes | Tokens | Tokens/word | Tokens/byte | Fallback tokens | Fallback rate | Max line tokens/word |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50000 | 5880443 | 48942124 | 9889370 | 1.681739 | 0.202063 | 50325 | 0.005089 | 45.000000 |

## Highest-Fertility Lines

| Tokens/word | Tokens | Words | Text prefix |
| ---: | ---: | ---: | --- |
| 45.000000 | 45 | 1 | leftarm1=7EC9E4\|body1=7EC9E4\|rightarm1=7EC9E4\|shorts1=000000\|socks1=000000\| |
| 37.000000 | 37 | 1 | leftarm2=FFFFFF\|body2=FFFFFF\|rightarm2=FFFFFF\|shorts2=000000\|socks2=000000\| |
| 34.000000 | 34 | 1 | ucmaz.home.uludag.edu.tr/PDF/ilh/2003-12(1)/M8.pdf‎ |
| 29.000000 | 58 | 2 | - https://web.archive.org/web/20081023024627/http://www.donanimhaber.com/NewsDetail.aspx?Id=11282 |
| 24.000000 | 72 | 3 | Y-Chromosome - *https://web.archive.org/web/20040728005528/http://www.scs.uiuc.edu/~mcdonald/WorldHaplogroupsMaps.pdf |
| 17.500000 | 35 | 2 | Mail::to($user->email)->send(new App\Mail\WelcomeMessage); |
| 17.333333 | 52 | 3 | +---+---+---+---+---+---+---+---+---+---+---+---+ Sayılar ekseni |
| 16.000000 | 96 | 6 | Medyaradar.com Röportajı (14 Ağustos 2012) https://web.archive.org/web/20120815222344/http://www.medyaradar.com/haber/konusanlarkonusulanlar-84607/dogan-grubu-hic-para-harcamadan-en-cok-geliri-postadan-kazaniyor.html |
| 14.000000 | 42 | 3 | Resmi Sitesi http://www.yashrajfilms.com/microsites/rnbdjmicro/rnbdj.html |
| 10.800000 | 54 | 5 | Coisas Pequenas (Small Things): http://www.youtube.com/watch?v=1vZpw6SlK5A&feature=related |
| 10.500000 | 42 | 4 | IIA (hızlı kasılma)-----hızlı-----------------50 milisaniye--------hızlı |
| 9.500000 | 57 | 6 | Биография на сайте Агентства экономической информации |
| 8.818182 | 97 | 11 | "Solcu Kardeşime Mektup" (Köşe yazısı), 2013, Hasan Hüseyin Sünbül, http://www.radikal.com.tr/yorum/bir_ulkucuden_solcu_kardesine_mektup-1149154, http://hhsunbul.blogspot.com.tr/2014/09/solcu-kardesime-mektup.html |
| 8.666667 | 52 | 6 | Благовеста Иванова. Българските старини в Цариград |
| 8.363636 | 92 | 11 | Buddhist Encyclopedia (n.d.). Seven Sets. Retrieved from "Buddhist Encyclopedia" at https://web.archive.org/web/20081020141018/http://buddhism.2be.net/Seven_Sets. |
| 7.888889 | 142 | 18 | Watson, John B. Psychological Care of Infant and Child. New York: W. W. Norton & Co., 1928. http://books.google.com/books?id=BadqAAAAMAAJ&q=john+watson+psychological+care&dq=john+watson+psychological+care&hl=en&sa=X&ei=L |
| 7.714286 | 54 | 7 | Chevallier, Jacques, "Hukuk Devleti", İmaj Yay. 2010.http://www.kitapyurdu.com/kitap/default.asp?id=572175&sa=140323124 |
| 7.666667 | 23 | 3 | option domain-name-servers 192.168.1.1,192.168.1.2; |
| 7.625000 | 61 | 8 | a great number of Pinker's articles in https://web.archive.org/web/20060118201913/http://pinker.wjh.harvard.edu/articles/ |
| 7.600000 | 38 | 5 | New American Bible - http://www.usccb.org/nab/bible/malachi/malachi1.htm |

## Reading

- Corpus-level fertility should be read together with BPB and fallback rate.
- Very high line fertility is mostly caused by corpus formatting issues such as glued text without spaces.
- Morphological stress words can still have high fertility even when corpus-level average is acceptable.
- This report does not decide the final vocab size; it is an input to the 32K/48K/64K ablation.
