# Devir-Teslim İyileştirme Yol Haritası

> Türkçe · [English version](roadmap.en.md)

Tarih: 2026-07-11
Girdi: `docs/handover.md` (bulgu numaraları B1-B8 oradan)
İlke: Her faz kendi kabul kapısıyla biter; kapıdan geçmeyen faz merge edilmez.

---

## Devralan mühendis için ilk 1 saat

```text
1. README.md oku (çift dilli genel bakış).
2. CLAUDE.md oku (commit kuralları: author celikbros + iki co-author trailer,
   Claude trailer'ı YOK; v3.8 dondurma guardrail'leri).
3. docs/handover.md oku (neresi çürük, neden).
4. Bu dosyayı oku (ne yapılacak, hangi sırayla).
5. docs/current_resume_point.md İLK bölümünü oku (güncel durum her zaman
   dosyanın EN ÜSTÜNDEDİR; alt bölümler tarihsel katmandır, kafa karıştırmasın).
6. Ortamı doğrula:
   python -m pytest --basetemp=<yazılabilir-temp>   -> 319 passed beklenir
   (çıplak pytest, Windows temp ACL sorunu yüzünden 93 ortam hatası verebilir;
   bkz. otopsi B8)
7. Guardrail'ler (HER değişiklikten sonra yeşil kalmak zorunda):
   - python -m pytest yeşil
   - data/eval/tr_gold_expanded.tsv: 50/50 exact
   - data/eval/tr_stress_public.tsv: 34/34 roundtrip
   - protected span break rate 0.0000
   - v3.8 id kontratı: SP 0..63999, byte fallback 64000..64255,
     kontrol 64256..64383, <pad>=64256 — DEĞİŞMEZ
```

Roller: Bu repo = tokenizer ekibi. LLM tarafı (Gardash) ve veri fabrikası
(Derlem) AYRI ekiplerdir; onların klasörlerine dokunulmaz, talepleri
belge/teslimat olarak karşılanır.

---

## Faz 0 — Acil onarım (bloklayıcı; hedef: hemen)

Amaç: Kuyruktaki PII re-tokenize işinin araçlarını çalışır hale getirmek +
en utanç verici tutarsızlıkları kapatmak. Algoritmik davranış DEĞİŞMEZ.

```text
0.1  GARDASH_ROOT ortam değişkeni: B3'teki 5 script'in "C:/CELIK-GARDASH"
     hardcoded varsayılanları env-türevli hale gelir (env yoksa eski literal
     korunur -> test/doküman geriye uyumlu, ama tek env ile taşınabilir).
0.2  tokenize_corpus.py --config/--tokenizer zorunlu argüman olur (B4;
     sessiz v3.5 seçimi imkânsızlaşır).
0.3  configs/v3_8_pii_clean_retokenize_sp64k.toml şablonu eklenir
     (PII işi için; yollar placeholder, doldurma talimatı içinde).
     Kanonik v3_8_final_sidecar_sp64k.toml TARİHSEL KAYIT olarak kalır,
     başına açıklayıcı yorum eklenir.
0.4  pyproject: [production] extra = sentencepiece (B5).
0.5  Dürüstlük: CLI'a --lossless bayrağı; README'de "lossless" iddiası
     yalnızca v3.8 sidecar zincirine kapsamlanır; CLI'ın deterministik
     PROTOTİP olduğu açıkça yazılır (B2).
KAPI: pytest 319 yeşil + gold 50/50 + stress 34/34 + CLI --lossless
     roundtrip smoke (çift boşluk/tab/newline birebir).
```

## Faz 1 — PII-temiz re-tokenize servisi (dışsal tetik: Derlem release'i)

Plan hazır: `docs/v3_8_pii_clean_retokenize_readiness.md`.

```text
- Tetik: Derlem frozen release (tam sha256 + kesin satır/byte + LF teyidi +
  224 satırlık farkın manifest açıklaması).
- İş Gardash ortamında koşulur; bu repo zinciri/validator'ları sağlar ve
  aggregate gate kanıtını inceler.
- KURAL (2026-07-11 revizyonu): Derlem tetiği belirsiz süre uzakta olduğu için
  Faz 2, geri-uyumlu shim'ler + bit-aynılık kapısıyla ERKEN başlatıldı (karar
  notu Faz 2'de). PII işi geldiğinde HEAD yeşilse oradan, değilse Faz 2 öncesi
  son tag'den koşulur; eski script giriş noktaları birebir çalışmaya devam eder.
KAPI: SP alignment mismatch 0 · smoke roundtrip %100 · max id < 64.384 ·
  tokens/raw byte ~0.1843 bandında.
```

## Faz 2 — Cerrahi çıkarma (production'ı arşivden ayır; B1)

```text
2.1  src/tr_tokenizer/production/ paketi: analyze_line + protected_spans +
     finite-protected encoder + kind çözümü script'lerden BURAYA taşınır.
2.2  scripts/tokenize_corpus.py ince CLI kabuğuna iner (yalnızca
     tr_tokenizer.production'dan import eder; sys.path hack'i ölür).
2.3  U+2581 benzeri sentinel mantığı TEK yerde toplanır (shotgun surgery biter).
KAPI (taviz yok): mevcut test paketi yeşil + tokenize çıktısı repo içi smoke
     fixture'larında BİT-AYNI + Gardash'tan istenecek 10k örneklem
     re-tokenize'ında checksums.json ile BİT-AYNI. Bit-aynılık kanıtlanamayan
     taşıma revert edilir.
```

Başlatma kararı ve repo-içi kapı sonucu (2026-07-11):

```text
Karar: Derlem tetiği belirsiz olduğundan Faz 2 erken başlatıldı; risk,
  (a) eski script konumlarının production paketinden re-export eden shim'lere
  dönüştürülmesi (tarihsel komutlar/importlar birebir çalışır) ve
  (b) taşıma-öncesi baseline'a karşı bit-aynılık kapısıyla sıfırlandı.
Taşınanlar:
  production/detector.py  <- materialize_v2_soft_morph_artifacts (analyze_line ailesi)
  production/spans.py     <- audit_v2_1 (Span/protected_spans) + tokenize_v3_1
                             (EncodedTokenSpan/span_to_json/token_mask_for_line)
  production/sp.py        <- evaluate_v2_finite (load_sp_processor) + run_tiny
                             (_processor_* yardımcıları)
  production/config.py    <- run_tiny (TokenizerConfig/ProbeConfig/load_probe_config)
                             + tokenize_v3_1 (find_tokenizer) + evaluate_v2_protected_encoder
                             (ProtectedPiece/load_selected_pieces)
  tokenize_corpus.py artık yalnızca tr_tokenizer.production + stdlib import eder.
Kapı kanıtı (demo SP1k model, 2 girdi: 15 satırlık zorlu set [U+2581 literal
  dahil] + demo corpus; workers=1 ve workers=2):
  tokens.bin / loss_mask.bin / index.jsonl / sidecar.jsonl: 3 kıyasta da BİT-AYNI
  manifest.json farkı: yalnızca gömülü çıktı dizin yolları (beklenen)
  test paketi: 319/319 yeşil
Kalan: Gardash'tan 10k örneklem bit-aynılık teyidi (Faz 1 PII işiyle birlikte
  doğal olarak gelir); 2.3 için boundary_weighted_bpe.py içindeki bağımsız
  U+2581 kopyası Faz 3 karantinasında ele alınacak.
```

## Faz 3 — Karantina ve paket temizliği (B6/B7)

```text
3.1  Kapalı deney script'leri scripts/ -> research/ altına taşınır
     (Faz 2'den ÖNCE YAPILAMAZ; production hâlâ onlardan import ediyor).
3.2  boundary_weighted_bpe.py, baseline_bpe.py, external_baselines.py
     paketten çıkar (research/ ya da ayrı arşiv). İlgili testler taşınır.
3.3  Paket sürümü karar: API'den modül çıkarmak = en az minor bump (3.9.0);
     v3.8 TOKENIZER kontratı etkilenmez (o model/id kontratıdır, pip paketi değil).
3.4  docs/current_resume_point.md sadeleştirme: tarihsel katmanlar
     docs/history/ altına, dosyada yalnızca güncel durum + işaretçiler kalır.
KAPI: pytest yeşil + guardrail'ler + README'deki her komut taze clone'da çalışır.
```

## Faz 4 — Sonraki sürüm hattı ("v4"; dışsal tetik)

```text
Tetik: yeni corpus kapsamı (çok dilli / kod-ağırlıklı; örn. Gardash v2 verisi:
FineWeb-2/CulturaX TR 30-100B + The Stack + sentetik ders kitabı).
Zorunlu yeniden koşulacak kapılar (docs/tamga_v3_8_release_and_maintenance_roadmap.md):
  vocab boyutu seçimi (Gardash dersi: 64k vocab küçük modelde parametrelerin
  ~%37'si olabiliyor -> 32k/48k yeniden aday) · fertility + fallback canary ·
  sabit-byte LM kıyası · roundtrip + sidecar gate'leri · LLM entegrasyon smoke.
Tasarım girdileri: docs/multilingual_strategy.md (katmanlama-önce-vocab-sonra,
  geri döndürülemezlik bayrakları) · sentinel çarpışması dersi (U+2581 vakası:
  web corpus'u HER sentinel'i içerir varsay; kaçış kuralı + erken tam-tarama
  reconstruct denetimi) · SP eğitiminin bellek tavanı (1M örneklem dersi).
v3.8'e DOKUNULMAZ; yeni hat yeni sürümdür.
```

---

## Durum takibi

| Faz | Durum | Commit izi | Not |
|---|---|---|---|
| 0 | ✅ tamamlandı (2026-07-11) | `3df0523` (0.1-0.3), `3cb5080` (0.4-0.5) | kapı: 319/319 test + lossless smoke 6/6 + env-override/zorunlu-arg doğrulamaları |
| 1 | ⏳ Derlem release bekliyor | — | readiness: `docs/v3_8_pii_clean_retokenize_readiness.md` + şablon config; araçlar Faz 0'da onarıldı |
| 2 | 🔄 repo-içi kapılar GEÇTİ (2026-07-11) | `5625c02` | production paketi + shim'ler; 4 artifact × 3 kıyas bit-aynı; dışsal 10k teyidi Faz 1 ile gelir |
| 3 | ⏸ Faz 2 kapanışı sonrası | — | sıra bağımlılığı kesin; shim'ler sayesinde script taşıma artık düşük risk |
| 4 | ⏸ dışsal tetik | — | yeni corpus kapsamı (çok dilli / kod-ağırlıklı) |

Belge zinciri (devirde okunma sırası): otopsi Bölüm 4 kapanış tablosu →
bu tablo → `docs/current_resume_point.md` en üst bölümü. Bir faz kapandığında
üçü birden güncellenir; commit mesajları kanıtın kendisini taşır.

Bu tabloyu her faz geçişinde güncelleyin; ayrıntılı güncel durum her zaman
`docs/current_resume_point.md` başına yazılır.
