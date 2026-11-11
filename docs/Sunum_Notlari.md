# ServisFlow — Sınıf Sunumu Konuşma Notları

> Sınıfta sözlü anlatım için hazırlanmıştır. Okunacak metin değil, **ezberlenmeden doğal anlatılacak ana fikirlerdir.** Her üye kendi use case'ini 30–45 saniyede anlatabilmelidir.

---

## 1. Açılış (Ekip lideri — ~45 sn)

> “Projemizin adı **ServisFlow**. Küçük oto servislerinde işler hâlâ deftere yazılıyor; bir aracın geçmişi kayboluyor, hangi işin bittiği belli olmuyor ve gün sonunda ne kadarlık iş yapıldığı elle hesaplanıyor. Biz bunu **araç bazlı bir iş takip sistemiyle** çözüyoruz: her araç ziyareti için To-Do listesi gibi işler açılıyor, iş bitince ✓ işaretleniyor ve sistem bu işi **tamamlandığı günün** brüt iş bedeline **yalnızca bir kez** yazıyor.”

> “Kapsamı bilinçli olarak dar tuttuk. İlk taslağımızda stok yönetimi, çoklu rol ve audit log vardı; bunları **‘az özellik, yüksek kalite’** ilkesiyle çıkardık. Amacımız her özelliği testlerle, ölçümlerle ve kod incelemesiyle kanıtlanmış şekilde teslim etmek.”

---

## 2. Use case'ler — Her üye kendi cümlesi

**UC-01 — Kimlik Doğrulama ve Güvenli Oturum Yönetimi**
> “Kullanıcı girişini OWASP'ın önerdiği **Argon2id** algoritmasıyla parolayı özetleyerek yapıyoruz; veritabanında düz metin parola yok. Yanlış kullanıcı adı ve yanlış parola için aynı mesajı veriyoruz ki saldırgan hangi kullanıcı adının var olduğunu öğrenemesin. Oturum açılmadan hiçbir ekran görüntülenemiyor. Üç kez yanlış parola girilirse robot doğrulaması çıkıyor, ve işletme sahibi giriş yaptığında hesabına yapılan hatalı denemeleri tarih-saatiyle görüyor; böylece biri parolasını denemişse haberi oluyor.”

**UC-02 — Müşteri Kaydı, Girdi Doğrulama ve Arama**
> “Müşteri kaydında her alanı **sunucu tarafında doğruluyoruz**: zorunlu alan, uzunluk sınırı, telefon formatı. Türkçe karakterli isimlerde büyük/küçük harf duyarsız arama yapıyoruz. Bu use case'i **sınır değer analizi** ile test edeceğiz: 0, 1, 100 ve 101 karakterlik isimler.”

**UC-03 — Araç Kaydı, Plaka Normalizasyonu ve Tekillik Denetimi**
> “Aynı plaka farklı yazılabiliyor: ‘34 bjk 321’ ile ‘34BJK321’ aynı araç. Sistem plakayı kaydetmeden önce **normalize ediyor** ve veritabanında **tekillik kısıtı** uyguluyor. Böylece aynı araç iki kez açılamıyor, **veri bütünlüğü** korunuyor.”

**UC-04 — Servis Ziyareti Açılışı ve Otomatik Zaman Damgalama**
> “Araç her servise geldiğinde yeni bir ziyaret, yani iş emri açılıyor. Açılış zamanını **kullanıcı değil sistem atıyor**; elle tarih girişi yok, dolayısıyla tarih manipülasyonu ve yazım hatası yok. Bir aracın farklı günlerdeki ziyaretleri ayrı tutuluyor; böylece araç geçmişi oluşuyor.”

**UC-05 — Görev Tabanlı İş Listesi Yönetimi**
> “Her ziyarete To-Do mantığında işler ekleniyor: başlık, not ve tutar. Tutarları **kuruş cinsinden tamsayı** olarak saklıyoruz, bu sayede ondalık yuvarlama hatası yapısal olarak oluşamıyor. Tamamlanmış bir iş artık düzenlenemiyor; geçmiş veri kilitleniyor.”

**UC-06 — İdempotent Görev Tamamlama ve Tutar Kilitleme**
> “Projenin kalbi burası. İş ✓ ile tamamlandığında tamamlanma zamanı atanıyor ve tutar kilitleniyor. Bu işlem **idempotent**: kullanıcı ✓'ye iki kez bassa da iş bir kez tamamlanıyor, tutar iki kez sayılmıyor. Durumlar arası geçişleri bir **durum diyagramıyla** tanımladık ve her geçişi **durum geçiş testiyle** doğrulayacağız.”

**UC-07 — Araç Servis Geçmişi ve Zaman Dilimi Duyarlı Dönemsel Raporlama**
> “Günlük, haftalık, aylık ve yıllık brüt iş bedelini işin **açıldığı değil tamamlandığı** tarihe göre hesaplıyoruz. Zamanı UTC saklıyor, raporda **İstanbul saatine** çeviriyoruz. Gece 23:59 ile 00:00 arasında tamamlanan işin doğru güne düşmesini sınır testleriyle doğruluyoruz. Toplamı ayrı bir sayaç olarak tutmuyor, her seferinde sorgudan hesaplıyoruz; bu yüzden çift sayım mümkün değil.”

---

## 3. Kalite yaklaşımı (QA lideri — ~45 sn)

> “Kalite özelliklerimizi **ISO/IEC 25010** ürün kalite modeline göre sınıflandırdık: güvenlik, güvenilirlik, fonksiyonel doğruluk, bakım yapılabilirlik ve kullanılabilirlik. Her biri için ölçülebilir hedef koyduk.”

| Hedef | Araç |
| :--- | :--- |
| İş mantığında ≥ %80 test kapsamı | pytest-cov |
| Fonksiyon başına McCabe ≤ 10 | radon |
| Yüksek önemli güvenlik bulgusu = 0 | bandit |
| Her PR'da en az 1 onay, CI yeşil olmadan birleştirme yok | GitHub Actions |

> “Mimariyi katmanlı kurduk: arayüz, iş kuralları ve veri erişimi ayrı. İş kuralları arayüzden bağımsız olduğu için arayüzü açmadan test edebiliyoruz. Test tekniklerimiz: **sınır değer analizi, denklik sınıfları, durum geçiş testi** (kara kutu) ve **kod kapsama** (beyaz kutu).”

---

## 4. Hocanın sorabileceği sorular ve hazır cevaplar

**S: Neden stok yönetimini çıkardınız? Proje çok basit değil mi?**
> “Kapsamı bilerek daralttık. Ders kalite standartları üzerine; on özelliği yarım test etmek yerine yedi use case'i tam test edip ölçmeyi tercih ettik. Basit görünen kısımlarda bile kalite açısından zor problemler var: idempotent tamamlama, saat dilimi sınırları, para hassasiyeti, plaka tekilliği.”

**S: İdempotent ne demek?**
> “Aynı işlemi birden çok kez yapmanın sonucu değiştirmemesi. ✓'ye iki kez basılması veya ağ yüzünden isteğin iki kez gitmesi işi iki kez saymıyor.”

**S: Parayı neden float tutmuyorsunuz?**
> “Float ikili tabanda ondalık sayıları tam gösteremez; 0,1 + 0,2 tam 0,3 etmez. Kuruş cinsinden tamsayı saklayınca yuvarlama hatası olmuyor.”

**S: Neden UTC saklayıp İstanbul'a çeviriyorsunuz?**
> “Veritabanında tek ve tutarlı bir zaman standardı olsun diye. Gün sınırını ise kullanıcının yaşadığı takvime göre, yani İstanbul saatine göre çiziyoruz.”

**S: Raporda gösterilen tutar gelir mi?**
> “Hayır, **tamamlanan işlerin brüt bedeli**. Tahsilat veya kâr takibi yapmıyoruz; bu bilinçli bir kapsam sınırı.”

**S: Yapay zekâyı nasıl kullandınız?**
> “Doküman taslağı ve revizyonunda ChatGPT ve Claude kullandık. Kullanımı **DIR yöntemiyle** raporumuzda beyan ediyoruz; kararları ve gözden geçirmeyi ekip yaptı.”

**S: Hangi standartları kullandınız?**
> “Kalite özellikleri için ISO/IEC 25010, gereksinim yazımı için ISO/IEC/IEEE 29148, test planı için ISO/IEC/IEEE 29119'u referans aldık. Karmaşıklık ölçümü için McCabe metriği.”

**S: Ekipte iş bölümü nasıl takip ediliyor?**
> “Her use case'in bir sahibi var. Katkıyı GitHub'daki commit, pull request ve review kayıtlarıyla izliyoruz; her PR'ı en az bir başka üye inceliyor.”

---

## 5. Kapanış (~15 sn)

> “Özetle ServisFlow; dar ama net bir problemi, ölçülebilir kalite hedefleri, standartlara dayalı gereksinimler ve planlı testlerle çözen bir proje. Faz 2'de ayrıntılı test planı ve risk analizini sunacağız.”
