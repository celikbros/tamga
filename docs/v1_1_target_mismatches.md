# v1.1 Target Mismatches

v1.1 sadece dusuk riskli pretokenizer ve apostrof akisini hedefler.
`negative_word` ve `ambiguity` kategorileri bu turda davranissal hedef degildir.

## Before v1.1 Baseline

| Category | Exact match | F1 |
| --- | ---: | ---: |
| challenge overall | 21/108 | 0.7570 |
| numbers_dates | 0/9 | 0.5693 |
| proper_name | 2/9 | 0.8409 |
| punctuation | 2/9 | 0.8392 |

## proper_name

| Text | Expected | Actual |
| --- | --- | --- |
| Ahmet'in evinden döndüm. | `["▁Ahmet","'","+in","▁ev","+in","+den","▁dön","+dü","+m","."]` | `["▁Ahmet","'","+in","▁evin","+den","▁dön","+dü","+m","."]` |
| İzmir'dekiler toplantıya katıldı. | `["▁İzmir","'","+de","+ki","+ler","▁toplantı","+ya","▁katıl","+dı","."]` | `["▁İzmir","'","+de","+ki","+ler","▁toplantıya","▁katıldı","."]` |
| Mehmet'in arabasından ses geldi. | `["▁Mehmet","'","+in","▁araba","+sı","+ndan","▁ses","▁gel","+di","."]` | `["▁Mehmet","'","+in","▁araba","+sın","+dan","▁ses","▁gel","+di","."]` |
| Van'ın gölünü anlattılar. | `["▁Van","'","+ın","▁göl","+ü","+nü","▁anlat","+tı","+lar","."]` | `["▁Van","'","+ın","▁gölü","+nü","▁anlat","+tı","+lar","."]` |

## numbers_dates

| Text | Expected | Actual |
| --- | --- | --- |
| 2025'ten sonra değişti. | `["▁2025","'","+ten","▁sonra","▁değiş","+ti","."]` | `["2025","'","+ten","▁sonra","▁değişti","."]` |
| 3.14 değerini yazdım. | `["▁3.14","▁değer","+i","+ni","▁yaz","+dı","+m","."]` | `["3.14","▁değeri","+ni","▁yaz","+dı","+m","."]` |
| 34-ABC-1907 plakası vardı. | `["▁34-ABC-1907","▁plaka","+sı","▁var","+dı","."]` | `["34","-","▁ABC","-","1907","▁plakası","▁vardı","."]` |
| %25'lik artış oldu. | `["%","▁25","'","+lik","▁artış","▁ol","+du","."]` | `["%","25","'","+lik","▁artış","▁oldu","."]` |

## punctuation

| Text | Expected | Actual |
| --- | --- | --- |
| “Merhaba,” dedi. | `["\"","▁Merhaba",",","\"","▁de","+di","."]` | `["\"","▁Merhaba",",","\"","▁dedi","."]` |
| Evet; ama sonra döndü. | `["▁Evet",";","▁ama","▁sonra","▁dön","+dü","."]` | `["▁Evet",";","▁ama","▁sonra","▁döndü","."]` |
| Ali, Ayşe'ye baktı. | `["▁Ali",",","▁Ayşe","'","+ye","▁bak","+tı","."]` | `["▁Ali",",","▁Ayşe","'","+ye","▁baktı","."]` |
| README.md'yi açtın mı? | `["▁README.md","'","+yi","▁aç","+tı","+n","▁mı","?"]` | `["▁README.md","'","▁yi","▁aç","+tı","+n","▁mı","?"]` |

## v1.1 Scope

- Mark numeric/code-like tokens with the word-start marker.
- Keep decimal, time, slash-date, plate-like and file-like units intact.
- Split apostrophe suffixes after file-like and numeric-like stems.
- Add only narrow stems needed by the targeted pretokenizer fixtures.
- Do not broaden the general greedy suffix splitter.
