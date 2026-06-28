# Tamga

Turkish-first, lossless LLM tokenizer and production corpus toolchain.

Tamga adini eski Turk kulturundeki isaret, muhurlu simge ve kimlik izi
anlamindan alir. Tokenizer, metni modelin kullanacagi geri donuslu isaretlere
donusturur.

v3.8 tokenizer paketi CELIK-GARDAS Faz 4 pretraining icin production-final
olarak kabul edilmistir. Final corpus ve model artifact'lari private handoff
paketinde tutulur; bu repository arastirma gecmisini, kaynak kodu, testleri ve
production corpus araclarini icerir.

Geriye uyumluluk icin Python namespace'i `tr_tokenizer` olarak kalir. Yeni CLI
adi `tamga`; eski `tr-tokenizer` ve `tr-centric-tokenizer` komutlari alias olarak
korunur.

Danismanlar icin ayrintili durum raporu:
[docs/advisor_brief.md](docs/advisor_brief.md)

v1.6 oncesi danisman degerlendirme istegi:
[docs/advisor_update_v1_6_request.md](docs/advisor_update_v1_6_request.md)

v1.6 danisman geri bildirimi triage:
[docs/advisor_feedback_triage_v1_6.md](docs/advisor_feedback_triage_v1_6.md)

v1.6 confidence interval findings:
[docs/v1_6_confidence_interval_findings.md](docs/v1_6_confidence_interval_findings.md)

v1.6 protected span findings:
[docs/v1_6_protected_span_findings.md](docs/v1_6_protected_span_findings.md)

v1.6 natural/demo corpus fertility findings:
[docs/v1_6_fertility_findings.md](docs/v1_6_fertility_findings.md)

Multilingual/Turkic long-term strategy notes:
[docs/multilingual_strategy.md](docs/multilingual_strategy.md) and
[docs/multilingual_observations.md](docs/multilingual_observations.md)

AI expert-review triage for Turkish and multilingual/Turkic feedback:
[docs/ai_expert_review_triage.md](docs/ai_expert_review_triage.md)

Multilingual/Turkic reviewer materials:
[docs/multilingual_reviewer_packet.md](docs/multilingual_reviewer_packet.md),
[docs/multilingual_reviewer_request_message.md](docs/multilingual_reviewer_request_message.md),
and [docs/multilingual_reviewer_response_form.md](docs/multilingual_reviewer_response_form.md)

Fictional reviewer response examples:
[docs/reviewer_response_examples/README.md](docs/reviewer_response_examples/README.md)

Current resume point:
[docs/current_resume_point.md](docs/current_resume_point.md)

## Ilk Calistirma

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

python -m pytest
python -m tr_tokenizer "Türkiye'den kedilerden geldim."
# Editable install sonrasinda:
tamga "Türkiye'den kedilerden geldim."
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

v1.4 icin davranis degistirmeyen karar cercevesi:
[docs/v1_4_decision_framework.md](docs/v1_4_decision_framework.md)
v1.4 ilk aday listesi:
[docs/v1_4_candidate_shortlist.md](docs/v1_4_candidate_shortlist.md)
v1.4 S1 buffered ablative analiz notu:
[docs/v1_4_s1_buffered_ablative_analysis.md](docs/v1_4_s1_buffered_ablative_analysis.md)
v1.5 real tokenizer baseline plani:
[docs/v1_5_real_tokenizer_baselines.md](docs/v1_5_real_tokenizer_baselines.md)

v1.5 baseline bulgulari:
[docs/v1_5_baseline_findings.md](docs/v1_5_baseline_findings.md)

v1.5 English smoke bulgulari:
[docs/v1_5_english_smoke_findings.md](docs/v1_5_english_smoke_findings.md)

v1.5 multilingual smoke bulgulari:
[docs/v1_5_multilingual_smoke_findings.md](docs/v1_5_multilingual_smoke_findings.md)

v1.6 do-no-harm routing plani:
[docs/v1_6_do_no_harm_routing_plan.md](docs/v1_6_do_no_harm_routing_plan.md)

v1.6b Batch 1 technical comparator guard:
[docs/v1_6b_batch1_technical_comparator_guard.md](docs/v1_6b_batch1_technical_comparator_guard.md)

v1.6b Batch 2 Arabic/Greek script fallback:
[docs/v1_6b_batch2_arabic_greek_fallback.md](docs/v1_6b_batch2_arabic_greek_fallback.md)

v1.6b Batch 3 English/European apostrophe guard:
[docs/v1_6b_batch3_apostrophe_guard.md](docs/v1_6b_batch3_apostrophe_guard.md)

v1.6b Batch 4 non-Turkish Latin word guard:
[docs/v1_6b_batch4_non_turkish_latin_guard.md](docs/v1_6b_batch4_non_turkish_latin_guard.md)

v1.6b R3 Azerbaijani routing decision:
[docs/v1_6b_r3_deferred_decision.md](docs/v1_6b_r3_deferred_decision.md)

v1.7 plan:
[docs/v1_7_plan.md](docs/v1_7_plan.md)

v1.7 heldout eval plan:
[docs/v1_7_heldout_eval_plan.md](docs/v1_7_heldout_eval_plan.md)

v1.7 missing baseline protocol:
[docs/v1_7_missing_baseline_protocol.md](docs/v1_7_missing_baseline_protocol.md)

v1.7 baseline matrix config:
[configs/v1_7_baselines.toml](configs/v1_7_baselines.toml)

v1.7 SentencePiece sweep config:
[configs/v1_7_sentencepiece_sweep.toml](configs/v1_7_sentencepiece_sweep.toml)

v1.7 local SentencePiece pilot sweep config:
[configs/v1_7_sentencepiece_pilot_sweep.toml](configs/v1_7_sentencepiece_pilot_sweep.toml)

v1.7 claim-grade corpus plan:
[docs/v1_7_claim_grade_corpus_plan.md](docs/v1_7_claim_grade_corpus_plan.md)

v1.7 claim-grade corpus prep config:
[configs/v1_7_claim_grade_corpus.toml](configs/v1_7_claim_grade_corpus.toml)

v1.7 CELIK_AI local corpus/tokenizer audit:
[docs/v1_7_celik_ai_corpus_tokenizer_audit.md](docs/v1_7_celik_ai_corpus_tokenizer_audit.md)

v1.7 CELIK gold corpus quality audit:
[artifacts/v1_7_celik_gold_corpus_quality_audit_100k.md](artifacts/v1_7_celik_gold_corpus_quality_audit_100k.md)

v1.7 CELIK gold filtered pilot findings:
[docs/v1_7_celik_gold_filtered_pilot_findings.md](docs/v1_7_celik_gold_filtered_pilot_findings.md)

v1.7 CELIK gold clean sweep findings:
[docs/v1_7_celik_gold_clean_sweep_findings.md](docs/v1_7_celik_gold_clean_sweep_findings.md)

v1.7 SentencePiece pilot findings:
[docs/v1_7_sentencepiece_pilot_findings.md](docs/v1_7_sentencepiece_pilot_findings.md)

v1.7 downstream probe protocol:
[docs/v1_7_downstream_probe_protocol.md](docs/v1_7_downstream_probe_protocol.md)

v1.7 downstream probe prep findings:
[docs/v1_7_downstream_probe_prep_findings.md](docs/v1_7_downstream_probe_prep_findings.md)

LLM handoff packet:
[docs/llm_handoff_packet.md](docs/llm_handoff_packet.md)

v1.7 downstream probe handoff:
[docs/v1_7_downstream_probe_handoff.md](docs/v1_7_downstream_probe_handoff.md)

v2.0 router/MorphBPE RFC:
[docs/v2_0_router_morphbpe_rfc.md](docs/v2_0_router_morphbpe_rfc.md)

v1.3 oncesi hidden/heldout eval protokolu:
[docs/hidden_eval_protocol.md](docs/hidden_eval_protocol.md)
ve etiketleme kilavuzu:
[docs/hidden_eval_labeling_guideline.md](docs/hidden_eval_labeling_guideline.md).
Etiketleyiciye verilecek kisa paket:
[docs/hidden_eval_labeler_packet.md](docs/hidden_eval_labeler_packet.md).
Danismana/etiketleyiciye gonderilecek hazir mesaj:
[docs/hidden_eval_request_message.md](docs/hidden_eval_request_message.md).
Etiketleyici bulma ve ilk temas plani:
[docs/labeler_recruitment_plan.md](docs/labeler_recruitment_plan.md).
Bos public template:
[data/eval/templates/tr_hidden_eval_template.tsv](data/eval/templates/tr_hidden_eval_template.tsv).

Dis insan etiketleyici/hoca sureci su an zorunlu kritik yol degildir. Teknik
ilerleme icin pratik v1.3 hatti:
[docs/v1_3_practical_track.md](docs/v1_3_practical_track.md).
v1.3 kapanis raporu:
[docs/v1_3_closing_report.md](docs/v1_3_closing_report.md).

Gercek hidden eval dosyasi public repo'ya konmaz. Onerilen private path:
`data/eval/private/tr_hidden_eval.tsv`. Public raporlarda yalnizca aggregate
metrikler yer alir; hidden cumleler veya token listeleri yazilmaz.

Hidden eval aggregate raporu:

```powershell
python scripts/evaluate_hidden_eval.py data/eval/private/tr_hidden_eval.tsv --markdown-out artifacts/v1_3_hidden_eval_report.md
```

Public v1.3 stress raporu:

```powershell
python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_3_public_stress_report.md
```

Coverage telemetry:

```powershell
python scripts/report_coverage.py data/eval/tr_gold_expanded.tsv --markdown-out artifacts/v1_3_coverage_expanded.md
python scripts/report_coverage.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_3_coverage_stress.md
```

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

## Real Tokenizer Baselines

v1.5, toy BPE disinda production-like tokenizer aileleriyle karsilastirma
altyapisini baslatir. Dis tokenizer bagimliliklari opsiyoneldir; paketler veya
local model cache yoksa ilgili baseline `skipped` olarak raporlanir.

```powershell
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --markdown-out artifacts/v1_5_real_tokenizer_report_expanded.md
python scripts/compare_real_tokenizers.py data/eval/tr_challenge.tsv --markdown-out artifacts/v1_5_real_tokenizer_report_challenge.md
```

Opsiyonel Hugging Face veya SentencePiece baseline eklemek icin:

```powershell
python scripts/train_sentencepiece_baselines.py data/train/tr_bpe_train.txt artifacts/sp_bpe_1000 --model-type bpe --vocab-size 1000
python scripts/train_sentencepiece_baselines.py data/train/tr_bpe_train.txt artifacts/sp_unigram_1000 --model-type unigram --vocab-size 1000
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --hf qwen=Qwen/Qwen2.5-0.5B --markdown-out artifacts/v1_5_qwen_report.md
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --sentencepiece sp_bpe=artifacts/sp_bpe_1000.model --sentencepiece sp_unigram=artifacts/sp_unigram_1000.model
```

Varsayilan Hugging Face modu local cache ile sinirlidir. Eksik modeli indirmek
icin bilincli olarak `--allow-download` verilir.

v1.7 visible baseline matrix config'i:

```powershell
python scripts/report_baseline_matrix.py configs/v1_7_baselines.toml
```

Bu komut expanded, challenge, English smoke ve multilingual smoke icin ayri
Markdown raporlari uretir:

```text
artifacts/v1_7_baseline_matrix_expanded.md
artifacts/v1_7_baseline_matrix_challenge.md
artifacts/v1_7_baseline_matrix_english_smoke.md
artifacts/v1_7_baseline_matrix_multilingual_smoke.md
```

Config varsayilan olarak Hugging Face modellerini kapali tutar; yerel cache veya
bilincli indirme izni olmadan external model indirmez.

Local Hugging Face `tokenizers` JSON dosyalari da opsiyonel baseline olarak
eklenebilir:

```powershell
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --tokenizers-json celik_64k_byte_bpe=C:\CELIK_AI\celik_core\celik_core\tokenizer.json --markdown-out artifacts/v1_7_celik_64k_tokenizer_report_expanded.md
```

Bu local path repo icin zorunlu degildir; sadece bu makinedeki eski CELIK
ByteLevel BPE tokenizer'ini referans olarak olcer.

v1.7 SentencePiece sweep scaffolding:

```powershell
python scripts/run_sentencepiece_sweep.py configs/v1_7_sentencepiece_sweep.toml
```

Bu config su anda sadece demo corpus uzerinde 1k BPE ve 1k Unigram calistirir.
4k/8k/16k/32k/48k/64k varyantlari config'te hazirdir ama claim-grade corpus ve
leakage kontrolu olmadan kapali tutulur.

v1.7 claim-grade corpus prep/leakage skeleton:

```powershell
python scripts/prepare_claim_grade_corpus.py configs/v1_7_claim_grade_corpus.toml --manifest-only --max-scan-lines 1000
```

Bu komut local/private corpus kaynaklarini okur, eval leakage icin exact,
normalized ve n-gram kontrollerini raporlar, ve yalnizca aggregate manifest
dosyalarini public repo'ya koyar:

```text
artifacts/v1_7_claim_grade_corpus_manifest.md
artifacts/v1_7_claim_grade_leakage_report.md
```

Buyuk corpus metinleri `data/train/private/` ve uretilen claim-grade text
ornekleri `data/train/claim_grade/` altinda git disi tutulur.

Local CELIK_AI SentencePiece pilot sweep:

```powershell
python scripts/prepare_claim_grade_corpus.py configs/v1_7_claim_grade_corpus.toml --max-scan-lines 15000
python scripts/run_sentencepiece_sweep.py configs/v1_7_sentencepiece_pilot_sweep.toml
```

Bu pilot claim-grade degildir. `artifacts/private/` altindaki model/vocab
dosyalari git disi kalir; public repo'da yalnizca aggregate raporlar tutulur.

Deprecated raw JSONL corpus quality audit:

```powershell
python scripts/audit_jsonl_corpus_quality.py data/train/private/celik_ai/archive/deprecated/celik_gold_corpus.raw.deprecated.jsonl --max-lines 100000 --markdown-out artifacts/v1_7_celik_gold_corpus_quality_audit_100k.md
```

Bu rapor tarihsel raw kopya icindir. Aktif v1.7 calismasi clean kopyayi kullanir.
Rapor corpus metni yayinlamaz; yalnizca JSONL yapisi, duplicate, uzun satir,
script/language hint ve bozulma sinyallerini aggregate olarak verir.

Deprecated raw filtered local CELIK gold corpus pilot:

```powershell
python scripts/prepare_claim_grade_corpus.py configs/v1_7_celik_gold_filtered_sample.toml --max-scan-lines 120000
python scripts/run_sentencepiece_sweep.py configs/v1_7_celik_gold_sentencepiece_pilot_sweep.toml --force
```

Bu pilot tarihsel raw kaynak icindir ve artik aktif hat degildir. Aktif hat
asagidaki clean local CELIK gold corpus sweep'tir. Filtrelenmis local sample ve
SentencePiece model/vocab dosyalari git disinda kalir; public repo'da yalnizca
aggregate manifest, leakage ve visible eval raporlari tutulur:

```text
artifacts/v1_7_celik_gold_filtered_sample_manifest.md
artifacts/v1_7_celik_gold_filtered_sample_leakage_report.md
artifacts/v1_7_celik_gold_sentencepiece_pilot_sweep_expanded.md
artifacts/v1_7_celik_gold_sentencepiece_pilot_sweep_challenge.md
```

Clean local CELIK gold corpus sweep:

```powershell
python scripts/prepare_claim_grade_corpus.py configs/v1_7_celik_gold_clean_sample.toml --max-scan-lines 120000
python scripts/run_sentencepiece_sweep.py configs/v1_7_celik_gold_clean_sentencepiece_sweep.toml --force
```

Bu hat `data/train/private/celik_ai/celik_gold_corpus.clean.jsonl` private
kopyasini kullanir. Public repo'da yalnizca aggregate leakage/manifest ve
visible baseline raporlari tutulur:

```text
artifacts/v1_7_celik_gold_clean_sample_manifest.md
artifacts/v1_7_celik_gold_clean_sample_leakage_report.md
artifacts/v1_7_celik_gold_clean_pilot_eval_leakage_report.md
artifacts/v1_7_celik_gold_clean_sentencepiece_sweep_expanded.md
artifacts/v1_7_celik_gold_clean_sentencepiece_sweep_challenge.md
```

Direct eval-leakage check on the actual clean SP training pilot:

```powershell
python scripts/check_eval_leakage.py --corpus data/train/claim_grade/celik_gold_clean_pilot.txt --corpus-format text --gold data/eval/tr_gold_expanded.tsv --challenge data/eval/tr_challenge.tsv --report-out artifacts/v1_7_celik_gold_clean_pilot_eval_leakage_report.md
```

The direct report uses Turkish-aware normalization, word-level 8-gram overlap,
and a separate `short_full` category for one-word eval examples. Corpus snippets
are omitted from public reports unless `--include-snippets` is explicitly used.

Downstream probe prep:

```powershell
python scripts/prepare_downstream_probe.py configs/v1_7_downstream_probe_demo.toml
python scripts/prepare_downstream_probe.py configs/v1_7_downstream_probe_celik_gold_pilot.toml
python scripts/prepare_downstream_probe.py configs/v1_7_downstream_probe_celik_gold_clean_pilot.toml
```

Bu komutlar LLM egitmez. Ayni raw split uzerinde tokenizer bazli private JSONL
token ciktilari ve public aggregate hazirlik raporlari uretir:

```text
artifacts/v1_7_downstream_probe_prep_demo.md
artifacts/v1_7_downstream_probe_prep_celik_gold_pilot.md
artifacts/v1_7_downstream_probe_prep_celik_gold_clean_pilot.md
```

Private token JSONL dosyalari `artifacts/private/` altinda git disi kalir.

## Metric Confidence Intervals

v1.6a adds bootstrap confidence interval reporting for visible eval metrics. This
does not replace hidden eval; it only makes small-set uncertainty explicit.

```powershell
python scripts/report_confidence_intervals.py data/eval/tr_gold_expanded.tsv --samples 1000 --markdown-out artifacts/v1_6_ci_expanded.md
python scripts/report_confidence_intervals.py data/eval/tr_challenge.tsv --samples 1000 --markdown-out artifacts/v1_6_ci_challenge.md
```

All-baseline CI reports can include toy BPE, SentencePiece, and local-cache
Hugging Face tokenizers:

```powershell
python scripts/report_confidence_intervals.py data/eval/tr_challenge.tsv --samples 500 --toy-bpe toy_bpe_1000=artifacts/bpe_1000.json --sentencepiece sp_bpe=artifacts/sp_bpe_1000.model --sentencepiece sp_unigram=artifacts/sp_unigram_1000.model --hf qwen=Qwen/Qwen2.5-0.5B --hf mistral=mistralai/Mistral-7B-v0.1 --hf llama=meta-llama/Llama-3.2-1B --markdown-out artifacts/v1_6_ci_all_challenge.md
```

Findings summary:
[docs/v1_6_confidence_interval_findings.md](docs/v1_6_confidence_interval_findings.md)

Generated CI reports also include English and multilingual smoke sets:
`artifacts/v1_6_ci_all_en_smoke.md` and
`artifacts/v1_6_ci_all_multilingual_smoke.md`.

`tr_stress_public.tsv` morfolojik gold degil, protected-span smoke setidir. Onun
icin mevcut stress raporu kullanilir:

```powershell
python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/stress_public_report.md
```

Protected-span baseline report:

```powershell
python scripts/report_protected_spans.py data/eval/tr_stress_public.tsv --toy-bpe toy_bpe_1000=artifacts/bpe_1000.json --sentencepiece sp_bpe=artifacts/sp_bpe_1000.model --sentencepiece sp_unigram=artifacts/sp_unigram_1000.model --hf qwen=Qwen/Qwen2.5-0.5B --hf mistral=mistralai/Mistral-7B-v0.1 --hf llama=meta-llama/Llama-3.2-1B --markdown-out artifacts/v1_6_protected_span_report_stress.md
```

Findings summary:
[docs/v1_6_protected_span_findings.md](docs/v1_6_protected_span_findings.md)

Natural/demo corpus fertility report:

```powershell
python scripts/report_fertility.py data/train/tr_bpe_train.txt --toy-bpe toy_bpe_1000=artifacts/bpe_1000.json --sentencepiece sp_bpe=artifacts/sp_bpe_1000.model --sentencepiece sp_unigram=artifacts/sp_unigram_1000.model --hf qwen=Qwen/Qwen2.5-0.5B --hf mistral=mistralai/Mistral-7B-v0.1 --hf llama=meta-llama/Llama-3.2-1B --markdown-out artifacts/v1_6_fertility_report_demo_corpus.md
```

Findings summary:
[docs/v1_6_fertility_findings.md](docs/v1_6_fertility_findings.md)

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
- Cok dilli/Turk dilleri hedefi v2.0 icindir; v1.x non-Turkish smoke
  sonuclari regression hedefi degil, planlama girdisidir.

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
- v1.3: public stress tests, telemetry, hidden-eval protokolu ve aggregate-only
  raporlama.
- v1.4: dusuk riskli safe-rule candidate batch; broad suffix expansion yok.
- v1.5: real tokenizer baselines, SentencePiece/HF karsilastirmalari, English ve
  multilingual smoke setleri.
- v1.6a: measurement strengthening tamamlandi: confidence intervals,
  protected-span break metrics, natural/demo corpus fertility report.
- v1.6b: low-risk do-no-harm routing guards; ilk aday technical
  comparator/package span guard (`transformers>=4.40`, `tokenizers>=0.19`).
  Batch 1 tamamlandi; English smoke `5/10 -> 6/10`, public stress `29/29`,
  protected spans `25/25`.
  Batch 2 tamamlandi; Arabic/Greek script fallback ile multilingual smoke
  `8/20 -> 11/20`, public stress `31/31`, protected spans `25/25`.
  Batch 3 tamamlandi; English smoke `6/10 -> 8/10`, multilingual smoke
  `11/20 -> 12/20`, Turkish apostrophe regression `50/50` korundu.
  Batch 4 tamamlandi; non-Turkish Latin word guard ile multilingual smoke
  `12/20 -> 17/20`, Turkish regression `50/50` korundu.
- v1.6b R3 Azerice routing guard uygulanmadi; danisman konsensusu ile v2.0
  router/MorphBPE planina ertelendi.
- v1.7: independent heldout eval plani, missing baseline plani
  (Morfessor, Turkish-trained BPE/Unigram, BERTurk/XLM-R/mT5), downstream probe
  protokolu, visible baseline matrix config'i, SentencePiece sweep scaffolding
  ve v2.0 router/MorphBPE RFC iskeleti.
- v2.0: MorphBPE/hybrid prototype; full Turkic/multilingual morphology iddiasi
  yok, once routing/fallback mimarisi.
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
