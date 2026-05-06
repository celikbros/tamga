# v1.2 Error Taxonomy: tr_challenge.tsv

## Summary

| Metric | Value |
| --- | ---: |
| Examples | 108 |
| Exact match | 40/108 |
| Mismatches | 68 |

## Label Summary

| Label | Count |
| --- | ---: |
| do_not_fix_yet | 9 |
| exact_match | 40 |
| hybrid_candidate | 17 |
| needs_context | 7 |
| needs_lexicon | 28 |
| safe_rule_candidate | 7 |

## Category x Label

| Category | do_not_fix_yet | exact_match | hybrid_candidate | needs_context | needs_lexicon | safe_rule_candidate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0 | 2 | 0 | 7 | 0 | 0 |
| code_mixed | 0 | 3 | 6 | 0 | 0 | 0 |
| informal | 0 | 3 | 0 | 0 | 6 | 0 |
| negative_word | 9 | 0 | 0 | 0 | 0 | 0 |
| numbers_dates | 0 | 6 | 0 | 0 | 0 | 3 |
| proper_name | 0 | 8 | 0 | 0 | 0 | 1 |
| punctuation | 0 | 6 | 0 | 0 | 0 | 3 |
| question | 0 | 4 | 3 | 0 | 2 | 0 |
| softening | 0 | 2 | 0 | 0 | 7 | 0 |
| suffix_chain | 0 | 0 | 0 | 0 | 9 | 0 |
| verb_future | 0 | 2 | 7 | 0 | 0 | 0 |
| verb_past | 0 | 4 | 1 | 0 | 4 | 0 |

## Mismatch Decisions

| Label | Category | Text | Reason | Next step |
| --- | --- | --- | --- | --- |
| needs_lexicon | suffix_chain | Arabacılarımızdakilerden haber aldık. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | suffix_chain | Evlerinizdekilerden bazıları yenilendi. | over-splitting also appears; add regressions before lexicon changes | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | suffix_chain | Kitapçılarımızdan gelenleri ayırdık. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | suffix_chain | Defterlerimizdekilerden ikisini sakladım. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | suffix_chain | Odalarımızdakilerden büyüğü boyandı. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | suffix_chain | Çantalarımızdan çıkardıklarımız masadaydı. | over-splitting also appears; add regressions before lexicon changes | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | suffix_chain | Sorularımızdakilerden zoru çözüldü. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | suffix_chain | Kayıtlarımızdakilerden eskisini sildiler. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | suffix_chain | Dosyalarımızdan seçtikleriniz gönderildi. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| safe_rule_candidate | proper_name | Mehmet'in arabasından ses geldi. | remaining issue is isolated to punctuation/apostrophe/token-boundary flow | add a narrow fixture before any tokenizer change |
| needs_lexicon | softening | Ağacın dalları kırılmıştı. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | softening | Renginden emin olamadım. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | softening | Kanadının ucunda iz vardı. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | softening | Bileğinden saatini çıkardı. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | softening | Kapağını kapatmadan çıktı. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | softening | Ayağını yavaşça bastı. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | softening | Dudağını oynatmadan sustu. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| do_not_fix_yet | negative_word | Yazın sıcak günleri uzundur. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| do_not_fix_yet | negative_word | Kadın yakın sokakta bekledi. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| do_not_fix_yet | negative_word | Altın renkli kalem kayboldu. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| do_not_fix_yet | negative_word | Kalın odunları depoya taşıdık. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| do_not_fix_yet | negative_word | Kedi yakında uyuyordu. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| do_not_fix_yet | negative_word | Yarın alın yazısı konuşuldu. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| do_not_fix_yet | negative_word | Odun kalın kabukluydu. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| do_not_fix_yet | negative_word | Yakın kadın kitabı okudu. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| do_not_fix_yet | negative_word | Altın kedi oyuncağı değildi. | fixing this class risks false-positive splits in common words | expand negative regressions and keep the conservative core |
| needs_lexicon | verb_past | Okudular ama anlamadılar. | under-splitting points to a missing guarded stem or verb pattern | consider a small lexicon batch with frozen regression checks |
| hybrid_candidate | verb_past | Yazdım, sildim, yeniden yazdım. | mixed mismatch pattern crosses lexical and suffix decisions | label examples manually before adding rules |
| needs_lexicon | verb_past | Gördüler mi bilmiyorum. | under-splitting points to a missing guarded stem or verb pattern | consider a small lexicon batch with frozen regression checks |
| needs_lexicon | verb_past | Baktın ama fark etmedin. | under-splitting points to a missing guarded stem or verb pattern | consider a small lexicon batch with frozen regression checks |
| needs_lexicon | verb_past | Taşıdılar ve yerleştirdiler. | under-splitting points to a missing guarded stem or verb pattern | consider a small lexicon batch with frozen regression checks |
| hybrid_candidate | verb_future | Gidebilecek misiniz yarın? | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | verb_future | Yapamayacaklarınızı biliyoruz. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | verb_future | Alabileceğimizi söyledik. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | verb_future | Gelmeyeceksiniz sanmıştım. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | verb_future | Okuyabilecekler mi acaba? | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | verb_future | Döneceğimizi haber verdik. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | verb_future | Seçilebileceklerden biri oydu. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| needs_lexicon | question | Bu dosyayı açtın mı? | under-splitting points to a missing guarded stem or verb pattern | consider a small lexicon batch with frozen regression checks |
| needs_lexicon | question | Geliyordunuz değil mi? | under-splitting points to a missing guarded stem or verb pattern | consider a small lexicon batch with frozen regression checks |
| hybrid_candidate | question | Bu sonucu yazacak mısın? | mixed mismatch pattern crosses lexical and suffix decisions | label examples manually before adding rules |
| hybrid_candidate | question | Neden beklediniz acaba? | mixed mismatch pattern crosses lexical and suffix decisions | label examples manually before adding rules |
| hybrid_candidate | question | README.md'yi yeniden açtın mı? | mixed mismatch pattern crosses lexical and suffix decisions | label examples manually before adding rules |
| needs_lexicon | informal | Napıyon burada? | over-splitting also appears; add regressions before lexicon changes | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | informal | Bakıcam sonra dönerim. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | informal | Yapıcam dedim ya. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | informal | Yazıcam sana akşam. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | informal | Görücem sonucu yakında. | over-splitting also appears; add regressions before lexicon changes | batch small surface-stem additions with negative-word regressions |
| needs_lexicon | informal | Koşuyom sandı herkes. | expected-only stems or suffixes suggest a guarded lexicon gap | batch small surface-stem additions with negative-word regressions |
| hybrid_candidate | code_mixed | OpenAIlaştırılmış başlıkları ayırdık. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | code_mixed | API'deki tokenları yeniledim. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | code_mixed | Python'dan gelen logları okudum. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | code_mixed | server_v2.log içinde hata buldum. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | code_mixed | JSON'daki alanları temizledik. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| hybrid_candidate | code_mixed | CLI'da yeni komut gördüm. | productive chain is likely better handled by morphology-aware fallback | defer to MorphBPE/hybrid design unless a very narrow rule is obvious |
| needs_context | ambiguity | Yazın tatile gittik. | surface form can have multiple analyses without context | do not add a broad rule before ambiguity policy is decided |
| needs_context | ambiguity | Yazarım ama göndermem. | surface form can have multiple analyses without context | do not add a broad rule before ambiguity policy is decided |
| needs_context | ambiguity | Gül dalında açtı. | surface form can have multiple analyses without context | do not add a broad rule before ambiguity policy is decided |
| needs_context | ambiguity | At yarışta koştu. | surface form can have multiple analyses without context | do not add a broad rule before ambiguity policy is decided |
| needs_context | ambiguity | Ben bunu yazarım. | surface form can have multiple analyses without context | do not add a broad rule before ambiguity policy is decided |
| needs_context | ambiguity | Ocak ayında başladık. | surface form can have multiple analyses without context | do not add a broad rule before ambiguity policy is decided |
| needs_context | ambiguity | Saz çalan çocuk güldü. | surface form can have multiple analyses without context | do not add a broad rule before ambiguity policy is decided |
| safe_rule_candidate | numbers_dates | 12:30'da toplantı başladı. | remaining issue is isolated to punctuation/apostrophe/token-boundary flow | add a narrow fixture before any tokenizer change |
| safe_rule_candidate | numbers_dates | 5'inci satırı sildim. | remaining issue is isolated to punctuation/apostrophe/token-boundary flow | add a narrow fixture before any tokenizer change |
| safe_rule_candidate | numbers_dates | 2024/05/01 tarihinde yazıldı. | remaining issue is isolated to punctuation/apostrophe/token-boundary flow | add a narrow fixture before any tokenizer change |
| safe_rule_candidate | punctuation | Hayır! Bunu yapma. | remaining issue is isolated to punctuation/apostrophe/token-boundary flow | add a narrow fixture before any tokenizer change |
| safe_rule_candidate | punctuation | Peki... sonra ne oldu? | remaining issue is isolated to punctuation/apostrophe/token-boundary flow | add a narrow fixture before any tokenizer change |
| safe_rule_candidate | punctuation | (Ankara'dan) yeni döndüm. | remaining issue is isolated to punctuation/apostrophe/token-boundary flow | add a narrow fixture before any tokenizer change |

## v1.3 Candidate View

- Start with `safe_rule_candidate` only if a fixture can isolate the behavior.
- Batch `needs_lexicon` examples and protect negative regressions first.
- Keep `needs_context` and `do_not_fix_yet` out of deterministic rules.
- Treat `hybrid_candidate` as MorphBPE design input.
