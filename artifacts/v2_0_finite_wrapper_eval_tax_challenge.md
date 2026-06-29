# v2.0 Finite Wrapper Eval Tax Audit

Dataset: `data/eval/tr_challenge.tsv`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Numeric protected SP passthrough: `True`

This report decomposes how much the finite protected wrapper changes
visible eval behavior compared with the bare SP model.

## Overall

| Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 108 | 0.7351 | 0.6755 | -0.0597 | 2.2010 | 2.2977 | +0.3426 |

## Route Tag Counts

| Route tag | Examples |
| --- | ---: |
| `no_protected` | 94 |
| `numeric_like` | 9 |
| `file_like` | 5 |

## By Route Tag

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `file_like` | 5 | 0.5859 | 0.2817 | -0.3042 | 2.6800 | 3.7200 | +5.2000 |
| `no_protected` | 94 | 0.7483 | 0.7303 | -0.0180 | 2.2303 | 2.2429 | +0.0426 |
| `numeric_like` | 9 | 0.7119 | 0.2703 | -0.4416 | 1.6829 | 1.8537 | +0.7778 |

## By Feature Tag

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `apostrophe` | 27 | 0.7674 | 0.6087 | -0.1587 | 1.9832 | 2.1092 | +0.5556 |
| `file_like` | 5 | 0.5859 | 0.2817 | -0.3042 | 2.6800 | 3.7200 | +5.2000 |
| `hard_suffix` | 27 | 0.7674 | 0.6087 | -0.1587 | 1.9832 | 2.1092 | +0.5556 |
| `numeric_like` | 9 | 0.7119 | 0.2703 | -0.4416 | 1.6829 | 1.8537 | +0.7778 |
| `whitespace` | 108 | 0.7351 | 0.6755 | -0.0597 | 2.2010 | 2.2977 | +0.3426 |

## By Eval Category

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ambiguity` | 9 | 0.8041 | 0.7835 | -0.0206 | 1.8929 | 1.8929 | +0.0000 |
| `code_mixed` | 9 | 0.6310 | 0.5000 | -0.1310 | 2.5641 | 3.0769 | +2.2222 |
| `informal` | 9 | 0.7586 | 0.7586 | +0.0000 | 2.2400 | 2.2400 | +0.0000 |
| `negative_word` | 9 | 0.8269 | 0.8269 | +0.0000 | 1.6765 | 1.6765 | +0.0000 |
| `numbers_dates` | 9 | 0.7119 | 0.2703 | -0.4416 | 1.6829 | 1.8537 | +0.7778 |
| `proper_name` | 9 | 0.8133 | 0.8133 | +0.0000 | 1.9737 | 1.9737 | +0.0000 |
| `punctuation` | 9 | 0.7121 | 0.7188 | +0.0066 | 2.4062 | 2.6250 | +0.7778 |
| `question` | 9 | 0.8333 | 0.7759 | -0.0575 | 1.9714 | 2.0571 | +0.3333 |
| `softening` | 9 | 0.6769 | 0.6615 | -0.0154 | 2.4286 | 2.4286 | +0.0000 |
| `suffix_chain` | 9 | 0.6272 | 0.6036 | -0.0237 | 2.7778 | 2.7778 | +0.0000 |
| `verb_future` | 9 | 0.6942 | 0.6942 | +0.0000 | 2.6250 | 2.6250 | +0.0000 |
| `verb_past` | 9 | 0.8158 | 0.7500 | -0.0658 | 2.5312 | 2.5312 | +0.0000 |

## Worst F1 Deltas

| Category | Route tag | F1 delta | Token delta | Text |
| --- | --- | ---: | ---: | --- |
| `numbers_dates` | `numeric_like` | -0.8333 | +0 | `2025'ten sonra değişti.` |
| `numbers_dates` | `numeric_like` | -0.7564 | +0 | `2GB'lık dosya indi.` |
| `numbers_dates` | `numeric_like` | -0.6154 | +1 | `1.000'den fazla kayıt vardı.` |
| `code_mixed` | `no_protected` | -0.6000 | +0 | `API'deki tokenları yeniledim.` |
| `numbers_dates` | `numeric_like` | -0.5874 | +0 | `12:30'da toplantı başladı.` |
| `question` | `file_like` | -0.4702 | +3 | `README.md'yi yeniden açtın mı?` |
| `numbers_dates` | `numeric_like` | -0.4615 | +1 | `3.14 değerini yazdım.` |
| `numbers_dates` | `numeric_like` | -0.4250 | +1 | `5'inci satırı sildim.` |
| `verb_past` | `no_protected` | -0.4167 | +0 | `Yazdım, sildim, yeniden yazdım.` |
| `punctuation` | `file_like` | -0.3982 | +3 | `README.md'yi açtın mı?` |
| `code_mixed` | `file_like` | -0.3835 | +7 | `server_v2.log içinde hata buldum.` |
| `code_mixed` | `file_like` | -0.3333 | +5 | `README_final.md'yi güncelledim.` |
| `numbers_dates` | `numeric_like` | -0.2078 | +1 | `2024/05/01 tarihinde yazıldı.` |
| `suffix_chain` | `no_protected` | -0.1818 | +0 | `Kayıtlarımızdakilerden eskisini sildiler.` |
| `numbers_dates` | `numeric_like` | -0.1714 | +1 | `34-ABC-1907 plakası vardı.` |
| `softening` | `no_protected` | -0.1538 | +0 | `Ayağını yavaşça bastı.` |
| `ambiguity` | `no_protected` | -0.1250 | +0 | `Yüzdüm ve yoruldum.` |
| `code_mixed` | `file_like` | -0.0294 | +8 | `config_prod.json dosyasını sildiniz mi?` |
| `punctuation` | `no_protected` | +0.0000 | +0 | `"Tamam," diye yazdı.` |
| `punctuation` | `no_protected` | +0.0000 | +0 | `(Ankara'dan) yeni döndüm.` |

## Reading

If most F1 loss is concentrated in protected route tags, wrapper design
is the bottleneck. If no-protected rows also lose F1, normal text
segmentation is being changed unexpectedly.
