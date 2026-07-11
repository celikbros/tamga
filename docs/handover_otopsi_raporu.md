# Devir-Teslim Otopsi Raporu (Forensic Audit)

Tarih: 2026-07-11
Kapsam: tamga reposu (v3.8.0 sonrası durum)
Amaç: Projeyi devralacak mühendisin, neyin ne olduğunu ve nerelerin çürük
olduğunu tek belgeden öğrenmesi. Övgü yok; her bulgu dosya/satır referanslı.

> Sonraki adım planı için: `docs/handover_iyilestirme_yol_haritasi.md`
> Güncel proje durumu için: `docs/current_resume_point.md`

---

## 0. Projenin gerçek kimliği (30 saniyede)

Bu repo TEK proje gibi görünen İKİ şey içerir:

1. **Prototip** — `src/tr_tokenizer/` (1.665 satır): deterministik, kural
   tabanlı Türkçe morfoloji bölücüsü. `tamga` CLI'ının çalıştırdığı şey budur
   (`src/tr_tokenizer/__main__.py:30`). Kendi docstring'i "prototype" der
   (`src/tr_tokenizer/__init__.py:1`). **Production tokenizer BU DEĞİLDİR.**
2. **Ürün** — v3.8 production tokenizer
   (`sp64k_final_protected_passthrough_sidecar_controls128`): SentencePiece
   unigram 64k + korumalı rota passthrough + byte fallback + 128 kontrol id +
   sidecar. Kayıpsızlık (byte-exact roundtrip) garantisi BU zincire aittir ve
   kanıtlıdır (bkz. `docs/v3_8_phase2_acceptance_status.md`). Model dosyası
   **repoda yoktur** (private handoff); encode mantığı `src/`te değil
   **script katmanındadır**.

Araştırma süreci v1.x deterministik morfoloji fikriyle başladı; v2.0 ölçümleri
bu mekanizmanın SP64k'yı yenemediğini gösterdi (kapalı negatif sonuçlar:
`docs/v2_0_*_findings.md` serisi); v3.x hattı SP + koruma + sidecar ile
production'a gitti. **Veri kazandı, marka eski mekanizmanın üstünde kaldı.**

## 1. Kanıtlı ana bulgular

### B1. Ters bağımlılık: production, deney arşivinden import ediyor (KRİTİK)

`scripts/tokenize_corpus.py:19-31` (production tokenization giriş noktası)
şu araştırma script'lerinden import yapar:

```text
scripts/audit_v2_1_sidecar_operation_simulation.py  -> protected_spans
scripts/evaluate_v2_finite_protected_sp64_intrinsic.py
scripts/materialize_v2_soft_morph_artifacts.py      -> analyze_line (korumalı span dedektörü!)
scripts/run_tiny_lm_bpb_probe.py                    -> production "kind" çözümü (1.589 satırlık deney harness'ı; satır 195/1065/1087)
scripts/tokenize_v3_1_corpus_smoke.py
```

`scripts/` bir paket bile değildir (`__init__.py` yok); zincir
`tokenize_corpus.py:16-17`'deki `sys.path.insert` ile ve yalnızca repo
kökünden çalışır. Sonuç: U+2581 dedektör fix'i ÜÇ dosyaya yamanmak zorunda
kaldı (`docs/v3_8_detector_reconstruct_crash_fix.md`) — shotgun surgery kanıtı.

### B2. Varsayılan mod "lossless" DEĞİL; README aksini söylüyor (KRİTİK)

Ampirik (2026-07-11, `encode()`/`decode()` varsayılan ayarlarla):

```text
FAIL 'iki  bosluk'   -> 'iki bosluk'      (çift boşluk kaybı)
FAIL 'tab\tvar'      -> 'tab var'
FAIL 'satir\nsonu'   -> 'satir sonu'
FAIL ' basta bosluk' -> 'basta bosluk'
FAIL 'soru ?!'       -> 'soru?!'          (noktalama heuristiği kaybı)
```

Sebep: `src/tr_tokenizer/__main__.py` `preserve_whitespace=False` ile kurar;
`decode()` boşlukları tahmin eder (`tokenizer.py:134-178`, `_NO_SPACE_BEFORE`
satır 27). Gerçek kayıpsız yol (`_decode_lossless`, satır 181) opt-in'dir.
Guardrail seti (`tr_stress_public` 34/34) tekli boşluklu örneklerden oluştuğu
için bunu hiç yakalamadı. "Lossless" iddiası yalnızca v3.8 sidecar zinciri
için doğrudur.

### B3. Ölü mutlak yollar kritik araçların içinde (KRİTİK — aktif iş bloklayıcı)

`C:/CELIK-GARDASH` klasörü artık YOK (LLM projesi 2026-07-05'te
`C:\CELIKBROS PROJECTS\gardash`'a taşındı). Buna rağmen şuralarda hardcoded:

```text
scripts/run_v3_8_final_release_gates.py   (satır 11, 362-379)  <- PII re-tokenize işinin gate'leri
scripts/run_v3_8_final_sp_retrain.py      (satır 188-190, 309-315, 377)
scripts/tokenize_v3_1_corpus_smoke.py     (satır 400, 405)
scripts/materialize_v3_1_ablation_split.py (satır 82)
scripts/report_v3_1_gardash_fertility.py  (satır 388, 398)
configs/v3_8_final_sidecar_sp64k.toml     (satır 2-4, 24)      <- kanonik v3.8 config'i
configs/v3_0_gardash_sidecar.toml, configs/v1_7_baselines.toml (arşiv)
```

Kuyruktaki tek reaktif iş (PII-temiz re-tokenize,
`docs/v3_8_pii_clean_retokenize_readiness.md`) tam bu araçlardan geçer.

### B4. Bayat varsayılanlar: production script v3.5'e işaret ediyor (YÜKSEK)

`scripts/tokenize_corpus.py:520-521` varsayılanı:
`configs/v3_5_sidecar_sp64k_stratified_480mb.toml` +
`sp64k_stratified_480mb_protected_passthrough_sidecar`. Bayrak vermeyi
unutan operatör sessizce YANLIŞ NESİL tokenizer config'i yükler.

### B5. Paketleme tutarsızlığı (ORTA)

`pyproject.toml:25` `dependencies = []`; ama production zinciri
`sentencepiece` ister — o da yalnızca opsiyonel `[baselines]` extra'sında
(satır 31-35). Taze kurulumda `tokenize_corpus.py` ImportError verir.

### B6. Paket içinde ölü/kapatılmış kod (ORTA)

```text
src/tr_tokenizer/boundary_weighted_bpe.py  (208 satır)  kapalı araştırma dalı
  (dokümanlarda "demoted/diagnostic-only"); tek kullanıcı: 1 probe script + testi
src/tr_tokenizer/baseline_bpe.py           (145 satır)  v1.5 toy BPE baseline
src/tr_tokenizer/external_baselines.py     (163 satır)  kıyas sarmalayıcıları
```

Bunlar kurulabilir paketin API'sinde durmamalı.

### B7. Kod biçiminde araştırma defteri (DÜŞÜK ama gürültü kaynağı)

109 script / 37.432 satır (25 `audit_*`, 22 `materialize_*`...) vs 1.665
satırlık çekirdek. Çoğu, dokümanlarda KAPALI ilan edilmiş deneylerin araçları.
Arşiv olarak değerli; `scripts/` içinde durdukça production'la iç içe (B1).

### B8. Küçükler

```text
- "lexicon-aware" akış pratikte elle liste: stems.py ~69, informal.py ~19,
  morphology.py ~55 kayıt. Çalışıyor; adlandırma abartılı.
- docs/current_resume_point.md 1.900 satır, içinde 6+ adet birbirini geçersiz
  kılan "Latest Actual State" başlığı — güncel gerçek dosya İÇİNDE aranıyor.
- Repo kökünde silinemeyen (yabancı NTFS sahipli) 8 pytest çöp klasörü +
  tests/fixtures/tmp5yzyy371 kalıntısı (admin ile temizlenecek).
```

## 2. Felsefe değerlendirmesi

- **Kök fikir doğru ve sahada doğrulandı:** Türkçe-öncelikli + koruma-öncelikli
  + kayıpsız + ölçümle karar. v3.8 paketi gerçek eğitimde (130M koşu, ~0.2B
  token) sıfır loader hatasıyla tüketildi.
- **Metodoloji de doğru işledi:** proje kendi kurucu mekanizmasını (deterministik
  morfoloji) ölçümle eledi ve veriye uydu. Negatif sonuçlar kapatılıp belgelendi.
- **Çelişki uygulamada:** (1) kurulumun verdiği şey kayıplı prototip, vitrindeki
  iddia "lossless" (B2); (2) "production-final/FROZEN" damgası sayıları dondurdu,
  taşıyıcı mühendisliği değil (B1/B3/B4); (3) marka prototipi gösteriyor, ürünün
  repoda adresi yok (B0/B5).

## 3. Hüküm: Yık ve yeniden yazma — YAPMA. Cerrahi çıkarma — YAP.

Greenfield rewrite REDDEDİLDİ, gerekçe:

1. Reponun asıl varlığı kod değil: dondurulmuş v3.8 kontratı + bit-exact
   yeniden üretilebilirlik kanıt zinciri (checksum'lar, gate raporları;
   tüketici bunlarla EĞİTİM YAPTI) + eval setleri + 319 test + kapalı negatif
   sonuç arşivi. Rewrite bunları iyileştirmez, ilkini riske atar.
2. Kurtarılacak gerçek production kodu küçüktür (~3-4k satır: `analyze_line`,
   `protected_spans`, finite-protected encoder, `tokenize_corpus`, gate'ler).
3. Kabul kapısı hazırdır: her taşıma `checksums.json`'a karşı bit-aynılıkla
   kanıtlanabilir. Davranış değişimi sıfır olduğu sürece bu, donmuş algoritmik
   hattı "açmak" sayılmaz.

Uygulama sırası ve kapıları: `docs/handover_iyilestirme_yol_haritasi.md`.
