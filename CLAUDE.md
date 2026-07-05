# CLAUDE.md

Bu dosya, bu depoda çalışan AI ajanları (Claude Code vb.) için bağlayıcı proje
kurallarını içerir.

## Commit kuralları (zorunlu)

- Author her zaman `celikbros <62828186+celikbros@users.noreply.github.com>`
  olur (repo git config'inde ayarlıdır; değiştirme).
- Her commit mesajının sonuna şu iki co-author trailer'ı eklenir; başka trailer
  (Claude dahil) eklenmez:

```text
Co-Authored-By: Mehmet Ömer Efe Çelik <293130995+momerefe@users.noreply.github.com>
Co-Authored-By: celikalperen <89036584+celikalperen@users.noreply.github.com>
```

- E-postalar GitHub `users.noreply` formatındadır; numeric ID'ler GitHub
  API'den doğrulanmıştır (momerefe=293130995, celikalperen=89036584). Bu sayede
  her iki isim commit'lerde profillerine bağlı görünür.

## Uzak depo ve erişim

- Remote: `git@github.com-tamga:celikbros/tamga.git`
  (`~/.ssh/config` içindeki `github.com-tamga` alias'ı, deploy key
  `~/.ssh/tamga_deploy`).
- Deploy key'ler GitHub'da repo Settings → Deploy keys altında yönetilir.

## Proje durumu ve guardrail'ler

- Tamga v3.8 production-final olarak **DONDURULMUŞTUR** (CELIK-GARDAS Faz 4
  pretraining). Tokenizer algoritmik hattını yalnızca şu durumlar yeniden açar:
  tekrarlanabilir regresyon, güvenlik/reconstruction hatası veya açık yeni
  corpus kapsamı. Çok dilli/kod-ağırlıklı genişleme yeni sürüm gerektirir;
  v3.8'i değiştiremez.
- Kanonik belgeler: `docs/v3_8_production_final_closure.md`,
  `docs/tamga_v3_8_release_and_maintenance_roadmap.md`,
  `docs/current_resume_point.md` (güncel durum her zaman burada).
- Regression guardrail'leri: `python -m pytest` yeşil kalmalı;
  `tr_gold_expanded.tsv` 50/50; `tr_stress_public.tsv` 34/34 roundtrip;
  protected span break rate 0.0000.
- Geniş Türkçe morfoloji kuralı eklenmez; Azerice morfoloji veya span-level
  routing v3.8 hattında başlatılmaz.
- Private corpus/model dosyaları (`data/train/private/`, `artifacts/private/`,
  `data/eval/private/`) asla public repoya girmez; public raporlar yalnızca
  aggregate metrik içerir.
