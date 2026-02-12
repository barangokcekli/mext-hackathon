# Çoklu Ajan Kampanya Zekası Sistemi - Ekip Paylaşım Dökümanı

## 📋 Proje Özeti

Multi-tenant, bölge bazlı kampanya oluşturma sistemi. 3 ajan mimarisi ile deterministik segmentasyon ve kampanya planlama.

**Amaç:** Kozmetik şirketlerinin müşteri ve stok verilerine göre otomatik, kişiselleştirilmiş kampanyalar oluşturması.

---

## 🎯 Temel Özellikler

- **Multi-tenant:** Her şirket kendi verilerini yükler, izole çalışır
- **Bölge bazlı:** Türkiye'deki 7 bölge için iklim ve mevsim bazlı karar
- **3 Ajan Mimarisi:** Orkestratör → Müşteri Analiz + Stok Analiz → Kampanya Planlayıcı
- **Deterministik:** ML yok, sadece kural bazlı mantık
- **Marj Korumalı:** Hiçbir indirim %75'i aşamaz (minimum %25 marj)

---

## 🏗️ Sistem Mimarisi

```
Frontend (React)
    ↓
Orkestratör Ajan
    ├─→ Müşteri Analiz Ajanı (paralel)
    └─→ Stok Analiz Ajanı (paralel)
         ↓
    Kampanya Planlayıcı Ajan
         ↓
    Kampanya JSON
```

### Akış Özeti

1. Kullanıcı hedef, şehir, müşteri ID (opsiyonel) girer
2. Orkestratör tenant verisini yükler
3. Müşteri ve Stok analizi paralel çalışır
4. Kampanya Planlayıcı strateji belirler, ürün seçer, indirim hesaplar
5. Frontend kampanya kartını gösterir

**Önemli:** Döngü yok, tek geçiş. Ajanlar birbirini çağırmaz.

---

## 📊 Veri Yapısı

### Tenant İzolasyonu

```
/data/
  ├── shared/
  │   └── regions.json              ← Tüm tenant'lar ortak
  │
  ├── farmasi/
  │   ├── products.json
  │   ├── customers.json
  │   └── catalog_sources.json
  │
  └── {tenantId}/
      ├── products.json
      ├── customers.json
      └── catalog_sources.json
```

### Müşteri Verisi (customers.json)

```json
{
  "customerId": "C-1001",
  "city": "Istanbul",
  "age": 32,
  "gender": "F",
  "registeredAt": "2024-03-15",
  "productHistory": [
    {
      "productId": "P-2001",
      "category": "SKINCARE",
      "totalQuantity": 8,
      "totalSpent": 479.20,
      "orderCount": 8,
      "firstPurchase": "2025-01-15",
      "lastPurchase": "2026-01-20",
      "avgDaysBetween": 30
    }
  ]
}
```

**Önemli:** Alışveriş geçmişi `productHistory[]` olarak müşteri kaydında gömülü. Ayrı sipariş dosyası yok.

### Ürün Verisi (products.json)

```json
{
  "productId": "P-2001",
  "productName": "Dr. C. Tuna Tea Tree Face Wash",
  "category": "SKINCARE",
  "subcategory": "Yüz Temizleme",
  "tags": ["temizleyici", "jel", "akne"],
  "season": "all",
  "currentStock": 900,
  "last30DaysSales": 75,
  "unitCost": 20.00,
  "unitPrice": 59.90
}
```

### Bölge Verisi (regions.json)

```json
{
  "name": "Marmara",
  "climateType": "Metropol",
  "medianBasket": 85.00,
  "trend": "SKINCARE",
  "seasonalNeeds": {
    "winter": ["nemlendirici", "dudak-bakım", "el-kremi"]
  },
  "cities": ["Istanbul", "Bursa", "Kocaeli"]
}
```

---

## 🤖 Ajan Sorumlulukları

### 1. Orkestratör Ajan

**Görevleri:**
- Tenant doğrulama
- Veri yükleme (customers + products)
- Şehir → bölge çözümleme
- Ajan koordinasyonu
- Hata yönetimi

**Yapmaz:**
- Kampanya kararı almaz
- Veri analiz etmez
- Segmentasyon yapmaz

### 2. Müşteri Analiz Ajanı

**Görevleri:**
- Müşteri segmentasyonu (yaş, kayıp, değer, sadakat)
- Kategori yakınlığı
- Çeşitlilik profili
- Düzenli ürün tespiti
- Bütçe tahmini

**Çıktı:** CustomerInsightJSON

### 3. Stok Analiz Ajanı

**Görevleri:**
- Stok performans analizi
- Yıldız ürün tespiti (hızlı satanlar)
- Yavaş ürün tespiti (stok baskısı)
- Mevsimsel uyum kontrolü

**Çıktı:** StockInsightJSON

### 4. Kampanya Planlayıcı Ajanı

**Görevleri:**
- Hedef → strateji eşlemesi
- Ürün seçimi (bütçe, mevsim, çeşitlilik)
- İndirim hesaplama (marj tabanı %25)
- Mesajlaşma oluşturma
- Ürün önerileri

**Çıktı:** CampaignJSON

---

## 📐 Segmentasyon Kuralları

### Müşteri Segmentleri

| Segment | Kriter | Kampanya Etkisi |
|---|---|---|
| **Yaş** | | |
| GenZ | 18-25 | Trend ürünler, düşük fiyat, sosyal medya |
| GençYetişkin | 26-35 | Cilt bakım, anti-aging başlangıç |
| Yetişkin | 36-50 | Premium, parfüm, sadakat |
| Olgun | 51+ | Anti-aging, özel bakım |
| **Kayıp** | | |
| Aktif | <30 gün | Çapraz satış, düşük indirim |
| Ilık | 30-60 gün | Hatırlatma, orta indirim |
| Riskli | >60 gün | Geri kazanım, yüksek indirim |
| **Değer** | | |
| YüksekDeğer | >bölge medyanı | Premium paketler, düşük indirim yeterli |
| Standart | ≤bölge medyanı | Değer odaklı, fiyat avantajı |
| **Sadakat** | | |
| Platin | ≥12 ay, aylık ≥2 sipariş | Özel erişim, ekstra hediye |
| Altın | ≥6 ay, aylık ≥1 sipariş | Sadakat bonusu, ücretsiz kargo |
| Gümüş | ≥3 sipariş | Standart + küçük teşvik |
| Bronz | Yeni/az alışveriş | Tanışma indirimi |
| **Çeşitlilik** | | |
| Kaşif | >0.7 | Yeni ürünler, keşif paketleri |
| Dengeli | 0.4-0.7 | Favori + 1 yeni ürün |
| Sadık | ≤0.4 | Favori ürünlerde miktar indirimi |

### Ürün Segmentleri

| Segment | Kriter | Kampanya Rolü | İndirim |
|---|---|---|---|
| Yıldız | Stok günü ≤20 | Çapa ürün | %0-5 |
| Normal | 20-60 gün | Tamamlayıcı | %5-15 |
| Yavaş | >60 gün | Eritme hedefi | %15-35 |
| Ölü Stok | Satış yok | Agresif tasfiye | %35-75 |

---

## 🎯 Kampanya Stratejileri

### Hedef × Segment Matrisi

| Hedef | Değer | Kayıp | Strateji | İndirim Max |
|---|---|---|---|---|
| GelirArtır | Yüksek | Aktif | CrossSell | 10% |
| GelirArtır | Yüksek | Riskli | WinBack | 20% |
| StokErit | Standart | Aktif | FlashSale | 25% |
| StokErit | Standart | Riskli | MaxClearance | 35% |

### Karar Akışı

```
1. Bütçe Kontrolü (avgBasket * 1.2)
2. Sadakat Katmanı (Platin → özel erişim)
3. Düzenli Ürün Kontrolü (zamanı gelmiş → dahil et)
4. Çeşitlilik Profili (Kaşif → yeni ürün)
5. Mevsim + Bölge Filtresi
6. Yaş + Cinsiyet Filtresi
7. Hedef Mantığı (GelirArtır / StokErit)
8. Marj + Bütçe Son Kontrol
```

---

## 🔧 Teknik Detaylar

### API Endpoint

```
POST /api/campaign
Content-Type: application/json

{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue" | "ClearOverstock",
  "city": "Istanbul",
  "customerId": "C-1001",  // opsiyonel
  "event": "MothersDay"    // opsiyonel
}
```

### Yanıt (CampaignJSON)

```json
{
  "campaignId": "CMP-20260212-IST-001",
  "objective": "IncreaseRevenue",
  "targetSegment": {
    "churn": "Active",
    "value": "HighValue",
    "affinity": "SKINCARE"
  },
  "strategy": {
    "type": "CrossSell",
    "discountPercent": 10
  },
  "products": {
    "hero": [...],
    "complementary": [...]
  },
  "messaging": {
    "headline": "Anneler Günü Özel Paketi",
    "subtext": "Favori ürünleriniz bir arada"
  },
  "recommendations": [...]
}
```

---

## 📦 Ürün Kategorileri (Farmasi)

### Ana Kategoriler

1. **MAKEUP** - Makyaj (fondöten, maskara, ruj, far)
2. **SKINCARE** - Cilt Bakımı (temizleyici, serum, nemlendirici, SPF)
3. **FRAGRANCE** - Parfüm & Koko (kadın, erkek, unisex)
4. **PERSONALCARE** - Kişisel Bakım (ağız, deodorant, vücut)
5. **HAIRCARE** - Saç Bakımı (şampuan, maske, serum)
6. **WELLNESS** - Sağlık (vitamin, kolajen, enerji)

### Mevsimsel Etiketleme

| Mevsim + İklim | Öncelikli Etiketler |
|---|---|
| Kış + Soğuk | besleyici, yoğun, nemlendirici, dudak-bakım, el-kremi |
| Yaz + Sıcak-Nemli | SPF, hafif, mat, bronzlaştırıcı |
| İlkbahar | temizleyici, serum, anti-aging, tonik |
| Sonbahar | onarıcı, besleyici, maske, nemlendirici |

---

## 🚀 Hızlı Başlangıç

### 1. Veri Hazırlama

```bash
# Mock data'yı incele
cd mock-data
cat README.md

# Tenant verisi
- farmasi/customers.json (8 müşteri)
- farmasi/products.json (19 ürün)
- regions.json (7 bölge)
- tenants.json (tenant kayıtları)
```

### 2. Test Senaryoları

**Senaryo 1: Aktif YüksekDeğer Müşteri**
```json
{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue",
  "city": "Istanbul",
  "customerId": "C-1001"
}
```

**Senaryo 2: Bölge Modu (Müşteri ID Yok)**
```json
{
  "tenantId": "farmasi",
  "objective": "ClearOverstock",
  "city": "Ankara"
}
```

**Senaryo 3: Etkinlik ile**
```json
{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue",
  "city": "Izmir",
  "customerId": "C-1003",
  "event": "MothersDay"
}
```

---

## ⚙️ Önemli Kurallar

### 1. Marj Tabanı
- Hiçbir indirim %75'i aşamaz
- Minimum %25 marj her zaman korunur
- `maksİndirim = brütMarj - 25`

### 2. Bütçe Kontrolü
- `estimatedBudget = avgBasket * 1.2`
- Paket toplamı bütçeyi aşarsa en düşük öncelikli ürün çıkar

### 3. Döngü Yok
- Orkestratör → Analiz → Planlayıcı (tek geçiş)
- Ajanlar birbirini çağırmaz
- Geri bildirim döngüsü yok

### 4. Deterministik
- ML kullanılmaz
- Tüm kararlar kural bazlı
- Aynı girdi → aynı çıktı

### 5. Tek Ülke
- Sadece Türkiye
- Şehir/bölge bazlı kararlar
- 7 bölge, farklı iklim tipleri

---

## 🎨 Frontend Özellikleri

### Kampanya Kontrol Paneli

1. **Şirket Seçimi** - Tenant dropdown
2. **Hedef Seçimi** - GelirArtır / StokErit
3. **Şehir Seçimi** - Dropdown (regions.json'dan)
4. **Müşteri ID** - Opsiyonel input
5. **Etkinlik** - Opsiyonel dropdown
6. **Kampanya Kartı** - JSON görünüm

### Veri Yönetimi Paneli

- Ürün kataloğu yükle (CSV/JSON veya URL scrape)
- Müşteri verisi yükle (CSV/JSON)
- Mevcut veriyi görüntüle/düzenle

---

## 📝 Katalog Scraper (Opsiyonel)

### Özellikler

- Headless browser ile e-ticaret sitelerinden ürün çekme
- Otomatik kategori/tag eşlemesi
- Önizleme + onay mekanizması
- Varsayılan stok değerleri atama

### API

```
POST /api/catalog/scrape
{
  "tenantId": "farmasi",
  "url": "https://farmasi.com.tr/farmasi",
  "maxPages": 5
}

POST /api/catalog/import
{
  "tenantId": "farmasi",
  "products": [...],
  "generateStock": true
}
```

---

## 🏆 Hackathon Stratejisi

### Zaman Dağılımı (5 saat)

1. **1. Saat** - JSON arayüzleri tanımla (kritik!)
2. **2-3. Saat** - Ajan mantıkları
3. **4. Saat** - Entegrasyon
4. **5. Saat** - Test + demo hazırlık

### Takım Dağılımı (3 kişi)

- **Dev 1:** Orkestratör + API
- **Dev 2:** Analiz + Kampanya Planlayıcı mantığı
- **Dev 3:** Frontend

### Sadeleştirme Kademeleri

1. **Tam:** 3 ajan + etkinlik + müşteri/bölge mod
2. **Orta:** Etkinlik çıkar
3. **Minimal:** Sadece bölge modu
4. **Acil:** Tek ajan + Postman demo

---

## 🔍 Örnek Çıktı

### Müşteri Analiz Çıktısı

```json
{
  "customerId": "C-1001",
  "ageSegment": "GençYetişkin",
  "churnSegment": "Active",
  "valueSegment": "HighValue",
  "loyaltyTier": "Altın",
  "affinityCategory": "SKINCARE",
  "diversityProfile": "Dengeli",
  "estimatedBudget": 102.60,
  "missingRegulars": [
    {
      "productId": "P-2001",
      "daysOverdue": 5
    }
  ]
}
```

### Stok Analiz Çıktısı

```json
{
  "heroProducts": [
    {
      "productId": "P-2004",
      "stockDays": 8,
      "inventoryPressure": false
    }
  ],
  "slowMovers": [
    {
      "productId": "P-2003",
      "stockDays": 95,
      "inventoryPressure": true
    }
  ]
}
```

---

## 📚 Döküman Referansları

### Temel Dökümanlar

- **README.md** - Proje genel bakış
- **SPEC.md** - Teknik şartname, mimari, API
- **DB_SCHEMA.md** - Veri modeli, ilişkiler, metrikler
- **SEGMENTATION.md** - Müşteri ve ürün segmentasyon kuralları

### Ajan Dökümanları

- **ORCHESTRATOR_AGENT.md** - Orkestratör ajan
- **CUSTOMER_ANALYSIS_AGENT.md** - Müşteri analiz ajanı
- **STOCK_ANALYSIS_AGENT.md** - Stok analiz ajanı
- **CAMPAIGN_PLANNER_AGENT.md** - Kampanya planlayıcı ajan

### Referans Dökümanlar

- **FARMASI_CATEGORIES.md** - Ürün kategori yapısı
- **mock-data/README.md** - Test verisi açıklaması

---

## 💡 Önemli Notlar

### Veri Yapısı

- Alışveriş geçmişi `productHistory[]` olarak müşteri kaydında gömülü
- Ayrı sipariş dosyası yok
- Şirketler ürün verisi olmadan da başlayabilir (boş dizi)

### Bölge Mantığı

- 7 bölge, 4 iklim tipi
- Her bölgenin medyan sepet tutarı farklı
- Mevsimsel ihtiyaçlar bölgeye göre değişir

### Müşteri Modu vs Bölge Modu

- **Müşteri ID varsa:** Bireysel segmentasyon
- **Müşteri ID yoksa:** Bölge bazlı genel profil

### Etkinlik Etkisi

- Sadece mesajlaşmayı değiştirir
- Hedef mantığını geçersiz kılmaz
- Opsiyoneldir

---

## 🎯 Başarı Kriterleri

1. ✅ Aynı girdi → aynı çıktı (deterministik)
2. ✅ Marj tabanı her zaman korunur
3. ✅ Bütçe aşılmaz
4. ✅ Döngü yok, tek geçiş
5. ✅ Tenant izolasyonu sağlanır
6. ✅ Bölge bazlı filtreleme çalışır
7. ✅ Mevsimsel uyum kontrol edilir

---

## 📞 İletişim ve Destek

Sorularınız için:
- Proje dökümanlarını inceleyin
- Mock data'yı test edin
- API endpoint'lerini Postman ile deneyin

**Başarılar! 🚀**
