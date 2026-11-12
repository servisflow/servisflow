# PROJE RAPORU: FAZ 3 ÇIKTILARI — Kalite Odaklı Tasarım ve Geliştirme

- **Proje Adı:** ServisFlow — Araç Bazlı Servis İş Takibi ve Dönemsel Brüt İş Bedeli Raporlama
- **Ders:** Yazılım Kalite Standartları (YAZ401)
- **Doküman Durumu:** Taslak v0.2 — yedi use case ve arayüz birleşti; DIR puanları ekip onayında · `main` dal koruması 12.11.2026'da açıldı
- **Başlangıç:** 12.11.2026 · **Teslim:** Hafta 9 (izlence)
- **Koordinasyon:** Üye 5 (Kerem Erden, Yazılım Mimarı) · Üye 7 (Ahmet Selim Dostabakan, QA) · Üye 6 (Mehmet Ünsalan)

| Yönerge maddesi | Bu belgedeki karşılığı |
| :--- | :--- |
| i. Faz 2 çıktılarının gözden geçirilmesi ve iyileştirilmesi | Bölüm 1 |
| ii. Mimari ve tasarım seçeneklerinin oluşturulması, teknik kararların verilmesi, gözden geçirilmesi ve iyileştirilmesi | Bölüm 2 |
| iii. Kodlama ve kod gözden geçirmelerinin yapılıp iyileştirilmesi | Bölüm 3 |

---

## 1. Faz 2 Çıktılarının Gözden Geçirilmesi (Faz 3 - i)

Faz 2 çıktıları, kod iskeleti yazılırken gerçek araçlarla karşılaştırılarak gözden geçirildi.

| No | Yer | Bulgu | Önem | Karar |
| :--- | :--- | :--- | :---: | :--- |
| **RV3-01** | Faz 2 RV-14, R-08 | Hata ayrıntılarını gizlemek için `client.showErrorDetails = false` öngörülmüştü. Streamlit 1.67 belgelerine göre `false` artık **“stacktrace”** anlamına geliyor ve yığın izi tarayıcıda **gösterilmeye devam ediyor**. Önlem kâğıt üstünde doğru görünüp gerçekte işe yaramayacaktı. | Yüksek | Doğru değer `"none"`. `.streamlit/config.toml` dosyasına bu değer yazıldı; Faz 2 raporu v1.2'de düzeltildi. TC-30 bu ayarı doğrulayacak. |
| **RV3-02** | Faz 2 KK-2, 2.3 | PR şablonu ekip kararıyla kaldırıldı. | Düşük | KK-2: CI yeşil + 1 onay + ilgili issue. İnceleme noktaları rehber olarak kaldı (Faz 2 v1.1). |
| **RV3-03** | Veri modeli, RV-07 | `LoginAttempt` tablosunda denemenin hangi kullanıcı adıyla yapıldığı tutulmuyordu; var olmayan bir kullanıcı adıyla yapılan denemeler (R-02) kaydedilemiyordu. | Orta | `LoginAttempt.username` alanı eklendi. |
| **RV3-04** | KK-2 | KK-2 “ilgili issue bağlı” şartını koyuyor, ancak depoda hiç issue yoktu. | Orta | İskelet (#2) ve her use case (#3 – #9) için birer issue açıldı (Bölüm 3.3). |
| **RV3-05** | Kurulum, KK-4 | Paket kurulabilir tanımlanmamıştı; Streamlit uygulaması `servisflow` paketini içe aktaramıyordu. | Orta | `pyproject.toml`'a derleme sistemi eklendi; kurulum `pip install -e .` ile yapılır. |
| **RV3-06** | Faz 2 sunumu | Öğretim elemanının Faz 2 sunumundaki geri bildirimi | — | `[Ekip tarafından eklenecek]` |

---

## 2. Mimari ve Tasarım Kararları (Faz 3 - ii)

### 2.1. Mimari Seçenekler

| Kriter | A. Streamlit, katmanlı monolit | B. FastAPI (REST) + Streamlit istemci | C. Django (MVC + yönetim paneli) |
| :--- | :--- | :--- | :--- |
| Ekibin bilgi düzeyi | Yüksek (yalnızca Python + Streamlit) | Orta (API tasarımı, iki ayrı uygulama) | Düşük (yeni çatı, şablon dili) |
| Test edilebilirlik | İş kuralları `services` katmanında, arayüzden bağımsız test edilir | Yüksek; ancak API katmanı için ayrıca test gerekir | Yüksek; ancak çatıya bağlı test altyapısı öğrenilmeli |
| Güvenlik yüzeyi | Tek süreç, dışa açık API yok | API kimlik doğrulaması, CORS ve token yönetimi eklenir | Hazır kimlik doğrulama var; ancak geniş yapılandırma yüzeyi |
| Kapsama uygunluk | Tek kullanıcı, tek şube için yeterli | Çok istemcili senaryolar için fazla | Yönetim paneli ve çoklu rol özellikleri kullanılmayacak |
| Geliştirme süresi (vize haftaları) | En kısa | Uzun | Uzun |
| **Karar** | **Seçildi** | Reddedildi | Reddedildi |

**Gerekçe:** Tek kullanıcılı, tek şubeli bir uygulamada ayrı bir API katmanı güvenlik yüzeyini ve test yükünü artırır ama bir fayda sağlamaz. Faz 1'de planlanan FastAPI bu nedenle v0.4'te çıkarılmıştı; Faz 3'te karar seçeneklerle birlikte yeniden değerlendirildi ve korundu.

### 2.2. Mimari Karar Kayıtları (ADR)

Karar kayıtları Nygard'ın ADR biçiminin sadeleştirilmiş hâliyle yazılmıştır: bağlam, karar, reddedilen alternatif, sonuç.

**ADR-001 — Katmanlı monolit.**
*Bağlam:* İş kurallarının arayüzden bağımsız test edilmesi gerekiyor (NFR-02). *Karar:* `ui → services → repository` katmanları; `ui` yalnızca `services`'i çağırır, `services` Streamlit'i içe aktarmaz, `repository` iş kuralı içermez. *Reddedilen:* İş kurallarını Streamlit sayfalarına yazmak (test edilemez). *Sonuç:* Kapsama ölçümü `ui` hariç yapılır.

**ADR-002 — SQLite + SQLAlchemy 2 ORM.**
*Bağlam:* Tek şube, tek kullanıcı; SQL enjeksiyonu yüksek risk (R-04). *Karar:* SQLite dosyası, SQLAlchemy ORM ile parametreli erişim; yabancı anahtar denetimi bağlantı başında açılır. Veritabanı kısıtları (tekil plaka, tutar aralığı, durum–tamamlanma tutarlılığı) iş kurallarının **son savunma hattı**dır. *Reddedilen:* Elle yazılmış SQL (enjeksiyon riski), PostgreSQL (kurulum yükü). *Sonuç:* Testler bellekte SQLite ile çalışır. *İnceleme sonrası ek (PR #10):* SQLite sütun türünü ve `String(n)` uzunluğunu dayatmaz; tutarın tamsayı olması (`typeof(amount_kurus) = 'integer'`), metin uzunlukları, boş başlık/ad ve telefon biçimi açık CHECK kısıtlarıyla yazıldı. Veritabanı adresi çalışma dizininden bağımsızdır: varsayılan olarak proje kökündeki `servisflow.db`, `SERVISFLOW_DB_URL` ortam değişkeniyle değiştirilebilir.

**ADR-003 — Para tamsayı kuruş.**
*Bağlam:* Ondalık sayılarda yuvarlama hatası (NFR-05). *Karar:* Tutar `amount_kurus` tamsayısı. Arayüzden **tam TL** alınır (KR-08 sonrası BR-01 v1.4) ve `Decimal` ile kuruşa çevrilir. Veritabanında 100 – 100.000.000 kuruş aralığı ve 100'ün katı olma kısıtı vardır. Saklamanın kuruş olarak kalması, kuruş ileride gerekirse şema değişikliğini önler. *Reddedilen:* `float` (0,1 + 0,2 ≠ 0,3).

**ADR-004 — Zaman: UTC saklama ve saat sağlayıcısı.**
*Bağlam:* Gün sınırları İstanbul saatine göre (BR-06) ve testte gece yarısı sınanmalı (TC-26). *Karar:* Tüm zamanlar saat dilimli olarak UTC saklanır (`UTCDateTime` türü saat dilimsiz zamanı reddeder). Servisler zamanı dışarıdan verilen bir `Clock` nesnesinden alır; testlerde `FixedClock` kullanılır. Dönem sınırları İstanbul saatiyle hesaplanıp UTC'ye çevrilir. *Reddedilen:* Doğrudan `datetime.now()` (test edilemez), yerel saat saklama (yaz saati ve taşınabilirlik sorunları).

**ADR-005 — İdempotent tamamlama ve sorgudan toplam.**
*Bağlam:* Çift tıklamada çift sayım (R-07). *Karar:* Tamamlama tek koşullu güncellemedir: `UPDATE ... SET status='DONE', completed_at=:now WHERE id=:id AND status='TODO'`. Etkilenen satır 0 ise işlem değişiklik yapmadan başarılı sayılır. Dönem toplamı bir sayaçta tutulmaz, her seferinde sorgudan hesaplanır. *Reddedilen:* Önce oku sonra yaz (iki istek arasında yarış durumu), toplam sayacı (geri almada tutarsızlık).

**ADR-006 — Kimlik doğrulama.**
*Karar:* Parolalar `argon2-cffi` ile Argon2id özetlenir. 3 hatalı girişten sonra CAPTCHA istenir; CAPTCHA uygulamanın kendi sunucusunda üretilir. Hatalı deneme sayısı yalnızca `LoginAttempt` tablosundan, kullanıcı adına göre hesaplanır; var olan ve olmayan kullanıcı adları aynı şekilde sayılır. Böylece CAPTCHA'nın çıkması kullanıcı adının var olup olmadığını sızdırmaz (R-02; PR #10 incelemesi). CAPTCHA biçimi: sunucuda `secrets` ile üretilen iki sayının toplama sorusu (görsel metin, ek kütüphane ve erişilebilirlik sorunu getirdiği için seçilmedi). Olmayan kullanıcı adında da aynı süre harcansın diye parola sahte bir Argon2 özetiyle karşılaştırılır. *Reddedilen:* Dış CAPTCHA servisi (veri üçüncü tarafa gider, internet gerekir).

**ADR-007 — Hata gösterimi.**
*Karar:* Servis katmanı yalnızca `ServisFlowError` türevlerini (`ValidationError`, `NotFoundError`, `ConflictError`) kullanıcıya gösterilebilir mesajla fırlatır; arayüz bunları kullanıcıya gösterir. Diğer tüm hatalarda tarayıcıda genel mesaj görünür (`showErrorDetails = "none"`, RV3-01), ayrıntı yalnızca sunucu konsoluna yazılır. Ayar hem `.streamlit/config.toml` dosyasında hem de uygulama kodunda (`st.set_option`) verilir; böylece uygulama proje kökü dışından başlatılsa da geçerlidir (PR #10 incelemesi).

**ADR-008 — Geliştirme süreci.**
*Karar:* `main` dalı korumalıdır: değişiklik yalnızca PR ile, CI'daki 7 kontrol geçtikten ve PR'ı açan dışında bir üyenin onayından sonra girer. Kural yöneticilere de uygulanır. Her use case kendi dalında (`uc-0X-...`) ve kendi PR'ında geliştirilir.

### 2.3. Servis Arayüz Sözleşmesi

Her use case sahibinin uygulayacağı fonksiyon imzaları aşağıdadır. Bu bir **öneridir**; sahibi, gerekçesini PR'a yazarak değiştirebilir. Tüm servisler `session` (SQLAlchemy oturumu) ve gerekiyorsa `clock` alır; hata durumunda Bölüm 2.2 ADR-007'deki hata türlerini fırlatır.

| UC | Modül | Fonksiyonlar |
| :--- | :--- | :--- |
| UC-01 | `services/auth.py` | `create_owner(session, username, password)` · `captcha_required(session, username) -> bool` · `authenticate(session, clock, username, password, captcha_passed) -> User` · `failed_attempts_since_last_login(session, username) -> list[datetime]` · `new_captcha() -> tuple[str, int]` · `check_captcha(expected, given) -> bool` |
| UC-02 | `services/customers.py` | `normalize_phone(raw) -> str \| None` · `create_customer(session, clock, full_name, phone=None) -> Customer` · `update_customer(session, customer_id, full_name, phone)` · `search_customers(session, text) -> list[Customer]` |
| UC-03 | `services/vehicles.py` | `normalize_plate(raw) -> str` · `register_vehicle(session, customer_id, plate, brand, model) -> Vehicle` · `find_vehicle_by_plate(session, plate) -> Vehicle` · `suggest_plates(session, text) -> list[Vehicle]` · `list_vehicles(session) -> list[Vehicle]` · `format_plate(plate) -> str` (KR-09) |
| UC-04 | `services/visits.py` | `open_visit(session, clock, vehicle_id, complaint=None) -> ServiceVisit` |
| UC-05 | `services/tasks.py` | `to_kurus(amount: Decimal) -> int` · `add_task(session, clock, visit_id, title, amount, note=None) -> ServiceTask` · `update_task(session, task_id, title, amount, note)` · `delete_task(session, task_id)` · `visit_totals(session, visit_id) -> tuple[int, int]` |
| UC-06 | `services/completion.py` | `complete_task(session, clock, task_id) -> ServiceTask` · `undo_completion(session, clock, task_id) -> ServiceTask` |
| UC-07 | `services/reports.py` | `period_bounds(kind, day) -> tuple[datetime, datetime]` · `gross_total(session, start, end) -> int` · `vehicle_history(session, vehicle_id) -> list[ServiceVisit]` |

### 2.4. Veri Modeli (uygulanan)

`src/servisflow/repository/models.py` dosyasında Faz 1 v1.3 veri modeli uygulanmıştır. Faz 2 sonrası değişiklikler: `User.last_login_at`, `LoginAttempt (username, attempted_at, success)` (RV3-03). `User.failed_attempts` alanı, aynı bilgiyi `LoginAttempt` ile iki yerde tuttuğu ve kullanıcı adı sızıntısına yol açabileceği için PR #10 incelemesinde kaldırıldı. Veritabanı kısıtları: `vehicle.plate_normalized` tekil ve 5–9 karakter, `service_task.amount_kurus` tamsayı ve 1 – 100.000.000 aralığında, `status = 'DONE'` ⇔ `completed_at` dolu, iş başlığı ve müşteri adı boş olamaz ve en fazla 100 karakter, açıklama ve not en fazla 500 karakter, telefon boş ya da 10 rakam.

---

## 3. Kodlama ve Kod Gözden Geçirmeleri (Faz 3 - iii)

### 3.1. Süreç

1. Use case için panodaki issue alınır, `In Progress` sütununa taşınır.
2. `main`'den `uc-0X-kisa-ad` dalı açılır; kod ve testleri aynı dalda yazılır.
3. PR açılır; açıklamada issue (`Closes #N`) ve karşılanan FR/UC yazılır, YZ kullanıldıysa belirtilir.
4. CI'daki 7 kontrol geçmelidir; PR'ı açan dışında bir üye Faz 2 Bölüm 2.3'teki noktalara göre inceler.
5. İnceleme yorumları düzeltilir, onaydan sonra birleştirilir. İnceleme bulguları Bölüm 3.4'e işlenir.

### 3.2. İskelet (İlk PR)

| Bileşen | Dosya | Durum |
| :--- | :--- | :--- |
| Hata türleri | `services/errors.py` | Tamam |
| Saat sağlayıcısı | `services/clock.py` | Tamam, 4 test |
| Veritabanı bağlantısı | `repository/db.py` | Tamam |
| Veri modeli ve kısıtlar | `repository/models.py` | Tamam, 11 test |
| Uygulama girişi | `ui/app.py` | Tamam; Streamlit `AppTest` ile hatasız açıldığı doğrulandı |
| Hata gösterimi ayarı | `.streamlit/config.toml` | Tamam (RV3-01) |

İskelet ölçümleri (12.11.2026, yerel): 17 test geçti · `ui` hariç satır + dal kapsaması %100 · ortalama McCabe 1,37 (A) · bandit yüksek bulgu 0 · pip-audit açık 0.

### 3.3. Use Case Geliştirme Planı

| UC | Sahibi | Issue | Dal | Durum |
| :--- | :--- | :--- | :--- | :--- |
| UC-01 | Ahmet Karavuş | #3 | `uc-01-oturum` | Servis katmanı #15 ile birleşti (Kerem Erden, YZ destekli); giriş ekranı ayrı PR'da |
| UC-02 | Alperhan Karşı | #4 | `uc-02-musteri` | Servis katmanı #15 ile birleşti (Kerem Erden, YZ destekli); arayüz UC-01 sonrası |
| UC-03 | Mehmet Kenan Dilberoğlu | #5 | `uc-03-arac` | Servis katmanı #15 ile birleşti (Kerem Erden, YZ destekli); arayüz UC-01 sonrası |
| UC-04 | Ilgın Çutok | #6 | `uc-04-ziyaret` | Servis katmanı #15 ile birleşti (Kerem Erden, YZ destekli); arayüz UC-01 sonrası |
| UC-05 | Kerem Erden | #7 | `uc-05-is-listesi` | Servis katmanı #15 ile birleşti; arayüz UC-01 sonrası |
| UC-06 | Mehmet Ünsalan | #8 | `uc-06-tamamlama` | Servis katmanı #16 ile birleşti (Kerem Erden, YZ destekli); arayüz UC-01 sonrası |
| UC-07 | Ahmet Selim Dostabakan | #9 | `uc-07-rapor` | Servis katmanı #11 ile birleşti; KR-05 – KR-07 düzeltmeleri ayrı PR'la; arayüz UC-01 sonrası |

### 3.4. Kod İnceleme Kayıtları

| PR | Konu | Yazan | İnceleyen | Bulgular | Düzeltme |
| :--- | :--- | :--- | :--- | :--- | :--- |
| #10 | İskelet (#2) | Ahmet Selim Dostabakan (YZ destekli) | Kerem Erden | Onaylandı; birleştirmeyi engellemeyen 4 bulgu (KR-01 – KR-04, aşağıda) | Düzeltme: PR #12 |
| #11 | UC-07 servis katmanı (#9) | Ahmet Selim Dostabakan (YZ destekli) | Kerem Erden | Olumlu; birleştirmeyi engellemeyen 3 öneri (KR-05 – KR-07, aşağıda) | Düzeltme commit'i #11 birleştikten sonra dala geldiği için main'e girmedi; PR #17 ile taşındı. **Süreç notu:** Birleştirmeyi inceleyen yaptı; sonraki PR'larda birleştirmeyi PR'ı açan yapıyor. |
| #12 | KR-01 – KR-04 düzeltmeleri | Ahmet Selim Dostabakan (YZ destekli) | Kerem Erden | Onaylandı ve birleştirildi. **Süreç notu:** Onay metni önce yanlışlıkla UC-07 (#11) incelemesini taşıyordu; #12'nin kendi incelemesiyle değiştirildi ve PR'a düzenleme notu eklendi. Engellemeyen notlar: KR-02 test sayısı 13 (14 değil), `create_all` var olan veritabanına kısıt eklemez, SQLite `trim()` yalnızca boşluğu kırpar, telefon kısıtı “5 ile başlar” kuralını denetlemez. | Test sayısı bu tabloda düzeltildi; `trim` sorunu #15'te `str.strip()` ile giderildi; telefon kuralı servis katmanında (#15). Eski veritabanı notu açık. |
| #13 | `CLAUDE.md` (Claude oturumları için proje kılavuzu) | Ahmet Selim Dostabakan (YZ destekli) | Kerem Erden | Onaylandı. Bulgu: `pip install -e .` ile oluşan `*.egg-info/` `.gitignore`'da yok. **Süreç notu:** Onay metni neyin kontrol edildiğini belirtmiyordu. | PR #14 |
| #14 | `.gitignore`: `*.egg-info/` | Kerem Erden (YZ destekli) | Ahmet Selim Dostabakan | Onaylandı | — |
| #15 | UC-01 – UC-05 servis katmanı (#3 – #7) | Kerem Erden (YZ destekli) | Ahmet Selim Dostabakan | İlk inceleme onay değil yorum olarak gönderildi ve yalnızca UC-05'i kapsıyordu (**süreç notu**). Son haldeki onay: 178 test, plaka ve telefon normalizasyonu elle denendi, CAPTCHA sayımı ve DONE kilidi kodda incelendi. Engellemeyen not: ADR-006'daki CAPTCHA biçimi UC-01 sahibiyle ekipçe teyit edilmeli. | CAPTCHA biçimi teyidi açık |
| #16 | UC-06 servis katmanı (#8) | Kerem Erden (YZ destekli) | Ahmet Selim Dostabakan | Onaylandı: 188 test; koşullu UPDATE, İstanbul gün sınırı ve K1 – K4 karar tablosu incelendi. | — |
| #17 | KR-05 – KR-07'nin main'e taşınması, inceleme kayıtları | Ahmet Selim Dostabakan (kod), Kerem Erden (YZ destekli; rapor) | Ahmet Selim Dostabakan | Onaylandı: kodun değişmediği ve 3.4 kayıtları kontrol edildi. | — |
| #18 | UC-01 arayüzü: giriş ekranı | Kerem Erden (YZ destekli) | Ahmet Selim Dostabakan | **Süreç notu:** Onay, PR açıldıktan 51 saniye sonra ve CI bitmeden verildi; metinde yazan elle denemeler bu sürede yapılamazdı. İçerik denetimi 13.11.2026'daki ortak incelemede yapıldı (aşağıda). | KR-08, KR-09 |
| #19 | Arayüz: müşteri/araç, servis ve işler, rapor | Kerem Erden (YZ destekli) | Ahmet Selim Dostabakan | **Süreç notu:** Onay metni, doldurulması gereken şablonun boş hâli (köşeli parantezlerle) olarak gönderildi; onay anında içerik denetimi yapılmadı. İçerik denetimi 13.11.2026'daki ortak incelemede yapıldı (aşağıda). | KR-08, KR-09 |

**PR #10 inceleme bulguları (Kerem Erden).** İnceleyen, iskeleti yerelde çalıştırıp kalite kapılarını kendisi tekrarladı ve `showErrorDetails` değerini kurulu Streamlit'in kaynağından doğruladı. Bulgular yazar tarafından yerelde yeniden üretilerek doğrulandı:

| No | Bulgu | Etki | Düzeltme |
| :--- | :--- | :--- | :--- |
| **KR-01** | SQLite tür dayatmıyor: `amount_kurus = 1600.5` kabul edildi ve `real` olarak saklandı. | ADR-003 ve NFR-05'in “son savunma hattı” iddiası geçersizdi. | `typeof(amount_kurus) = 'integer'` kısıtı ve testi. |
| **KR-02** | `String(n)` uzunlukları uygulanmıyor: 300 karakterlik ad, 21 karakterlik plaka ve boş başlık kaydedildi. | R-11'deki uzunluk sınırları yalnızca servis katmanına kalıyordu. | Ad, başlık, plaka, telefon, açıklama ve not için CHECK kısıtları ve 13 test. |
| **KR-03** | Hatalı giriş sayısı hem `User.failed_attempts` hem `LoginAttempt` içinde tutuluyor; `failed_attempts` kullanılırsa CAPTCHA yalnızca gerçek kullanıcı adında çıkar. | Kullanıcı adının var olup olmadığı sızar (R-02). | `failed_attempts` kaldırıldı; sayım kuralı ADR-006'ya yazıldı. |
| **KR-04** | Veritabanı yolu ve `.streamlit/config.toml` çalışma dizinine bağlı. | Uygulama proje kökü dışından başlatılırsa NFR-08 devre dışı kalır, veritabanı başka yerde oluşur. | Veritabanı yolu proje köküne sabitlendi (ortam değişkeniyle değiştirilebilir); hata ayarı koddan da veriliyor. Uygulama başka bir dizinden başlatılarak doğrulandı. |

**PR #11 inceleme bulguları (Kerem Erden).** İnceleyen UC-07'yi yerelde çalıştırdı, kalite kapılarını tekrarladı ve test planında olmayan bir durumu da denedi: yıl geçişindeki hafta (31.12.2026 → 28.12.2026 – 04.01.2027), doğru çalışıyor.

| No | Bulgu | Etki | Düzeltme |
| :--- | :--- | :--- | :--- |
| **KR-05** | FR-07'nin “eski ziyaretteki işler yeni ziyaretle karışmaz” kabul ölçütü testte doğrulanmıyor; TC-28 yalnızca ziyaret sırasına bakıyor. | Bir kabul ölçütü testsiz kalıyordu (izlenebilirlik). | Her ziyaretin yalnızca kendi işlerini içerdiğini doğrulayan test eklendi. |
| **KR-06** | `vehicle_history` sonrasında her ziyaretin işlerine erişmek ziyaret başına ayrı sorgu üretiyor (N+1): 3 ziyarette 5 sorgu. | Bu ölçekte performans sorunu değil; ziyaret sayısıyla büyür. | Yazar ölçümü yineledi (3 ziyarette 5 sorgu). İşler `selectinload` ile tek ek sorguda yükleniyor. Ziyaret sayısından bağımsız olarak 3 sorgu olduğunu doğrulayan test eklendi; düzeltme geri alındığında test 7 sorgu görüp başarısız oluyor. |
| **KR-07** | Bu PR'ın inceleme kaydı rapora eklenmemiş. | Kod incelemesinin izlenebilirliği. | Bu tablo. |

**Ortak inceleme (13.11.2026, #18 ve #19 için).** Kerem Erden uygulamayı kendi bilgisayarında temiz kurulumla açtı (bu sırada Windows'ta `pip install -e .` *WinError 145* hatası görüldü ve README'ye not düşüldü); Ahmet Selim Dostabakan ile ekran paylaşımında tüm testler ve uygulama çalıştırıldı, giriş, müşteri/araç, ziyaret, iş, ✓ ve rapor akışları birlikte denendi. Bulgular:

| No | Bulgu | Etki | Düzeltme |
| :--- | :--- | :--- | :--- |
| **KR-08** | Tutar alanının kuruşlu olması kullanımda anlamsız: alan `1200.00` gösteriyor ve +/- düğmeleri 0,01 TL artırıyor; oto serviste işçilik ve parça fiyatları tam TL. | Kullanılabilirlik; gereksiz giriş hatası riski. | Ekip kararıyla BR-01 v1.4: tutar **tam TL** (1 – 1.000.000 TL). Saklama kuruş olarak kaldı (ADR-003); veritabanına “100'ün katı” kısıtı eklendi. Alan 1 TL adımlı, ekranda `1.200 TL`. TC-15 ve TC-16 güncellendi. |
| **KR-09** | Plakayla arama yalnızca tam plakayla çalışıyor; `06 b` yazıp Enter'a basınca `06 BUM 00` bulunmalı. | Kullanılabilirlik (TC-31 süresi). | **Servis ve işler:** plaka kutusu, yazdıkça süzülen bir seçim listesi oldu (arama motorlarındaki öneri listesi gibi). Etiketler boşluklu plakayla başlar (`06 BUM 00`, `format_plate`) ve süzgeç “baştan eşleşme” kipindedir; `06` yazınca tüm 06'lı plakalar, `06 b` yazınca `06 BA…` ve `06 BUM…` önerilir. Seçim yapılmadan araç bilgileri açılmaz. Streamlit'in varsayılan bulanık süzgeci gerçek tarayıcıda denendi ve reddedildi (`06 b` için `06 BA 1234`'ü göstermedi, `34 bjk` için sonuç vermedi). **Müşteriler ve araçlar:** `suggest_plates` ile plaka başından eşleşen araçlar listelenir (en az 2 karakter, en fazla 10, `%` ve `_` joker çalışmaz). |

**#15 ve #16 inceleme metinleri hakkında.** İki onayın metin taslağı YZ ile hazırlandı; taslak, inceleyenin çalıştıracağı komutları ve bakacağı kod yerlerini içeriyordu. Kontrollerin yapıldığı inceleyenin beyanına dayanır.

---

## 4. Faz 3 İçin DIR Beyanı (Taslak — puanlar ekip onayında)

Faz 3'te YZ, kodlamanın ve kod incelemesinin her aşamasında kullanıldı. Kullanım beş iş paketine ayrıldı. **Puanları ekip verir** (CLAUDE.md); aşağıdaki gerekçeler gerçekleşen işlemlere dayanır, yapılmayanlar “eksik” olarak yazılmıştır. Her paketin sonundaki “YZ önerisi”, ekibin değerlendirmesi için bir başlangıç noktasıdır.

Ortak bağlam (tüm paketler, A1 – A4, A6): YZ'ye onaylı Faz 1 ve Faz 2 raporları, iş kuralları (BR), test senaryoları (TC), ADR'ler ve kalite eşikleri verildi; `CLAUDE.md` ile kurallar kalıcı hâle getirildi: kapsam genişletilmeyecek, yapılmamış doğrulama yapılmış gibi yazılmayacak, puanları ve kararları YZ vermeyecek, kişisel veri depoya girmeyecek. YZ ajan olarak çalıştı (dosya düzenleme, test çalıştırma, dal ve PR açma); `main` korumalı olduğu için her değişiklik bir insanın onayıyla birleşti (A9, B6).

### 4.1. İş Paketi 4 — Kod İskeleti ve Mimari Karar Kayıtları

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 12.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Code, ajan) |
| **İlgili üyeler** | Ahmet Selim Dostabakan (yönlendirme); inceleme: Kerem Erden (#10) |
| **Görevin YZ kullanım sınırı** | Yeşil (kod geliştirme, teknik dokümantasyon). Mimari kararların kabulü ve kod incelemesi ekibe aittir. |
| **Üretilen çıktı** | Veri modeli, saat sağlayıcısı, veritabanı katmanı, hata türleri, ilk testler; ADR-001 – ADR-008; servis sözleşmesi (2.3); dal koruması (#10, #12) |

| Boyut | Puan | Kontrol listesi dayanaklı gerekçe |
| :--- | :---: | :--- |
| **D** | `[ekip]` | Ortak bağlam (A1 – A4, A6). Mimari seçenekler (2.1) ve reddedilen alternatifler ADR'lerde yazıldı (A8: karar ekipte). |
| **I** | `[ekip]` | YZ, Streamlit'in kurulu sürüm belgesine bakarak Faz 2'deki yanlış `showErrorDetails` değerini buldu (RV3-01). İnceleyen dört bulgu (KR-01 – KR-04) çıkardı; bulgular önce yerelde yeniden üretildi, sonra düzeltildi (B1, B3). Farklı modeller karşılaştırılmadı (B4 eksik). |
| **R** | `[ekip]` | İnceleyen iskeleti kendi ortamında çalıştırıp kalite kapılarını tekrarladı ve SQLite'ın tür ile uzunluk dayatmadığını canlı denemeyle gösterdi (C3, C4). Her bulgu için test eklendi. İnceleme yorumunun taslağı YZ ile hazırlandı (İP-8). |

*YZ önerisi:* D 4 · I 4 · R 4 → 51.

### 4.2. İş Paketi 5 — UC-07 Servis Katmanı ve `CLAUDE.md`

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 12.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Code, ajan) |
| **İlgili üyeler** | Ahmet Selim Dostabakan (yönlendirme); inceleme: Kerem Erden (#11, #13, #17) |
| **Görevin YZ kullanım sınırı** | Yeşil |
| **Üretilen çıktı** | `services/reports.py` ve testleri (TC-24 – TC-29); `CLAUDE.md` |

| Boyut | Puan | Kontrol listesi dayanaklı gerekçe |
| :--- | :---: | :--- |
| **D** | `[ekip]` | Ortak bağlam; gün sınırları ve yarı açık aralık ADR-004/005 ile önceden tanımlıydı (A2, A6). |
| **I** | `[ekip]` | İnceleyenin önerileri (KR-05 – KR-07) uygulandı; N+1 bulgusu önce ölçülerek yeniden üretildi (B1, B2). |
| **R** | `[ekip]` | İnceleyen test planında olmayan bir durumu (yıl geçişindeki hafta) ayrıca denedi (C3, C4). **Eksik / süreç notu:** Düzeltme commit'i #11 birleştikten sonra geldiği için main'e girmedi; durum fark edilip #17 ile taşındı (3.4). |

*YZ önerisi:* D 4 · I 4 · R 4 → 51.

### 4.3. İş Paketi 6 — UC-01 – UC-06 Servis Katmanı

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 12.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Code, ajan) |
| **İlgili üyeler** | Kerem Erden (yönlendirme); inceleme: Ahmet Selim Dostabakan (#15, #16). UC-01 – UC-04 ve UC-06'nın sahipleri bu işe katılmadı (bkz. Not). |
| **Görevin YZ kullanım sınırı** | Yeşil. CAPTCHA biçimi (ADR-006 açık konusu) YZ tarafından önerildi; UC-01 sahibiyle teyidi açık. |
| **Üretilen çıktı** | `auth.py`, `customers.py`, `vehicles.py`, `visits.py`, `tasks.py`, `completion.py`, kurulum betiği ve testleri (şu an 162 test; #15 ve #16 birleştiğinde 142) |

| Boyut | Puan | Kontrol listesi dayanaklı gerekçe |
| :--- | :---: | :--- |
| **D** | `[ekip]` | Ortak bağlam; her UC için BR ve TC'ler kabul ölçütü olarak verildi (A2, A6). Güvenlik beklentileri (R-01, R-02, KR-03) açıkça tanımlıydı (A4, A9). |
| **I** | `[ekip]` | Testler koddan önce yazıldı ve kırmızı görüldü. **Mutasyon testi:** Kod 22 yerden kasten bozuldu; ilk turda 4 mutant yaşadı (float yasağı, `user is not None` koruması, TC-32 üst sınırı, bir eşdeğer mutant). Üçü için test eklendi, eşdeğer mutantın gerekçesi yazıldı (B1, B3). YZ'nin kendi rapor metnine yazdığı ekip içi ayrım ifadesi push'tan önce düzeltildi (B3, gizlilik). B4 eksik. |
| **R** | `[ekip]` | Kalite kapıları yerelde ve CI'da; TC-23 iki gerçek veritabanı bağlantısıyla sınandı (C3). **Eksik / süreç notu:** #15'in ilk incelemesi PR açıklamasının yeniden yazımıydı; ikinci onay ve #16 onayı, YZ'nin hazırladığı metinle verildi (İP-8). Kodun içerik denetimi insan tarafından ortak incelemede (13.11.2026) uygulama üzerinden yapıldı; satır satır kod okuması sınırlı kaldı (C4 kısmen, C6 kısmen: üyeler kendi UC dosyalarını sözlü savunma için okuyor). |

*YZ önerisi:* D 4 · I 4 · R 3 → 38.

**Not (dengeli katkı):** UC-01 – UC-04 sahipleri GitHub organizasyonunda olmadığı ve UC-06 sahibi bu dönemde ulaşılamadığı için servis katmanları Kerem Erden yönlendirmesiyle yazıldı. Arayüz ve kullanıcı kabul testi (TC-31) sahiplerinin katkısına açıktır.

### 4.4. İş Paketi 7 — Arayüz (Streamlit ekranları) ve KR-08, KR-09

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 12 – 13.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Code, ajan; gerçek tarayıcı denemesi için Playwright) |
| **İlgili üyeler** | Kerem Erden (yönlendirme); inceleme: Ahmet Selim Dostabakan (#18, #19, #20); ortak inceleme: Kerem Erden ve Ahmet Selim Dostabakan |
| **Görevin YZ kullanım sınırı** | Yeşil. BR-01 değişikliği (tam TL) ekip kararıdır. |
| **Üretilen çıktı** | Giriş, müşteri/araç, servis ve işler, rapor ekranları; 34 arayüz testi (AppTest) |

| Boyut | Puan | Kontrol listesi dayanaklı gerekçe |
| :--- | :---: | :--- |
| **D** | `[ekip]` | Ortak bağlam; ekranların yalnızca servisleri çağırması (ADR-001) ve hata gösterimi (ADR-007) sınır olarak verildi (A2, A4). |
| **I** | `[ekip]` | YZ'nin ilk taslağındaki iki hata testlerle bulundu ve düzeltildi (başarısız girişin çift sayılması, CAPTCHA alanının geç çıkması). Ortak incelemede ekip iki kullanılabilirlik bulgusu çıkardı (KR-08, KR-09) ve kuruşun kaldırılması kararını verdi (B3, A8). Plaka listesi için YZ'nin ilk çözümü (tam eşleşme, ardından bulanık süzgeç) ekip örneğiyle (`06 b`) reddedildi; süzgeç seçenekleri gerçek tarayıcıda karşılaştırıldı (B2, B4 kısmen: model değil yöntem karşılaştırması). |
| **R** | `[ekip]` | Her ekran AppTest ile ve gerçek tarayıcıda uçtan uca çalıştırıldı (C3). **Ortak inceleme (13.11.2026):** temiz kurulum, tüm testler, uygulama ekran paylaşımında birlikte denendi; Windows'taki kurulum hatası bulunup belgelendi (C4). **Eksik / süreç notu:** #18 ve #19 onayları içerik denetimi olmadan verildi (3.4); içerik denetimi ortak incelemede yapıldı. |

*YZ önerisi:* D 4 · I 5 · R 3 → 48. (I için 5'in dayanağı: ekip örneğiyle YZ çözümünün iki kez reddedilmesi ve alternatiflerin karşılaştırılması; ekip 4'ü de seçebilir.)

### 4.5. İş Paketi 8 — Kod İncelemesi Desteği

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 12 – 13.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Cowork oturumu: Kerem Erden; Claude Code oturumu: Kerem Erden) |
| **İlgili üyeler** | Kerem Erden (#10, #11 incelemeleri); Ahmet Selim Dostabakan (#15 – #20 onayları) |
| **Görevin YZ kullanım sınırı** | Sarı (koşullu). İnceleme yorumunun taslağı YZ'den alınabilir; yorumdaki her doğrulama iddiası inceleyenin kendi yaptığı işleme dayanmalıdır. |
| **Üretilen çıktı** | #10 ve #11 inceleme yorumlarının taslağı; #15, #16, #17, #18, #20 onay metinlerinin taslağı ve inceleyenin çalıştıracağı komut listesi; #19 için doldurulacak şablon |

| Boyut | Puan | Kontrol listesi dayanaklı gerekçe |
| :--- | :---: | :--- |
| **D** | `[ekip]` | YZ'den, yorumda yalnızca inceleyenin gerçekten yaptığı işlemlerin yazılması istendi; taslaklarla birlikte çalıştırılacak komutlar verildi (A4, A6). |
| **I** | `[ekip]` | #10 ve #11'de YZ'nin bulguları inceleyen tarafından kendi ortamında tekrarlandı (B1). #18 – #19 sonrasında süreç değiştirildi: hazır metin yerine kontrol listesi, ardından doğrulanabilir şablon verildi (B3). |
| **R** | `[ekip]` | **Eksik:** #18'de onay, PR açıldıktan 51 saniye sonra ve CI bitmeden gönderildi; #19'da şablon doldurulmadan gönderildi. Bu iki onayın metni gerçekleşmemiş doğrulamaları içeriyor. Durum 3.4'te süreç notu olarak kaydedildi; içerik denetimi 13.11.2026'daki ortak incelemede yapıldı ve iki bulgu üretti (KR-08, KR-09). #20 onayında inceleyen kendi cümlesini ekledi. |

*YZ önerisi:* D 3 · I 3 · R 2 → 14 (Bant 2). Bu paket, Faz 3'ün en zayıf noktasıdır ve öyle beyan edilmelidir; yüksek puan yasak kullanımı uygun hâle getirmediği gibi, düşük puan da dürüst beyanın değerini azaltmaz.

### 4.6. Özet Beyan Tablosu

| Üretilen artifact & YZ aracı | Kullanım amacı | İnsan müdahalesi ve düzeltme | Doğrulama yöntemi |
| :--- | :--- | :--- | :--- |
| İskelet, ADR / Claude Code | Veri modeli, katmanlar, mimari kayıtlar | KR-01 – KR-04 bulguları ve düzeltmeleri | İnceleyenin kendi ortamında çalıştırması, canlı deneme, CI |
| UC-07 servisi / Claude Code | Dönemsel rapor | KR-05 – KR-07 | Yıl geçişi haftasının ek denemesi, sorgu sayısı ölçümü |
| UC-01 – UC-06 servisleri / Claude Code | İş kuralları | Mutasyonla bulunan test açıkları kapatıldı; gizlilik ifadesi düzeltildi | 162 test, mutasyon testi, CI, ortak inceleme |
| Arayüz / Claude Code, Playwright | Ekranlar | KR-08 (tam TL, ekip kararı), KR-09 (plaka önerisi); iki hata testlerle düzeltildi | AppTest, gerçek tarayıcı, ekran paylaşımlı ortak inceleme |
| İnceleme yorumları / Claude Cowork, Claude Code | Yorum taslağı | Hazır metin yerine kontrol listesi ve şablona geçildi | **Kısmen:** #18, #19 onayları doğrulama içermiyor (3.4) |

## 5. Kaynaklar (Faz 3)

1. **Nygard, M. (2011).** *Documenting Architecture Decisions.* ADR biçimi.
2. **SQLAlchemy 2.1 belgeleri**, ORM bildirimsel eşleme ve `TypeDecorator`.
3. **Streamlit belgeleri**, yapılandırma seçeneği `client.showErrorDetails` ve `streamlit.testing.v1.AppTest`.
4. **argon2-cffi belgeleri** ve **OWASP Password Storage Cheat Sheet**.
5. **Anthropic Claude (Claude Code, Claude Cowork)**, 12 – 13.11.2026; kullanım Bölüm 4'te beyan edilmiştir.
6. **Streamlit belgeleri**, `st.selectbox` (`filter_mode`) ve `streamlit.testing.v1.AppTest`.
7. **Playwright belgeleri**, Chromium ile tarayıcı otomasyonu.
8. **DeMillo, R. A., Lipton, R. J., & Sayward, F. G. (1978).** Hints on Test Data Selection: Help for the Practicing Programmer. *Computer, 11*(4), 34–41. Mutasyon testinin kaynağı. `[ekip: birincil kaynaktan doğrulanacak, C1]`
