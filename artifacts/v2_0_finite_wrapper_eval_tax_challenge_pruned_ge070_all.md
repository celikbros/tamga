# v2.0 Finite Wrapper Eval Tax Audit

Dataset: `data/eval/tr_challenge.tsv`
SP model: `artifacts/private/v2_0_pruned_sp/highrate_ge070_all_floor_unigram_64000.model`
Numeric protected SP passthrough: `True`

This report decomposes how much the finite protected wrapper changes
visible eval behavior compared with the bare SP model.

## Overall

| Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 108 | 0.7447 | 0.6582 | -0.0865 | 2.3525 | 2.4491 | +0.3426 |

## Route Tag Counts

| Route tag | Examples |
| --- | ---: |
| `no_protected` | 94 |
| `numeric_like` | 9 |
| `file_like` | 5 |

## By Route Tag

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `file_like` | 5 | 0.5769 | 0.2895 | -0.2874 | 2.8800 | 3.9200 | +5.2000 |
| `no_protected` | 94 | 0.7562 | 0.7083 | -0.0479 | 2.3785 | 2.3912 | +0.0426 |
| `numeric_like` | 9 | 0.7581 | 0.3077 | -0.4504 | 1.8293 | 2.0000 | +0.7778 |

## By Feature Tag

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `apostrophe` | 27 | 0.7758 | 0.5907 | -0.1851 | 2.1176 | 2.2437 | +0.5556 |
| `file_like` | 5 | 0.5769 | 0.2895 | -0.2874 | 2.8800 | 3.9200 | +5.2000 |
| `hard_suffix` | 27 | 0.7758 | 0.5907 | -0.1851 | 2.1176 | 2.2437 | +0.5556 |
| `numeric_like` | 9 | 0.7581 | 0.3077 | -0.4504 | 1.8293 | 2.0000 | +0.7778 |
| `whitespace` | 108 | 0.7447 | 0.6582 | -0.0865 | 2.3525 | 2.4491 | +0.3426 |

## By Eval Category

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ambiguity` | 9 | 0.8350 | 0.7961 | -0.0388 | 2.1071 | 2.1071 | +0.0000 |
| `code_mixed` | 9 | 0.6358 | 0.4967 | -0.1391 | 2.6923 | 3.2051 | +2.2222 |
| `informal` | 9 | 0.7416 | 0.6517 | -0.0899 | 2.3200 | 2.3200 | +0.0000 |
| `negative_word` | 9 | 0.8224 | 0.7664 | -0.0561 | 1.7647 | 1.7647 | +0.0000 |
| `numbers_dates` | 9 | 0.7581 | 0.3077 | -0.4504 | 1.8293 | 2.0000 | +0.7778 |
| `proper_name` | 9 | 0.8228 | 0.7848 | -0.0380 | 2.1842 | 2.1842 | +0.0000 |
| `punctuation` | 9 | 0.7015 | 0.6923 | -0.0092 | 2.4688 | 2.6875 | +0.7778 |
| `question` | 9 | 0.7717 | 0.6341 | -0.1375 | 2.1714 | 2.2571 | +0.3333 |
| `softening` | 9 | 0.6866 | 0.6716 | -0.0149 | 2.5714 | 2.5714 | +0.0000 |
| `suffix_chain` | 9 | 0.7000 | 0.6444 | -0.0556 | 3.1852 | 3.1852 | +0.0000 |
| `verb_future` | 9 | 0.6992 | 0.6992 | +0.0000 | 2.7083 | 2.7083 | +0.0000 |
| `verb_past` | 9 | 0.8182 | 0.7532 | -0.0649 | 2.5938 | 2.5938 | +0.0000 |

## Worst F1 Deltas

| Category | Route tag | F1 delta | Token delta | Text |
| --- | --- | ---: | ---: | --- |
| `numbers_dates` | `numeric_like` | -0.8333 | +0 | `2025'ten sonra değişti.` |
| `numbers_dates` | `numeric_like` | -0.7564 | +0 | `2GB'lık dosya indi.` |
| `numbers_dates` | `numeric_like` | -0.7143 | +1 | `1.000'den fazla kayıt vardı.` |
| `code_mixed` | `no_protected` | -0.6667 | +0 | `API'deki tokenları yeniledim.` |
| `informal` | `no_protected` | -0.6000 | +0 | `Yazıcam sana akşam.` |
| `numbers_dates` | `numeric_like` | -0.5874 | +0 | `12:30'da toplantı başladı.` |
| `numbers_dates` | `numeric_like` | -0.5333 | +1 | `3.14 değerini yazdım.` |
| `question` | `no_protected` | -0.5000 | +0 | `Yarın gelecek misin?` |
| `negative_word` | `no_protected` | -0.4615 | +0 | `Yakın kadın kitabı okudu.` |
| `question` | `file_like` | -0.4314 | +3 | `README.md'yi yeniden açtın mı?` |
| `numbers_dates` | `numeric_like` | -0.4250 | +1 | `5'inci satırı sildim.` |
| `verb_past` | `no_protected` | -0.4000 | +0 | `Yazdım, sildim, yeniden yazdım.` |
| `suffix_chain` | `no_protected` | -0.3846 | +0 | `Kayıtlarımızdakilerden eskisini sildiler.` |
| `punctuation` | `file_like` | -0.3810 | +3 | `README.md'yi açtın mı?` |
| `code_mixed` | `file_like` | -0.3333 | +5 | `README_final.md'yi güncelledim.` |
| `code_mixed` | `file_like` | -0.3214 | +7 | `server_v2.log içinde hata buldum.` |
| `question` | `no_protected` | -0.2857 | +0 | `Ankara'dan mı geldiniz?` |
| `ambiguity` | `no_protected` | -0.2500 | +0 | `Yüz kişi geldi.` |
| `informal` | `no_protected` | -0.2222 | +0 | `Napıyon burada?` |
| `numbers_dates` | `numeric_like` | -0.1667 | +1 | `2024/05/01 tarihinde yazıldı.` |

## Reading

If most F1 loss is concentrated in protected route tags, wrapper design
is the bottleneck. If no-protected rows also lose F1, normal text
segmentation is being changed unexpectedly.
