# v2.0 Finite Wrapper Eval Tax Audit

Dataset: `data/eval/tr_challenge.tsv`
SP model: `artifacts/private/v2_0_teacher_distilled_sp/teacher_distilled_16000lines_unigram_64000.model`
Numeric protected SP passthrough: `True`

This report decomposes how much the finite protected wrapper changes
visible eval behavior compared with the bare SP model.

## Overall

| Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 108 | 0.7509 | 0.7219 | -0.0290 | 2.3525 | 2.4413 | +0.3148 |

## Route Tag Counts

| Route tag | Examples |
| --- | ---: |
| `no_protected` | 94 |
| `numeric_like` | 9 |
| `file_like` | 5 |

## By Route Tag

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `file_like` | 5 | 0.5524 | 0.3243 | -0.2281 | 2.9200 | 3.8400 | +4.6000 |
| `no_protected` | 94 | 0.7713 | 0.7757 | +0.0043 | 2.3912 | 2.4038 | +0.0426 |
| `numeric_like` | 9 | 0.6891 | 0.3214 | -0.3676 | 1.7073 | 1.8780 | +0.7778 |

## By Feature Tag

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `apostrophe` | 27 | 0.7596 | 0.6573 | -0.1023 | 2.1092 | 2.2101 | +0.4444 |
| `file_like` | 5 | 0.5524 | 0.3243 | -0.2281 | 2.9200 | 3.8400 | +4.6000 |
| `hard_suffix` | 27 | 0.7596 | 0.6573 | -0.1023 | 2.1092 | 2.2101 | +0.4444 |
| `numeric_like` | 9 | 0.6891 | 0.3214 | -0.3676 | 1.7073 | 1.8780 | +0.7778 |
| `whitespace` | 108 | 0.7509 | 0.7219 | -0.0290 | 2.3525 | 2.4413 | +0.3148 |

## By Eval Category

| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ambiguity` | 9 | 0.8041 | 0.8041 | +0.0000 | 1.8929 | 1.8929 | +0.0000 |
| `code_mixed` | 9 | 0.6279 | 0.6093 | -0.0186 | 2.6667 | 3.1538 | +2.1111 |
| `informal` | 9 | 0.7865 | 0.7865 | +0.0000 | 2.3200 | 2.3200 | +0.0000 |
| `negative_word` | 9 | 0.8302 | 0.8302 | +0.0000 | 1.7353 | 1.7353 | +0.0000 |
| `numbers_dates` | 9 | 0.6891 | 0.3214 | -0.3676 | 1.7073 | 1.8780 | +0.7778 |
| `proper_name` | 9 | 0.8408 | 0.8408 | +0.0000 | 2.1579 | 2.1579 | +0.0000 |
| `punctuation` | 9 | 0.6963 | 0.7077 | +0.0114 | 2.5000 | 2.6875 | +0.6667 |
| `question` | 9 | 0.8000 | 0.7500 | -0.0500 | 2.1143 | 2.1714 | +0.2222 |
| `softening` | 9 | 0.7015 | 0.7015 | +0.0000 | 2.5714 | 2.5714 | +0.0000 |
| `suffix_chain` | 9 | 0.7447 | 0.7447 | +0.0000 | 3.4815 | 3.4815 | +0.0000 |
| `verb_future` | 9 | 0.7692 | 0.7692 | +0.0000 | 3.0000 | 3.0000 | +0.0000 |
| `verb_past` | 9 | 0.7792 | 0.7792 | +0.0000 | 2.5938 | 2.5938 | +0.0000 |

## Worst F1 Deltas

| Category | Route tag | F1 delta | Token delta | Text |
| --- | --- | ---: | ---: | --- |
| `numbers_dates` | `numeric_like` | -0.8333 | +0 | `2025'ten sonra değişti.` |
| `numbers_dates` | `numeric_like` | -0.7564 | +0 | `2GB'lık dosya indi.` |
| `numbers_dates` | `numeric_like` | -0.6154 | +1 | `1.000'den fazla kayıt vardı.` |
| `numbers_dates` | `numeric_like` | -0.5874 | +0 | `12:30'da toplantı başladı.` |
| `question` | `file_like` | -0.4167 | +2 | `README.md'yi yeniden açtın mı?` |
| `punctuation` | `file_like` | -0.3459 | +2 | `README.md'yi açtın mı?` |
| `code_mixed` | `file_like` | -0.3333 | +7 | `server_v2.log içinde hata buldum.` |
| `numbers_dates` | `numeric_like` | -0.1714 | +1 | `34-ABC-1907 plakası vardı.` |
| `numbers_dates` | `numeric_like` | -0.1667 | +1 | `2024/05/01 tarihinde yazıldı.` |
| `numbers_dates` | `numeric_like` | -0.1667 | +1 | `5'inci satırı sildim.` |
| `numbers_dates` | `numeric_like` | -0.1538 | +1 | `3.14 değerini yazdım.` |
| `code_mixed` | `file_like` | -0.0476 | +4 | `README_final.md'yi güncelledim.` |
| `code_mixed` | `file_like` | -0.0294 | +8 | `config_prod.json dosyasını sildiniz mi?` |
| `punctuation` | `no_protected` | +0.0000 | +0 | `"Tamam," diye yazdı.` |
| `punctuation` | `no_protected` | +0.0000 | +0 | `(Ankara'dan) yeni döndüm.` |
| `code_mixed` | `no_protected` | +0.0000 | +0 | `API'deki tokenları yeniledim.` |
| `proper_name` | `no_protected` | +0.0000 | +0 | `Ahmet'in evinden döndüm.` |
| `verb_future` | `no_protected` | +0.0000 | +0 | `Alabileceğimizi söyledik.` |
| `question` | `no_protected` | +0.0000 | +0 | `Ali, Ayşe'ye baktı mı?` |
| `punctuation` | `no_protected` | +0.0000 | +0 | `Ali, Ayşe'ye baktı.` |

## Reading

If most F1 loss is concentrated in protected route tags, wrapper design
is the bottleneck. If no-protected rows also lose F1, normal text
segmentation is being changed unexpectedly.
