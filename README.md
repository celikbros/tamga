# Tamga

**Türkçe-öncelikli, kayıpsız LLM tokenizer'ı ve production corpus araç zinciri.**
*Turkish-first, lossless LLM tokenizer and production corpus toolchain.*

[Türkçe](#türkçe) · [English](#english)

---

## Türkçe

Tamga, adını eski Türk kültüründeki işaret, mühürlü simge ve kimlik izi
anlamından alır. Tokenizer, metni modelin kullanacağı geri dönüşlü işaretlere
dönüştürür.

### Durum

v3.8 tokenizer paketi, CELIK-GARDAS Faz 4 pretraining için
**production-final** kabul edilmiş ve dondurulmuştur:

```text
tokenizer: sp64k_final_protected_passthrough_sidecar_controls128
efektif vocabulary boyutu: 64.384
tam corpus satırı: 6.027.968
tam corpus token'ı: 2.499.949.602
token/raw byte: 0.184311
SP alignment mismatch: 0
statü: ACCEPTED / FROZEN
```

Final corpus ve model artifact'ları private handoff paketinde tutulur; bu
depo araştırma geçmişini, kaynak kodu, testleri ve production corpus
araçlarını içerir. Kanonik kapanış ve sonraki-sürüm kuralları:

- [docs/v3_8_production_final_closure.md](docs/v3_8_production_final_closure.md)
- [docs/tamga_v3_8_release_and_maintenance_roadmap.md](docs/tamga_v3_8_release_and_maintenance_roadmap.md)
- [docs/current_resume_point.md](docs/current_resume_point.md) — güncel durum

### Kurulum ve İlk Çalıştırma

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

python -m pytest
python -m tr_tokenizer "Türkiye'den kedilerden geldim."
# Editable install sonrasında:
tamga "Türkiye'den kedilerden geldim."
```

Örnek çıktı:

```text
["▁Türkiye", "'", "+den", "▁kedi", "+ler", "+den", "▁gel", "+di", "+m", "."]
Türkiye'den kedilerden geldim.
```

Geriye uyumluluk için Python namespace'i `tr_tokenizer` olarak kalır. Yeni CLI
adı `tamga`; eski `tr-tokenizer` ve `tr-centric-tokenizer` komutları alias
olarak korunur.

### Değerlendirme

```powershell
python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
python scripts/write_eval_report.py data/eval/tr_gold_expanded.tsv artifacts/eval_report_expanded.md
```

- `tr_gold_expanded.tsv` çekirdek regression setidir; exact match beklenir
  (50/50).
- `tr_challenge.tsv` daha geniş ve zor bir challenge setidir; exact match
  sözleşmesi yoktur, yeni hataları görünür yapmak için vardır.
- `tr_stress_public.tsv` protected-span smoke setidir; 34/34 roundtrip
  korunmalıdır.

Boundary F1 tanımı için [docs/evaluation.md](docs/evaluation.md).

### Tasarım Prensipleri

- Kelime başlangıcı `▁` marker'ıyla gösterilir.
- Apostrof sonrası ekler ayrılır: `Türkiye'den → ▁Türkiye ' +den`.
- Yüzey gövde korunur: `kitaplarımdan → ▁Kitap +lar +ım +dan`.
- İnformal biçimler standart dile çevrilmez: `Gelicem → ▁Gel +icem`.
- Protected span'ler (sayı, dosya adı, teknik ifade vb.) kayıpsız korunur;
  decode her zaman byte-exact geri dönüş verir.
- Kısa riskli ekler genel greedy splitter'a konmaz; lexicon-aware güvenli
  akışta kullanılır.

Ayrıntılı gerekçeler: [docs/design.md](docs/design.md)

### Proje Yapısı

```text
src/tr_tokenizer/   Python paket kodu
tests/              Pytest testleri
data/eval/          Gold ve challenge eval setleri
data/train/         Demo BPE train corpus
scripts/            Evaluation, corpus ve rapor scriptleri
configs/            Sweep/probe/corpus config'leri
docs/               Tasarım, karar ve kapanış notları
artifacts/          Üretilen aggregate rapor çıktıları
```

Private corpus/model dosyaları (`data/train/private/`, `artifacts/private/`,
`data/eval/private/`) git dışında tutulur; public raporlar yalnızca aggregate
metrik içerir.

### Araştırma Geçmişi

v1.0'dan v3.8'e uzanan ayrıntılı sürüm geçmişi, komutlar ve rapor bağlantıları
için: [docs/readme_research_history_tr.md](docs/readme_research_history_tr.md)

---

## English

Tamga takes its name from the seal-like identity marks of early Turkic
culture. The tokenizer turns text into fully reversible marks for a language
model to consume.

### Status

The v3.8 tokenizer package is accepted as **production-final** and frozen for
the Turkish-primary CELIK-GARDAS Phase 4 pretraining run:

```text
tokenizer: sp64k_final_protected_passthrough_sidecar_controls128
effective vocabulary size: 64,384
full-corpus lines: 6,027,968
full-corpus tokens: 2,499,949,602
tokens/raw byte: 0.184311
SP alignment mismatches: 0
status: ACCEPTED / FROZEN
```

Final corpus and model artifacts live in a private handoff package; this
repository contains the research history, source code, tests, and production
corpus tooling. Canonical closure and next-version rules:

- [docs/v3_8_production_final_closure.md](docs/v3_8_production_final_closure.md)
- [docs/tamga_v3_8_release_and_maintenance_roadmap.md](docs/tamga_v3_8_release_and_maintenance_roadmap.md)
- [docs/current_resume_point.md](docs/current_resume_point.md) — current state

### Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

python -m pytest
python -m tr_tokenizer "Türkiye'den kedilerden geldim."
# After the editable install:
tamga "Türkiye'den kedilerden geldim."
```

Example output:

```text
["▁Türkiye", "'", "+den", "▁kedi", "+ler", "+den", "▁gel", "+di", "+m", "."]
Türkiye'den kedilerden geldim.
```

For backward compatibility the Python namespace remains `tr_tokenizer`. The
CLI is `tamga`; the legacy `tr-tokenizer` and `tr-centric-tokenizer` commands
are kept as aliases.

### Evaluation

```powershell
python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
python scripts/write_eval_report.py data/eval/tr_gold_expanded.tsv artifacts/eval_report_expanded.md
```

- `tr_gold_expanded.tsv` is the core regression set; exact match is required
  (50/50).
- `tr_challenge.tsv` is a broader, harder challenge set with no exact-match
  contract; it exists to surface new errors.
- `tr_stress_public.tsv` is the protected-span smoke set; 34/34 roundtrip must
  hold.

See [docs/evaluation.md](docs/evaluation.md) for the boundary F1 definition.

### Design Principles

- Word starts are marked with `▁`.
- Suffixes after apostrophes are split: `Türkiye'den → ▁Türkiye ' +den`.
- Surface stems are preserved: `kitaplarımdan → ▁Kitap +lar +ım +dan`.
- Informal forms are not normalized to standard Turkish:
  `Gelicem → ▁Gel +icem`.
- Protected spans (numbers, file names, technical strings, …) are preserved
  losslessly; decoding is always byte-exact.
- Short, risky suffixes are excluded from the general greedy splitter and only
  used on the lexicon-aware safe path.

Detailed rationale: [docs/design.md](docs/design.md)

### Project Layout

```text
src/tr_tokenizer/   Python package code
tests/              Pytest test suite
data/eval/          Gold and challenge eval sets
data/train/         Demo BPE training corpus
scripts/            Evaluation, corpus, and report scripts
configs/            Sweep/probe/corpus configs
docs/               Design, decision, and closure notes
artifacts/          Generated aggregate report outputs
```

Private corpus/model files (`data/train/private/`, `artifacts/private/`,
`data/eval/private/`) stay out of git; public reports contain aggregate
metrics only.

### Research History

For the detailed v1.0 → v3.8 version history with commands and report links,
see [docs/readme_research_history_tr.md](docs/readme_research_history_tr.md)
(Turkish).
