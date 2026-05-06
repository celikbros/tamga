# Design Notes

## Neden Türkçe Merkezli Tokenizer?

Turkce eklemeli bir dildir. Anlam ve gramer bilgisi cogunlukla koklere eklenen
ek zincirleriyle tasinir. Standart subword yontemleri sik gecen yuzey parcalari
ogrenebilir, ancak bu parcalar her zaman morfolojik sinirlarla hizalanmaz.

## Neden Kelime-Token Degil?

Kelimeyi tek token yapmak token sayisini azaltabilir, fakat `geldim` gibi bir
yuzey bicimde `gel`, gecmis zaman ve kisi bilgisini tek parcanin icine saklar.
Bu proje, kelimeyi tamamen parcalamak yerine anlamli morfolojik sinirlari
korumayi hedefler.

## Neden Yuzey Govde?

Bu prototip normalize edici degil, yuzey metni koruyan bir parcalayicidir.
`kitaplarımdan -> ▁Kitap +lar +ım +dan` ve
`kitabımdan -> ▁Kitab +ım +dan` ayrimi bu yuzden onemlidir. Kokun sozluk
biçimini zorla geri kurmak yerine metindeki yuzey govde korunur.

## Neden Kisa Ekleri Genel Greedy Splitter'a Koymuyoruz?

`+ın`, `+i` gibi kisa ekler cok risklidir. Bunlari her yerde acarsak
`kadın -> kad +ın`, `kedi -> ked +i`, `altın -> alt +ın` gibi hatalar uretiriz.
Bu nedenle kisa ekler sadece lexicon-aware veya informal-aware guvenli akislarda
kullanilir.

## Neden Boundary F1?

Token sayisi tek basina kalite degildir. BPE bazen daha az token uretebilir, ama
morfolojik sinirlari ezebilir. Boundary F1, gold tokenlarin olusturdugu karakter
sinirlarini tahmin edilen token sinirlariyla karsilastirir. Bu metrik,
morfolojik sinir uyumunu izlemek icin basit ve aciklanabilir bir sinyaldir.

## Nihai Hedef

Bu prototip deterministik morfoloji katmanini arastirir. Nihai hedef:

- deterministic morphology layer
- morfem sinirina saygili MorphBPE fallback
- Turkce ve Turk dilleri icin daha iyi subword dagilimi
- Ingilizce/kod cluster destegi
- byte fallback
- cok dilli vocabulary allocation
