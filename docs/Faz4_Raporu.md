# PROJE RAPORU: FAZ 4 ÇIKTILARI — Sistematik Test ve Kalite Güvencesi

- **Proje Adı:** ServisFlow — Araç Bazlı Servis İş Takibi ve Dönemsel Brüt İş Bedeli Raporlama
- **Ders:** Yazılım Kalite Standartları (YAZ401)
- **Doküman Durumu:** Taslak v0.1 — McCabe ölçümü ve ilk iyileştirmeler tamam; testlerin tamamlanması, kullanıcı testi ve devreye alma sürüyor
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
| RV4-02 | Plaka seçim listesinde boşluksuz yazım (`06b`) eşleşmiyor; yalnızca boşluklu yazım (`06 b`) çalışıyor. | KR-09 | Açık; kullanıcı testinde (TC-31) gözlenecek |
| RV4-03 | ADR-006 CAPTCHA biçimi (toplama sorusu) UC-01 sahibiyle teyit edilmedi. | #15 incelemesi | Açık |
| RV4-04 | Kaynakçadaki mutasyon testi makalesi birincil kaynaktan doğrulanmadı. | Faz 3, Kaynaklar | Açık (`[ekip]`) |
| RV4-05 | NFR-01 hedefini (McCabe ≤ 7) aşan iki fonksiyon. | Bu belge, Bölüm 3 | **Kapandı** (3.3) |

`[ekip: Faz 3 için hocanın geri bildirimi gelirse buraya eklenecek]`

---

## 2. Testler (Faz 4 - ii)

### 2.1. Test Senaryolarının Karşılanma Durumu

Faz 2 test planındaki 32 senaryonun 30'u otomatik testlerle karşılanıyor (pytest; arayüz için Streamlit AppTest). Toplam 247 test, `ui` hariç satır ve dal kapsaması %100 (NFR-02).

| Teknik | Senaryolar | Otomatik test dosyaları |
| :--- | :--- | :--- |
| Denklik sınıfı | TC-01, TC-05, TC-06, TC-08 – TC-12, TC-16 | `test_auth`, `test_customers`, `test_vehicles`, `test_tasks`, `test_ui_customers`, `test_ui_visits` |
| Sınır değer | TC-04, TC-07, TC-15, TC-26, TC-29 | `test_auth`, `test_customers`, `test_tasks`, `test_reports`, `test_ui_login` |
| Durum geçişi ve karar tablosu | TC-17 – TC-21 | `test_tasks`, `test_completion`, `test_ui_visits` |
| Beyaz kutu | TC-02, TC-13 | `test_auth`, `test_visits` |
| Kara kutu (sistem) | TC-03, TC-14, TC-22, TC-24, TC-25, TC-27, TC-28, TC-32 | `test_ui_login`, `test_ui_customers`, `test_ui_reports`, `test_visits`, `test_reports`, `test_auth` |
| Hata tahmini | TC-23 | `test_completion` (iki gerçek veritabanı bağlantısı) |
| **Açık** | **TC-30** (veritabanı erişilemezken genel hata mesajı), **TC-31** (kullanıcı kabul testi) | — |

Ek olarak Faz 3'te mutasyon testi yapıldı (22 mutant; yaşayan 4 mutanttan 3'ü için test eklendi, 1'i eşdeğer) ve uygulama gerçek tarayıcıda (Playwright) uçtan uca çalıştırıldı.

### 2.2. Kullanıcı Kabul Testi (TC-31)

`[ekip: yürütülecek]` Senaryo: İşletme sahibi profilindeki bir kişi, ustanın bildirdiği bir işi baştan sona kaydeder (müşteri → araç → ziyaret → iş → ✓ → rapor). Ölçüt: ≤ 3 dakika, yardımsız (NFR-06). Her katılımcı için süre, takıldığı adımlar ve önerileri kaydedilecek.

### 2.3. Bulunan Hatalar ve Düzeltmeler

| No | Hata | Bulan | Düzeltme |
| :--- | :--- | :--- | :--- |
| `[ekip]` | | | |

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

`[ekip: yöntem seçilecek]` Mevcut durum: kurulum ve çalıştırma adımları README'de; hesap `python -m servisflow.create_owner` ile oluşturuluyor; Windows'ta `pip install -e .` hatası (WinError 145) ve geçici çözümü belgelendi. Eski veritabanı notu (RV4-01) eklenecek.

---

## 5. Faz 4 İçin DIR Beyanı (Taslak)

### 5.1. İş Paketi 9 — McCabe Ölçümü ve İyileştirme

| Alan | İçerik |
| :--- | :--- |
| **Tarih** | 13.11.2026 |
| **YZ aracı** | Anthropic Claude (Claude Code, ajan) |
| **İlgili üyeler** | Kerem Erden (yönlendirme); inceleme: `[PR'ı inceleyen üye]` |
| **Görevin YZ kullanım sınırı** | Yeşil (ölçüm, kod iyileştirme, teknik dokümantasyon). Ölçüm yorumunun kabulü ekibe aittir. |
| **Üretilen çıktı** | `radon` ölçümleri, iki fonksiyonun yeniden düzenlenmesi, bu bölümün taslağı |

| Boyut | Puan | Gerekçe |
| :--- | :---: | :--- |
| **D** | `[ekip]` | |
| **I** | `[ekip]` | |
| **R** | `[ekip]` | PR incelemesinden sonra yazılacak. |

---

## 6. Kaynaklar (Faz 4)

1. **McCabe, T. J. (1976).** A Complexity Measure. *IEEE Transactions on Software Engineering, SE-2*(4), 308–320.
2. **Radon belgeleri**, `radon cc` ve `radon mi` (döngüsel karmaşıklık ve bakım yapılabilirlik indeksi).
3. **Anthropic Claude (Claude Code)**, 13.11.2026; kullanım Bölüm 5'te beyan edilmiştir.
