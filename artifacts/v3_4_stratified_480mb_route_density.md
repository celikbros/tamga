# v2.1 Sidecar Protected Route Density Audit

Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_4_sample/stratified_480mb.txt`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Max lines per split/file: `all`
Include EOS in token pressure: `False`
Token pressure mode: `False`

This audit estimates whether the selected passthrough sidecar baseline
is exposed to a different protected-span density than the v1.8 pilot.
It also reports the local pre-split token tax on the same text.

## Split Summary

| Split | Lines | Raw bytes | Protected spans | Protected bytes | Protected bytes/raw byte | Protected line share | SP tokens/raw byte | Passthrough tokens/raw byte | Pre-split tokens/raw byte | Pre-split tax tokens/raw byte | Pre-split tax relative |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `stratified_480mb` | 498086 | 495521318 | 3175697 | 14228732 | 0.028715 | 0.599280 | n/a | n/a | n/a | n/a | n/a |

## Route Summary

| Route | Occurrences | Bytes | Bytes/raw byte | Line share | Unique surfaces | Top surfaces |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `numeric_like` | 2706067 | 9405143 | 0.018980 | 0.567189 | 228645 | `1`:108361, `2`:92983, `3`:77279, `5`:55388, `4`:55339, `10`:45306, `6`:38950, `0`:38784 |
| `file_like` | 249850 | 3227658 | 0.006514 | 0.121306 | 130629 | `A.Ş`:5418, `T.C`:2073, `Bavul.com`:1825, `M.Ö`:1451, `ta.prwidgets.getjs`:1212, `prw_rup`:1079, `ibex_photo_carousel`:918, `ibex_room_grid`:890 |
| `apostrophe_surface` | 69093 | 610946 | 0.001233 | 0.060130 | 24807 | `Kur'an`:3655, `Kur'ân`:682, `İbnü'l`:475, `Ebu'l`:358, `2'nci`:331, `Don't`:271, `FETÖ'cü`:243, `ve'l`:241 |
| `non_turkish_latin_word` | 65239 | 549831 | 0.001110 | 0.036644 | 27412 | `José`:445, `à`:348, `André`:287, `São`:263, `Atlético`:255, `América`:188, `René`:177, `Español`:171 |
| `cyrillic_word` | 56873 | 219626 | 0.000443 | 0.004612 | 6160 | `а`:12969, `е`:12517, `і`:5656, `о`:2701, `г`:2013, `ѕ`:1840, `у`:935, `ег`:500 |
| `arabic_word` | 17358 | 130514 | 0.000263 | 0.003439 | 6536 | `ا`:777, `م`:395, `ي`:376, `ن`:271, `ك`:269, `و`:211, `ب`:202, `ل`:187 |
| `greek_word` | 7121 | 48780 | 0.000098 | 0.003770 | 2238 | `α`:711, `μ`:314, `β`:235, `Β`:197, `λ`:177, `Δ`:149, `π`:135, `σ`:120 |
| `azerbaijani_word` | 2371 | 20114 | 0.000041 | 0.002829 | 1514 | `və`:81, `Azərbaycan`:32, `ilə`:23, `ə`:22, `Xəzər`:17, `Aviabiletlər`:17, `Mənim`:16, `Mən`:12 |
| `url` | 162 | 10269 | 0.000021 | 0.000317 | 159 | `http://turgayfisekci.wordpress.com/`:3, `http://www.samlarkoyu.net`:2, `http://www.usccb.org/nab/bible/malachi/malachi1.htm`:1, `http://www.yashrajfilms.com/microsites/rnbdjmicro/rnbdj.html`:1, `https://web.archive.org/web/20060118201913/http://pinker.wjh.harvard.edu/articles/`:1, `https://web.archive.org/web/20081007014530/http://www.russiatoday.com/ossetianwar/news/30985`:1, `http://www.atimes.com/atimes/Central_Asia/IL06Ag01.html`:1, `http://www.radikal.com.tr/yorum/bir_ulkucuden_solcu_kardesine_mektup-1149154`:1 |
| `percent_encoded` | 1457 | 4713 | 0.000010 | 0.001980 | 74 | `%20`:1246, `%1B`:22, `%0B`:19, `%C5%9F%C4%B1`:10, `%ba`:9, `%2B`:8, `%C4%B1`:7, `%4B`:6 |
| `technical_comparator` | 48 | 590 | 0.000001 | 0.000034 | 20 | `parents.length==0`:18, `length!=0`:6, `B7>=1000`:4, `length==0`:2, `j.currentSlide==0`:2, `y==0`:2, `i>=1`:1, `i<=5`:1 |
| `uzbek_apostrophe_word` | 58 | 548 | 0.000001 | 0.000084 | 42 | `Oʻzbekcha`:5, `Semʻî`:4, `Eşʻarî`:3, `Hiʻiaka`:3, `Şamilʼnin`:3, `Yupʼik`:2, `bidʻat`:2, `Hawaiʻi`:2 |

## Gate

Use this report before any future global pre-split decision.

- If protected bytes/raw byte is much higher than the v1.8 pilot, the
  global pre-split tax is likely understated by previous results.
- If only a few routes dominate, prefer selective pre-split by route
  class over global pre-split.
- Run with `--with-token-pressure` only for small samples or when
  the extra encoding cost is acceptable.
- `sp64_protected_passthrough_sidecar` remains the default v2.1
  baseline unless token-boundary alignment is a committed requirement.
