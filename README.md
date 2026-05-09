# tr-centric-tokenizer

A Turkish-centered morphology-aware tokenizer research prototype.

Bu proje production tokenizer degildir. Amac, Turkce eklemeli yapida morfolojik
sinirlari koruyan deterministik bir cekirdek tasarlamak, bunu gold eval setleri
ve toy BPE baseline'lariyla olculebilir hale getirmektir.

Kapsam ileride Turkce deterministic tokenizer, Turkce merkezli cok dilli
tokenizer, Turk dilleri tokenizer cluster, MorphBPE fallback, BPE baseline
comparison ve LLM tokenizer research basliklarina genisleyebilir.

Danismanlar icin ayrintili durum raporu:
[docs/advisor_brief.md](docs/advisor_brief.md)

## Ilk Calistirma

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

python -m pytest
python -m tr_tokenizer "Türkiye'den kedilerden geldim."
```

Ornek:

```text
["▁Türkiye", "'", "+den", "▁kedi", "+ler", "+den", "▁gel", "+di", "+m", "."]
Türkiye'den kedilerden geldim.
```

## Evaluation

```powershell
python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
python scripts/write_eval_report.py data/eval/tr_gold_expanded.tsv artifacts/eval_report_expanded.md
python scripts/write_eval_report.py data/eval/tr_challenge.tsv artifacts/eval_report_challenge.md
```

`tr_gold_expanded.tsv` cekirdek regression setidir ve v1.0-rc1 icin exact match
beklenir. `tr_challenge.tsv` daha genis ve zor bir challenge setidir; exact
match sozlesmesi yoktur, yeni hatalari gorunur yapmak icin vardir.

Boundary F1 tanimi icin [docs/evaluation.md](docs/evaluation.md) dosyasina
bakin.

## Challenge Error Analysis

`tr_challenge.tsv` regression sozlesmesi degil, hata analizi/dev setidir. v1.0-rc2
bu setteki mismatch'leri kategori, missing token ve over/under-splitting
heuristic'leriyle raporlar.

```powershell
python scripts/analyze_mismatches.py data/eval/tr_challenge.tsv artifacts/challenge_mismatch_analysis.md
```

v1.1 hedef mismatch notlari icin
[docs/v1_1_target_mismatches.md](docs/v1_1_target_mismatches.md) dosyasina
bakin.

v1.1 ozet raporu [artifacts/v1_1_report.md](artifacts/v1_1_report.md),
ambiguity/negative-word karar notlari ise
[docs/ambiguity_policy.md](docs/ambiguity_policy.md) icindedir.

v1.2 error taxonomy raporu icin:

```powershell
python scripts/label_challenge_mismatches.py data/eval/tr_challenge.tsv data/eval/tr_challenge_labeled.tsv --markdown-out artifacts/v1_2_error_taxonomy_report.md
```

Etiket tanimlari [docs/v1_2_error_taxonomy.md](docs/v1_2_error_taxonomy.md)
icindedir.

v1.3 oncesi hidden/heldout eval protokolu:
[docs/hidden_eval_protocol.md](docs/hidden_eval_protocol.md)
ve etiketleme kilavuzu:
[docs/hidden_eval_labeling_guideline.md](docs/hidden_eval_labeling_guideline.md).
Etiketleyiciye verilecek kisa paket:
[docs/hidden_eval_labeler_packet.md](docs/hidden_eval_labeler_packet.md).
Bos public template:
[data/eval/templates/tr_hidden_eval_template.tsv](data/eval/templates/tr_hidden_eval_template.tsv).

Gercek hidden eval dosyasi public repo'ya konmaz. Onerilen private path:
`data/eval/private/tr_hidden_eval.tsv`. Public raporlarda yalnizca aggregate
metrikler yer alir; hidden cumleler veya token listeleri yazilmaz.

## BPE Sweep

Bu BPE baseline production tokenizer degildir. Minimal, pure-Python toy BPE
yalnizca morfoloji-duyarli tokenizer ile standart subword yaklasimini
karsilastirmak icin kullanilir.

```powershell
python scripts/check_eval_leakage.py data/train/tr_bpe_train.txt data/eval/tr_gold_expanded.tsv
python scripts/train_baseline_bpe.py data/train/tr_bpe_train.txt artifacts/bpe_200.json --vocab-size 200
python scripts/train_baseline_bpe.py data/train/tr_bpe_train.txt artifacts/bpe_500.json --vocab-size 500
python scripts/train_baseline_bpe.py data/train/tr_bpe_train.txt artifacts/bpe_1000.json --vocab-size 1000
python scripts/compare_bpe_sweep.py data/eval/tr_gold_expanded.tsv artifacts/bpe_200.json artifacts/bpe_500.json artifacts/bpe_1000.json --markdown-out artifacts/bpe_sweep_report.md
```

`data/train/tr_bpe_train.txt` eval cumlelerini birebir icermeyen demo corpus'tur;
production corpus degildir.

## Tasarim Prensipleri

- Kelime baslangici `▁` marker'iyle gosterilir.
- Apostrof sonrasi ekler ayrilir: `Türkiye'den -> ▁Türkiye ' +den`.
- Yuzey govde korunur: `kitaplarımdan -> ▁Kitap +lar +ım +dan`,
  `kitabımdan -> ▁Kitab +ım +dan`.
- Kisa riskli ekler genel greedy splitter'a konmaz; lexicon-aware guvenli akista
  kullanilir.
- Informal bicimler standart dile cevrilmez:
  `Gelicem -> ▁Gel +icem`, `Gidiyom -> ▁Gid +iyom`.
- Code/proper-name orneklerinde yuzey form korunur:
  `README.md`, `API'den`, `OpenAIlaştırılamayanlardanmış`.

Daha ayrintili gerekceler icin [docs/design.md](docs/design.md) dosyasina bakin.

## Sinirlamalar

- Bu henuz production tokenizer degildir.
- Gold eval kucuk ve elle tasarlanmistir.
- Challenge eval genisletilmis olsa da dogal corpus yerine kontrollu orneklerden
  olusur.
- BPE baseline toy baseline'dir; akademik veya endustriyel BPE/Unigram yerine
  gecmez.
- Gercek LLM kalitesi icin kucuk model pretraining veya downstream deneyi gerekir.
- Mevcut sistem deterministic kural/lexicon tabanlidir; nihai sistem
  MorphBPE/hybrid olabilir.

## Roadmap

- v1.0: frozen deterministic research prototype, raporlar ve regression setleri.
- v1.1: low-risk pretokenizer fixes, number/date/file-like guards.
- v1.2: challenge mismatch taxonomy, davranis degisikligi olmadan planlama.
- v1.3: hidden/heldout eval protokolu, kalibrasyon ve tarafsiz sinyal kurulumu.
- v1.4: yalnizca dusuk riskli safe-rule candidate batch.
- v1.5: lexicon batch discipline ve independent morphological reference
  integration hazirligi.
- v2.0: deterministic morphology layer + MorphBPE trainer.
- Uzun vadede: Turkce/Turk dilleri subword fallback, Ingilizce/kod cluster,
  byte fallback ve cok dilli vocabulary allocation.

## Proje Yapisi

```text
src/tr_tokenizer/   Python paket kodu
tests/              Pytest testleri
data/eval/          Gold ve challenge eval setleri
data/train/         Demo BPE train corpus
scripts/            Evaluation, BPE train ve rapor scriptleri
docs/               Tasarim ve evaluation notlari
artifacts/          Uretilen model ve rapor ciktilari
```
