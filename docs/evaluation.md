# Evaluation

## Gold Boundaries

Gold tokenlar, bu prototipte morfolojik boundary referansi olarak kabul edilir.
Ornek:

```text
Geldim. -> ["▁Gel","+di","+m","."]
```

Bu satirda `Gel`, `di`, `m` ve noktalama sonlari karakter siniri olarak
degerlendirilir.

## Boundary F1

Boundary F1, iki tokenizasyonun metin icinde olusturdugu karakter sinirlarini
karsilastirir.

- Precision: tahmin edilen boundary'lerin ne kadari gold boundary ile eslesiyor?
- Recall: gold boundary'lerin ne kadari tahmin edildi?
- F1: precision ve recall'un harmonik ortalamasi.

Bu metrik token sayisini dogrudan odullendirmez. BPE daha az token uretebilir;
bu bazen verimli olabilir. Ancak daha az token, morfolojik sinirlarin korundugu
anlamina gelmez. Ornegin `Geldim` tek token olursa token sayisi azalir ama
`gel +di +m` bilgisi kaybolur.

Bu nedenle v0.9 raporlari hem token/kelime oranini hem de boundary F1 skorunu
birlikte verir.

## Demo Corpus

`data/train/tr_bpe_train.txt` production corpus degildir. Eval cumlelerini
birebir icermeyen, BPE sweep karsilastirmasini daha adil hale getirmek icin
hazirlanmis kucuk bir demo corpus'tur.
