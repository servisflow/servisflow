# PROJE RAPORU: FAZ 4 ÇIKTILARI — Sistematik Test ve Kalite Güvencesi

- **Proje Adı:** ServisFlow — Araç Bazlı Servis İş Takibi ve Dönemsel Brüt İş Bedeli Raporlama
- **Ders:** Yazılım Kalite Standartları (YAZ401)
- **Doküman Durumu:** Taslak v0.5 — DIR İP-9 ve İP-10 ekip puanları işlendi; McCabe (#22) ve TC-30 (#23) tamam; TC-31 yürütüldü, bulunan H4-02 düzeltildi (#24); uygulama Streamlit Community Cloud'da yayında (14.11.2026)
- **Başlangıç:** 13.11.2026 · **Teslim:** Hafta 12 (izlence)

| Yönerge maddesi | Bu belgedeki karşılığı |
| :--- | :--- |
| i. Faz 3 çıktılarının gözden geçirilmesi ve iyileştirilmesi | Bölüm 1 |
| ii. Beyaz kutu, kara kutu, kullanıcı vb. testlerin yeterli seviyede yapılması ve hataların düzeltilmesi | Bölüm 2 |
| iii. Modül bazında McCabe karmaşıklığının hesaplanması ve yorumlanması | Bölüm 3 |
| iv. Devreye alım süreçlerinin gerçeklenmesi | Bölüm 4 |

---

## 1. Faz 3 Çıktılarının Gözden Geçirilmesi (Faz 4 - i)

Faz 3 Raporu (v0.3) ve kod üzerinde açık kalan maddeler:

| No | Konu | Kaynak | Durum |
| :--- | :--- | :--- | :--- |
| RV4-01 | `create_all` var olan veritabanına yeni kısıt eklemez; eski yerel `servisflow.db` dosyaları silinmeli. Göç (migration) aracı kapsam dışı. | #12, #20 incelemeleri | Açık; devreye alma talimatına yazılacak (Bölüm 4) |
| RV4-02 | Plaka seçim listesinde boşluksuz yazım (`06b`) eşleşmiyor; yalnızca boşluklu yazım (`06 b`) çalışıyor. | KR-09 | TC-31'de gözlenmedi: boşluksuz `54tty` yazımında araç listede çıktı. Kapandı. |
| RV4-03 | ADR-006 CAPTCHA biçimi (toplama sorusu) UC-01 sahibiyle teyit edilmedi. | #15 incelemesi | Açık |
| RV4-04 | Kaynakçadaki mutasyon testi makalesi birincil kaynaktan doğrulanmadı. | Faz 3, Kaynaklar | Açık (`[ekip]`) |
| RV4-05 | NFR-01 hedefini (McCabe ≤ 7) aşan iki fonksiyon. | Bu belge, Bölüm 3 | **Kapandı** (3.3) |

`[ekip: Faz 3 için hocanın geri bildirimi gelirse buraya eklenecek]`

---

## 2. Testler (Faz 4 - ii)

### 2.1. Test Senaryolarının Karşılanma Durumu

Faz 2 test planındaki 32 senaryonun 31'i otomatik testlerle (pytest; arayüz için Streamlit AppTest), TC-31 kullanıcı kabul testiyle karşılandı (2.2). Toplam 258 test (devreye alma testleri dahil, Bölüm 4.2), `ui` hariç satır ve dal kapsaması %100 (NFR-02).

| Teknik | Senaryolar | Otomatik test dosyaları |
| :--- | :--- | :--- |
| Denklik sınıfı | TC-01, TC-05, TC-06, TC-08 – TC-12, TC-16 | `test_auth`, `test_customers`, `test_vehicles`, `test_tasks`, `test_ui_customers`, `test_ui_visits` |
| Sınır değer | TC-04, TC-07, TC-15, TC-26, TC-29 | `test_auth`, `test_customers`, `test_tasks`, `test_reports`, `test_ui_login` |
| Durum geçişi ve karar tablosu | TC-17 – TC-21 | `test_tasks`, `test_completion`, `test_ui_visits` |
| Beyaz kutu | TC-02, TC-13 | `test_auth`, `test_visits` |
| Kara kutu (sistem) | TC-03, TC-14, TC-22, TC-24, TC-25, TC-27, TC-28, TC-32 | `test_ui_login`, `test_ui_customers`, `test_ui_reports`, `test_visits`, `test_reports`, `test_auth` |
| Hata tahmini | TC-23, TC-30 | `test_completion` (iki gerçek veritabanı bağlantısı), `test_ui_errors` (erişilemeyen veritabanı) |
| Kullanıcı kabul | TC-31 | Ekip dışı katılımcıyla elle yürütüldü (2.2) |

Ek olarak Faz 3'te mutasyon testi yapıldı (22 mutant; yaşayan 4 mutanttan 3'ü için test eklendi, 1'i eşdeğer) ve uygulama gerçek tarayıcıda (Playwright) uçtan uca çalıştırıldı.

### 2.2. Kullanıcı Kabul Testi (TC-31)

Senaryo: İşletme sahibi profilindeki bir kişi, ustanın bildirdiği bir işi baştan sona kaydeder (müşteri → araç → ziyaret → iş → ✓ → rapor). Ölçüt: ≤ 3 dakika, yardımsız (NFR-06).

**Plan (ekip kararı):**

- **Uygulayan:** Ekip dışından, sistemi daha önce görmemiş bir katılımcı (bir ekip üyesinin aile bireyi; kişisel bilgisi rapora yazılmaz). · **Yöneten:** Kerem Erden · **Gözlemciler:** Ahmet Selim Dostabakan, Mehmet Ünsalan · **Onaylayan:** Mehmet Ünsalan
- **Yürütme:** Katılımcıya yalnızca görev kağıdı verilir; ekip yol göstermez. Katılımcı yardım isterse ilgili adım “yardım gerekti” olarak işaretlenir ve süre durdurulmaz.
- **Ortam:** Bulutta yayınlanan sürüm (Bölüm 4); böylece test aynı zamanda devreye alınan sürümü doğrular.
- **Veri:** Yalnızca uydurma veriler (gerçek müşteri, plaka veya telefon girilmez).
- **Kısıt:** Katılımcı oto servis işletmecisi değildir; senaryodaki iş akışını (ziyaret, iş, ✓) gerçek bir işletme sahibi kadar tanımaz. Tek katılımcıyla yapılan test genellenemez.

**Görev kağıdı** (süre 2. adımda başlar, 8. adımda durur):

| # | Görev | Beklenen | Gözlenen | Yardım gerekti mi? |
| :---: | :--- | :--- | :--- | :---: |
| 1 | `sorumlu` hesabıyla giriş yap | Ana sayfa açılır | — | — |
| 2 | Yeni müşteri ekle: “Ali Deneme”, 05001112233 | “Müşteri kaydedildi.” | — | — |
| 3 | Bu müşteriye araç ekle: 34 ABC 123, Fiat Egea | “Araç kaydedildi.”, araç tabloda | — | — |
| 4 | Servis ve işler ekranında plaka listesine önce `34a`, sonra `34 a` yazıp aracı seç | `34 a` ile araç listede çıkar; `34a` sonucu not edilir (RV4-02) | — | — |
| 5 | Şikâyet “Frenden ses geliyor” ile ziyaret aç | “Ziyaret açıldı”, tarih sistemden gelir | — | — |
| 6 | İki iş ekle: “Ön balata değişimi” 1500 TL, “Yağ değişimi” 1200 TL | Açık işler: 2.700 TL | — | — |
| 7 | Balata işini ✓ ile tamamla | Açık 1.200 TL · Tamamlanan 1.500 TL | — | — |
| 8 | Rapor ekranında bugünün günlük toplamına bak | 1.500 TL | — | — |
| 9 | Çıkış yap | Giriş ekranına dönülür | — | — |

**Yürütme (14.11.2026):** Kerem Erden yönetti; Ahmet Selim Dostabakan ve Mehmet Ünsalan izledi.

- **Plandan sapmalar:**
  - Test yerel kurulumda yapıldı. Bulut yayını #24 birleşmeden yapılamadığı için ortam “bulut” olamadı.
  - Katılımcı, görev kağıdındaki veriler yerine kendi uydurduğu verilerle aynı akışı yürüttü. Bu yüzden yukarıdaki tablo satır satır doldurulmadı.
  - Veritabanında ekibin önceki denemelerinden kalan kayıtlar vardı.
- **Yürütülen akış:** Katılımcı test hesabıyla giriş yaptı ve sırasıyla şunları yaptı:
  - yeni müşteri ekledi (uydurma ad),
  - bu müşteriye 54 TTY 01 plakalı (uydurma) bir araç ekledi,
  - ziyaret açıp 200 TL tutarlı “silecek değişimi” işini ekledi,
  - işi ✓ ile tamamladı,
  - haftalık rapora baktı.
- **Rapor kontrolü:** Haftalık toplam 10.300 TL göründü. Bu tutar, rapor tablosundaki üç tamamlanmış işin toplamıdır: önceki denemelerden 100 TL ve 10.000 TL, katılımcının işinden 200 TL. Toplam ile satırlar tutarlı.
- **RV4-02 (`54tty` boşluksuz yazım):** Katılımcı denedi; araç listede çıktı.

**Sonuç:**

- **Süre:** 2 dk 20 sn.
- **Yardım:** İstenmedi.
- **NFR-06 ölçütü** (≤ 3 dakika, yardımsız): Karşılandı.
- **Bulgu:** H4-02 (2.3). Müşteri ekranında başka müşteri seçildiğinde düzenleme formu ilk seçilen müşterinin bilgilerinde kalıyordu.
- **Onay:** Mehmet Ünsalan, `[ekip: PR onayı]`.

### 2.3. Bulunan Hatalar ve Düzeltmeler

| No | Hata | Bulan | Düzeltme |
| :--- | :--- | :--- | :--- |
| H4-01 | TC-30: veritabanına erişilemezken uygulama Streamlit'in İngilizce hata kutusunu gösteriyordu (“This app has encountered an error… click on 'Manage app'”). Güvenlik gereği zaten karşılanıyordu: tarayıcıya yığın izi gitmiyordu (`stack_trace` boş), ayrıntı yalnızca sunucu konsolundaydı. Sorun kullanılabilirlikti: teknik, İngilizce ve uygulamayla ilgisiz bir yönerge. | TC-30 testi (önce kırmızı) | Veritabanı hataları (`SQLAlchemyError`) `main()` içinde yakalanıyor: kullanıcıya Türkçe genel mesaj, ayrıntı `logging` ile sunucu günlüğüne (ADR-007). İki test: giriş ekranı ve oturum açıkken işlem sırasında; ikisi de yığın izi, dosya yolu ve SQL ayrıntısının sayfada olmadığını denetler. |
| H4-02 | Müşteri ekranında başka bir müşteri seçildiğinde düzenleme formu (ad, telefon) ilk seçilen müşterinin bilgilerini göstermeye devam ediyordu. Bu durumda “Güncelle”ye basılırsa seçili müşterinin kaydının üzerine önceki müşterinin adı ve telefonu yazılıyordu (veri bozulması). Neden: Form alanlarının anahtarı sabitti (`duz_ad`). Streamlit sabit anahtarlı alanın değerini korur ve yeni `value` değerini yok sayar. | TC-31, ekip dışı katılımcı | Alan anahtarları müşteri kimliğini içeriyor (`duz_ad_<id>`); araç ekleme alanları da öyle (yarım kalan girdi başka müşteriye taşınmasın diye). Önce hatayı yeniden üreten iki test yazıldı (kırmızı): biri formun seçilen müşteriyi göstermesini, öteki “Güncelle”nin başka müşterinin bilgisini yazmamasını denetliyor. Düzeltmeden sonra ikisi de yeşil. Diğer ekranlardaki düzenleme formları zaten iş/ziyaret kimliğiyle anahtarlanmıştı. |
| `[ekip]` | | | |

### 2.4. Kod İnceleme Kayıtları (Faz 4)

| PR | Konu | Yazan | İnceleyen | Bulgular |
| :--- | :--- | :--- | :--- | :--- |
| #22 | McCabe ölçümü ve iyileştirme, rapor taslağı | Kerem Erden (YZ destekli) | Mehmet Ünsalan | Kerem Erden'in bilgisayarında ekran paylaşımıyla birlikte çalıştırıldı: 247 test geçti; `radon cc` en yüksek 6, `render` 9 → 3, `search_customers` 8 → 6. Onaylandı ve birleştirildi. |
| #23 | TC-30: veritabanına erişilemezken genel hata mesajı | Kerem Erden (YZ destekli) | Mehmet Ünsalan | Kerem Erden'in bilgisayarında ekran paylaşımıyla birlikte çalıştırıldı: `tests/test_ui_errors.py` 2 test geçti; veritabanı yolu bilerek bozulmuş uygulamada sayfada yalnızca Türkçe genel mesaj göründü, Traceback yoktu; hata ayrıntısı (SQLAlchemy `OperationalError`, e3q8) yalnızca terminalde göründü. Onaylandı ve birleştirildi. |
| #24 | Devreye alma (bulut), TC-31 sonucu, H4-02 düzeltmesi | Kerem Erden (YZ destekli) | Mehmet Ünsalan | Kerem Erden'in ekran paylaşımıyla, Ahmet Selim Dostabakan ile birlikte yönlendirilerek incelendi: `test_ui_customers` ve `test_ui_deploy` 14 test geçti; H4-02 uygulamada denendi: başka müşteri seçildiğinde form seçilen müşterinin bilgilerini gösteriyor, Murat seçiliyken “Güncelle” Ahmet'in kaydını bozmadı. Onaylandı ve birleştirildi. |

---

## 3. McCabe Karmaşıklığı (Faz 4 - iii)

### 3.1. Yöntem

McCabe döngüsel karmaşıklığı (CC), bir fonksiyondaki bağımsız yol sayısıdır: karar noktası sayısı (`if`, `for`, `while`, `and`, `or`, `except`, koşullu ifade) + 1. Bir fonksiyonun tüm yollarını sınamak için gereken en az test sayısının alt sınırıdır. Ölçüm `radon cc` ile tüm `src/` için yapıldı (arayüz dahil); bakım yapılabilirlik indeksi (MI) `radon mi` ile ölçüldü. Eşik NFR-01'dir: fonksiyon başına CC ≤ 10 (CI'da `xenon` ile zorunlu), hedef ≤ 7. Radon notları: A = 1–5, B = 6–10, C = 11–20.

### 3.2. Modül Bazında Sonuçlar (13.11.2026, iyileştirme sonrası)

| Modül | Fonksiyon | Ortalama CC | En yüksek CC |
| :--- | ---: | ---: | :--- |
| `ui/visits_page.py` | 9 | 3,44 | 6 (`_task_row`) |
| `services/customers.py` | 7 | 3,00 | 6 (`search_customers`) |
| `ui/app.py` | 7 | 2,86 | 6 (`login_page`) |
| `services/auth.py` | 10 | 2,80 | 6 (`create_owner`) |
| `services/tasks.py` | 9 | 2,67 | 6 (`to_kurus`) |
| `services/visits.py` | 1 | 5,00 | 5 (`open_visit`) |
| `services/vehicles.py` | 8 | 2,75 | 5 (`suggest_plates`) |
| `services/reports.py` | 7 | 1,71 | 5 (`_local_period`) |
| `ui/customers_page.py` | 9 | 2,78 | 4 (`_plate_search`) |
| `create_owner.py` | 1 | 3,00 | 3 |
| `ui/reports_page.py` | 2 | 2,50 | 3 |
| `repository/models.py` | 2 | 2,50 | 3 |
| `ui/common.py` | 9 | 1,89 | 3 |
| `services/completion.py` | 4 | 1,75 | 3 |
| `repository/db.py` | 4 | 1,50 | 2 |
| `services/clock.py` | 5 | 1,20 | 2 |
| **Toplam** | **94** | **2,52** | **6** |

Dağılım: 88 fonksiyon A (1–5), 6 fonksiyon B (6), C ve üstü yok. MI: 20 modülün tamamı A (en düşük `ui/customers_page.py` 44,6; en yüksek `services/clock.py` 85,7).

### 3.3. İyileştirme: Hedefi Aşan İki Fonksiyon

İlk ölçümde (13.11.2026) iki fonksiyon NFR-01 sınırının (10) altında ama hedefin (7) üstündeydi:

| Fonksiyon | Önce | Sonra | Neden yüksekti | Yapılan |
| :--- | :---: | :---: | :--- | :--- |
| `ui/customers_page.render` | 9 | 3 | Tek fonksiyon arama, müşteri tablosu, müşteri seçimi, düzenleme ve araç tablosunu birlikte çiziyordu (birden fazla sorumluluk). | Üç yardımcıya bölündü: `_customer_table`, `_select_customer`, `_vehicle_table` (her biri CC 3). |
| `services/customers.search_customers` | 8 | 6 | Ad ve telefon eşleşmesi tek liste ifadesinde art arda `or` / `and` koşullarıyla yazılmıştı; her koşul CC'yi 1 artırır. | Telefon eşleşmesi `_phone_matches` fonksiyonuna taşındı (CC 3). |

Davranışın değişmediği, değişiklik öncesi ve sonrası aynı 247 testin geçmesiyle doğrulandı. Fonksiyon başına ortalama CC 2,59 → 2,52 oldu. **Bedeli:** `ui/customers_page.py`'nin MI değeri 45,9 → 44,6'ya düştü; MI kod hacmini de hesaba kattığı için fonksiyon sayısının artması indeksi biraz düşürür. Okunabilirlik ve test edilebilirlik kazancı bu küçük düşüşe değer görüldü.

### 3.4. Yorum

1. **Karmaşıklık arayüzde ve girdi doğrulamada toplanıyor, iş kurallarının çekirdeğinde değil.** En kritik kurallar düşük CC'li: idempotent tamamlama (`completion.py`, ort. 1,75) ve dönemsel rapor (`reports.py`, ort. 1,71). Bu, katmanlı mimarinin (ADR-001) ve koşullu tek `UPDATE` kararının (ADR-005) doğrudan sonucu: durum denetimi dallanma yerine veritabanı koşuluna taşındı.
2. **CC 6 olan fonksiyonlar doğası gereği çok koşullu.** `to_kurus` (tür, sonluluk, tam TL, aralık) ve `create_owner` (ad uzunluğu, parola uzunluğu, tek hesap) birden çok iş kuralını sırayla uygular; her kural ayrı bir dal ve ayrı bir testtir. Bölmek okunurluğu artırmaz, kuralların dağılmasına yol açar.
3. **CC test sayısıyla tutarlı.** Örneğin `to_kurus` için CC 6, buna karşılık 20'den fazla parametreli test var; tüm dallar sınır değerleriyle sınanıyor (kapsama %100).
4. **Eşik CI'da korunuyor.** `xenon --max-absolute B` her PR'da çalışır; CC'si 10'u aşan bir fonksiyon `main`'e giremez.

---

## 4. Devreye Alma (Faz 4 - iv)

### 4.1. Yöntem

Ekip kararıyla iki yol birlikte sunulur:

- **Yerel kurulum:** README'deki adımlar; hesap `python -m servisflow.create_owner` ile açılır. Windows'ta `pip install -e .` hatası (WinError 145) ve geçici çözümü belgelendi. Eski veritabanı notu (RV4-01) `[ekip]`.
- **Bulut (Streamlit Community Cloud):** Uygulama GitHub deposundan yayınlanır ve bir web adresinden açılır. Ücretsizdir; `main` dalına her birleştirmeden sonra yeni sürüm yayınlanır. Demo ve kullanıcı testi (TC-31) bu sürümle yapılır.

### 4.2. Bulut İçin Koddaki Değişiklikler

| Sorun | Çözüm | Doğrulama |
| :--- | :--- | :--- |
| Bulut depoyu paket olarak kurmaz; `import servisflow` başarısız olur. | Kök dizinde `streamlit_app.py`: `src` klasörünü içe aktarma yoluna ekler ve asıl uygulamayı çalıştırır. | `test_ui_deploy`: giriş noktası giriş ekranını hatasız açar. |
| Bulutta kabuk yoktur; `create_owner` betiği çalıştırılamaz. | `auth.ensure_owner` + `app.bootstrap_owner`: bulutun sır (Secrets) ayarında `[owner]` varsa ve hiç hesap yoksa hesap oluşturulur. Var olan hesap ezilmez. Sır yoksa (yerel) hiçbir şey yapılmaz. | `test_auth` (3 test), `test_ui_deploy` (3 test): hesap oluşur ve giriş yapılır; yeniden çizimde ikinci hesap açılmaz; sır yokken hesap oluşmaz; geçersiz parola kullanıcıya gösterilmez, günlüğe parolasız yazılır. |
| Parola depoya girmemeli. | Parola yalnızca bulutun sır ayarında; yerel sır dosyası `.streamlit/secrets.toml` `.gitignore`'da. | `git status` sır dosyasını göstermiyor. |
| Giriş noktası CI dışında kalmamalı. | CI'daki black ve flake8 adımlarına `streamlit_app.py` eklendi. | CI `kalite` işi |

Ek olarak uygulama yerelde `streamlit run streamlit_app.py` ile, sır dosyasından gelen hesapla başlatıldı ve gerçek tarayıcıda (Playwright) giriş yapıldı.

### 4.3. Bilinen Kısıtlar

- **Kalıcı olmayan veritabanı:** Bulutta SQLite dosyası uygulamanın geçici diskindedir. Uygulama uyuyup yeniden başladığında veya yeniden yayınlandığında kayıtlar silinir; hesap sırlardan yeniden oluşur. Gerçek bir işletmede kalıcı bir veritabanı (örneğin barındırılan PostgreSQL) veya yerel kurulum gerekir; bu, MVP kapsamı dışındadır.
- **Herkese açık adres:** Giriş ekranına herkes ulaşabilir; ekranların geri kalanı oturum ister (FR-01) ve 3 hatalı denemeden sonra CAPTCHA çıkar. Yine de yalnızca uydurma veri girilir.
- **Uyku:** Uygulama bir süre kullanılmazsa uyur; ilk açılış birkaç saniye sürer.
- **Günlükler:** Sunucu günlüğü (ör. TC-30 hata ayrıntısı) bulutta “Manage app” panelinde görünür; kullanıcı ekranına gitmez.

### 4.4. Yayın Kaydı

| Alan | Kayıt |
| :--- | :--- |
| **Adres** | https://servisflow.streamlit.app/ |
| **Tarih** | 14.11.2026 |
| **Yayınlayan** | Kerem Erden |
| **Ayarlar** | Depo `servisflow/servisflow`, dal `main`, ana dosya `streamlit_app.py`; sorumlu hesabı bulutun sır ayarında |
| **Karşılaşılan engel** | İlk denemede GitHub “not authorized” hatası verdi: `servisflow` organizasyonunda üçüncü taraf uygulama (OAuth App) erişim kısıtlaması açıktı. Kısıtlama tümden kaldırılmadı; yalnızca Streamlit'e organizasyon erişimi verildi (en az yetki ilkesi). Erişimi organizasyon sahibi Kerem Erden verdi (GitHub, OAuth uygulama ayarı, “Grant”). |
| **İlk açılış gözlemi** | Giriş ekranı açıldı; sır ayarında tanımlanan kullanıcı adı ve parolayla giriş yapıldı (hesap sırlardan oluşturuldu). |

---

## 5. Faz 4 İçin DIR Beyanı

### 5.1. İş Paketi 9 — McCabe Ölçümü ve İyileştirme

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 13.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Code, ajan) |
| **İlgili üyeler** | Kerem Erden (yönlendirme); inceleme: Mehmet Ünsalan (#22) |
| **Görevin YZ kullanım sınırı** | Yeşil (ölçüm, kod iyileştirme, teknik dokümantasyon). Ölçüm yorumunun kabulü ekibe aittir. |
| **Üretilen çıktı** | `radon` ölçümleri, iki fonksiyonun yeniden düzenlenmesi, bu bölümün taslağı |

| Boyut | Puan | Gerekçe |
| :--- | :---: | :--- |
| **D** | 4 | Eşik ve hedef önceden tanımlıydı (NFR-01: CC ≤ 10, hedef ≤ 7); ölçüm aracı CI'da zorunluydu (`xenon`) (A2, A6). |
| **I** | 4 | YZ ölçümü yaptı ve hedefi aşan iki fonksiyonu böldü; bedelini (MI 45,9 → 44,6) kendisi raporladı. Ekip iyileştirmeyi birlikte tartıştı (Kerem Erden'in beyanı) (B3). Farklı modeller karşılaştırılmadı (B4 eksik). |
| **R** | 4 | Mehmet Ünsalan, Kerem Erden'in ekran paylaşımında 247 testi ve `radon cc` çıktısını birlikte çalıştırdı: en yüksek CC 6, `render` 9 → 3, `search_customers` 8 → 6 (C3, C4). |

**Skor (ekip kararı):** D = 4, I = 4, R = 4 → DIR = Floor(0,8 × 64) = **51** → **Bant 3**. *(YZ önerisi: D 4 · I 3 · R 4 → 38; ekip tartışması kayda geçtikten sonra I 3 → 4.)*

### 5.2. İş Paketi 10 — Devreye Alma (Bulut), TC-31 ve H4-02

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 13.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Code, ajan) |
| **İlgili üyeler** | Kerem Erden (yönlendirme, yayın), Ahmet Selim Dostabakan ve Mehmet Ünsalan (TC-31 gözlemi); inceleme: Mehmet Ünsalan (#24, #25) |
| **Görevin YZ kullanım sınırı** | Yeşil (kod, test, teknik dokümantasyon). Yayın işlemini ve kullanıcı testini ekip yapar. |
| **Üretilen çıktı** | `streamlit_app.py`, sırlardan hesap oluşturma ve testleri, README bulut bölümü, Bölüm 4 ve TC-31 görev kağıdı taslağı |

| Boyut | Puan | Gerekçe |
| :--- | :---: | :--- |
| **D** | 4 | Yöntem (Streamlit Community Cloud) ekip kararı (A8). Gizlilik sınırları önceden kondu: parola depoya girmez, testlerde yalnızca uydurma veri kullanılır (A7). |
| **I** | 4 | Ekip, YZ'nin TC-31 planını değiştirdi: uygulayan geliştirici yerine ekip dışı katılımcı oldu (B3). Yayın ekranındaki yanlış ana dosya yolu yayından önce düzeltildi. OAuth kısıtlamasında kısıtlama kaldırılmadı, yalnızca Streamlit'e izin verildi (en az yetki). H4-02 önce testle yeniden üretildi, sonra düzeltildi (B1). Farklı modeller karşılaştırılmadı (B4 eksik). |
| **R** | 4 | Ekip dışı katılımcı gerçek bir hata buldu (H4-02) (C3). Düzeltme, ekran paylaşımında Ahmet Selim Dostabakan ve Mehmet Ünsalan'ın yönlendirmesiyle uygulamada yeniden denendi (C4). Canlı sitede giriş ekranı ve sırlardaki hesapla giriş doğrulandı. **Eksik:** Canlı sitede tam akış (müşteri → rapor) denenmedi. |

**Skor (ekip kararı):** D = 4, I = 4, R = 4 → DIR = Floor(0,8 × 64) = **51** → **Bant 3**. *(YZ önerisi: D 4 · I 4 · R 4 → 51. Canlı sitede tam akış denenirse R 5 → 64.)*

---

## 6. Kaynaklar (Faz 4)

1. **McCabe, T. J. (1976).** A Complexity Measure. *IEEE Transactions on Software Engineering, SE-2*(4), 308–320.
2. **Radon belgeleri**, `radon cc` ve `radon mi` (döngüsel karmaşıklık ve bakım yapılabilirlik indeksi).
3. **Anthropic Claude (Claude Code)**, 13.11.2026; kullanım Bölüm 5'te beyan edilmiştir.
