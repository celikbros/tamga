# v2.0 Finite Wrapper Eval Tax Audit

Dataset: `data/eval/tr_challenge.tsv`
SP model: `artifacts/private/v2_0_pruned_sp/highrate_ge070_nonword_floor_unigram_64000.model`
Numeric protected SP passthrough: `True`

This report decomposes how much the finite protected wrapper changes
visible eval behavior compared with the bare SP model.

## Overall

| Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 108 | 0.7486 | 0.6875 | -0.0611 | 2.2611 | 2.3577 | +0.3426 |

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
| `no_protected` | 94 | 0.7637 | 0.7430 | -0.0207 | 2.3028 | 2.3155 | +0.0426 |
| `numeric_like` | 9 | 0.7119 | 0.2703 | -0.4416 | 1.6829 | 1.8537 | +0.7778 |

## By Feature Tag

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `apostrophe` | 27 | 0.7780 | 0.6176 | -0.1605 | 2.0420 | 2.1681 | +0.5556 |
| `file_like` | 5 | 0.5859 | 0.2817 | -0.3042 | 2.6800 | 3.7200 | +5.2000 |
| `hard_suffix` | 27 | 0.7780 | 0.6176 | -0.1605 | 2.0420 | 2.1681 | +0.5556 |
| `numeric_like` | 9 | 0.7119 | 0.2703 | -0.4416 | 1.6829 | 1.8537 | +0.7778 |
| `whitespace` | 108 | 0.7486 | 0.6875 | -0.0611 | 2.2611 | 2.3577 | +0.3426 |

## By Eval Category

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ambiguity` | 9 | 0.8041 | 0.7835 | -0.0206 | 1.8929 | 1.8929 | +0.0000 |
| `code_mixed` | 9 | 0.6316 | 0.4901 | -0.1415 | 2.6410 | 3.1538 | +2.2222 |
| `informal` | 9 | 0.7586 | 0.7586 | +0.0000 | 2.2400 | 2.2400 | +0.0000 |
| `negative_word` | 9 | 0.8381 | 0.8381 | +0.0000 | 1.7059 | 1.7059 | +0.0000 |
| `numbers_dates` | 9 | 0.7119 | 0.2703 | -0.4416 | 1.6829 | 1.8537 | +0.7778 |
| `proper_name` | 9 | 0.8258 | 0.8258 | +0.0000 | 2.1053 | 2.1053 | +0.0000 |
| `punctuation` | 9 | 0.7121 | 0.7188 | +0.0066 | 2.4062 | 2.6250 | +0.7778 |
| `question` | 9 | 0.8333 | 0.7759 | -0.0575 | 1.9714 | 2.0571 | +0.3333 |
| `softening` | 9 | 0.6870 | 0.6718 | -0.0153 | 2.4643 | 2.4643 | +0.0000 |
| `suffix_chain` | 9 | 0.7039 | 0.6704 | -0.0335 | 3.1481 | 3.1481 | +0.0000 |
| `verb_future` | 9 | 0.6992 | 0.6992 | +0.0000 | 2.7083 | 2.7083 | +0.0000 |
| `verb_past` | 9 | 0.8366 | 0.7712 | -0.0654 | 2.5625 | 2.5625 | +0.0000 |

## Worst F1 Deltas

| Category | Route tag | F1 delta | Token delta | Text |
| --- | --- | ---: | ---: | --- |
| `numbers_dates` | `numeric_like` | -0.8333 | +0 | `2025'ten sonra değişti.` |
| `numbers_dates` | `numeric_like` | -0.7564 | +0 | `2GB'lık dosya indi.` |
| `code_mixed` | `no_protected` | -0.6667 | +0 | `API'deki tokenları yeniledim.` |
| `numbers_dates` | `numeric_like` | -0.6154 | +1 | `1.000'den fazla kayıt vardı.` |
| `numbers_dates` | `numeric_like` | -0.5874 | +0 | `12:30'da toplantı başladı.` |
| `question` | `file_like` | -0.4702 | +3 | `README.md'yi yeniden açtın mı?` |
| `numbers_dates` | `numeric_like` | -0.4615 | +1 | `3.14 değerini yazdım.` |
| `numbers_dates` | `numeric_like` | -0.4250 | +1 | `5'inci satırı sildim.` |
| `verb_past` | `no_protected` | -0.4167 | +0 | `Yazdım, sildim, yeniden yazdım.` |
| `punctuation` | `file_like` | -0.3982 | +3 | `README.md'yi açtın mı?` |
| `code_mixed` | `file_like` | -0.3835 | +7 | `server_v2.log içinde hata buldum.` |
| `code_mixed` | `file_like` | -0.3333 | +5 | `README_final.md'yi güncelledim.` |
| `suffix_chain` | `no_protected` | -0.2400 | +0 | `Kayıtlarımızdakilerden eskisini sildiler.` |
| `numbers_dates` | `numeric_like` | -0.2078 | +1 | `2024/05/01 tarihinde yazıldı.` |
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
