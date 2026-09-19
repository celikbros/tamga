# tamga → Gardaş model rafı: sentencepiece sürüm sınırı

> **Kimden:** `tamga` (tokenizer) · **Kime:** `gardas-modeller` (raf) · **Bilgi:** `gardas-motor`
> **Tarih:** 2026-09-19 · **Taşıyan:** kurucu (elden) · **Tür: BİLGİ — istek yok**

18 Eylül'de gönderdiğimiz bayt/karakter notunun devamıdır.

## Ne değişti

tamga paketinin tokenizer bağımlılığı artık `sentencepiece>=0.2,<0.2.2` ile
sınırlı (tamga commit `d178ff4`). Sebep: v3.8 hattı `EncodeAsImmutableProto`
kullanıyor ve o API karakter ofseti veriyor. 0.2.2 bu API'yi kaldırdı; yerine
gelen `Encode(return_type="proto")` bayt ofseti veriyor.

Tokenizer modeli, vocab, config ve v3.8 çıktısı **değişmedi**.

## Sizi etkiliyor mu

- **raf / afacan:** Hayır. tamga paketini kurmuyorsunuz, çeyiz kopyasını
  kullanıyorsunuz. Bayt dilimli fonksiyonunuz 0.2.2 ortamında doğru.
  Ortamınız 0.2.1'e inerse o fonksiyon yanlış bayt üretir; o durumda API'ye
  göre dilimleyin.
- **gardas-motor:** Hayır. Rust motoru baytla doğru diliyor; çeyiz kopyası
  değişmedi.

## İleriye dönük

İleride yeni bir çeyiz verilirse, desteklenen sentencepiece sürümü ve ofset
anlamı sürüm notunda açıkça yazılacak.

Yanıt gerekmiyor.
