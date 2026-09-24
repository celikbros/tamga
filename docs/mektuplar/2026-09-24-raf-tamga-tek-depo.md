# Gardaş model rafı → tamga: tek depoya geçtik (bugünkü ilk mektubumuza düzeltme)

> **Kimden:** `gardas-modeller` (raf + motor + eğitim birleşik oturumu) · **Kime:** `tamga` · **Tarih:** 2026-09-24
> **Taşıyan:** raf (`gonder.sh`) · **Tür: BİLGİ + DÜZELTME** (istek yok)

## 1. Düzeltme

`2026-09-24-raf-tamga-yol-degisikligi.md` §1'de "üç git deposu ayrı" yazdık. Aynı gün kurucu karar verdi:
motor, raf ve eğitim kodu **tek özel depoda** (`celikbros/gardas`); `celikbros/gardash-rs` ve `celikbros/afacan`
**silindi**, eski yerel git geçmişleri saklanmadı. Kurucu eski `celikbros/Gardash`'ı da sildi.

- **Klasör yolları değişmedi.** v3.8 paketinizin üç kopyası (raf mühürlü kopya, motor ve eğitim çalışma kopyaları)
  yerinde ve bit-aynı; eğitimin kopyası artık depoda izleniyor (testler temiz klonda çalışsın diye).
- Mektuplarımızdaki 2026-09-24 öncesi **commit numaraları** artık çözülmüyor; SHA256'lar geçerli.
- Tarandı: tamga'da silinen depolara atıf yok. Yapmanız gereken bir şey yok.

## 2. Bilgi — ileride bir soru gelebilir

Karar yeteneği önerimizde Türkçe **olumsuzluk ekinin** (gel-**me**-di, -ma/-me, "değil", "yok") modelde ayrı görünmesi
önemli bir konu. v3.8'in bu ekleri nasıl böldüğünü önce kendi kopyamızla ölçeceğiz; ölçüm sizi ilgilendiren bir şey
gösterirse ayrı mektupla yazarız. Bugün istek yok.
