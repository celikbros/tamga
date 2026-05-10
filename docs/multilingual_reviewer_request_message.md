# Multilingual Reviewer Request Messages

This file contains ready-to-send messages for professors, students, or NLP peers
who can review multilingual/Turkic risks. These messages are not for the Turkish
hidden eval labeler task.

## Academic / Professor Email

```text
Subject: Turkish-centered tokenizer project: short multilingual/Turkic review request

Dear [Name],

I am working on tr-centric-tokenizer, a Turkish-centered morphology-aware
tokenizer research prototype.

The current v1.x system focuses on Turkish deterministic morphology. Before we
move toward a multilingual/Turkic-aware v2.0 design, we want external review on
the architecture so that we do not make hard-to-reverse decisions around
Unicode normalization, script handling, apostrophe conventions, fallback, or
vocabulary allocation.

This is not a request to implement code or annotate a full dataset. We are
looking for a short expert review of the multilingual strategy:

- Does the proposed layer order make sense?
- What risks do you see for [language/script area]?
- Which examples should later become smoke tests?
- Are there normalization or script issues we must decide before vocabulary
  training?

Estimated time: 30-60 minutes.

Relevant files:

- docs/multilingual_strategy.md
- docs/multilingual_observations.md
- docs/multilingual_reviewer_packet.md
- docs/multilingual_reviewer_response_form.md

If you have a graduate student or colleague familiar with Turkish/Turkic NLP,
computational linguistics, or [target language/script], I would also be grateful
if you could forward this request.

We can acknowledge reviewers in the project documentation and, if the work later
becomes a paper and the contribution grows substantially, discuss appropriate
academic credit.

Thank you,
[Your Name]
```

## Student / Peer Message

```text
Merhaba [Name],

Turkish-centered morphology-aware tokenizer projemiz icin kisa bir
multilingual/Turkic review almak istiyoruz.

Bu bir kod yazma ya da buyuk veri etiketleme isi degil. Amac, v2.0'a gecmeden
once geri donulmez mimari riskleri yakalamak:

- Unicode/script handling
- apostrof kullanimi
- normalizasyon
- Turk dilleri icin ozel karakterler
- fallback ve vocabulary allocation

Tahmini sure: 30-60 dakika.

Okunacak kisa dosyalar:

- docs/multilingual_strategy.md
- docs/multilingual_observations.md
- docs/multilingual_reviewer_packet.md
- docs/multilingual_reviewer_response_form.md

Senden bekledigimiz sey, response form'daki basliklara gore kisa yorum ve
gerekirse 5-10 ornek cumle/token riski onermek.

Bu review hidden eval degil; verdigin ornekler daha sonra public smoke-test
adaylari olabilir. Gizli veri ya da lisansli corpus gondermene gerek yok.

Uygun olursa dosyalari gondereyim.
```

## Short Follow-Up

```text
Merhaba [Name],

Onceki mesajdaki tokenizer review icin sadece kisa bir hatirlatma yapmak
istedim. Bu is yaklasik 30-60 dakikalik mimari risk review'i; kod yazma veya
dataset etiketleme beklemiyoruz.

Uygun degilse sorun degil. Uygunsa response form'a kisa maddeler halinde cevap
vermen yeterli.

Tesekkurler.
```
