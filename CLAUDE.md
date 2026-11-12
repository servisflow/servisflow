# CLAUDE.md — ServisFlow çalışma kılavuzu

Bu dosya, bu depoda çalışan Claude oturumları içindir. Ekip üyeleri hangi hesaptan çalışırsa çalışsın aynı kuralları uygular.

## Dil ve iletişim

- Kullanıcıyla **Türkçe** konuş. Kod içi yorumlar ve docstring'ler Türkçe, kod adları İngilizce.
- Ekip, Yazılım Kalite Standartları (YAZ401) dersinin 7 kişilik proje ekibidir; kullanıcılar yazılım öğrencisidir. Terimleri kısa açıkla.
- Grup sohbetine gidecek mesajlar düz metin olsun (emoji ve Markdown yok).

## Proje

**ServisFlow:** Küçük bir oto servis için araç bazlı iş takibi. Müşteri → araç → servis ziyareti → To-Do benzeri işler (başlık, not, tutar) → ✓ ile tamamlama → tamamlandığı güne göre günlük/haftalık/aylık/yıllık brüt iş bedeli raporu.

- **Tek kullanıcı:** işletme sorumlusu. Ustalar sisteme girmez, işi sorumluya bildirir.
- **Kapsam dışı:** stok, parça satırları, çoklu rol, audit log, ödeme/fatura. Kapsamı genişletme önerme; dar MVP ekip ve hoca kararıdır.
- Önceki fikir Q-Task'tı (kurumsal görev ve SLA takibi); kapsam geniş olduğu için ServisFlow'a geçildi.

## Ders yönergesi (özet)

- 5 faz. Teslimler (izlence): Faz 1 Hafta 4 · Faz 2 Hafta 7 · Faz 3 Hafta 9 · Faz 4 Hafta 12 · Faz 5 Hafta 14. Vize Hafta 8–9.
  - Faz 3: Faz 2 review; mimari/tasarım seçenekleri ve teknik kararlar; kodlama ve kod incelemesi.
  - Faz 4: Faz 3 review; beyaz/kara kutu ve kullanıcı testleri, hata düzeltme; modül bazında McCabe hesaplama ve yorumlama; devreye alma.
  - Faz 5: tüm çıktıların son hali, demo, her üyenin öğrendikleri.
- Final rapor referanslar dahil en fazla 20 sayfa; şablon: Ekip ve katkılar → Faz 1–5 çıktıları → iş/görev bazında DIR beyanları → Referanslar → Ekler. Repo linki ve çalıştırma/test talimatı raporda olmalı.
- Her YZ kullanımı **DIR** ile beyan edilir ve kaynakçaya yazılır.

## DIR (Discover–Interact–Review) kuralları

- Kaynak: dersin İSTÜN DIR Rehberi V2 ve Yapay Zekâ Kullanım Beyanı Şablonu.
- D, I, R her biri **1–5 tam sayı** (yarım puan yok). **DIR = Floor(0,8 × D × I × R)**. Bantlar: 0–10, 11–35, 36–60, 61–100.
- Gerekçelerde kontrol listesi kodları kullanılır: A1–A11 (Keşfet), B1–B6 (Etkileş), C1–C8 (Gözden geçir).
- **Puanları ekip verir.** Claude puan önerebilir ama yapılmamış bir doğrulamayı yapılmış gibi yazmaz; eksikleri açıkça “eksik” diye belirtir.
- Kişisel veri (öğrenci numarası vb.) YZ'ye verilmez (A7).
- Bu depodaki YZ destekli her PR açıklamasında YZ kullanımı belirtilir; ilgili fazın raporunun DIR bölümüne iş paketi olarak eklenir.

## Depo düzeni

```text
src/servisflow/ui/          Streamlit ekranları (yalnızca services'i çağırır)
src/servisflow/services/    İş kuralları; Streamlit içe aktarmaz
src/servisflow/repository/  SQLAlchemy modelleri ve sorgular; iş kuralı yok
tests/                      pytest; her test bellekte temiz SQLite ve sabit saat alır
docs/FazN_Raporu.md         Faz raporları
teslim/                     .gitignore'da; öğrenci numaralı kopyalar, ekip içi notlar
```

## Çalışma akışı (zorunlu)

- `main` korumalıdır: doğrudan push **yapılamaz**. Her değişiklik (belgeler dahil): `main`'den dal → commit → PR → CI'daki `kalite` işi yeşil → PR'ı açan dışında 1 ekip üyesinin onayı → birleştirme. Kural yöneticilere de uygulanır.
- Dal adları: `uc-0X-kisa-ad` (use case), diğerleri kısa ve açıklayıcı.
- PR açıklaması: `Closes #N`, karşılanan FR/UC/BR, doğrulama sonuçları, YZ kullanımı.
- İnceleme bulguları `KR-NN` numarasıyla `docs/Faz3_Raporu.md` Bölüm 3.4'e işlenir. İnceleyenin bulgusunu önce yerelde yeniden üret, sonra düzelt, mümkünse bulguyu yakalayan bir test ekle.
- Use case issue'ları: #3 UC-01 … #9 UC-07. Sahipler `docs/Faz1_Raporu.md` Bölüm 1'de.

## Kurulum ve kalite kapıları

```bash
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
streamlit run src/servisflow/ui/app.py
```

CI (`.github/workflows/ci.yml`) ile aynı kontroller; PR açmadan önce yerelde çalıştır:

```bash
black --check src tests
flake8 src tests
bandit -r src --severity-level high
pip-audit -r requirements.txt -r requirements-dev.txt
xenon src --max-absolute B --max-modules B --max-average A
pytest --cov
```

Eşikler: fonksiyon başına McCabe ≤ 10 · `ui` hariç satır + dal kapsaması ≥ %80 · bandit yüksek bulgu 0 · pip-audit açık 0.

Windows notu: `black`'in derlenmiş paketi uzun dosya yollarında yüklenemeyebilir; `pip install --no-binary black black==<sürüm>` ile derlenmemiş sürümü kur.

## Kodlama kuralları (ADR'ler: `docs/Faz3_Raporu.md` Bölüm 2.2)

- **Zaman:** Servisler `datetime.now()` çağırmaz; `services.clock.Clock` alır. Testlerde `FixedClock`. Tüm zamanlar saat dilimli; veritabanında UTC. Gün sınırları `Europe/Istanbul`.
- **Para:** Tamsayı kuruş (`amount_kurus`); `float` yok. 0,01 – 1.000.000,00 TL.
- **Veritabanı:** Yalnızca ORM / parametreli sorgu. SQLite tür ve uzunluk dayatmaz; sınırlar hem servis katmanında hem CHECK kısıtlarında.
- **Tamamlama (✓):** Tek koşullu güncelleme (`WHERE status = 'TODO'`), idempotent. Geri alma yalnızca aynı İstanbul günü içinde. Dönem toplamı sayaçta tutulmaz, sorgudan hesaplanır.
- **Hatalar:** Kullanıcıya gösterilecek hatalar `services.errors` türleri. Streamlit `client.showErrorDetails = "none"` (`false` yığın izini gösterir).
- **Giriş:** Argon2id; 3 hatalı denemeden sonra kendi sunucumuzda üretilen CAPTCHA; hatalı deneme sayımı yalnızca `LoginAttempt.username` üzerinden (var olan/olmayan kullanıcı adı aynı davranır).
- Servis fonksiyon imzaları: `docs/Faz3_Raporu.md` Bölüm 2.3.

## Belgeler ve gizlilik

- Depo **herkese açık.** Öğrenci numarası, gerçek müşteri verisi, ekip içi plan ve sunum çalışma metinleri depoya girmez; bunlar `teslim/` klasöründe tutulur.
- Raporlarda gerçekleşmemiş test, inceleme veya doğrulama yapılmış gibi yazılmaz.
- Bir raporda yapılan değişiklik, rapordaki sürüm/durum satırına ve gerekiyorsa değişiklik geçmişine işlenir.
- Ders materyalleri (yönerge, izlence, rehberler) depoya eklenmez.
