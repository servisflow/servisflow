# PROJE RAPORU: FAZ 3 ÇIKTILARI — Kalite Odaklı Tasarım ve Geliştirme

- **Proje Adı:** ServisFlow — Araç Bazlı Servis İş Takibi ve Dönemsel Brüt İş Bedeli Raporlama
- **Ders:** Yazılım Kalite Standartları (YAZ401)
- **Doküman Durumu:** Taslak v0.1 — geliştirme sürüyor · `main` dal koruması 12.11.2026'da açıldı
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
*Bağlam:* Ondalık sayılarda yuvarlama hatası (NFR-05). *Karar:* Tutar `amount_kurus` tamsayısı; arayüzden en fazla 2 ondalıklı değer alınır, `Decimal` ile kuruşa çevrilir. Veritabanında 1 – 100.000.000 kuruş aralığı kısıtı vardır. *Reddedilen:* `float` (0,1 + 0,2 ≠ 0,3).

**ADR-004 — Zaman: UTC saklama ve saat sağlayıcısı.**
*Bağlam:* Gün sınırları İstanbul saatine göre (BR-06) ve testte gece yarısı sınanmalı (TC-26). *Karar:* Tüm zamanlar saat dilimli olarak UTC saklanır (`UTCDateTime` türü saat dilimsiz zamanı reddeder). Servisler zamanı dışarıdan verilen bir `Clock` nesnesinden alır; testlerde `FixedClock` kullanılır. Dönem sınırları İstanbul saatiyle hesaplanıp UTC'ye çevrilir. *Reddedilen:* Doğrudan `datetime.now()` (test edilemez), yerel saat saklama (yaz saati ve taşınabilirlik sorunları).

**ADR-005 — İdempotent tamamlama ve sorgudan toplam.**
*Bağlam:* Çift tıklamada çift sayım (R-07). *Karar:* Tamamlama tek koşullu güncellemedir: `UPDATE ... SET status='DONE', completed_at=:now WHERE id=:id AND status='TODO'`. Etkilenen satır 0 ise işlem değişiklik yapmadan başarılı sayılır. Dönem toplamı bir sayaçta tutulmaz, her seferinde sorgudan hesaplanır. *Reddedilen:* Önce oku sonra yaz (iki istek arasında yarış durumu), toplam sayacı (geri almada tutarsızlık).

**ADR-006 — Kimlik doğrulama.**
*Karar:* Parolalar `argon2-cffi` ile Argon2id özetlenir. 3 hatalı girişten sonra CAPTCHA istenir; CAPTCHA uygulamanın kendi sunucusunda üretilir. Hatalı deneme sayısı yalnızca `LoginAttempt` tablosundan, kullanıcı adına göre hesaplanır; var olan ve olmayan kullanıcı adları aynı şekilde sayılır. Böylece CAPTCHA'nın çıkması kullanıcı adının var olup olmadığını sızdırmaz (R-02; PR #10 incelemesi). *Açık konu:* CAPTCHA'nın biçimi (görsel metin mi, basit işlem sorusu mu) UC-01 PR'ında Ahmet Karavuş tarafından seçilip bu kayda eklenecek. *Reddedilen:* Dış CAPTCHA servisi (veri üçüncü tarafa gider, internet gerekir).

**ADR-007 — Hata gösterimi.**
*Karar:* Servis katmanı yalnızca `ServisFlowError` türevlerini (`ValidationError`, `NotFoundError`, `ConflictError`) kullanıcıya gösterilebilir mesajla fırlatır; arayüz bunları kullanıcıya gösterir. Diğer tüm hatalarda tarayıcıda genel mesaj görünür (`showErrorDetails = "none"`, RV3-01), ayrıntı yalnızca sunucu konsoluna yazılır. Ayar hem `.streamlit/config.toml` dosyasında hem de uygulama kodunda (`st.set_option`) verilir; böylece uygulama proje kökü dışından başlatılsa da geçerlidir (PR #10 incelemesi).

**ADR-008 — Geliştirme süreci.**
*Karar:* `main` dalı korumalıdır: değişiklik yalnızca PR ile, CI'daki 7 kontrol geçtikten ve PR'ı açan dışında bir üyenin onayından sonra girer. Kural yöneticilere de uygulanır. Her use case kendi dalında (`uc-0X-...`) ve kendi PR'ında geliştirilir.

### 2.3. Servis Arayüz Sözleşmesi

Her use case sahibinin uygulayacağı fonksiyon imzaları aşağıdadır. Bu bir **öneridir**; sahibi, gerekçesini PR'a yazarak değiştirebilir. Tüm servisler `session` (SQLAlchemy oturumu) ve gerekiyorsa `clock` alır; hata durumunda Bölüm 2.2 ADR-007'deki hata türlerini fırlatır.

| UC | Modül | Fonksiyonlar |
| :--- | :--- | :--- |
| UC-01 | `services/auth.py` | `create_owner(session, username, password)` · `captcha_required(session, username) -> bool` · `authenticate(session, clock, username, password, captcha_passed) -> User` · `failed_attempts_since_last_login(session, username) -> list[datetime]` |
| UC-02 | `services/customers.py` | `normalize_phone(raw) -> str \| None` · `create_customer(session, clock, full_name, phone=None) -> Customer` · `update_customer(session, customer_id, full_name, phone)` · `search_customers(session, text) -> list[Customer]` |
| UC-03 | `services/vehicles.py` | `normalize_plate(raw) -> str` · `register_vehicle(session, customer_id, plate, brand, model) -> Vehicle` · `find_vehicle_by_plate(session, plate) -> Vehicle` |
| UC-04 | `services/visits.py` | `open_visit(session, clock, vehicle_id, complaint=None) -> ServiceVisit` |
| UC-05 | `services/tasks.py` | `to_kurus(amount: Decimal) -> int` · `add_task(session, clock, visit_id, title, amount, note=None) -> ServiceTask` · `update_task(session, task_id, title, amount, note)` · `delete_task(session, task_id)` |
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
| UC-01 | Ahmet Karavuş | #3 | `uc-01-oturum` | Bekliyor |
| UC-02 | Alperhan Karşı | #4 | `uc-02-musteri` | Bekliyor |
| UC-03 | Mehmet Kenan Dilberoğlu | #5 | `uc-03-arac` | Bekliyor |
| UC-04 | Ilgın Çutok | #6 | `uc-04-ziyaret` | Bekliyor |
| UC-05 | Kerem Erden | #7 | `uc-05-is-listesi` | Bekliyor |
| UC-06 | Mehmet Ünsalan | #8 | `uc-06-tamamlama` | Bekliyor |
| UC-07 | Ahmet Selim Dostabakan | #9 | `uc-07-rapor` | Bekliyor |

### 3.4. Kod İnceleme Kayıtları

| PR | Konu | Yazan | İnceleyen | Bulgular | Düzeltme |
| :--- | :--- | :--- | :--- | :--- | :--- |
| #10 | İskelet (#2) | Ahmet Selim Dostabakan (YZ destekli) | Kerem Erden | Onaylandı; birleştirmeyi engellemeyen 4 bulgu (KR-01 – KR-04, aşağıda) | Düzeltme PR'ı: `iskelet-inceleme-duzeltmeleri` |
| #11 | UC-07 servis katmanı (#9) | Ahmet Selim Dostabakan (YZ destekli) | Kerem Erden | `[İnceleme sürüyor]` | |

**PR #10 inceleme bulguları (Kerem Erden).** İnceleyen, iskeleti yerelde çalıştırıp kalite kapılarını kendisi tekrarladı ve `showErrorDetails` değerini kurulu Streamlit'in kaynağından doğruladı. Bulgular yazar tarafından yerelde yeniden üretilerek doğrulandı:

| No | Bulgu | Etki | Düzeltme |
| :--- | :--- | :--- | :--- |
| **KR-01** | SQLite tür dayatmıyor: `amount_kurus = 1600.5` kabul edildi ve `real` olarak saklandı. | ADR-003 ve NFR-05'in “son savunma hattı” iddiası geçersizdi. | `typeof(amount_kurus) = 'integer'` kısıtı ve testi. |
| **KR-02** | `String(n)` uzunlukları uygulanmıyor: 300 karakterlik ad, 21 karakterlik plaka ve boş başlık kaydedildi. | R-11'deki uzunluk sınırları yalnızca servis katmanına kalıyordu. | Ad, başlık, plaka, telefon, açıklama ve not için CHECK kısıtları ve 14 test. |
| **KR-03** | Hatalı giriş sayısı hem `User.failed_attempts` hem `LoginAttempt` içinde tutuluyor; `failed_attempts` kullanılırsa CAPTCHA yalnızca gerçek kullanıcı adında çıkar. | Kullanıcı adının var olup olmadığı sızar (R-02). | `failed_attempts` kaldırıldı; sayım kuralı ADR-006'ya yazıldı. |
| **KR-04** | Veritabanı yolu ve `.streamlit/config.toml` çalışma dizinine bağlı. | Uygulama proje kökü dışından başlatılırsa NFR-08 devre dışı kalır, veritabanı başka yerde oluşur. | Veritabanı yolu proje köküne sabitlendi (ortam değişkeniyle değiştirilebilir); hata ayarı koddan da veriliyor. Uygulama başka bir dizinden başlatılarak doğrulandı. |

---

## 4. Faz 3 İçin DIR Beyanı (Taslak)

### 4.1. İş Paketi 4 — Kod İskeleti ve Mimari Karar Kayıtları

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 12.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Code) |
| **İlgili üyeler** | Ahmet Selim Dostabakan (yönlendirme); inceleme: `[PR'ı inceleyen üye]` |
| **Görevin YZ kullanım sınırı** | Yeşil (kod geliştirme ve teknik dokümantasyon). Mimari kararların kabulü ve kod incelemesi ekibe aittir. |

**Süreç özeti:** YZ'ye onaylı Faz 1 ve Faz 2 raporları, veri modeli, kalite kapıları ve önceki mimari kararlar verildi. YZ veri modelini, saat sağlayıcısını, veritabanı katmanını ve testlerini yazdı; kalite kapılarını yerelde çalıştırdı; Streamlit yapılandırma seçeneğini kurulu sürümün kendi belgesinden kontrol ederek Faz 2'deki yanlış değeri (RV3-01) tespit etti.

| Boyut | Puan | Gerekçe |
| :--- | :---: | :--- |
| **D** | `[ekip]` | |
| **I** | `[ekip]` | |
| **R** | `[ekip]` | PR incelemesinden sonra yazılacak. |

---

## 5. Kaynaklar (Faz 3)

1. **Nygard, M. (2011).** *Documenting Architecture Decisions.* ADR biçimi.
2. **SQLAlchemy 2.1 belgeleri**, ORM bildirimsel eşleme ve `TypeDecorator`.
3. **Streamlit belgeleri**, yapılandırma seçeneği `client.showErrorDetails` ve `streamlit.testing.v1.AppTest`.
4. **argon2-cffi belgeleri** ve **OWASP Password Storage Cheat Sheet**.
5. **Anthropic Claude (Claude Code)**, 12.11.2026; kullanım Bölüm 4'te beyan edilmiştir.
