# Evaluation Report: tr_challenge.tsv

## Summary

| Metric | Value |
| --- | ---: |
| Examples | 108 |
| Exact match | 21/108 |
| Precision | 0.8037 |
| Recall | 0.7155 |
| F1 | 0.7570 |

## Category Summary

| Category | Exact match | F1 |
| --- | ---: | ---: |
| ambiguity | 2/9 | 0.7304 |
| code_mixed | 2/9 | 0.8364 |
| informal | 2/9 | 0.6374 |
| negative_word | 0/9 | 0.6387 |
| numbers_dates | 0/9 | 0.5693 |
| proper_name | 2/9 | 0.8409 |
| punctuation | 2/9 | 0.8392 |
| question | 3/9 | 0.8467 |
| softening | 2/9 | 0.7034 |
| suffix_chain | 0/9 | 0.7184 |
| verb_future | 2/9 | 0.6970 |
| verb_past | 4/9 | 0.9029 |

## Mismatches

### suffix_chain: Arabacılarımızdakilerden haber aldık.

- Expected: `["▁Araba","+cı","+lar","+ımız","+da","+ki","+ler","+den","▁haber","▁al","+dı","+k","."]`
- Actual: `["▁Arabacı","+lar","+ımız","+da","+ki","+ler","+den","▁haber","▁al","+dı","+k","."]`
- Expected only: `["▁Araba","+cı"]`
- Actual only: `["▁Arabacı"]`

### suffix_chain: Evlerinizdekilerden bazıları yenilendi.

- Expected: `["▁Ev","+ler","+iniz","+de","+ki","+ler","+den","▁bazı","+ları","▁yenilen","+di","."]`
- Actual: `["▁Evlerin","+iz","+de","+ki","+ler","+den","▁bazıları","▁yenilendi","."]`
- Expected only: `["▁Ev","+ler","+iniz","▁bazı","+ları","▁yenilen","+di"]`
- Actual only: `["▁Evlerin","+iz","▁bazıları","▁yenilendi"]`

### suffix_chain: Kitapçılarımızdan gelenleri ayırdık.

- Expected: `["▁Kitap","+çı","+lar","+ımız","+dan","▁gelen","+ler","+i","▁ayır","+dı","+k","."]`
- Actual: `["▁Kitapçı","+lar","+ımız","+dan","▁gelenleri","▁ayır","+dı","+k","."]`
- Expected only: `["▁Kitap","+çı","▁gelen","+ler","+i"]`
- Actual only: `["▁Kitapçı","▁gelenleri"]`

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

### proper_name: Ahmet'in evinden döndüm.

- Expected: `["▁Ahmet","'","+in","▁ev","+in","+den","▁dön","+dü","+m","."]`
- Actual: `["▁Ahmet","'","+in","▁evin","+den","▁dön","+dü","+m","."]`
- Expected only: `["+in","▁ev"]`
- Actual only: `["▁evin"]`

### proper_name: İzmir'dekiler toplantıya katıldı.

- Expected: `["▁İzmir","'","+de","+ki","+ler","▁toplantı","+ya","▁katıl","+dı","."]`
- Actual: `["▁İzmir","'","+de","+ki","+ler","▁toplantıya","▁katıldı","."]`
- Expected only: `["▁toplantı","+ya","▁katıl","+dı"]`
- Actual only: `["▁toplantıya","▁katıldı"]`

### proper_name: Bursa'dan gelenleri gördünüz mü?

- Expected: `["▁Bursa","'","+dan","▁gelen","+ler","+i","▁gör","+dü","+nüz","▁mü","?"]`
- Actual: `["▁Bursa","'","+dan","▁gelenleri","▁gör","+dü","+nüz","▁mü","?"]`
- Expected only: `["▁gelen","+ler","+i"]`
- Actual only: `["▁gelenleri"]`

### proper_name: Mehmet'in arabasından ses geldi.

- Expected: `["▁Mehmet","'","+in","▁araba","+sı","+ndan","▁ses","▁gel","+di","."]`
- Actual: `["▁Mehmet","'","+in","▁araba","+sın","+dan","▁ses","▁gel","+di","."]`
- Expected only: `["+sı","+ndan"]`
- Actual only: `["+sın","+dan"]`

### proper_name: Trabzon'daki evimize gittik.

- Expected: `["▁Trabzon","'","+da","+ki","▁ev","+imiz","+e","▁git","+ti","+k","."]`
- Actual: `["▁Trabzon","'","+da","+ki","▁evimize","▁git","+ti","+k","."]`
- Expected only: `["▁ev","+imiz","+e"]`
- Actual only: `["▁evimize"]`

### proper_name: Van'ın gölünü anlattılar.

- Expected: `["▁Van","'","+ın","▁göl","+ü","+nü","▁anlat","+tı","+lar","."]`
- Actual: `["▁Van","'","+ın","▁gölü","+nü","▁anlat","+tı","+lar","."]`
- Expected only: `["▁göl","+ü"]`
- Actual only: `["▁gölü"]`

### proper_name: Ece'nin notlarından yararlandık.

- Expected: `["▁Ece","'","+nin","▁not","+lar","+ın","+dan","▁yararlan","+dı","+k","."]`
- Actual: `["▁Ece","'","+nin","▁notların","+dan","▁yararlan","+dı","+k","."]`
- Expected only: `["▁not","+lar","+ın"]`
- Actual only: `["▁notların"]`

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
- Actual: `["▁Kanad","+ı","+nın","▁ucun","+da","▁iz","▁vardı","."]`
- Expected only: `["▁uç","+un","▁var","+dı"]`
- Actual only: `["▁ucun","▁vardı"]`

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
- Actual: `["▁README.md","'","▁yi","▁ye","+ni","+den","▁aç","+tı","+n","▁mı","?"]`
- Expected only: `["+yi","▁yeniden"]`
- Actual only: `["▁yi","▁ye","+ni","+den"]`

### question: Ali, Ayşe'ye baktı mı?

- Expected: `["▁Ali",",","▁Ayşe","'","+ye","▁bak","+tı","▁mı","?"]`
- Actual: `["▁Ali",",","▁Ayşe","'","+ye","▁baktı","▁mı","?"]`
- Expected only: `["▁bak","+tı"]`
- Actual only: `["▁baktı"]`

### informal: Napıyon burada?

- Expected: `["▁Napı","+yon","▁burada","?"]`
- Actual: `["▁Napı","+yon","▁bura","+da","?"]`
- Expected only: `["▁burada"]`
- Actual only: `["▁bura","+da"]`

### informal: Gidiyom şimdi eve.

- Expected: `["▁Gid","+iyom","▁şimdi","▁ev","+e","."]`
- Actual: `["▁Gid","+iyom","▁şimdi","▁eve","."]`
- Expected only: `["▁ev","+e"]`
- Actual only: `["▁eve"]`

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

### code_mixed: README_final.md'yi güncelledim.

- Expected: `["▁README_final.md","'","+yi","▁güncelle","+di","+m","."]`
- Actual: `["▁README_final.md","'","▁yi","▁güncelle","+di","+m","."]`
- Expected only: `["+yi"]`
- Actual only: `["▁yi"]`

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

### numbers_dates: 2025'ten sonra değişti.

- Expected: `["▁2025","'","+ten","▁sonra","▁değiş","+ti","."]`
- Actual: `["2025","'","+ten","▁sonra","▁değişti","."]`
- Expected only: `["▁2025","▁değiş","+ti"]`
- Actual only: `["2025","▁değişti"]`

### numbers_dates: 3.14 değerini yazdım.

- Expected: `["▁3.14","▁değer","+i","+ni","▁yaz","+dı","+m","."]`
- Actual: `["3.14","▁değeri","+ni","▁yaz","+dı","+m","."]`
- Expected only: `["▁3.14","▁değer","+i"]`
- Actual only: `["3.14","▁değeri"]`

### numbers_dates: 34-ABC-1907 plakası vardı.

- Expected: `["▁34-ABC-1907","▁plaka","+sı","▁var","+dı","."]`
- Actual: `["34","-","▁ABC","-","1907","▁plakası","▁vardı","."]`
- Expected only: `["▁34-ABC-1907","▁plaka","+sı","▁var","+dı"]`
- Actual only: `["34","-","-","▁ABC","1907","▁plakası","▁vardı"]`

### numbers_dates: %25'lik artış oldu.

- Expected: `["%","▁25","'","+lik","▁artış","▁ol","+du","."]`
- Actual: `["%","25","'","+lik","▁artış","▁oldu","."]`
- Expected only: `["▁25","▁ol","+du"]`
- Actual only: `["25","▁oldu"]`

### numbers_dates: 12:30'da toplantı başladı.

- Expected: `["▁12:30","'","+da","▁toplantı","▁başla","+dı","."]`
- Actual: `["12",":","30","'","+da","▁toplantı","▁başladı","."]`
- Expected only: `["▁12:30","▁başla","+dı"]`
- Actual only: `["12",":","30","▁başladı"]`

### numbers_dates: 1.000'den fazla kayıt vardı.

- Expected: `["▁1.000","'","+den","▁fazla","▁kayıt","▁var","+dı","."]`
- Actual: `["1.000","'","+den","▁fazla","▁kayıt","▁vardı","."]`
- Expected only: `["▁1.000","▁var","+dı"]`
- Actual only: `["1.000","▁vardı"]`

### numbers_dates: 5'inci satırı sildim.

- Expected: `["▁5","'","+inci","▁satır","+ı","▁sil","+di","+m","."]`
- Actual: `["5","'","+inci","▁satırı","▁sil","+di","+m","."]`
- Expected only: `["▁5","▁satır","+ı"]`
- Actual only: `["5","▁satırı"]`

### numbers_dates: 2024/05/01 tarihinde yazıldı.

- Expected: `["▁2024/05/01","▁tarih","+in","+de","▁yazıl","+dı","."]`
- Actual: `["2024","/","05","/","01","▁tarihin","+de","▁yaz","+ıl","+dı","."]`
- Expected only: `["▁2024/05/01","▁tarih","+in","▁yazıl"]`
- Actual only: `["2024","/","/","05","01","▁tarihin","▁yaz","+ıl"]`

### numbers_dates: 2GB'lık dosya indi.

- Expected: `["▁2GB","'","+lık","▁dosya","▁in","+di","."]`
- Actual: `["2","▁GB","'","+lık","▁dosya","▁in","+di","."]`
- Expected only: `["▁2GB"]`
- Actual only: `["2","▁GB"]`

### punctuation: “Merhaba,” dedi.

- Expected: `["\"","▁Merhaba",",","\"","▁de","+di","."]`
- Actual: `["\"","▁Merhaba",",","\"","▁dedi","."]`
- Expected only: `["▁de","+di"]`
- Actual only: `["▁dedi"]`

### punctuation: Evet; ama sonra döndü.

- Expected: `["▁Evet",";","▁ama","▁sonra","▁dön","+dü","."]`
- Actual: `["▁Evet",";","▁ama","▁sonra","▁döndü","."]`
- Expected only: `["▁dön","+dü"]`
- Actual only: `["▁döndü"]`

### punctuation: Ali, Ayşe'ye baktı.

- Expected: `["▁Ali",",","▁Ayşe","'","+ye","▁bak","+tı","."]`
- Actual: `["▁Ali",",","▁Ayşe","'","+ye","▁baktı","."]`
- Expected only: `["▁bak","+tı"]`
- Actual only: `["▁baktı"]`

### punctuation: README.md'yi açtın mı?

- Expected: `["▁README.md","'","+yi","▁aç","+tı","+n","▁mı","?"]`
- Actual: `["▁README.md","'","▁yi","▁aç","+tı","+n","▁mı","?"]`
- Expected only: `["+yi"]`
- Actual only: `["▁yi"]`

### punctuation: Hayır! Bunu yapma.

- Expected: `["▁Hayır","!","▁Bunu","▁yap","+ma","."]`
- Actual: `["▁Hayır","!","▁Bunu","▁yapma","."]`
- Expected only: `["▁yap","+ma"]`
- Actual only: `["▁yapma"]`

### punctuation: Peki... sonra ne oldu?

- Expected: `["▁Peki",".",".",".","▁sonra","▁ne","▁ol","+du","?"]`
- Actual: `["▁Pe","+ki",".",".",".","▁sonra","▁ne","▁oldu","?"]`
- Expected only: `["▁Peki","▁ol","+du"]`
- Actual only: `["▁Pe","+ki","▁oldu"]`

### punctuation: (Ankara'dan) yeni döndüm.

- Expected: `["(","▁Ankara","'","+dan",")","▁yeni","▁dön","+dü","+m","."]`
- Actual: `["(","▁Ankara","'","+dan",")","▁ye","+ni","▁dön","+dü","+m","."]`
- Expected only: `["▁yeni"]`
- Actual only: `["▁ye","+ni"]`

