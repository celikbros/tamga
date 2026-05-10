# Hidden Eval Request Message

This file contains a ready-to-send message for an advisor or annotator. It is
public and contains no hidden eval examples.

## Short Message

```text
Merhaba,

tr-centric-tokenizer projesi için küçük bir hidden/heldout evaluation seti
hazırlamak istiyoruz.

Amaç: tokenizer'a yeni kural eklemeden önce, sistemin daha önce görmediği
örneklerde nasıl davrandığını ölçmek.

Önemli noktalar:

- Hidden set public GitHub reposuna konmayacak.
- Önce hidden setten ayrı 5 kalibrasyon örneği etiketlenecek.
- Bu 5 örnek danışman/ikinci göz tarafından format ve etiketleme mantığı için
  kontrol edilecek.
- Kalibrasyon onaylandıktan sonra ayrı 40 gerçek hidden örnek hazırlanacak.
- Kalibrasyon örnekleri bu 40 hidden örneğe dahil edilmeyecek.
- Geliştirici hidden cümleleri görmeyecek.
- Bize mümkünse sadece aggregate metrikler dönecek.

Kalibrasyon geçiş eşiği:

- 5/5 kabul: 40 hidden örneğe geç.
- 3-4/5 kabul: hatalı satırları özel olarak tartış, sorun giderildiyse geç.
- 0-2/5 kabul: guideline veya örnekler revize edilsin, yeni 5 kalibrasyon
  örneği hazırlansın.

Beklenen dosya formatı:

category<TAB>text<TAB>gold_independent_tokens_json<TAB>gold_policy_tokens_json<TAB>divergence_note

İki ayrı gold sütunu var:

1. gold_independent_tokens_json:
   Bağımsız Türkçe morfoloji yorumu / etiketleyici kararı.

2. gold_policy_tokens_json:
   Bu projenin yüzey biçimi koruyan tokenizer politikasına göre beklenen çıktı.

Bu iki gold farklıysa divergence_note zorunlu. Tek cümlelik kısa açıklama yeterli.

İlk hidden set hedefi: 40 örnek.

Kategori dağılımı:

- ambiguity: 7
- negative_word: 7
- suffix_chain: 4
- softening: 4
- proper_name: 3
- code_mixed: 3
- verb_future: 2
- verb_past: 2
- loanword_rare: 2
- question: 2
- informal: 2
- punctuation: 1
- numbers_dates: 1

Etiketleyici için okunacak kısa dosyalar:

- docs/hidden_eval_labeler_packet.md
- docs/hidden_eval_labeling_guideline.md
- data/eval/templates/tr_hidden_eval_template.tsv

Private eval komutu:

python scripts/evaluate_hidden_eval.py data/eval/private/tr_hidden_eval.tsv --markdown-out artifacts/v1_3_hidden_eval_report.md

Bu komut hidden cümleleri veya token listelerini yazdırmadan sadece aggregate
metrik üretmek için tasarlandı.

Uygunsa önce 5 kalibrasyon örneğiyle başlayalım.
```

## What We Need Back

Ask the advisor/annotator to return only:

```text
1. Calibration is approved / needs revision.
2. Overall policy exact/F1.
3. Overall independent exact/F1.
4. Category-level policy F1.
5. Category-level independent F1.
6. Any high-level concern without revealing hidden examples.
```

## What We Should Not Receive

To keep the set hidden, the implementer should not receive:

- the 40 hidden sentences
- full expected token lists
- mismatch examples
- screenshots that reveal hidden rows

If a row must be discussed, use an anonymized representative example and mark
the original row for future rotation.
