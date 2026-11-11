# Faz 2 Sunumu — Sözlü Anlatım Çalışma Metni

> Bu metin sunum slaytlarıyla aynı sırayı izler. **Ezberlemeyin**; her bölümün altındaki **anahtar kelimeleri** aklınızda tutun, cümleleri kendi ağzınıza göre söyleyin. Yaklaşık süre: **12–14 dakika** (soru-cevap hariç). Hoca daha kısa süre verirse “kısaltılabilir” diye işaretlenen slaytları geçin.

## Kim nerede konuşuyor?

| Slayt | Konu | Konuşmacı | Süre |
| :--- | :--- | :--- | :--- |
| 1–2 | Açılış, gündem | Ahmet Selim Dostabakan | 1 dk |
| 3 | ServisFlow hatırlatma | Ilgın Çutok | 40 sn |
| 4–6 | İnceleme yöntemi, öne çıkan bulgular | Ahmet Selim Dostabakan + Mehmet Kenan Dilberoğlu (RV-02) | 2,5 dk |
| 7 | RV-07: CAPTCHA kararı | Ahmet Karavuş | 1 dk |
| 8–9 | Kalite kapıları | Ahmet Selim Dostabakan | 1 dk |
| 10 | CI’daki 7 kontrol | Kerem Erden | 45 sn |
| 11–12 | Test seviyeleri, karar tablosu | Mehmet Ünsalan | 1,5 dk |
| 13 | Test senaryoları | Ahmet Selim Dostabakan | 45 sn |
| 14–18 | Güvenlik risk değerlendirmesi | Kerem Erden | 3 dk |
| 19–21 | DIR, Faz 3 planı, kapanış | Ahmet Selim Dostabakan | 1,5 dk |

Konuşmacı değiştirmek isterseniz tabloyu güncelleyin; önemli olan herkesin kendi konuşacağı slaytı önceden bilmesi.

**Geçiş kuralı:** Sıra size geldiğinde bir önceki konuşmacı sizi adınızla çağırır (“Bu bulguyu Mehmet Kenan anlatacak.”). Böylece sessiz bekleme olmaz.

---

## Slayt 1 — Kapak · *Selim*

> “Merhaba hocam, merhaba arkadaşlar. Biz ServisFlow ekibiyiz. Bugün projemizin ikinci fazını, yani **stratejik kalite ve kontrat planlamasını** sunacağız.”

**Anahtar kelimeler:** ServisFlow · Faz 2 · stratejik kalite ve kontrat planlaması

## Slayt 2 — Faz 2’de ne yaptık? · *Selim*

> “Yönerge Faz 2 için üç şey istiyor; sunumumuz da bu üç bölümden oluşuyor.
> Birincisi, Faz 1’de yazdığımız gereksinimleri inceleyip düzelttik; 14 bulgu çıktı.
> İkincisi, kodun hangi koşulda kabul edileceğini, yani kalite kapılarını ve test planını tanımladık.
> Üçüncüsü, daha kod yazmadan güvenlik risklerini çıkardık.
> En sonda bu faz için yapay zekâ kullanım beyanımızı, yani DIR puanımızı göstereceğiz.
> Önce projemizi kısaca hatırlatalım; Ilgın anlatacak.”

**Anahtar kelimeler:** üç madde · 14 bulgu · kalite kapıları + test planı · güvenlik riskleri · DIR

## Slayt 3 — ServisFlow hatırlatma · *Ilgın*

> “ServisFlow küçük bir oto servis için iş takip uygulaması. Araç servise gelince bir ziyaret açılıyor, içine To-Do listesi gibi işler ekleniyor: ‘ön sol teker’, ‘yağ değişimi’ gibi.
> İş bitince yanına tik konuyor ve işin tutarı **tamamlandığı güne** yazılıyor. Böylece günlük, haftalık, aylık toplamı görebiliyoruz.
> Sistemi **sadece işletme sorumlusu** kullanıyor; ustalar yaptıkları işi ona söylüyor, kaydı o giriyor.
> Bu tek kullanıcı kararı aslında Faz 2 incelemesinde netleşti. Selim anlatacak.”

**Anahtar kelimeler:** ziyaret → iş → tik → tamamlandığı gün · tek kullanıcı: işletme sorumlusu

---

## Bölüm 1 — Faz 1 İncelemesi

### Slayt 4 — Bölüm geçişi · *Selim*

> “İlk bölüm: Faz 1 çıktılarının gözden geçirilmesi.” *(Hemen sonraki slayta geçin.)*

### Slayt 5 — İnceleme yöntemi · *Selim*

> “Gereksinimleri rastgele okumadık. **ISO/IEC/IEEE 29148** standardında iyi bir gereksinimin özellikleri tanımlı; biz bunlardan beşini ölçüt aldık.
> Bir gereksinim **tek anlamlı** olmalı, yani iki kişi okuyunca aynı şeyi anlamalı. **Doğrulanabilir** olmalı, yani test edilebilmeli. **Tutarlı** olmalı, başka bir kuralla çelişmemeli. **Eksiksiz** olmalı ve bir teste **izlenebilir** olmalı.
> Bu ölçütlerle 14 bulgu çıkardık; üçü yüksek önemliydi. Yaklaşık iki saatlik toplantıda her use case sahibi kendi bölümünü inceledi ve **14 bulgunun hepsini kabul ettik.**”

**Anahtar kelimeler:** ISO/IEC/IEEE 29148 · tek anlamlı, doğrulanabilir, tutarlı, eksiksiz, izlenebilir · 14 bulgu, 3 yüksek, hepsi kabul · walkthrough

### Slayt 6 — Öne çıkan üç bulgu · *Selim + Mehmet Kenan*

**Selim (RV-01):**
> “En önemli bulgu şuydu: bir işin tikini kaldırıp tutarını değiştirip tekrar tik koyunca, **geçen haftanın raporu kimse fark etmeden değişebiliyordu.** Artık tik yalnızca **aynı gün içinde** geri alınabiliyor; gün geçince iş kesinleşiyor.
> İkinci bulguyu plaka kısmının sahibi Mehmet Kenan anlatacak.”

**Mehmet Kenan (RV-02):**
> “Plakayı büyük harfe çevirirken Türkçe kuralı kullanıyorduk. Bu durumda küçük ‘i’ harfi büyük ‘İ’ oluyor. Ama **Türk plakalarında İ, Ş, Ç gibi harfler yok**, yani sistem geçersiz bir plaka üretiyordu. Latin büyük harfe geçtik ve geçerli plaka biçimini tanımladık: il kodu, bir ile üç harf, iki ile dört rakam.”

**Selim (RV-08):**
> “Üçüncüsü, sisteme kimin giriş yaptığı belirsizdi: her usta mı, işletme sahibi mi? Toplantıda netleştirdik: **tek kullanıcı, işletme sorumlusu.** Bir sonraki bulguyu Ahmet anlatacak.”

**Anahtar kelimeler:** RV-01 geçmiş rapor değişiyordu → aynı gün · RV-02 Türkçe İ → Latin harf · RV-08 kim giriyor → tek kullanıcı

### Slayt 7 — RV-07: CAPTCHA kararı · *Ahmet Karavuş*

> “Bu bulgu, yapay zekânın önerisini nasıl değiştirdiğimizin örneği.
> Hatalı girişler için taslakta ‘**5 hatalı denemede hesap 5 dakika kilitlensin**’ yazıyordu. Biz bunun yerine şunu seçtik:
> **Üç hatalı denemeden sonra robot doğrulaması, yani CAPTCHA** çıkıyor.
> **Her hatalı deneme kaydediliyor**; işletme sahibi giriş yaptığında, kendi hesabına yapılan hatalı denemeleri tarih ve saatiyle görüyor. Biri parolasını denediyse haberi oluyor.
> CAPTCHA’yı **kendi sunucumuzda** üreteceğiz; Google gibi dış bir servise veri göndermiyoruz.
> Bunu iki test senaryosuyla doğrulayacağız: TC-04 ve TC-32.
> İkinci bölüme Selim geçecek.”

**Anahtar kelimeler:** YZ önerisi: 5 hata → 5 dk kilit · ekip kararı: 3 hata → CAPTCHA · hatalı giriş listesi · kendi sunucumuzda · TC-04, TC-32

> ⚠️ Slaytta “tek hesap kilitlenirse işletme sahibi de giremez” gerekçesi yazıyor. Ekip olarak bu gerekçeyi benimsiyorsanız sözlü de söyleyin; benimsemiyorsanız söylemeyin.

---

## Bölüm 2 — Kalite Kapıları ve Test Planı

### Slayt 8 — Bölüm geçişi · *Selim*

> “İkinci bölüm: kodun hangi koşulda kabul edileceği ve nasıl test edileceği.”

### Slayt 9 — Dört kalite kapısı · *Selim*

> “Kalite kapısı, bir çıktının bir sonraki aşamaya geçmesi için sağlaması gereken **ölçülebilir koşullar**. Dört kapımız var.
> **KK-1** her faz kapanırken gereksinimlere bakıyor. **KK-2** en sık çalışan kapı: her pull request’te. **KK-3** Faz 4’te testlerin tamamlandığını, **KK-4** de yayından önce kurulumun gerçekten çalıştığını kontrol ediyor.
> Önemli ayrım şu: **test ölçer, kapı karar verir.** Mesela testler geçse bile kapsama yüzde sekseninin altındaysa kod birleştirilemez.
> KK-2’nin ayrıntısını Kerem anlatacak.”

**Anahtar kelimeler:** ölçülebilir koşul · KK-1 gereksinim, KK-2 her PR, KK-3 test tamamlama, KK-4 devreye alma · test ölçer, kapı karar verir

### Slayt 10 — CI’daki 7 kontrol · *Kerem*

> “KK-2 kâğıt üstünde değil, **GitHub Actions’ta çalışıyor.** Her pull request’te yedi kontrol sırayla çalışıyor: kod biçimi, stil, kod güvenliği, bağımlılık güvenliği, McCabe karmaşıklığı, testler ve kapsama.
> Biri kırmızı olursa kod birleştirilemez. **Şu an yedisi de yeşil.**
> Doğrudan ana dala göndermeyi yasaklayan kuralı, kodlamaya başlayacağımız **Faz 3’ün ilk günü** açacağız.
> Test planını Mehmet anlatacak.”

**Anahtar kelimeler:** GitHub Actions · 7 kontrol: black, flake8, bandit, pip-audit, radon/xenon, pytest, pytest-cov · hepsi yeşil · dal koruması Faz 3’te

### Slayt 11 — Dört test seviyesi · *Mehmet Ünsalan*

> “Test planımızı **ISO/IEC/IEEE 29119-3**’e göre yazdık. Dört seviye var.
> **Birim testi** tek bir fonksiyonu sınıyor; örneğin plakanın düzgün çevrilmesi.
> **Entegrasyon testi** parçaları birlikte sınıyor; örneğin aynı plakanın veritabanındaki tekillik kuralına takılması. Bunun için bellekte çalışan SQLite kullanacağız.
> **Sistem testi** uygulamanın girişten rapora uçtan uca akışı.
> **Kabul testi** de işletme sahibine benzeyen birinin uygulamayı yardım almadan, en fazla üç dakikada kullanabilmesi.
> Sağdaki altı tekniği senaryoları seçerken kullandık. Birini örnekle göstereyim.”

**Anahtar kelimeler:** ISO/IEC/IEEE 29119-3 · birim, entegrasyon, sistem, kabul · bellekte SQLite · 3 dakika

### Slayt 12 — Karar tablosu · *Mehmet Ünsalan*

> “Az önce anlatılan ‘tik yalnızca aynı gün geri alınır’ kuralı iki koşula bağlı: iş tamamlanmış mı, ve bugün mü tamamlandı?
> Karar tablosu bu koşulların bütün kombinasyonlarını yazıyor. Bugün tamamlandıysa geri alınıyor, dün tamamlandıysa reddediliyor, iş zaten açıksa hiçbir şey olmuyor.
> **Her sütun bir test senaryosuna dönüşüyor**; böylece kuralın gözden kaçan bir dalı kalmıyor.”

**Anahtar kelimeler:** iki koşul · her sütun = bir test · TC-19, TC-20, TC-21

### Slayt 13 — Test senaryoları · *Selim*

> “Faz 1’de 13 senaryomuz vardı, şimdi **32**. Soldaki çubuklar her use case’e kaç senaryo düştüğünü gösteriyor; güvenlik riskleri girişte yoğun olduğu için en çok senaryo orada.
> Sağda bir örnek var: **gece yarısı sınırı.** Saat 23:59:59’da tamamlanan iş o güne, 00:00:00’da tamamlanan ertesi güne yazılmalı.
> Bunu test edebilmek için saati sistemden değil, dışarıdan veriyoruz; testte saati istediğimiz ana sabitleyebiliyoruz.
> Faz 3’te herkes kendi senaryolarını teste çevirecek; testi olmayan kod kapıdan geçemeyecek.
> Güvenlik bölümünü Kerem anlatacak.”

**Anahtar kelimeler:** 13 → 32 · gece yarısı sınırı · saat dışarıdan verilir (clock) · testi olmayan kod geçemez

---

## Bölüm 3 — Güvenlik Risk Değerlendirmesi · *Kerem*

### Slayt 14 — Bölüm geçişi

> “Üçüncü bölüm: güvenlik açıklarını daha **tasarım aşamasında** önlemek.”

### Slayt 15 — Veri akışı ve güven sınırları

> “Riskleri çıkarmak için önce verinin nereden geçtiğini çizdik: işletme sorumlusunun tarayıcısı, arayüz, iş kuralları, veritabanı katmanı ve veritabanı dosyası.
> Turuncu kesikli çizgiler **güven sınırları.** Tarayıcıdan gelen her şeyi güvenilmez kabul ediyoruz ve sunucuda doğruluyoruz. Veritabanı dosyası depoya hiç girmiyor. Dışarıdan aldığımız paketler de ayrı bir sınır: tedarik zinciri.
> Sonra her bileşeni **STRIDE**’ın altı kategorisiyle taradık: kimlik sahteciliği, veriyi değiştirme, inkâr, bilgi sızıntısı, hizmet engelleme ve yetki yükseltme. **14 tehdit** çıktı.”

**Anahtar kelimeler:** veri akışı · güven sınırı · STRIDE altı kategori · 14 tehdit

### Slayt 16 — Risk matrisi

> “Her tehdide bir ile üç arası **olasılık** ve **etki** puanı verdim; risk ikisinin çarpımı. Sağ üst köşe en tehlikeli bölge.
> **Beş yüksek risk** çıktı. Puanları ekip toplantısında birlikte gözden geçirdik; ilk taslaktaki altı puanı düşürdük. Mesela girişsiz sayfa açma artık düşük olasılıklı, çünkü tasarımda önlemi var.
> Her tehdidi ayrıca **OWASP Top 10** ile eşledik.”

**Anahtar kelimeler:** olasılık × etki · 5 yüksek, 4 orta, 5 düşük · 6 puan düşürüldü · OWASP Top 10

### Slayt 17 — Beş yüksek risk

> “Beş yüksek riskin her biri için daha kod yazmadan bir önlem belirledik ve o önlemi doğrulayacak testi yazdık.
> Örneğin **SQL enjeksiyonuna** karşı veritabanına sadece ORM üzerinden erişiyoruz; bandit taraması ve kod incelemesi bunu denetliyor.
> **Çift sayıma** karşı tamamlama tek bir koşullu işlem: ‘iş hâlâ açıksa kapat.’ İkinci tıklama hiçbir şeyi değiştirmiyor.
> Altta da **bilerek kabul ettiğimiz riskler** var. Kapsamı dar tutmak için tam denetim kaydını, yani audit log’u çıkardık ve bunu açıkça yazdık.”

**Anahtar kelimeler:** her riske önlem + test · SQL enjeksiyonu → ORM · çift sayım → koşullu güncelleme · bilerek kabul edilen riskler

### Slayt 18 — 67 açık → 0

> “Risk değerlendirmesi kâğıt üstünde kalmadı. Kullandığımız paketleri **pip-audit** aracıyla taradığımızda, Faz 1’de seçtiğimiz Streamlit sürümünün kurduğu **Pillow** kütüphanesinde **67 bilinen güvenlik kaydı** çıktı.
> Bütün paketleri güncel sürümlere yükselttik, tarama temiz çıktı ve bütün kontroller yeniden geçti. Bu taramayı artık **her pull request’te otomatik** çalıştırıyoruz.
> Buradan çıkardığımız ders: **sürümü sabitlemek tek başına yetmez**; sabit kalan sürüm zamanla açık barındırabiliyor.
> Son bölümü Selim anlatacak.”

**Anahtar kelimeler:** pip-audit · Pillow 10.4.0 · 67 → 0 · her PR’da otomatik · sabitlemek yetmez

---

## Kapanış · *Selim*

### Slayt 19 — DIR

> “Bu fazda yapay zekâ olarak **Claude Code** kullandık ve dersin DIR rehberine göre puanladık: Keşfet 4, Etkileş 4, Gözden geçir 4. Formülle **51, Bant 3**: etkin ve dengeli yönetişim.
> Etkileşim puanımızın en güçlü dayanağı, yapay zekânın önerilerini değiştirmemiz: aktörü tek kullanıcıya çevirdik, hesap kilidi yerine CAPTCHA seçtik, risk puanlarının altısını düşürdük.
> Doğrulama tarafında kaynakları orijinalinden kontrol ettik; Kerem iş kurallarını gerçek bir oto servisle değerlendirdi.
> Neden 5 vermediğimizi de açıkça yazdık: rapor metni hâlâ büyük ölçüde yapay zekânın cümleleri, kendi üslubumuzla yeniden yazmadık.”

**Anahtar kelimeler:** Claude Code · 4-4-4 → 51, Bant 3 · üç müdahale · kaynak doğrulama + gerçek servis · neden 5 değil

### Slayt 20 — Sırada Faz 3

> “Faz 3’te kodlamaya başlıyoruz; teslimi dokuzuncu hafta. Kodlama vize haftalarına denk geldiği için kod iskeletini önceden hazırlayacağız.
> İlk gün ana dalı koruma altına alacağız; o andan sonra her değişiklik pull request ile, yeşil kontrollerle ve bir arkadaşımızın onayıyla girecek. Herkes kendi use case’ini testleriyle birlikte geliştirecek.”

### Slayt 21 — Teşekkürler

> “Dinlediğiniz için teşekkür ederiz. Sorularınızı alabiliriz.”

---

## Soru-Cevap Çalışması

Soru gelince **cevabı konunun sahibi versin.** Bilmediğiniz bir şey sorulursa uydurmayın: “Bunu raporumuzda şu bölümde ele aldık” ya da “Bunu not alıp Faz 3’te ele alacağız” demek yeterli.

| Soru | Kim cevaplar | Kısa cevap |
| :--- | :--- | :--- |
| Neden tek kullanıcı hesabı var? | Selim | Gerçek akışta sisteme işletme sahibi giriyor, ustalar ona bildiriyor. RV-08’de netleşti. Yetki matrisi gerekmiyor, kapsam dar kalıyor; karşılığında parola paylaşılmamalı (R-06). |
| Kilit yerine neden CAPTCHA? | Karavuş | CAPTCHA otomatik denemeyi yavaşlatıyor, hatalı giriş listesi sahibine haber veriyor. Kendi sunucumuzda üretiliyor, veri dışarı çıkmıyor. |
| Gereksinimleri neye göre incelediniz? | Selim | ISO/IEC/IEEE 29148’deki iyi gereksinim özellikleri: tek anlamlı, doğrulanabilir, tutarlı, eksiksiz, izlenebilir. |
| Kalite kapısı ile test arasındaki fark? | Selim | Test ölçer, kapı karar verir. Testler geçse de kapsama %80 altındaysa PR birleşmez. |
| Neden %80 kapsama, McCabe ≤ 10? | Mehmet Ü. | 10, McCabe’nin 1976’da önerdiği üst sınır. %80 ekibin hedefi; arayüz hariç, çünkü iş kuralları servis katmanında ve orası tam test edilebilir. |
| Birim ile entegrasyon testinin farkı? | Mehmet Ü. | Birim tek fonksiyonu, entegrasyon parçaları birlikte sınar. Örnek: plaka çevirme (birim), aynı plakanın veritabanında reddedilmesi (entegrasyon). |
| Gece yarısını nasıl test edeceksiniz? | Selim | Saat dışarıdan veriliyor (clock); testte 23:59:59 ve 00:00:00’a sabitleyip işin hangi güne düştüğüne bakıyoruz (TC-26). |
| Çift tıklamada tutar neden iki kez sayılmaz? | Mehmet Ü. | Tamamlama “iş hâlâ açıksa kapat” şeklinde tek koşullu işlem; ikinci istek hiçbir şeyi değiştirmez. Toplam da sayaçta tutulmuyor, her seferinde sorgudan hesaplanıyor. |
| STRIDE nedir? | Kerem | Tehditleri altı türe ayıran yöntem: kimlik sahteciliği, değiştirme, inkâr, sızıntı, hizmet engelleme, yetki yükseltme. |
| Audit log yok, bu açık değil mi? | Kerem | Bilerek çıkardık ve kalan risk olarak yazdık. Geçmiş raporun değişmesini başka yolla kapattık: tik yalnızca aynı gün geri alınıyor. |
| Açık bulundu, olasılık neden hâlâ 2? | Kerem | Açık bulundu ve kapatıldı; tarama artık her PR’da otomatik. Bu yüzden olasılığı 2’de tuttuk. |
| DIR’de R neden 5 değil? | Selim | Doğrulamayı yaptık (kaynaklar, gerçek servis), ama rehberdeki 5 için çıktının kendi üslubumuzla yeniden yazılması da gerekiyor; metin büyük ölçüde yapay zekânın cümleleri. |
| Yapay zekâyı nasıl kullandınız? | Selim | Taslağı Claude Code hazırladı; kararları, puanları ve eşikleri ekip verdi. Önerilerinin bir kısmını değiştirdik, kaynakları kendimiz doğruladık. Hepsi DIR beyanında. |
| Diğer üyelerin katkısı ne? | Selim | Her üyenin bir use case’i var ve kendi bölümünün bulgularını inceleyip onayladı. Faz 3’te herkes kendi use case’ini kendi PR’ında geliştirecek; katkı GitHub kayıtlarında görünecek. |

## Bilinmesi Gereken Terimler

| Terim | Bir cümlelik açıklama |
| :--- | :--- |
| **Walkthrough** | Ekibin bir belgeyi birlikte, madde madde okuyarak yaptığı inceleme. |
| **Kalite kapısı** | Bir sonraki aşamaya geçmek için sağlanması gereken ölçülebilir koşullar. |
| **CI (sürekli entegrasyon)** | Her kod gönderiminde testlerin ve kontrollerin otomatik çalışması. |
| **Pull request (PR)** | Bir değişikliğin ana koda eklenmeden önce incelenmesi için açılan istek. |
| **Kapsama (coverage)** | Testlerin kodun ne kadarını çalıştırdığı; satır ve dal olarak ölçülür. |
| **McCabe karmaşıklığı** | Bir fonksiyondaki bağımsız yol sayısı; yüksekse kod zor test edilir. |
| **Sınır değer analizi** | Hataların sınırlarda yoğunlaştığı varsayımıyla tam sınırı ve hemen yanını test etmek (0,00 / 0,01 TL gibi). |
| **Denklik sınıfı** | Aynı şekilde davranması beklenen girdileri bir grupta toplayıp her gruptan bir örnek test etmek. |
| **Karar tablosu** | Koşulların bütün kombinasyonlarını ve sonuçlarını gösteren tablo. |
| **İdempotent** | Aynı işlemi iki kez yapmanın sonucu değiştirmemesi (çift tik). |
| **STRIDE** | Tehditleri altı türe ayıran modelleme yöntemi. |
| **OWASP Top 10** | Web uygulamalarındaki en yaygın on güvenlik riski listesi. |
| **Güven sınırı** | Verinin güvenilir bir bölgeden güvenilmeyen bir bölgeye geçtiği yer. |
| **SQL enjeksiyonu** | Girdi alanına veritabanı komutu yazarak veriyi okuma veya bozma saldırısı. |
| **ORM** | Veritabanına SQL yazmadan, programlama diliyle erişmeyi sağlayan katman. |
| **CAPTCHA** | İnsan mı robot mu olduğunu ayırt etmek için gösterilen doğrulama. |
| **pip-audit** | Kullanılan Python paketlerinde bilinen güvenlik açığı olup olmadığını tarayan araç. |
| **DIR** | Yapay zekâ kullanımını Keşfet, Etkileş, Gözden Geçir boyutlarıyla puanlayan ders çerçevesi; skor = Floor(0,8 × D × I × R). |
