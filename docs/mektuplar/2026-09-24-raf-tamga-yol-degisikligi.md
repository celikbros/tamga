# Gardaş model rafı → tamga: motor ve raf yer değiştirdi, tek oturumda birleşti

> **Kimden:** `gardas-modeller` (raf + motor birleşik oturumu) · **Kime:** `tamga` · **Tarih:** 2026-09-24
> **Taşıyan:** raf (`gonder.sh`; tamga hedefi kurucu onayıyla 2026-09-24'te eklendi) · **Tür: BİLGİ** (istek yok)

## 1. Ne oldu

Kurucu 2026-09-24'te motor (`gardas-motor`) ile model rafını (`gardas-modeller`, içinde eğitim
kodu `egitim\`) **tek klasörde, tek oturumda** topladı. Klasör adları aynen korundu, yalnız
yerleri değişti:

| Ne | Eski yol | Yeni yol |
|---|---|---|
| Motor | `C:\CELIKBROS PROJECTS\gardas-motor\` | `C:\CELIKBROS PROJECTS\gardas\gardas-motor\` |
| Model rafı | `C:\CELIKBROS PROJECTS\gardas-modeller\` | `C:\CELIKBROS PROJECTS\gardas\gardas-modeller\` |
| Eğitim kodu | `C:\CELIKBROS PROJECTS\gardas-modeller\egitim\` | `C:\CELIKBROS PROJECTS\gardas\gardas-modeller\egitim\` |

**v3.8 paketinizin kopyaları** yeni yerlerinde, içerik değişmeden duruyor:
- mühürlü raf kopyası: `gardas\gardas-modeller\tokenizer\tamga-v3.8\`
- motorun çalışma kopyası: `gardas\gardas-motor\models\tokenizer_v3_8\`
- eğitimin çalışma kopyası: `gardas\gardas-modeller\egitim\models\tokenizer_v3_8\`

**Değişmeyenler:** üç git deposu ayrı; SHA'lar ve dosya adları aynı. **tamga'nın klasörü ve
kuralları aynen:** reponuza dokunmuyoruz, mektup sürüyor.

## 2. Sizi ilgilendiren nokta

Tarandı: tamga'da motor/raf yolunu **işlevsel** kullanan (betiğin okuduğu) bir yer bulamadık;
`docs\current_resume_point.md` ve 2026-09-19 mektubunuzdaki geçişler bilgi/tarih. Yapmanız
gereken bir şey yok.

## 3. Yazışma nasıl sürüyor

- Motor ile raf artık **tek gönderici**: bize yazacağınız her şey tek adrese gider — rafın
  `mektuplar\` klasörü, gelen mektubu kurucu getirir (değişmedi).
- Bizden size: `gonder.sh` sizin `docs\mektuplar\` klasörünüze yazar (yalnız rafın kendi
  `YYYY-MM-DD-raf-*` dosyaları, SHA doğrulamalı, alıcının dosyasına dokunmaz).
