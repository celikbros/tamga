# Challenge Mismatch Analysis: tr_challenge.tsv

## Overall Summary

| Metric | Value |
| --- | ---: |
| Examples | 108 |
| Exact match | 40/108 |
| Mismatches | 68 |
| Precision | 0.8600 |
| Recall | 0.7807 |
| F1 | 0.8184 |

## Category Summary

| Category | Exact match | Mismatch count | Token F1 | Avg token count diff |
| --- | ---: | ---: | ---: | ---: |
| negative_word | 0/9 | 9 | 0.6387 | -1.2222 |
| suffix_chain | 0/9 | 9 | 0.7524 | -1.5556 |
| verb_future | 2/9 | 7 | 0.6970 | -2.2222 |
| softening | 2/9 | 7 | 0.7260 | -1.5556 |
| ambiguity | 2/9 | 7 | 0.7304 | -1.0000 |
| informal | 3/9 | 6 | 0.6739 | -0.6667 |
| code_mixed | 3/9 | 6 | 0.8485 | -0.7778 |
| question | 4/9 | 5 | 0.8841 | 0.0000 |
| verb_past | 4/9 | 5 | 0.9029 | -0.3333 |
| numbers_dates | 6/9 | 3 | 0.9091 | -0.2222 |
| punctuation | 6/9 | 3 | 0.9388 | 0.1111 |
| proper_name | 8/9 | 1 | 0.9785 | 0.0000 |

## Mismatch List

### suffix_chain: Arabacılarımızdakilerden haber aldık.

- Expected: `["▁Araba","+cı","+lar","+ımız","+da","+ki","+ler","+den","▁haber","▁al","+dı","+k","."]`
- Actual: `["▁Arabacı","+lar","+ımız","+da","+ki","+ler","+den","▁haber","▁al","+dı","+k","."]`
- Expected only: `["▁Araba","+cı"]`
- Actual only: `["▁Arabacı"]`

### suffix_chain: Evlerinizdekilerden bazıları yenilendi.

- Expected: `["▁Ev","+ler","+iniz","+de","+ki","+ler","+den","▁bazı","+ları","▁yenilen","+di","."]`
- Actual: `["▁Ev","+ler","+in","+iz","+de","+ki","+ler","+den","▁bazıları","▁yenilendi","."]`
- Expected only: `["+iniz","▁bazı","+ları","▁yenilen","+di"]`
- Actual only: `["+in","+iz","▁bazıları","▁yenilendi"]`

### suffix_chain: Kitapçılarımızdan gelenleri ayırdık.

- Expected: `["▁Kitap","+çı","+lar","+ımız","+dan","▁gelen","+ler","+i","▁ayır","+dı","+k","."]`
- Actual: `["▁Kitapçı","+lar","+ımız","+dan","▁gelen","+ler","+i","▁ayır","+dı","+k","."]`
- Expected only: `["▁Kitap","+çı"]`
- Actual only: `["▁Kitapçı"]`

### suffix_chain: Defterlerimizdekilerden ikisini sakladım.

- Expected: `["▁Defter","+ler","+imiz","+de","+ki","+ler","+den","▁iki","+si","+ni","▁sakla","+dı","+m","."]`
- Actual: `["▁Defter","+ler","+imiz","+de","+ki","+ler","+den","▁ikisi","+ni","▁sakla","+dı","+m","."]`
- Expected only: `["▁iki","+si"]`
- Actual only: `["▁ikisi"]`

### suffix_chain: Odalarımızdakilerden büyüğü boyandı.

- Expected: `["▁Oda","+lar","+ımız","+da","+ki","+ler","+den","▁büyük","+ü","▁boyan","+dı","."]`
- Actual: `["▁Oda","+lar","+ımız","+da","+ki","+ler","+den","▁büyüğü","▁boyandı","."]`
- Expected only: `["▁büyük","+ü","▁boyan","+dı"]`
- Actual only: `["▁büyüğü","▁boyandı"]`

### suffix_chain: Çantalarımızdan çıkardıklarımız masadaydı.

- Expected: `["▁Çanta","+lar","+ımız","+dan","▁çıkar","+dık","+lar","+ımız","▁masa","+da","+ydı","."]`
- Actual: `["▁Çan","+ta","+lar","+ımız","+dan","▁çıkardık","+lar","+ımız","▁masadaydı","."]`
- Expected only: `["▁Çanta","▁çıkar","+dık","▁masa","+da","+ydı"]`
- Actual only: `["▁Çan","+ta","▁çıkardık","▁masadaydı"]`

### suffix_chain: Sorularımızdakilerden zoru çözüldü.

- Expected: `["▁Soru","+lar","+ımız","+da","+ki","+ler","+den","▁zor","+u","▁çözül","+dü","."]`
- Actual: `["▁Soru","+lar","+ımız","+da","+ki","+ler","+den","▁zoru","▁çözüldü","."]`
- Expected only: `["▁zor","+u","▁çözül","+dü"]`
- Actual only: `["▁zoru","▁çözüldü"]`

### suffix_chain: Kayıtlarımızdakilerden eskisini sildiler.

- Expected: `["▁Kayıt","+lar","+ımız","+da","+ki","+ler","+den","▁eski","+si","+ni","▁sil","+di","+ler","."]`
- Actual: `["▁Kayıt","+lar","+ımız","+da","+ki","+ler","+den","▁eskisi","+ni","▁sil","+di","+ler","."]`
- Expected only: `["▁eski","+si"]`
- Actual only: `["▁eskisi"]`

### suffix_chain: Dosyalarımızdan seçtikleriniz gönderildi.

- Expected: `["▁Dosya","+lar","+ımız","+dan","▁seç","+tik","+ler","+iniz","▁gönderil","+di","."]`
- Actual: `["▁Dosya","+lar","+ımız","+dan","▁seçtiklerin","+iz","▁gönderildi","."]`
- Expected only: `["▁seç","+tik","+ler","+iniz","▁gönderil","+di"]`
- Actual only: `["▁seçtiklerin","+iz","▁gönderildi"]`

### proper_name: Mehmet'in arabasından ses geldi.

- Expected: `["▁Mehmet","'","+in","▁araba","+sı","+ndan","▁ses","▁gel","+di","."]`
- Actual: `["▁Mehmet","'","+in","▁araba","+sın","+dan","▁ses","▁gel","+di","."]`
- Expected only: `["+sı","+ndan"]`
- Actual only: `["+sın","+dan"]`

### softening: Ağacın dalları kırılmıştı.

- Expected: `["▁Ağac","+ın","▁dal","+lar","+ı","▁kırıl","+mış","+tı","."]`
- Actual: `["▁Ağac","+ın","▁dalları","▁kırıl","+mış","+tı","."]`
- Expected only: `["▁dal","+lar","+ı"]`
- Actual only: `["▁dalları"]`

### softening: Renginden emin olamadım.

- Expected: `["▁Reng","+in","+den","▁emin","▁ol","+ama","+dı","+m","."]`
- Actual: `["▁Reng","+in","+den","▁emin","▁olama","+dı","+m","."]`
- Expected only: `["▁ol","+ama"]`
- Actual only: `["▁olama"]`

### softening: Kanadının ucunda iz vardı.

- Expected: `["▁Kanad","+ı","+nın","▁uç","+un","+da","▁iz","▁var","+dı","."]`
- Actual: `["▁Kanad","+ı","+nın","▁ucun","+da","▁iz","▁var","+dı","."]`
- Expected only: `["▁uç","+un"]`
- Actual only: `["▁ucun"]`

### softening: Bileğinden saatini çıkardı.

- Expected: `["▁Bileğ","+in","+den","▁saat","+i","+ni","▁çıkar","+dı","."]`
- Actual: `["▁Bileğ","+in","+den","▁saati","+ni","▁çıkardı","."]`
- Expected only: `["▁saat","+i","▁çıkar","+dı"]`
- Actual only: `["▁saati","▁çıkardı"]`

### softening: Kapağını kapatmadan çıktı.

- Expected: `["▁Kapağ","+ı","+nı","▁kapat","+ma","+dan","▁çık","+tı","."]`
- Actual: `["▁Kapağı","+nı","▁kapatma","+dan","▁çıktı","."]`
- Expected only: `["▁Kapağ","+ı","▁kapat","+ma","▁çık","+tı"]`
- Actual only: `["▁Kapağı","▁kapatma","▁çıktı"]`

### softening: Ayağını yavaşça bastı.

- Expected: `["▁Ayağ","+ı","+nı","▁yavaşça","▁bas","+tı","."]`
- Actual: `["▁Ayağı","+nı","▁yavaşça","▁bastı","."]`
- Expected only: `["▁Ayağ","+ı","▁bas","+tı"]`
- Actual only: `["▁Ayağı","▁bastı"]`

### softening: Dudağını oynatmadan sustu.

- Expected: `["▁Dudağ","+ı","+nı","▁oynat","+ma","+dan","▁sus","+tu","."]`
- Actual: `["▁Dudağı","+nı","▁oynatma","+dan","▁sustu","."]`
- Expected only: `["▁Dudağ","+ı","▁oynat","+ma","▁sus","+tu"]`
- Actual only: `["▁Dudağı","▁oynatma","▁sustu"]`

### negative_word: Yazın sıcak günleri uzundur.

- Expected: `["▁Yazın","▁sıcak","▁gün","+ler","+i","▁uzun","+dur","."]`
- Actual: `["▁Yaz","+ın","▁sıcak","▁günleri","▁uzun","+dur","."]`
- Expected only: `["▁Yazın","▁gün","+ler","+i"]`
- Actual only: `["▁Yaz","+ın","▁günleri"]`

### negative_word: Kadın yakın sokakta bekledi.

- Expected: `["▁Kadın","▁yakın","▁sokak","+ta","▁bekle","+di","."]`
- Actual: `["▁Kadın","▁yakın","▁sokak","+ta","▁bekledi","."]`
- Expected only: `["▁bekle","+di"]`
- Actual only: `["▁bekledi"]`

### negative_word: Altın renkli kalem kayboldu.

- Expected: `["▁Altın","▁renk","+li","▁kalem","▁kaybol","+du","."]`
- Actual: `["▁Altın","▁renkli","▁kalem","▁kaybol","+du","."]`
- Expected only: `["▁renk","+li"]`
- Actual only: `["▁renkli"]`

### negative_word: Kalın odunları depoya taşıdık.

- Expected: `["▁Kalın","▁odun","+lar","+ı","▁depo","+ya","▁taşı","+dı","+k","."]`
- Actual: `["▁Kalın","▁odunları","▁depoya","▁taşı","+dı","+k","."]`
- Expected only: `["▁odun","+lar","+ı","▁depo","+ya"]`
- Actual only: `["▁odunları","▁depoya"]`

### negative_word: Kedi yakında uyuyordu.

- Expected: `["▁Kedi","▁yakında","▁uyu","+yor","+du","."]`
- Actual: `["▁Kedi","▁yakın","+da","▁uyuyordu","."]`
- Expected only: `["▁yakında","▁uyu","+yor","+du"]`
- Actual only: `["▁yakın","+da","▁uyuyordu"]`

### negative_word: Yarın alın yazısı konuşuldu.

- Expected: `["▁Yarın","▁alın","▁yazı","+sı","▁konuşul","+du","."]`
- Actual: `["▁Yarın","▁alın","▁yaz","+ı","+sı","▁konuşuldu","."]`
- Expected only: `["▁yazı","▁konuşul","+du"]`
- Actual only: `["▁yaz","+ı","▁konuşuldu"]`

### negative_word: Odun kalın kabukluydu.

- Expected: `["▁Odun","▁kalın","▁kabuk","+lu","+ydu","."]`
- Actual: `["▁Odun","▁kalın","▁kabukluydu","."]`
- Expected only: `["▁kabuk","+lu","+ydu"]`
- Actual only: `["▁kabukluydu"]`

### negative_word: Yakın kadın kitabı okudu.

- Expected: `["▁Yakın","▁kadın","▁kitab","+ı","▁oku","+du","."]`
- Actual: `["▁Yakın","▁kadın","▁kitab","+ı","▁okudu","."]`
- Expected only: `["▁oku","+du"]`
- Actual only: `["▁okudu"]`

### negative_word: Altın kedi oyuncağı değildi.

- Expected: `["▁Altın","▁kedi","▁oyuncağ","+ı","▁değil","+di","."]`
- Actual: `["▁Altın","▁kedi","▁oyuncağ","+ı","▁değildi","."]`
- Expected only: `["▁değil","+di"]`
- Actual only: `["▁değildi"]`

### verb_past: Okudular ama anlamadılar.

- Expected: `["▁Oku","+du","+lar","▁ama","▁anla","+ma","+dı","+lar","."]`
- Actual: `["▁Oku","+du","+lar","▁ama","▁anlama","+dı","+lar","."]`
- Expected only: `["▁anla","+ma"]`
- Actual only: `["▁anlama"]`

### verb_past: Yazdım, sildim, yeniden yazdım.

- Expected: `["▁Yaz","+dı","+m",",","▁sil","+di","+m",",","▁yeniden","▁yaz","+dı","+m","."]`
- Actual: `["▁Yaz","+dı","+m",",","▁sil","+di","+m",",","▁ye","+ni","+den","▁yaz","+dı","+m","."]`
- Expected only: `["▁yeniden"]`
- Actual only: `["▁ye","+ni","+den"]`

### verb_past: Gördüler mi bilmiyorum.

- Expected: `["▁Gör","+dü","+ler","▁mi","▁bil","+mi","+yor","+um","."]`
- Actual: `["▁Gör","+dü","+ler","▁mi","▁bilmiyor","+um","."]`
- Expected only: `["▁bil","+mi","+yor"]`
- Actual only: `["▁bilmiyor"]`

### verb_past: Baktın ama fark etmedin.

- Expected: `["▁Bak","+tı","+n","▁ama","▁fark","▁et","+me","+di","+n","."]`
- Actual: `["▁Bak","+tı","+n","▁ama","▁fark","▁etme","+di","+n","."]`
- Expected only: `["▁et","+me"]`
- Actual only: `["▁etme"]`

### verb_past: Taşıdılar ve yerleştirdiler.

- Expected: `["▁Taşı","+dı","+lar","▁ve","▁yerleş","+tir","+di","+ler","."]`
- Actual: `["▁Taşı","+dı","+lar","▁ve","▁yerleştir","+di","+ler","."]`
- Expected only: `["▁yerleş","+tir"]`
- Actual only: `["▁yerleştir"]`

### verb_future: Gidebilecek misiniz yarın?

- Expected: `["▁Git","+ebil","+ecek","▁mi","+siniz","▁yarın","?"]`
- Actual: `["▁Gidebil","+ecek","▁mi","+siniz","▁yarın","?"]`
- Expected only: `["▁Git","+ebil"]`
- Actual only: `["▁Gidebil"]`

### verb_future: Yapamayacaklarınızı biliyoruz.

- Expected: `["▁Yap","+ama","+yacak","+lar","+ınız","+ı","▁bil","+iyor","+uz","."]`
- Actual: `["▁Yapamayacaklarınızı","▁biliyor","+uz","."]`
- Expected only: `["▁Yap","+ama","+yacak","+lar","+ınız","+ı","▁bil","+iyor"]`
- Actual only: `["▁Yapamayacaklarınızı","▁biliyor"]`

### verb_future: Alabileceğimizi söyledik.

- Expected: `["▁Al","+abil","+ecek","+imiz","+i","▁söyle","+di","+k","."]`
- Actual: `["▁Alabileceğimizi","▁söyle","+di","+k","."]`
- Expected only: `["▁Al","+abil","+ecek","+imiz","+i"]`
- Actual only: `["▁Alabileceğimizi"]`

### verb_future: Gelmeyeceksiniz sanmıştım.

- Expected: `["▁Gel","+me","+yecek","+siniz","▁san","+mış","+tı","+m","."]`
- Actual: `["▁Gelme","+yecek","+siniz","▁sanmış","+tı","+m","."]`
- Expected only: `["▁Gel","+me","▁san","+mış"]`
- Actual only: `["▁Gelme","▁sanmış"]`

### verb_future: Okuyabilecekler mi acaba?

- Expected: `["▁Oku","+yabil","+ecek","+ler","▁mi","▁acaba","?"]`
- Actual: `["▁Okuyabil","+ecek","+ler","▁mi","▁acaba","?"]`
- Expected only: `["▁Oku","+yabil"]`
- Actual only: `["▁Okuyabil"]`

### verb_future: Döneceğimizi haber verdik.

- Expected: `["▁Dön","+ecek","+imiz","+i","▁haber","▁ver","+di","+k","."]`
- Actual: `["▁Döneceğimizi","▁haber","▁ver","+di","+k","."]`
- Expected only: `["▁Dön","+ecek","+imiz","+i"]`
- Actual only: `["▁Döneceğimizi"]`

### verb_future: Seçilebileceklerden biri oydu.

- Expected: `["▁Seç","+il","+ebil","+ecek","+ler","+den","▁biri","▁o","+ydu","."]`
- Actual: `["▁Seçilebil","+ecek","+ler","+den","▁biri","▁oydu","."]`
- Expected only: `["▁Seç","+il","+ebil","▁o","+ydu"]`
- Actual only: `["▁Seçilebil","▁oydu"]`

### question: Bu dosyayı açtın mı?

- Expected: `["▁Bu","▁dosya","+yı","▁aç","+tı","+n","▁mı","?"]`
- Actual: `["▁Bu","▁dosyayı","▁aç","+tı","+n","▁mı","?"]`
- Expected only: `["▁dosya","+yı"]`
- Actual only: `["▁dosyayı"]`

### question: Geliyordunuz değil mi?

- Expected: `["▁Gel","+iyor","+du","+nuz","▁değil","▁mi","?"]`
- Actual: `["▁Geliyor","+du","+nuz","▁değil","▁mi","?"]`
- Expected only: `["▁Gel","+iyor"]`
- Actual only: `["▁Geliyor"]`

### question: Bu sonucu yazacak mısın?

- Expected: `["▁Bu","▁sonuç","+u","▁yaz","+acak","▁mı","+sın","?"]`
- Actual: `["▁Bu","▁sonucu","▁yaz","+acak","▁mı","+sın","?"]`
- Expected only: `["▁sonuç","+u"]`
- Actual only: `["▁sonucu"]`

### question: Neden beklediniz acaba?

- Expected: `["▁Neden","▁bekle","+di","+niz","▁acaba","?"]`
- Actual: `["▁Ne","+den","▁bekle","+di","+niz","▁acaba","?"]`
- Expected only: `["▁Neden"]`
- Actual only: `["▁Ne","+den"]`

### question: README.md'yi yeniden açtın mı?

- Expected: `["▁README.md","'","+yi","▁yeniden","▁aç","+tı","+n","▁mı","?"]`
- Actual: `["▁README.md","'","+yi","▁ye","+ni","+den","▁aç","+tı","+n","▁mı","?"]`
- Expected only: `["▁yeniden"]`
- Actual only: `["▁ye","+ni","+den"]`

### informal: Napıyon burada?

- Expected: `["▁Napı","+yon","▁burada","?"]`
- Actual: `["▁Napı","+yon","▁bura","+da","?"]`
- Expected only: `["▁burada"]`
- Actual only: `["▁bura","+da"]`

### informal: Bakıcam sonra dönerim.

- Expected: `["▁Bak","+ıcam","▁sonra","▁dön","+er","+im","."]`
- Actual: `["▁Bakıcam","▁sonra","▁döner","+im","."]`
- Expected only: `["▁Bak","+ıcam","▁dön","+er"]`
- Actual only: `["▁Bakıcam","▁döner"]`

### informal: Yapıcam dedim ya.

- Expected: `["▁Yap","+ıcam","▁de","+di","+m","▁ya","."]`
- Actual: `["▁Yapıcam","▁de","+di","+m","▁ya","."]`
- Expected only: `["▁Yap","+ıcam"]`
- Actual only: `["▁Yapıcam"]`

### informal: Yazıcam sana akşam.

- Expected: `["▁Yaz","+ıcam","▁sana","▁akşam","."]`
- Actual: `["▁Yazıcam","▁sana","▁akşam","."]`
- Expected only: `["▁Yaz","+ıcam"]`
- Actual only: `["▁Yazıcam"]`

### informal: Görücem sonucu yakında.

- Expected: `["▁Gör","+ücem","▁sonuç","+u","▁yakında","."]`
- Actual: `["▁Görücem","▁sonucu","▁yakın","+da","."]`
- Expected only: `["▁Gör","+ücem","▁sonuç","+u","▁yakında"]`
- Actual only: `["▁Görücem","▁sonucu","▁yakın","+da"]`

### informal: Koşuyom sandı herkes.

- Expected: `["▁Koş","+uyom","▁san","+dı","▁herkes","."]`
- Actual: `["▁Koşuyom","▁sandı","▁herkes","."]`
- Expected only: `["▁Koş","+uyom","▁san","+dı"]`
- Actual only: `["▁Koşuyom","▁sandı"]`

### code_mixed: OpenAIlaştırılmış başlıkları ayırdık.

- Expected: `["▁OpenAI","+laştır","+ıl","+mış","▁başlık","+lar","+ı","▁ayır","+dı","+k","."]`
- Actual: `["▁OpenAI","+laştır","+ıl","+mış","▁başlıkları","▁ayır","+dı","+k","."]`
- Expected only: `["▁başlık","+lar","+ı"]`
- Actual only: `["▁başlıkları"]`

### code_mixed: API'deki tokenları yeniledim.

- Expected: `["▁API","'","+de","+ki","▁token","+lar","+ı","▁yenile","+di","+m","."]`
- Actual: `["▁API","'","+de","+ki","▁tokenları","▁yenile","+di","+m","."]`
- Expected only: `["▁token","+lar","+ı"]`
- Actual only: `["▁tokenları"]`

### code_mixed: Python'dan gelen logları okudum.

- Expected: `["▁Python","'","+dan","▁gelen","▁log","+lar","+ı","▁oku","+du","+m","."]`
- Actual: `["▁Python","'","+dan","▁gelen","▁logları","▁oku","+du","+m","."]`
- Expected only: `["▁log","+lar","+ı"]`
- Actual only: `["▁logları"]`

### code_mixed: server_v2.log içinde hata buldum.

- Expected: `["▁server_v2.log","▁iç","+in","+de","▁hata","▁bul","+du","+m","."]`
- Actual: `["▁server_v2.log","▁için","+de","▁ha","+ta","▁bul","+du","+m","."]`
- Expected only: `["▁iç","+in","▁hata"]`
- Actual only: `["▁için","▁ha","+ta"]`

### code_mixed: JSON'daki alanları temizledik.

- Expected: `["▁JSON","'","+da","+ki","▁alan","+lar","+ı","▁temizle","+di","+k","."]`
- Actual: `["▁JSON","'","+da","+ki","▁alanları","▁temizle","+di","+k","."]`
- Expected only: `["▁alan","+lar","+ı"]`
- Actual only: `["▁alanları"]`

### code_mixed: CLI'da yeni komut gördüm.

- Expected: `["▁CLI","'","+da","▁yeni","▁komut","▁gör","+dü","+m","."]`
- Actual: `["▁CLI","'","+da","▁ye","+ni","▁komut","▁gör","+dü","+m","."]`
- Expected only: `["▁yeni"]`
- Actual only: `["▁ye","+ni"]`

### ambiguity: Yazın tatile gittik.

- Expected: `["▁Yazın","▁tatil","+e","▁git","+ti","+k","."]`
- Actual: `["▁Yaz","+ın","▁tatile","▁git","+ti","+k","."]`
- Expected only: `["▁Yazın","▁tatil","+e"]`
- Actual only: `["▁Yaz","+ın","▁tatile"]`

### ambiguity: Yazarım ama göndermem.

- Expected: `["▁Yaz","+ar","+ım","▁ama","▁gönder","+me","+m","."]`
- Actual: `["▁Yazar","+ım","▁ama","▁göndermem","."]`
- Expected only: `["▁Yaz","+ar","▁gönder","+me","+m"]`
- Actual only: `["▁Yazar","▁göndermem"]`

### ambiguity: Gül dalında açtı.

- Expected: `["▁Gül","▁dal","+ın","+da","▁aç","+tı","."]`
- Actual: `["▁Gül","▁dalın","+da","▁aç","+tı","."]`
- Expected only: `["▁dal","+ın"]`
- Actual only: `["▁dalın"]`

### ambiguity: At yarışta koştu.

- Expected: `["▁At","▁yarış","+ta","▁koş","+tu","."]`
- Actual: `["▁At","▁yarış","+ta","▁koştu","."]`
- Expected only: `["▁koş","+tu"]`
- Actual only: `["▁koştu"]`

### ambiguity: Ben bunu yazarım.

- Expected: `["▁Ben","▁bunu","▁yaz","+ar","+ım","."]`
- Actual: `["▁Ben","▁bunu","▁yazar","+ım","."]`
- Expected only: `["▁yaz","+ar"]`
- Actual only: `["▁yazar"]`

### ambiguity: Ocak ayında başladık.

- Expected: `["▁Ocak","▁ay","+ın","+da","▁başla","+dı","+k","."]`
- Actual: `["▁Ocak","▁ayın","+da","▁başla","+dı","+k","."]`
- Expected only: `["▁ay","+ın"]`
- Actual only: `["▁ayın"]`

### ambiguity: Saz çalan çocuk güldü.

- Expected: `["▁Saz","▁çal","+an","▁çocuk","▁gül","+dü","."]`
- Actual: `["▁Saz","▁çalan","▁çocuk","▁güldü","."]`
- Expected only: `["▁çal","+an","▁gül","+dü"]`
- Actual only: `["▁çalan","▁güldü"]`

### numbers_dates: 12:30'da toplantı başladı.

- Expected: `["▁12:30","'","+da","▁toplantı","▁başla","+dı","."]`
- Actual: `["▁12:30","'","+da","▁toplantı","▁başladı","."]`
- Expected only: `["▁başla","+dı"]`
- Actual only: `["▁başladı"]`

### numbers_dates: 5'inci satırı sildim.

- Expected: `["▁5","'","+inci","▁satır","+ı","▁sil","+di","+m","."]`
- Actual: `["▁5","'","+inci","▁satırı","▁sil","+di","+m","."]`
- Expected only: `["▁satır","+ı"]`
- Actual only: `["▁satırı"]`

### numbers_dates: 2024/05/01 tarihinde yazıldı.

- Expected: `["▁2024/05/01","▁tarih","+in","+de","▁yazıl","+dı","."]`
- Actual: `["▁2024/05/01","▁tarihin","+de","▁yaz","+ıl","+dı","."]`
- Expected only: `["▁tarih","+in","▁yazıl"]`
- Actual only: `["▁tarihin","▁yaz","+ıl"]`

### punctuation: Hayır! Bunu yapma.

- Expected: `["▁Hayır","!","▁Bunu","▁yap","+ma","."]`
- Actual: `["▁Hayır","!","▁Bunu","▁yapma","."]`
- Expected only: `["▁yap","+ma"]`
- Actual only: `["▁yapma"]`

### punctuation: Peki... sonra ne oldu?

- Expected: `["▁Peki",".",".",".","▁sonra","▁ne","▁ol","+du","?"]`
- Actual: `["▁Pe","+ki",".",".",".","▁sonra","▁ne","▁ol","+du","?"]`
- Expected only: `["▁Peki"]`
- Actual only: `["▁Pe","+ki"]`

### punctuation: (Ankara'dan) yeni döndüm.

- Expected: `["(","▁Ankara","'","+dan",")","▁yeni","▁dön","+dü","+m","."]`
- Actual: `["(","▁Ankara","'","+dan",")","▁ye","+ni","▁dön","+dü","+m","."]`
- Expected only: `["▁yeni"]`
- Actual only: `["▁ye","+ni"]`

## Most Common Expected-Only Tokens

| Token | Count |
| --- | ---: |
| `+ı` | 11 |
| `+lar` | 7 |
| `+di` | 4 |
| `+dı` | 4 |
| `+i` | 4 |
| `+ma` | 4 |
| `+u` | 3 |
| `+du` | 3 |
| `+me` | 3 |
| `+ıcam` | 3 |
| `+iniz` | 2 |
| `+si` | 2 |
| `▁çıkar` | 2 |
| `+dü` | 2 |
| `+ler` | 2 |
| `▁dal` | 2 |
| `+ama` | 2 |
| `+tı` | 2 |
| `+tu` | 2 |
| `▁Yazın` | 2 |

## Most Common Actual-Only Tokens

| Token | Count |
| --- | ---: |
| `▁ye` | 4 |
| `+ni` | 4 |
| `+da` | 3 |
| `+den` | 3 |
| `+iz` | 2 |
| `+ta` | 2 |
| `▁Yaz` | 2 |
| `+ın` | 2 |
| `▁yakın` | 2 |
| `▁yaz` | 2 |
| `▁sonucu` | 2 |
| `▁Arabacı` | 1 |
| `+in` | 1 |
| `▁bazıları` | 1 |
| `▁yenilendi` | 1 |
| `▁Kitapçı` | 1 |
| `▁ikisi` | 1 |
| `▁büyüğü` | 1 |
| `▁boyandı` | 1 |
| `▁Çan` | 1 |

## Suspected Missing Suffixes

| Token | Count |
| --- | ---: |
| `+ı` | 11 |
| `+lar` | 7 |
| `+di` | 4 |
| `+dı` | 4 |
| `+i` | 4 |
| `+ma` | 4 |
| `+u` | 3 |
| `+du` | 3 |
| `+me` | 3 |
| `+ıcam` | 3 |
| `+iniz` | 2 |
| `+si` | 2 |
| `+dü` | 2 |
| `+ler` | 2 |
| `+ama` | 2 |
| `+tı` | 2 |
| `+tu` | 2 |
| `+yor` | 2 |
| `+ydu` | 2 |
| `+ebil` | 2 |

## Suspected Missing Stems

| Token | Count |
| --- | ---: |
| `▁çıkar` | 2 |
| `▁dal` | 2 |
| `▁Yazın` | 2 |
| `▁yakında` | 2 |
| `▁yeniden` | 2 |
| `▁bil` | 2 |
| `▁Yap` | 2 |
| `▁Gel` | 2 |
| `▁san` | 2 |
| `▁sonuç` | 2 |
| `▁Yaz` | 2 |
| `▁yeni` | 2 |
| `▁Araba` | 1 |
| `▁bazı` | 1 |
| `▁yenilen` | 1 |
| `▁Kitap` | 1 |
| `▁iki` | 1 |
| `▁büyük` | 1 |
| `▁boyan` | 1 |
| `▁Çanta` | 1 |

## Suspected Over-Splitting Cases

| Category | Text | Detail |
| --- | --- | --- |
| suffix_chain | Evlerinizdekilerden bazıları yenilendi. | `+iniz split as ["+in","+iz"]` |
| suffix_chain | Çantalarımızdan çıkardıklarımız masadaydı. | `▁Çanta split as ["▁Çan","+ta"]` |
| negative_word | Yazın sıcak günleri uzundur. | `▁Yazın split as ["▁Yaz","+ın"]` |
| negative_word | Kedi yakında uyuyordu. | `▁yakında split as ["▁yakın","+da"]` |
| negative_word | Yarın alın yazısı konuşuldu. | `▁yazı split as ["▁yaz","+ı"]` |
| verb_past | Yazdım, sildim, yeniden yazdım. | `▁yeniden split as ["▁ye","+ni","+den"]` |
| question | Neden beklediniz acaba? | `▁Neden split as ["▁Ne","+den"]` |
| question | README.md'yi yeniden açtın mı? | `▁yeniden split as ["▁ye","+ni","+den"]` |
| informal | Napıyon burada? | `▁burada split as ["▁bura","+da"]` |
| informal | Görücem sonucu yakında. | `▁yakında split as ["▁yakın","+da"]` |
| code_mixed | server_v2.log içinde hata buldum. | `▁hata split as ["▁ha","+ta"]` |
| code_mixed | CLI'da yeni komut gördüm. | `▁yeni split as ["▁ye","+ni"]` |
| ambiguity | Yazın tatile gittik. | `▁Yazın split as ["▁Yaz","+ın"]` |
| numbers_dates | 2024/05/01 tarihinde yazıldı. | `▁yazıl split as ["▁yaz","+ıl"]` |
| punctuation | Peki... sonra ne oldu? | `▁Peki split as ["▁Pe","+ki"]` |
| punctuation | (Ankara'dan) yeni döndüm. | `▁yeni split as ["▁ye","+ni"]` |

## Suspected Under-Splitting Cases

| Category | Text | Detail |
| --- | --- | --- |
| suffix_chain | Arabacılarımızdakilerden haber aldık. | `["▁Araba","+cı"] collapsed into ▁Arabacı` |
| suffix_chain | Evlerinizdekilerden bazıları yenilendi. | `["▁bazı","+ları"] collapsed into ▁bazıları` |
| suffix_chain | Evlerinizdekilerden bazıları yenilendi. | `["▁yenilen","+di"] collapsed into ▁yenilendi` |
| suffix_chain | Kitapçılarımızdan gelenleri ayırdık. | `["▁Kitap","+çı"] collapsed into ▁Kitapçı` |
| suffix_chain | Defterlerimizdekilerden ikisini sakladım. | `["▁iki","+si"] collapsed into ▁ikisi` |
| suffix_chain | Odalarımızdakilerden büyüğü boyandı. | `["▁boyan","+dı"] collapsed into ▁boyandı` |
| suffix_chain | Çantalarımızdan çıkardıklarımız masadaydı. | `["▁çıkar","+dık"] collapsed into ▁çıkardık` |
| suffix_chain | Çantalarımızdan çıkardıklarımız masadaydı. | `["▁masa","+da","+ydı"] collapsed into ▁masadaydı` |
| suffix_chain | Sorularımızdakilerden zoru çözüldü. | `["▁zor","+u"] collapsed into ▁zoru` |
| suffix_chain | Sorularımızdakilerden zoru çözüldü. | `["▁çözül","+dü"] collapsed into ▁çözüldü` |
| suffix_chain | Kayıtlarımızdakilerden eskisini sildiler. | `["▁eski","+si"] collapsed into ▁eskisi` |
| suffix_chain | Dosyalarımızdan seçtikleriniz gönderildi. | `["▁gönderil","+di"] collapsed into ▁gönderildi` |
| softening | Ağacın dalları kırılmıştı. | `["▁dal","+lar","+ı"] collapsed into ▁dalları` |
| softening | Renginden emin olamadım. | `["▁ol","+ama"] collapsed into ▁olama` |
| softening | Bileğinden saatini çıkardı. | `["▁saat","+i"] collapsed into ▁saati` |
| softening | Bileğinden saatini çıkardı. | `["▁çıkar","+dı"] collapsed into ▁çıkardı` |
| softening | Kapağını kapatmadan çıktı. | `["▁Kapağ","+ı"] collapsed into ▁Kapağı` |
| softening | Kapağını kapatmadan çıktı. | `["▁kapat","+ma"] collapsed into ▁kapatma` |
| softening | Kapağını kapatmadan çıktı. | `["▁çık","+tı"] collapsed into ▁çıktı` |
| softening | Ayağını yavaşça bastı. | `["▁Ayağ","+ı"] collapsed into ▁Ayağı` |
| softening | Ayağını yavaşça bastı. | `["▁bas","+tı"] collapsed into ▁bastı` |
| softening | Dudağını oynatmadan sustu. | `["▁Dudağ","+ı"] collapsed into ▁Dudağı` |
| softening | Dudağını oynatmadan sustu. | `["▁oynat","+ma"] collapsed into ▁oynatma` |
| softening | Dudağını oynatmadan sustu. | `["▁sus","+tu"] collapsed into ▁sustu` |
| negative_word | Yazın sıcak günleri uzundur. | `["▁gün","+ler","+i"] collapsed into ▁günleri` |
| negative_word | Kadın yakın sokakta bekledi. | `["▁bekle","+di"] collapsed into ▁bekledi` |
| negative_word | Altın renkli kalem kayboldu. | `["▁renk","+li"] collapsed into ▁renkli` |
| negative_word | Kalın odunları depoya taşıdık. | `["▁odun","+lar","+ı"] collapsed into ▁odunları` |
| negative_word | Kalın odunları depoya taşıdık. | `["▁depo","+ya"] collapsed into ▁depoya` |
| negative_word | Kedi yakında uyuyordu. | `["▁uyu","+yor","+du"] collapsed into ▁uyuyordu` |

## Risky Fixes

- Do not add short suffixes such as `+ı`, `+i`, `+ın`, `+in` to the general greedy splitter.
- Do not normalize informal words into standard Turkish; keep surface forms.
- Do not broaden mixed-case/code rules into normal lowercase Turkish words.
- Treat ambiguity examples as policy decisions, not automatic lexicon gaps.

## v1.1 Recommendation Table

| Priority | Category | Suspected issue | Example | Suggested fix | Regression risk |
| --- | --- | --- | --- | --- | --- |
| P1 | negative_word | possible false-positive split risk | Yazın sıcak günleri uzundur. | prefer negative regressions over broader suffix rules | high |
| P2 | suffix_chain | long suffix chain stem/inventory gap such as ▁Araba | Arabacılarımızdakilerden haber aldık. | add a small surface-stem batch and re-run expanded regression | medium |
| P3 | verb_future | future/ability suffix chain gap such as +ebil | Gidebilecek misiniz yarın? | add only lexicon-aware verb patterns with frozen regression checks | medium |
| P4 | softening | missing surface stem such as ▁dal | Ağacın dalları kırılmıştı. | add selected surface stems only with negative-word regressions | medium |
| P5 | ambiguity | ambiguous word can be lexical item or stem+suffix | Yazın tatile gittik. | treat as high-risk; add policy before adding rules | high |
| P6 | informal | uncovered informal surface suffix such as +ıcam | Napıyon burada? | extend informal-only lexicon layer, not the general splitter | medium |
| P7 | code_mixed | code/file mixed token boundary gap | OpenAIlaştırılmış başlıkları ayırdık. | add narrow file-like and mixed-case cases without changing normal words | medium |
| P8 | question | question clitic or person suffix pattern | Bu dosyayı açtın mı? | separate question-particle layer from general noun suffixing | medium |
| P9 | verb_past | past tense stem alternation gap | Okudular ama anlamadılar. | add only known verb stems with tense-specific tests | medium |
| P10 | numbers_dates | number/date punctuation boundary handling | 12:30'da toplantı başladı. | add guarded number/date pretokenizer tests before any rule change | medium |
| P11 | punctuation | quoted punctuation or attached punctuation pattern | Hayır! Bunu yapma. | extend punctuation fixtures first, then add narrow pretokenizer cases | medium |
| P12 | proper_name | apostrophe/proper-name suffix gap such as +sı | Mehmet'in arabasından ses geldi. | expand apostrophe suffix inventory with exact regression examples | low |
