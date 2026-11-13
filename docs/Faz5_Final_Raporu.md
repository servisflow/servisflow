# PROJE RAPORU: FİNAL — ServisFlow

- **Proje adı:** ServisFlow — Araç Bazlı Servis İş Takibi ve Dönemsel Brüt İş Bedeli Raporlama
- **Ders:** Yazılım Kalite Standartları (YAZ401)
- **Doküman durumu:** Taslak v0.1 — Faz 1–4 çıktılarının özeti; Faz 5 bölümünde üyelerin öğrendikleri ve demo kaydı `[ekip]`
- **Depo:** <https://github.com/servisflow/servisflow> · **Canlı sürüm:** <https://servisflow.streamlit.app/>
- **Teslim:** Hafta 14 (izlence)

Bu rapor, beş fazın çıktılarını ders yönergesindeki şablona göre özetler: ekip ve katkılar → Faz 1–5 çıktıları → iş paketi bazında DIR beyanları → referanslar → ekler. Ayrıntılar her fazın kendi raporundadır ([Faz 1](Faz1_Raporu.md), [Faz 2](Faz2_Raporu.md), [Faz 3](Faz3_Raporu.md), [Faz 4](Faz4_Raporu.md)). Kurulum, çalıştırma ve test talimatı Ek B'dedir.

**Özet.** ServisFlow, küçük bir oto servisin işletme sorumlusunun her araç ziyareti için yapılan işleri kaydettiği, işleri ✓ ile tamamladığı ve tamamlandıkları güne göre günlük, haftalık, aylık ve yıllık brüt iş bedelini gördüğü tek kullanıcılı bir web uygulamasıdır. Yedi kullanım durumunun tamamı uygulandı. Son hâlde 258 otomatik test geçiyor; `ui` hariç satır ve dal kapsaması %100; fonksiyon başına en yüksek McCabe karmaşıklığı 6. Uygulama Streamlit Community Cloud'da yayında; ekip dışı bir katılımcıyla yapılan kullanıcı kabul testi 2 dk 20 sn'de yardımsız tamamlandı ve bir hata buldu, hata düzeltildi.

---

## 1. Ekip ve Katkılar

| Üye | Proje rolü | Sahip olduğu use case | Kayıtlı katkılar |
| :--- | :--- | :--- | :--- |
| Ahmet Karavuş | Kimlik doğrulama ve güvenlik geliştiricisi | UC-01 Giriş ve güvenli oturum | Faz 2 incelemesinde UC-01 bulgularını onayladı. `[ekip: diğer katkılar]` |
| Alperhan Karşı | İş analisti ve gereksinim mühendisi | UC-02 Müşteri kaydı ve arama | Faz 2 incelemesinde UC-02 bulgularını onayladı. `[ekip: diğer katkılar]` |
| Mehmet Kenan Dilberoğlu | Scrum master ve backend geliştirici | UC-03 Araç kaydı ve plaka tekilliği | Faz 2 incelemesinde UC-03 bulgularını onayladı. `[ekip: diğer katkılar]` |
| Ilgın Çutok | UI/UX ve dokümantasyon sorumlusu | UC-04 Servis ziyareti | Faz 2 incelemesinde UC-04 bulgularını onayladı. `[ekip: diğer katkılar]` |
| Kerem Erden | Yazılım mimarı ve DevSecOps | UC-05 İş listesi | Faz 1 ilk taslağı; Faz 2 risk puanları ve iş kurallarının gerçek bir oto serviste değerlendirilmesi; UC-01 – UC-06 servis ve arayüzlerinin YZ destekli geliştirilmesi; Faz 4 McCabe, devreye alma ve TC-31'in yönetimi; #10 – #13 kod incelemeleri |
| Mehmet Ünsalan | Backend ve beyaz kutu test uzmanı | UC-06 İdempotent tamamlama | Faz 1 v1.0 gözden geçirmesi; Faz 4 kod incelemeleri ve onayları (#22 – #26); TC-31 gözlemi ve onayı |
| Ahmet Selim Dostabakan | Ekip lideri, kalite güvence ve test lideri | UC-07 Araç geçmişi ve raporlama | Faz 1 v1.0 ve Faz 2'nin yönlendirilmesi; kod iskeleti ve UC-07 servis katmanı; Faz 3 kod incelemeleri (#14 – #20); ekran paylaşımlı ortak inceleme; TC-31 gözlemi |

**Sahiplik ve geliştirme.** Yönerge gereği her üye en az bir use case'in sahibidir. Kodun önemli bölümü, UC-01 – UC-04 sahipleri GitHub organizasyonunda olmadığı ve UC-06 sahibine Faz 3'te ulaşılamadığı için Kerem Erden yönlendirmesiyle yazıldı; sahip, geliştiren ve inceleyen ayrımı Faz 1 Raporu Bölüm 1'de ve Faz 3 Raporu 3.3'te kayıtlıdır. Bu dengesizlik ekipçe bilinen bir eksikliktir.

---

## 2. Faz 1 — Proje Konusu, Kapsam ve Gereksinimler

**Problem.** Küçük oto servislerinde işler deftere yazılır: aracın geçmişi kaybolur, hangi işin bittiği belirsizdir, dönemsel iş hacmi elle ve hatalı hesaplanır (aynı iş iki kez sayılabilir veya yanlış güne yazılabilir).

**Çözüm.** Her araç ziyareti için To-Do listesi benzeri iş başlıkları (başlık, not, tutar). İş ✓ ile tamamlanınca tutar kilitlenir ve **tamamlandığı güne** yazılır. Önceki fikir olan Q-Task (kurumsal görev ve SLA takibi), kapsamı ders süresine göre geniş bulunduğu için bırakıldı.

**Kapsam.** Güvenli giriş, müşteri ve araç kaydı, servis ziyareti, ziyarette birden çok iş, ✓ ile idempotent tamamlama ve aynı gün geri alma, araç geçmişi, dönemsel brüt iş bedeli raporu. **Kapsam dışı:** stok, parça satırları, çoklu rol, audit log, ödeme ve fatura, çoklu şube, bildirimler.

**Kullanım durumları (aktör: işletme sorumlusu; ustalar sisteme girmez).** UC-01 giriş ve güvenli oturum · UC-02 müşteri kaydı ve arama · UC-03 araç kaydı ve plaka tekilliği · UC-04 servis ziyareti açılışı · UC-05 iş listesi yönetimi · UC-06 idempotent tamamlama · UC-07 araç geçmişi ve dönemsel rapor.

**Temel iş kuralları.**

| Kod | Kural (son sürüm) |
| :--- | :--- |
| BR-01 | Tutar tam TL girilir (1 – 1.000.000 TL); kuruş cinsinden tamsayı saklanır (v1.4, KR-08) |
| BR-02, BR-03 | ✓ ile iş `DONE` olur, tutar kilitlenir; ikinci ✓ hiçbir şeyi değiştirmez (idempotent) |
| BR-04 | ✓ yalnızca aynı İstanbul günü içinde geri alınabilir |
| BR-05, BR-06 | Rapor yalnızca `DONE` işleri `completed_at` gününe göre toplar; gün sınırları `Europe/Istanbul` |
| BR-07 | Plaka boşluksuz, Latin büyük harfle normalize edilir ve tekildir |
| BR-08, BR-09 | Müşteri, araç ve ziyaret silinmez; telefon isteğe bağlıdır ve biçimi tanımlıdır |

**Fonksiyonel olmayan gereksinimler (ISO/IEC 25010).**

| Kod | Özellik | Hedef | Son durum |
| :--- | :--- | :--- | :--- |
| NFR-01 | Bakım yapılabilirlik | McCabe ≤ 10, hedef ≤ 7 | En yüksek 6 (Bölüm 5.3) |
| NFR-02 | Test edilebilirlik | `ui` hariç kapsama ≥ %80 | %100 satır + dal |
| NFR-03 | Güvenlik | Argon2id; bandit yüksek bulgu 0 | Karşılandı (CI) |
| NFR-04 | Güvenilirlik | Çift ✓ tek tamamlama | TC-18, TC-23 ile doğrulandı |
| NFR-05 | Doğruluk | Para hesabında yuvarlama hatası 0 | Tamsayı kuruş, `float` yasak |
| NFR-06 | Kullanılabilirlik | Ana akış yardımsız ≤ 3 dk | 2 dk 20 sn (TC-31) |
| NFR-07 | Gizlilik | Yalnızca sentetik veri | Tüm test ve demolarda uydurma veri |
| NFR-08 | Güvenlik | Hatada yalnızca genel mesaj | TC-30 ile doğrulandı |

**Teknoloji.** Python 3.11+, Streamlit, SQLAlchemy 2 ve SQLite, argon2-cffi; kalite araçları pytest ve pytest-cov, black, flake8, bandit, pip-audit, radon ve xenon; GitHub Actions. Çalışma biçimi Scrumban; her değişiklik PR ile.

---

## 3. Faz 2 — Gözden Geçirme, Kalite Kapıları, Test Planı ve Risk

### 3.1. Faz 1'in Gözden Geçirilmesi

Faz 1 gereksinimleri ISO/IEC/IEEE 29148'in iyi gereksinim özelliklerine (tek anlamlı, doğrulanabilir, tutarlı, eksiksiz, izlenebilir) göre incelendi. **14 bulgunun 14'ü kabul edildi** ve Faz 1 Raporu v1.3'e işlendi. Önemli örnekler:

- **RV-01 (Yüksek):** “✓ geri al → düzenle → ✓” yoluyla geçmiş günün raporu sessizce değişebiliyordu → geri alma aynı günle sınırlandı (BR-04).
- **RV-02:** Plaka Türkçe kurallarla büyük harfe çevriliyordu (`34 abi 12` → `34ABİ12`) → Latin büyük harf (BR-07).
- **RV-07 (Yüksek):** Hesap oluşturma ve kaba kuvvet savunması tanımsızdı → kurulum betiği ve 3 hatadan sonra CAPTCHA.
- **RV-08:** Aktör belirsizdi → tek kullanıcı “işletme sorumlusu”.
- **RV-14:** Streamlit hata ayrıntılarını tarayıcıda gösteriyordu → yeni NFR-08.

### 3.2. Kalite Kapıları

| Kapı | Ne zaman | Geçiş koşulu |
| :--- | :--- | :--- |
| KK-1 Gereksinim | Faz kapanışında | Yüksek bulgular kapalı; her FR bir UC'ye ve teste bağlı |
| KK-2 Birleştirme | Her PR | CI'daki 7 kontrol (biçim, stil, bandit, pip-audit, McCabe, test, kapsama) + PR'ı açan dışında 1 onay |
| KK-3 Test tamamlama | Faz 4 sonu | Planlanan testler çalışmış; kritik açık hata 0; McCabe yorumlanmış |
| KK-4 Devreye alma | Yayından önce | KK-3 geçilmiş; `main` yeşil; depoda gizli bilgi yok |

### 3.3. Test Planı

ISO/IEC/IEEE 29119-3 yapısında; **32 test senaryosu** (TC-01 – TC-32). Teknikler: sınır değer (tutar 0 / 1 / 1.000.000 / 1.000.001 TL), denklik sınıfları, karar tablosu (✓ geri alma, K1 – K4), durum geçişi (`TODO` ↔ `DONE`), hata tahmini (iki sekmeden aynı anda ✓, veritabanına erişilemezken işlem). Seviyeler: birim, entegrasyon, sistem (arayüz) ve kullanıcı kabul (TC-31). Her test bellekte temiz veritabanı ve sabit saatle çalışır.

### 3.4. Güvenlik Risk Değerlendirmesi

STRIDE ile 14 tehdit; olasılık × etki puanları Kerem Erden tarafından verildi ve ekipçe onaylandı. Beş yüksek risk ve önlemleri:

| Risk | Tehdit | Önlem | Doğrulama |
| :--- | :--- | :--- | :--- |
| R-01 | Parola tahmini | Argon2id; 3 hatadan sonra CAPTCHA; hatalı denemelerin gösterilmesi | TC-01, TC-04 |
| R-04 | SQL enjeksiyonu | Yalnızca ORM / parametreli sorgu | bandit, test |
| R-07 | Çift ✓ ile çift sayım | Koşullu tek `UPDATE`; toplam sorgudan hesaplanır | TC-18, TC-23 |
| R-08 | Hata ekranında yığın izi | `showErrorDetails = "none"`; genel mesaj | TC-30 |
| R-12 | Açığı olan bağımlılık | Sabit sürümler; CI'da pip-audit | CI (ilk taramada Pillow'da 67 açık bulundu, sürüm yükseltildi) |

---

## 4. Faz 3 — Tasarım, Kodlama ve Kod İncelemesi

### 4.1. Faz 2'nin Gözden Geçirilmesi

En önemli bulgu **RV3-01:** Faz 2'de öngörülen `client.showErrorDetails = false` ayarı, kullanılan Streamlit sürümünde “yığın izini göster” anlamına geliyordu; değer `"none"` yapıldı. Ayrıca hatalı deneme kaydına kullanıcı adı eklendi (RV3-03), her use case için GitHub issue açıldı (RV3-04) ve paket kurulabilir hâle getirildi (RV3-05).

### 4.2. Mimari Seçenekler ve Karar

Üç seçenek karşılaştırıldı: A) Streamlit ile katmanlı monolit, B) FastAPI + Streamlit istemci, C) Django. **A seçildi:** tek kullanıcılı, tek şubeli bir uygulamada ayrı bir API katmanı güvenlik yüzeyini ve test yükünü artırır ama fayda sağlamaz.

| ADR | Karar | Gerekçe |
| :--- | :--- | :--- |
| 001 | `ui → services → repository` katmanları; `services` Streamlit içe aktarmaz | İş kuralları arayüzden bağımsız test edilir |
| 002 | SQLite + SQLAlchemy ORM; sınırlar hem serviste hem CHECK kısıtlarında | SQL enjeksiyonu; SQLite tür ve uzunluk dayatmaz (KR-01, KR-02) |
| 003 | Para tamsayı kuruş; girişte tam TL ve `Decimal` | Yuvarlama hatası 0 |
| 004 | Zaman UTC saklanır; servisler saati `Clock` nesnesinden alır | İstanbul gün sınırları testte sabit saatle sınanır |
| 005 | Tamamlama tek koşullu `UPDATE ... WHERE status = 'TODO'`; toplam sorgudan | Çift tıklamada çift sayım olmaz |
| 006 | Argon2id; 3 hatadan sonra kendi ürettiğimiz CAPTCHA; sayım yalnızca kullanıcı adına göre | Var olan ve olmayan kullanıcı aynı davranır |
| 007 | Kullanıcıya yalnızca iş kuralı hataları gösterilir; diğerlerinde genel mesaj | İç yapı bilgisi sızmaz |
| 008 | `main` korumalı; PR + CI + 1 onay; kural yöneticilere de uygulanır | İncelenmemiş kod girmez |

### 4.3. Kodlama ve Kod İncelemesi

Kod, iskelet (#10) ve her use case için ayrı PR'larla geliştirildi (#11 – #20). İnceleme bulguları KR numarasıyla kaydedildi; her bulgu önce yerelde yeniden üretildi, sonra düzeltildi ve mümkünse bir testle sabitlendi.

| Bulgu | Konu | Sonuç |
| :--- | :--- | :--- |
| KR-01, KR-02 | SQLite `1600.5` tutarını ve 300 karakterlik adı kabul ediyordu | CHECK kısıtları ve testler |
| KR-03 | Hatalı deneme sayısı iki yerde tutuluyordu | Tek kaynak: `LoginAttempt` |
| KR-04 | Ayarlar çalışma dizinine bağlıydı | Yol ve ayar koddan verildi |
| KR-05, KR-06 | Araç geçmişi kabul ölçütü test edilmiyordu; N+1 sorgu | Test eklendi; sorgu sayısı ölçülüp düzeltildi |
| KR-08 | Kuruşlu tutar alanı kullanımda anlamsızdı | Ekip kararıyla tam TL (BR-01 v1.4) |
| KR-09 | Plaka araması yalnızca tam plakayla çalışıyordu | Başı yazılınca öneren seçim listesi |

KR-08 ve KR-09, ekibin uygulamayı ekran paylaşımıyla yaklaşık 30 dakika birlikte kullanmasıyla bulundu.

**Mutasyon testi.** Testlerin gücünü ölçmek için kod 22 yerden bilerek bozuldu. İlk turda 4 mutant yaşadı; üçü için test eklendi, biri eşdeğer mutant olarak gerekçelendirildi.

**Süreç hatası ve düzeltmesi.** #18 ve #19'un ilk onayları, YZ'nin önceden hazırladığı ve gerçekleşmemiş doğrulamalar içeren metinlerle verildi (#18'de PR açıldıktan 51 saniye sonra). Ekip bunu fark etti, ortak incelemeyi yaptı, onay metinlerini kendi gözlemleriyle güncelledi ve kalıcı bir kural koydu: YZ inceleme veya onay metni yazmaz; önce inceleyene kontrol listesi verir, yalnızca inceleyenin aktardığı gözlemleri metne dönüştürür.

---

## 5. Faz 4 — Test, Ölçüm ve Devreye Alma

### 5.1. Faz 3'ün Gözden Geçirilmesi

| No | Konu | Durum |
| :--- | :--- | :--- |
| RV4-01 | Eski veritabanı dosyasına yeni kısıtlar işlenmiyor | Kapandı: README'ye not |
| RV4-02 | Boşluksuz plaka yazımı (`06b`) eşleşmiyor şüphesi | Kapandı: TC-31'de `54tty` ile çalıştı |
| RV4-03 | CAPTCHA biçiminin UC-01 sahibiyle teyidi | Açık `[ekip]` |
| RV4-04 | Mutasyon testi kaynağının birincil kaynaktan doğrulanması | Açık `[ekip]` |
| RV4-05 | Hedefi (7) aşan iki fonksiyon | Kapandı (5.3) |

### 5.2. Testler

32 senaryonun 31'i otomatik testlerle, TC-31 elle (kullanıcı kabul testi) karşılandı. Son hâlde **258 test** geçiyor; `ui` hariç satır ve dal kapsaması **%100**. Arayüz testleri Streamlit AppTest ile; kritik akışlar ayrıca gerçek tarayıcıda (Playwright) denendi.

- **Beyaz kutu:** iç yapı bilinerek yazılan testler; örneğin parolanın veritabanında Argon2id özeti olarak saklanması (TC-02), ziyaret açılış zamanının sabit saatle sınanması (TC-13).
- **Kara kutu:** yalnızca girdi ve çıktı; örneğin 22 Ekim'de açılıp 23 Ekim'de ✓'lenen işin yalnızca 23 Ekim toplamında görünmesi (TC-24).
- **Hata tahmini:** iki ayrı veritabanı bağlantısından aynı anda ✓ (TC-23); veritabanına erişilemezken işlem (TC-30).

**Kullanıcı kabul testi (TC-31, 14.11.2026).** Uygulamayı daha önce görmemiş, ekip dışından bir katılımcı; gözlemciler Ahmet Selim Dostabakan ve Mehmet Ünsalan. Katılımcı kendi uydurduğu verilerle müşteri → araç → ziyaret → iş → ✓ → haftalık rapor akışını **2 dk 20 sn'de, yardımsız** tamamladı (ölçüt ≤ 3 dk). Test yerel kurulumda yapıldı. Sınırlılık: tek katılımcı, oto servis işletmecisi değil.

**Bulunan ve düzeltilen hatalar.**

| No | Hata | Bulan | Düzeltme |
| :--- | :--- | :--- | :--- |
| H4-01 | Veritabanına erişilemezken kullanıcı İngilizce teknik bir hata kutusu görüyordu. Güvenlik gereği zaten karşılanıyordu (yığın izi tarayıcıya gitmiyordu); sorun kullanılabilirlikti. | TC-30 testi | Türkçe genel mesaj; ayrıntı yalnızca sunucu günlüğüne |
| H4-02 | Başka müşteri seçilince düzenleme formu önceki müşteride kalıyordu; “Güncelle” seçili müşterinin kaydının üzerine önceki müşterinin bilgisini yazıyordu. | TC-31 katılımcısı | Form alanlarının anahtarı müşteri kimliğine bağlandı; önce hatayı yeniden üreten iki test yazıldı |

H4-02, %100 kapsamaya rağmen bulundu: kapsama bir satırın çalıştığını gösterir, sonucun doğru olduğunu göstermez.

### 5.3. McCabe Karmaşıklığı

McCabe döngüsel karmaşıklığı (CC) = karar noktası sayısı + 1; bir fonksiyonun tüm yollarını sınamak için gereken en az test sayısının alt sınırıdır. `radon cc` ile tüm `src/` ölçüldü; eşik CI'da `xenon` ile zorunlu.

| Ölçüm | 13.11.2026 (Faz 4 Raporu) | 14.11.2026 (son hâl) |
| :--- | :---: | :---: |
| Fonksiyon sayısı | 94 | 96 |
| En yüksek CC | 6 | 6 |
| CC 6 – 10 (radon B) | 6 | 6 |
| CC > 10 | 0 | 0 |

İki fonksiyon hedefi (7) aşıyordu ve bölündü: `customers_page.render` 9 → 3 (üç yardımcıya), `search_customers` 8 → 6 (telefon eşleşmesi ayrı fonksiyona). Bedeli: ilgili modülün bakım yapılabilirlik indeksi 45,9 → 44,6'ya düştü ve toplam karar noktası sayısı azalmadı, fonksiyonlara dağıldı; kazanç, her parçanın tek başına anlaşılıp test edilebilmesidir. **Yorum:** Karmaşıklık arayüzde ve girdi doğrulamada toplanıyor; en kritik kurallar (idempotent tamamlama, dönemsel rapor) ortalama CC 1,7 – 1,8 ile düşük, çünkü durum denetimi dallanma yerine veritabanı koşuluna taşındı (ADR-005). CC 6 olan `to_kurus` gibi fonksiyonlar sırayla uygulanan iş kurallarıdır; bölmek kuralları dağıtır.

### 5.4. Devreye Alma

Uygulama **Streamlit Community Cloud**'da yayında: <https://servisflow.streamlit.app/> (14.11.2026, yayınlayan Kerem Erden). Yerel kurulum da desteklenir (Ek B).

- **Engel 1:** Bulut, depoyu paket olarak kurmuyor → kök dizinde `streamlit_app.py` giriş noktası.
- **Engel 2:** Bulutta kabuk yok, hesap betiği çalıştırılamıyor → sorumlu hesabı bulutun sır (Secrets) ayarından oluşturuluyor; parola depoda yok.
- **Engel 3:** GitHub organizasyonunda üçüncü taraf uygulama kısıtlaması açıktı → kısıtlama kaldırılmadı, yalnızca Streamlit'e erişim verildi (en az yetki ilkesi).
- **Bilinen kısıt:** Bulutta veritabanı kalıcı değil; yeniden başlatmada kayıtlar silinir, hesap sırlardan yeniden oluşur. Adres herkese açık; yalnızca uydurma veri girilir.

Doğrulama: canlı sitede giriş ekranı ve sırlardaki hesapla giriş doğrulandı; tam akış ekip ve TC-31 katılımcısı tarafından canlı sitede denendi.

---

## 6. Faz 5 — Son Durum, Demo ve Öğrenilenler

### 6.1. Son Durum

| Gösterge | Değer |
| :--- | :--- |
| Uygulanan use case | 7 / 7 |
| Otomatik test | 258, hepsi geçiyor |
| Kapsama (`ui` hariç, satır + dal) | %100 |
| En yüksek McCabe | 6 (sınır 10, hedef 7) |
| bandit yüksek bulgu / pip-audit açık | 0 / 0 |
| Birleştirilen PR | #10 – #26 ve sonrası, her biri CI + 1 onayla |
| Açık maddeler | RV4-03, RV4-04 `[ekip]` |

### 6.2. Demo

Demo canlı sitede, uydurma verilerle yapılır: hatalı parola mesajı → müşteri ve araç ekleme (aynı plakanın farklı yazımla reddedilmesi) → iki müşteri arasında geçiş (H4-02 düzeltmesi) → plaka listesinden araç seçimi ve ziyaret → iki iş ve ✓ → günlük rapor. `[ekip: demo tarihi ve gözlemler]`

### 6.3. Ekip Olarak Çıkarılan Dersler

Kayıtlı olaylardan çıkan ortak dersler:

1. **Kapsama doğruluk değildir.** %100 kapsamaya rağmen H4-02'yi ekip dışı bir kullanıcı buldu; mutasyon testi ve kullanıcı testi, kapsamanın göremediğini gösterdi.
2. **Belgeye değil sürüme bak.** Faz 2'deki `showErrorDetails = false` kararı, kurulu sürümün belgesine bakılınca yanlış çıktı (RV3-01); SQLite'ın tür ve uzunluk dayatmadığı canlı denemeyle görüldü (KR-01, KR-02).
3. **Onay, yapılan doğrulamayı kaydeder.** Hazır onay metinleri gerçekleşmemiş doğrulamalar içerdi; kural değişti, artık onay metni yalnızca inceleyenin gördüğünü yazar.
4. **Kodu yazan, kabul testini yapmamalı.** Plan geliştiricinin test yapması yönündeydi; ekip bunu ekip dışı katılımcıyla değiştirdi ve gerçek bir hata bulundu.
5. **Dar kapsam kaliteye zaman bıraktı.** Q-Task'tan ServisFlow'a geçiş, her kural için test, ölçüm ve inceleme yapılmasını mümkün kıldı.

### 6.4. Her Üyenin Öğrendikleri

Her üye kendi adıyla yazar (en fazla 3 – 4 cümle): ne öğrendi, hangi hatayı fark edip düzeltti, YZ desteği olmadan neyi açıklayabilir.

| Üye | Öğrendikleri |
| :--- | :--- |
| Ahmet Karavuş | `[kendisi yazacak]` |
| Alperhan Karşı | `[kendisi yazacak]` |
| Mehmet Kenan Dilberoğlu | `[kendisi yazacak]` |
| Ilgın Çutok | `[kendisi yazacak]` |
| Kerem Erden | `[kendisi yazacak]` |
| Mehmet Ünsalan | `[kendisi yazacak]` |
| Ahmet Selim Dostabakan | `[kendisi yazacak]` |

---

## 7. İş Paketi Bazında DIR Beyanları

Her YZ kullanımı İSTÜN DIR Rehberi V2'ye göre beyan edildi: D (Discover), I (Interact), R (Review) 1 – 5 tam sayı; **DIR = Floor(0,8 × D × I × R)**. Puanları ekip verdi. Gerekçeler ve kontrol listesi kodları ilgili faz raporlarının DIR bölümlerinde, ayrıca imzalı beyan formlarındadır.

| Faz | İş paketi | YZ aracı | D | I | R | DIR | Bant |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | İP-1 Faz 1 ilk taslak | OpenAI ChatGPT | 3 | 4 | 3 | 28 | 2 |
| 1 | İP-2 Kapsam daraltma ve Faz 1 v1.0 | Claude Code | 4 | 4 | 4 | 51 | 3 |
| 2 | İP-3 Faz 2 raporu ve kalite altyapısı | Claude Code | 4 | 4 | 4 | 51 | 3 |
| 3 | İP-4 Kod iskeleti ve ADR'ler | Claude Code | 4 | 4 | 4 | 51 | 3 |
| 3 | İP-5 UC-07 servis katmanı | Claude Code | 4 | 4 | 4 | 51 | 3 |
| 3 | İP-6 UC-01 – UC-06 servis katmanı | Claude Code | 4 | 4 | 4 | 51 | 3 |
| 3 | İP-7 Arayüz, KR-08, KR-09 | Claude Code, Playwright | 4 | 5 | 4 | 64 | 4 |
| 3 | İP-8 Kod incelemesi desteği | Claude Code, Claude Cowork | 4 | 3 | 4 | 38 | 3 |
| 4 | İP-9 McCabe ölçümü ve iyileştirme | Claude Code | 4 | 4 | 4 | 51 | 3 |
| 4 | İP-10 Devreye alma, TC-31, H4-02 | Claude Code | 4 | 4 | 5 | 64 | 4 |
| 5 | İP-11 Final rapor taslağı | Claude Code | `[ekip]` | `[ekip]` | `[ekip]` | | |

**Gelişim.** İlk paket (İP-1) negatif yönergeler ve kabul kriterleri tanımlanmadığı için Bant 2'de kaldı. Sonraki paketlerde kurallar `CLAUDE.md`'de kalıcı hâle getirildi (kapsam genişletilmez, yapılmamış doğrulama yazılmaz, puanları ve kararları ekip verir, kişisel veri verilmez) ve paketler Bant 3 – 4'e çıktı. En düşük Faz 3 paketi (İP-8), hatalı onay metni yönteminin ekipçe fark edilip değiştirilmesiyle 38'de kaldı. Hiçbir pakette farklı modeller karşılaştırılmadı (B4 eksik).

**İP-11 (bu rapor).** Rapor taslağı Claude Code ile, Faz 1 – 4 raporlarından özetlenerek hazırlandı; yeni iddia eklenmedi, bilinmeyen yerler `[ekip]` bırakıldı. Puanlar ekip gözden geçirmesinden sonra verilecek. Beyan formlarında ayrıca önerilen kullanım alanları (Faz 3: 3.6, 3.7; Faz 4: 4.2, 4.5, 4.6) ekip onayından sonra bu tabloya eklenecek `[ekip]`.

---

## 8. Referanslar

1. ISO/IEC 25010:2023, *Systems and software engineering — SQuaRE — Product quality model*.
2. ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering*.
3. ISO/IEC/IEEE 29119-3:2021, *Software and systems engineering — Software testing — Part 3: Test documentation*.
4. McCabe, T. J. (1976). A Complexity Measure. *IEEE Transactions on Software Engineering, SE-2*(4), 308–320.
5. DeMillo, R. A., Lipton, R. J., & Sayward, F. G. (1978). Hints on Test Data Selection: Help for the Practicing Programmer. *Computer, 11*(4), 34–41. `[ekip: birincil kaynaktan doğrulanacak, RV4-04]`
6. Shostack, A. (2014). *Threat Modeling: Designing for Security.* Wiley.
7. Galin, D. (2004). *Software Quality Assurance: From Theory to Implementation.* Addison-Wesley.
8. Nygard, M. (2011). *Documenting Architecture Decisions.*
9. OWASP Top 10 (2021); OWASP Password Storage Cheat Sheet; OWASP Authentication Cheat Sheet.
10. Belgeler: Streamlit (`client.showErrorDetails`, `st.selectbox`, AppTest, Community Cloud), SQLAlchemy 2.1, argon2-cffi, pip-audit (PyPA), Radon, Playwright.
11. Bağrıyanık, S. *Yükseköğretimde Sorumlu Yapay Zekâ Kullanımına Dair Bir Öneri: DIR Çerçevesi* (İSTÜN DIR Rehberi V2) ve *Yapay Zekâ Kullanım Beyanı Şablonu*, ders materyali.
12. YAZ401 Yazılım Kalite Standartları ders yönergesi ve izlencesi, İstanbul Sağlık ve Teknoloji Üniversitesi, 2026–2027 Güz.
13. Q-Task: Kurumsal Görev, Kalite ve SLA Takip Sistemi, <https://github.com/alperhank/q-task-quality-system> (erişim: 22.10.2026).
14. Yapay zekâ araçları: OpenAI ChatGPT (22.10.2026); Anthropic Claude — Claude Code ve Claude Cowork (24.10 – 14.11.2026). Kullanım Bölüm 7'de beyan edilmiştir.

---

## Ekler

### Ek A. Bağlantılar

- Depo: <https://github.com/servisflow/servisflow>
- Canlı sürüm: <https://servisflow.streamlit.app/> (yalnızca uydurma veri; veriler kalıcı değildir)
- Faz raporları: [Faz 1](Faz1_Raporu.md) · [Faz 2](Faz2_Raporu.md) · [Faz 3](Faz3_Raporu.md) · [Faz 4](Faz4_Raporu.md)
- CI: GitHub Actions, `.github/workflows/ci.yml` (`kalite` işi)

### Ek B. Kurulum, Çalıştırma ve Test Talimatı

Gereksinim: Python 3.11 veya üstü, Git.

```bash
git clone https://github.com/servisflow/servisflow.git
cd servisflow
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
python -m servisflow.create_owner      # sorumlu hesabı (bir kez; parola en az 8 karakter)
streamlit run src/servisflow/ui/app.py # tarayıcıda http://localhost:8501
```

Testler ve kalite kontrolleri (CI ile aynı):

```bash
pytest --cov
black --check src tests streamlit_app.py
flake8 src tests streamlit_app.py
bandit -r src --severity-level high
pip-audit -r requirements.txt -r requirements-dev.txt
xenon src --max-absolute B --max-modules B --max-average A
```

Notlar: Windows'ta `pip install -e .` *WinError 145* verirse `python -m pip install --upgrade pip setuptools` sonrası tekrarlanır; eski bir `servisflow.db` dosyası `no such column` hatası verirse silinir (README).

### Ek C. Değişiklik Geçmişi

| Sürüm | Tarih | Değişiklik |
| :--- | :--- | :--- |
| v0.1 | 14.11.2026 | Faz 1 – 4 raporlarından ilk taslak; ekip ve öğrenme bölümleri `[ekip]` |
