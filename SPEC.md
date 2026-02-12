# Çoklu Ajan Kampanya Zekası Sistemi — Teknik Şartname

Sistem multi-tenant mimaride çalışır. Birden fazla şirket (tenant) kendi ürün, müşteri ve sipariş verilerini yükleyerek kendi kampanyalarını oluşturabilir. Karar mekanizması şehir ve bölge bazlıdır.

## 1. Üst Düzey Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React SPA)                    │
│                  Kampanya Kontrol Paneli                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Şirket Seçimi / Giriş                               │   │
│  │  ┌────────────────┐                                   │   │
│  │  │ Tenant (dd)    │  ← şirket seçer veya login olur  │   │
│  │  └────────────────┘                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────┐ ┌─────────┐  │
│  │   Hedef      │ │    Şehir    │ │ Müşteri  │ │ Etkinlik│  │
│  │  (dropdown)  │ │  (dropdown) │ │ ID (ops) │ │ (ops dd)│  │
│  └─────────────┘ └─────────────┘ └──────────┘ └─────────┘  │
│                        │ POST /api/campaign                 │
│                        ▼                                    │
│              [ Kampanya Kartı — JSON Görünüm ]              │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Veri Yönetimi Paneli                                 │   │
│  │  • Ürün kataloğu yükle (CSV/JSON veya URL scrape)    │   │
│  │  • Müşteri verisi yükle (CSV/JSON)                    │   │
│  │    (ürün bazlı alışveriş özeti productHistory[])      │   │
│  │  • Mevcut veriyi görüntüle / düzenle                  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (Node.js / Python)                │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               ORKESTRATÖR AJAN                         │ │
│  │                                                        │ │
│  │  1. Tenant doğrula + girdiyi doğrula                   │ │
│  │  2. Tenant verisini yükle                              │ │
│  │  3. Müşteri Analiz Ajanını çağır ────────┐             │ │
│  │  4. Stok Analiz Ajanını çağır ───────────┼──┐          │ │
│  │     (paralel çalışabilir)                │  │          │ │
│  │  5. Kampanya Planlayıcıyı çağır ─────────┼──┼──┐       │ │
│  │  6. Kampanya JSON'ını döndür              │  │  │       │ │
│  └──────────────────────────────────────────┘  │  │       │ │
│                                                │  │  │       │
│  ┌──────────────────────┐  ┌──────────────────▼──┼──┼────┐ │
│  │ MÜŞTERİ ANALİZ AJANI │  │  STOK ANALİZ AJANI  │  │    │ │
│  │                      │  │                     │  │    │ │
│  │ • Müşteri segmenti   │  │ • Yıldız ürünler    │  │    │ │
│  │ • Kayıp + değer      │  │ • Yavaş ürünler     │  │    │ │
│  │ • Sadakat katmanı    │  │ • Envanter baskısı  │  │    │ │
│  │ • Kategori yakınlığı │  │ • Mevsimsel uyum    │  │    │ │
│  │ • Çeşitlilik profili │  │ • Stok performansı  │  │    │ │
│  │ • Düzenli ürünler    │  │                     │  │    │ │
│  └──────────────────────┘  └─────────────────────┘  │    │ │
│                                                      │    │ │
│  ┌───────────────────────────────────────────────────▼────▼┐│
│  │           KAMPANYA PLANLAYICI AJANI                     ││
│  │                                                         ││
│  │ • Hedef → strateji                                      ││
│  │ • Marj tabanı (≥%25)                                    ││
│  │ • Etkinlik modifiyesi                                   ││
│  │ • Bölge bazlı filtreleme                                ││
│  │ • Ürün önerisi                                          ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              KATALOG SCRAPER SERVİSİ                   │ │
│  │  • URL al → Headless browser ile sayfayı render et     │ │
│  │  • Ürün listesini parse et (isim, fiyat, kategori)     │ │
│  │  • Otomatik kategori/tag eşlemesi yap                  │ │
│  │  • Tenant'ın products verisine yaz                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              VERİ İÇE AKTARMA SERVİSİ                 │ │
│  │  • CSV/JSON dosya yükleme                              │ │
│  │  • Alan eşleme (mapping) arayüzü                       │ │
│  │  • Veri doğrulama + hata raporu                        │ │
│  │  • POST /api/data/import                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            VERİ KATMANI (Tenant bazlı izolasyon)       │ │
│  │                                                        │ │
│  │  /data/{tenantId}/                                     │ │
│  │    ├── products.json                                   │ │
│  │    ├── customers.json  (productHistory[] gömülü)       │ │
│  │    └── catalog_sources.json                            │ │
│  │                                                        │ │
│  │  /data/shared/                                         │ │
│  │    └── regions.json  (tüm tenant'lar ortak kullanır)   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

Akış kesinlikle doğrusaldır: **Frontend → Orkestratör → Müşteri Analiz + Stok Analiz → Kampanya Planlayıcı → Frontend**. Döngüsel çağrı yoktur. Müşteri ve Stok analizi paralel çalışabilir (bağımsız).

Katalog Scraper ayrı bir servistir, kampanya akışının dışındadır. Ürün verisi önceden çekilir ve `products.json`'a yazılır.

---

## 1.1 Katalog Scraper Servisi

Kampanya akışından bağımsız çalışan bir yardımcı servistir. Bir e-ticaret sitesinin URL'sini alır, ürünleri çeker, kategorize eder ve `products.json`'a yazar.

### Akış

```
Kullanıcı                  Backend                         Hedef Site
───────                    ───────                         ──────────
  │                          │                                │
  │ POST /api/catalog/scrape │                                │
  │ { url, pages? }          │                                │
  │ ─────────────────────►   │                                │
  │                          │  Headless browser (Puppeteer)  │
  │                          │  ──────────────────────────►   │
  │                          │                                │
  │                          │  HTML + rendered DOM            │
  │                          │  ◄──────────────────────────   │
  │                          │                                │
  │                          │  Parse: ürün adı, fiyat,       │
  │                          │  kategori, resim URL            │
  │                          │                                │
  │                          │  Otomatik tag/kategori eşleme  │
  │                          │  (keyword matching)             │
  │                          │                                │
  │  ScrapedProductsJSON     │                                │
  │ ◄─────────────────────   │                                │
  │                          │                                │
  │ POST /api/catalog/import │                                │
  │ { products, overwrite? } │                                │
  │ ─────────────────────►   │                                │
  │                          │  products.json'a yaz            │
  │  { imported: 45 }        │                                │
  │ ◄─────────────────────   │                                │
```

### API Endpoint'leri

#### `POST /api/catalog/scrape`

URL'den ürünleri çeker, kategorize eder, önizleme döndürür (henüz kaydetmez).

İstek:
```json
{
  "tenantId": "farmasi",
  "url": "https://farmasi.com.tr/farmasi",
  "maxPages": 5,
  "selectors": {
    "productCard": ".product-card",
    "name": ".product-name",
    "price": ".product-price",
    "category": ".product-category",
    "image": ".product-image img"
  }
}
```

`selectors` opsiyoneldir. Verilmezse servis yaygın e-ticaret kalıplarını otomatik dener.

Yanıt:
```json
{
  "source": "farmasi.com.tr",
  "scrapedAt": "2026-02-12T15:00:00Z",
  "totalFound": 48,
  "products": [
    {
      "scrapedName": "VFX Pro Camera Ready Foundation",
      "scrapedPrice": 89.90,
      "scrapedCategory": "Makyaj > Fondöten",
      "imageUrl": "https://farmasi.com.tr/images/vfx-pro.jpg",
      "mapped": {
        "category": "MAKEUP",
        "subcategory": "Fondöten",
        "tags": ["fondöten", "mat", "doğal"],
        "season": "all",
        "confidence": 0.92
      }
    }
  ],
  "unmappedCount": 3,
  "unmapped": [
    { "scrapedName": "Bilinmeyen Ürün X", "scrapedCategory": "Diğer" }
  ]
}
```

#### `POST /api/catalog/import`

Scrape sonucunu onaylayıp tenant'ın `products.json`'ına kaydeder.

İstek:
```json
{
  "tenantId": "farmasi",
  "products": [ ... ],
  "overwrite": false,
  "generateStock": true
}
```

`generateStock: true` olduğunda her ürüne varsayılan stok değerleri atanır:
```
currentStock: random(200, 2000)
last30DaysSales: random(10, 300)
unitCost: scrapedPrice * 0.35  // tahmini %35 maliyet oranı
unitPrice: scrapedPrice
```

#### `GET /api/catalog/sources`

Daha önce çekilen kaynakları listeler.

Yanıt:
```json
{
  "sources": [
    {
      "url": "https://farmasi.com.tr/farmasi",
      "lastScraped": "2026-02-12T15:00:00Z",
      "productCount": 48
    }
  ]
}
```

### Otomatik Kategori Eşleme

Scraper, ürün adı ve site kategorisinden otomatik eşleme yapar:

```
Eşleme kuralları (keyword → category/subcategory/tags):

"fondöten|foundation|bb cream|cc cream" → MAKEUP / Fondöten
"maskara|mascara"                       → MAKEUP / Maskara
"ruj|lipstick|lip gloss|dudak"          → MAKEUP / Ruj & Dudak
"far|eyeshadow|göz"                     → MAKEUP / Far
"eyeliner|kalem"                        → MAKEUP / Eyeliner
"allık|blush|bronzer"                   → MAKEUP / Allık & Bronzer
"pudra|powder"                          → MAKEUP / Pudra
"primer"                                → MAKEUP / Primer

"serum"                                 → SKINCARE / Serum
"nemlendirici|moisturizer|cream|krem"   → SKINCARE / Nemlendirici
"temizleyici|cleanser|face wash|micel"  → SKINCARE / Yüz Temizleme
"maske|mask|peeling"                    → SKINCARE / Maske & Peeling
"spf|güneş|sun"                         → SKINCARE / Güneş Koruma
"anti-aging|age|kırışıklık|yaşlanma"    → SKINCARE / Anti-Aging
"tonik|toner"                           → SKINCARE / Tonik & Sprey

"parfüm|perfume|edp|edt|cologne"        → FRAGRANCE / (cinsiyet tespiti)
"şampuan|shampoo"                       → HAIRCARE / Şampuan
"saç kremi|conditioner"                 → HAIRCARE / Saç Kremi
"saç maskesi|hair mask"                 → HAIRCARE / Saç Maskesi

"diş macunu|toothpaste"                 → PERSONALCARE / Ağız Bakımı
"sabun|soap"                            → PERSONALCARE / Sabun
"deodorant|roll-on"                     → PERSONALCARE / Deodorant
"el kremi|hand cream"                   → PERSONALCARE / El & Ayak Bakımı
"vücut losyonu|body lotion"             → PERSONALCARE / Vücut Bakımı

"vitamin|takviye|supplement"            → WELLNESS / Takviye & Vitamin
"kolajen|collagen"                      → WELLNESS / Kolajen
"enerji|l-carnitine|kahve|coffee"       → WELLNESS / Enerji & Metabolizma
```

Eşleşme bulunamazsa `unmapped` listesine eklenir ve kullanıcıya manuel eşleme için sunulur.

### Teknik Gereksinimler

| Bileşen | Seçim | Gerekçe |
|---|---|---|
| Headless Browser | Puppeteer (Node) veya Playwright | JS-rendered siteleri destekler |
| HTML Parser | Cheerio (Node) veya BeautifulSoup (Python) | DOM'dan veri çıkarma |
| Keyword Matcher | Basit regex + sözlük | ML gerektirmez, deterministik |

### Hackathon Notu

Scraper tam otomatik çalışmak zorunda değil. Demo için:
1. Farmasi sitesini bir kez Puppeteer ile çek
2. Çıktıyı `products.json`'a kaydet
3. Demo sırasında "URL gir → çek" akışını göster
4. Eşleşmeyen ürünleri manuel düzelt

---

## 1.2 Veri İçe Aktarma Servisi (Multi-Tenant)

Şirketler kendi verilerini CSV veya JSON formatında yükleyebilir. Scraper kullanmak zorunda değiller.

### Veri Yükleme Akışı

```
Şirket Yöneticisi              Backend
──────────────────             ───────
  │                              │
  │ POST /api/data/import        │
  │ { tenantId, dataType,        │
  │   file (CSV/JSON) }          │
  │ ────────────────────────►    │
  │                              │  1. Dosyayı parse et
  │                              │  2. Alan eşlemesi yap
  │                              │  3. Veri doğrulama
  │                              │  4. /data/{tenantId}/ altına yaz
  │  { imported, errors }        │
  │ ◄────────────────────────    │
```

### API Endpoint'leri

#### `POST /api/tenant/register`

Yeni şirket kaydı oluşturur.

İstek:
```json
{
  "tenantId": "kozmetik-shop",
  "companyName": "Kozmetik Shop A.Ş.",
  "sector": "cosmetics",
  "contactEmail": "[email]"
}
```

Yanıt:
```json
{
  "tenantId": "kozmetik-shop",
  "apiKey": "ks_xxxxxxxxxxxx",
  "dataPath": "/data/kozmetik-shop/",
  "created": true
}
```

#### `GET /api/tenant/:tenantId/status`

Tenant'ın veri durumunu gösterir.

Yanıt:
```json
{
  "tenantId": "kozmetik-shop",
  "data": {
    "products": { "count": 120, "lastUpdated": "2026-02-12T10:00:00Z" },
    "customers": { "count": 5400, "lastUpdated": "2026-02-12T09:00:00Z" }
  },
  "ready": true
}
```

#### `POST /api/data/import`

CSV veya JSON dosyasını yükler.

İstek (multipart/form-data):
```
tenantId: "kozmetik-shop"
dataType: "products" | "customers"
file: products.csv
mappings: {                    // opsiyonel, alan eşleme
  "Ürün Kodu": "productId",
  "Ürün Adı": "productName",
  "Kategori": "category",
  "Stok": "currentStock",
  "Fiyat": "unitPrice",
  "Maliyet": "unitCost"
}
```

Yanıt:
```json
{
  "tenantId": "kozmetik-shop",
  "dataType": "products",
  "imported": 118,
  "skipped": 2,
  "errors": [
    { "row": 45, "field": "unitPrice", "error": "Sayısal değer bekleniyor" },
    { "row": 89, "field": "category", "error": "Bilinmeyen kategori: 'Aksesuar'" }
  ]
}
```

### Desteklenen Veri Formatları

| Veri Tipi | Zorunlu Alanlar | Opsiyonel Alanlar |
|---|---|---|
| products | productId, productName, category, unitPrice | subcategory, tags, season, currentStock, last30DaysSales, unitCost, sourceUrl |
| customers | customerId, city | region, age, gender, registeredAt, productHistory[] |

`productHistory[]` elemanları (opsiyonel):

| Alan | Zorunlu | Açıklama |
|---|---|---|
| productId | evet | Ürün kimliği |
| category | hayır | Ürün kategorisi (productId'den çözümlenebilir) |
| totalQuantity | evet | Toplam alınan adet |
| totalSpent | evet | Bu ürüne toplam harcanan tutar |
| orderCount | evet | Bu ürün için kaç kez sipariş verildi |
| firstPurchase | evet | İlk alım tarihi |
| lastPurchase | evet | Son alım tarihi |
| avgDaysBetween | hayır | Alımlar arası ortalama gün (null ise tek alım) |

Eksik opsiyonel alanlar için varsayılan değerler atanır:
- `unitCost` yoksa → `unitPrice * 0.35`
- `currentStock` yoksa → `500`
- `last30DaysSales` yoksa → `50`
- `region` yoksa → `city`'den `regions.json` ile çözümlenir
- `tags` yoksa → `category` + `subcategory`'den otomatik türetilir
- `productHistory` yoksa → `[]` (boş dizi, alışveriş verisi olmadan başlanabilir)

### Tenant Veri İzolasyonu

```
/data/
  ├── shared/
  │   └── regions.json              ← tüm tenant'lar ortak kullanır
  │
  ├── farmasi/
  │   ├── products.json
  │   ├── customers.json            ← productHistory[] gömülü
  │   └── catalog_sources.json
  │
  ├── kozmetik-shop/
  │   ├── products.json
  │   ├── customers.json            ← productHistory[] gömülü
  │   └── catalog_sources.json
  │
  └── guzellik-dunyasi/
      ├── products.json
      ├── customers.json            ← productHistory[] gömülü
      └── catalog_sources.json
```

Her tenant sadece kendi verisine erişebilir. `regions.json` paylaşımlıdır çünkü bölge/iklim verileri tüm şirketler için ortaktır. Alışveriş verileri ayrı dosya değildir — `customers.json` içindeki `productHistory[]` dizisinde ürün bazlı özet olarak gömülüdür.

---

## 2. Veri Akışı

```
İSTEK                            DAHİLİ                               YANIT
─────                            ──────                               ─────

{                          ┌──────────────┐
  tenantId: "...",         │ Orkestratör  │
  objective: "...",  ───►  │   Ajan       │
  city: "...",             └──────┬───────┘
  customerId?: "...",      │      │
  event?: "..."            │  tenant verisi yükle
}                          │  (/data/{tenantId}/)
                           │      │
                           │      ├──────────────────────┐
                           │      ▼                      ▼
                           │ ┌──────────────┐  ┌──────────────┐
                           │ │   Müşteri    │  │     Stok     │
                           │ │    Analiz    │  │    Analiz    │
                           │ │    Ajanı     │  │    Ajanı     │
                           │ └──────┬───────┘  └──────┬───────┘
                           │        │                 │
                           │  CustomerInsightJSON  StockInsightJSON
                           │        │                 │
                           │        └────────┬────────┘
                           │                 ▼
                           │        ┌──────────────────┐
                           │        │    Kampanya      │
                           │        │   Planlayıcı     │
                           │        │     Ajanı        │
                           │        └──────┬───────────┘
                           │               │
                           │          CampaignJSON
                           │               │
                           └───────────────┼──────────►  {
                                           │                campaign: { ... }
                                                         }
```

### Adım adım:

1. Frontend `/api/campaign` adresine `{ tenantId, objective, city, customerId?, event? }` gönderir
2. Orkestratör tenant'ı doğrular, `/data/{tenantId}/` altındaki verileri yükler (customers.json + products.json)
3. Orkestratör girdiyi doğrular, şehirden bölge ve iklim tipini çözümler
4. Orkestratör, Müşteri Analiz Ajanını `{ city, customerId?, customer, region, currentSeason }` ile çağırır
5. Orkestratör, Stok Analiz Ajanını `{ products, currentSeason, seasonalNeeds }` ile çağırır (paralel çalışabilir)
6. Müşteri Analiz Ajanı müşteri kaydındaki `productHistory[]` üzerinden segmentasyon yapar → `CustomerInsightJSON` döndürür
7. Stok Analiz Ajanı ürün stok durumunu analiz eder → `StockInsightJSON` döndürür
8. Orkestratör `{ objective, event?, customerInsight, stockInsight, regionContext }` verisini Kampanya Planlayıcıya iletir
9. Kampanya Planlayıcı hedef mantığını, marj tabanını, bölge filtresini, etkinlik modifiyesini uygular → `CampaignJSON` döndürür
10. Orkestratör son yanıtı sarmalayıp frontend'e döndürür

---

## 3. Ajan Sorumluluk Dağılımı

### 3.1 Orkestratör Ajan

| Özellik | Detay |
|---|---|
| Girdi | `{ tenantId, objective, city, customerId?, event? }` |
| Çıktı | Son `CampaignJSON` |
| Sorumluluklar | Tenant doğrulama, tenant verisini yükleme (customers + products), girdi doğrulama, şehir→bölge çözümleme, ajan sıralama, hata yönetimi |
| Yapmaz | Kampanya kararı almaz, veri analiz etmez, müşteri segmente etmez, stok analiz etmez |
| Döngü önleme | Tek geçiş: Müşteri Analiz + Stok Analiz → Planlayıcı. Tekrar deneme yok, geri bildirim döngüsü yok. |

```
dogrula(tenantId, girdi)
  → tenantVeri = yukle(tenantId)  // products, customers (productHistory gömülü)
  → musteriInsight = musteriAnalizAjani.calistir({ city, customerId, customer, region, currentSeason })
  → stokInsight = stokAnalizAjani.calistir({ products, currentSeason, seasonalNeeds })
  → kampanyaSonucu = kampanyaPlanlayici.calistir({ objective, event, customerInsight: musteriInsight, stockInsight: stokInsight, regionContext })
  → return kampanyaSonucu
```

### 3.2 Müşteri Analiz Ajanı

| Özellik | Detay |
|---|---|
| Girdi | `{ city, customerId?, customer, region, currentSeason }` |
| Çıktı | `CustomerInsightJSON` (müşteri segmentasyonu) |
| Sorumluluklar | Müşteri segmentasyonu, kategori yakınlığı, çeşitlilik profili, sadakat katmanı, düzenli ürün tespiti, bütçe tahmini |
| Yapmaz | Stok analiz etmez, kampanya üretmez, indirim belirlemez, strateji seçmez |

Temel hesaplamalar:
- Kayıp sınıflandırması (Aktif / Ilık / Riskli)
- Değer sınıflandırması (YüksekDeğer / Standart) — bölge medyanına göre
- Yaş segmenti (GenZ / GençYetişkin / Yetişkin / Olgun)
- Sadakat katmanı (Platin / Altın / Gümüş / Bronz)
- Kategori yakınlığı (en çok satın alınan kategori + Odaklı/Keşifçi)
- Çeşitlilik profili (Kaşif / Dengeli / Sadık)
- Düzenli ürünler (zamanı gelmiş ürünler)
- Bütçe tahmini (`avgBasket * 1.2`)

### 3.3 Stok Analiz Ajanı

| Özellik | Detay |
|---|---|
| Girdi | `{ products, currentSeason, seasonalNeeds }` |
| Çıktı | `StockInsightJSON` (stok performansı) |
| Sorumluluklar | Yıldız/yavaş ürün belirleme, envanter baskısı tespiti, mevsimsel uyum kontrolü, stok performans analizi |
| Yapmaz | Müşteri analiz etmez, kampanya üretmez, indirim belirlemez, strateji seçmez |

Temel hesaplamalar:
- Stok gün hesabı (`mevcutStok / (son30GunSatis / 30)`)
- Envanter baskısı bayrağı (`stokGunu > 60`)
- Yıldız ürünler (stok günü ≤20, satış hızına göre ilk 3)
- Yavaş hareket edenler (stok günü >60, satış hızına göre son 5)
- Mevsimsel uyum (`season === currentSeason` veya `tags` eşleşmesi)
- Brüt marj ve maksimum indirim hesabı

### 3.4 Kampanya Planlayıcı Ajanı

| Özellik | Detay |
|---|---|
| Girdi | `{ objective, event?, customerInsight, stockInsight, regionContext }` |
| Çıktı | `CampaignJSON` |
| Sorumluluklar | Strateji seçimi, marj tabanlı indirim hesabı, bölge bazlı ürün filtreleme, etkinlik mesajlaması, ürün önerileri |
| Yapmaz | Ham veri okumaz, müşteri segmente etmez, stok analiz etmez |

Temel kurallar:
- Marj tabanı: hiçbir indirim %75'i aşamaz (minimum %25 marj garantisi)
- Bölge filtresi: iklim tipine göre uygun ürün kategorileri önceliklendirilir
- Etkinlik modifiyesi: mesajlaşma/paketleme temasını ayarlar, hedefi geçersiz kılmaz
- Strateji seçimi hedef + segment kesişimine göre yapılır
- Ürün önerisi: müşteri profiline göre "bunu da deneyebilirsin" önerileri üretir (5 kural)

---

## 4. Veri Modelleri

### 4.1 Müşteri Kaydı (`customers.json`)

```json
{
  "customerId": "C-1001",
  "city": "Istanbul",
  "region": "Marmara",
  "age": 32,
  "gender": "F",
  "registeredAt": "2024-03-15",
  "productHistory": [
    { "productId": "P-2001", "category": "SKINCARE", "totalQuantity": 8, "totalSpent": 479.20, "orderCount": 8, "firstPurchase": "2025-01-15", "lastPurchase": "2026-01-20", "avgDaysBetween": 30 },
    { "productId": "P-2004", "category": "SKINCARE", "totalQuantity": 7, "totalSpent": 454.30, "orderCount": 5, "firstPurchase": "2025-02-10", "lastPurchase": "2026-02-01", "avgDaysBetween": 45 }
  ]
}
```

> Ürün bazlı alışveriş özeti (`productHistory[]`) müşteri kaydının içinde gömülüdür. Hangi üründen kaç tane aldığı, ne sıklıkla aldığı direkt görülür. Ayrı bir sipariş dosyası yoktur. Şirketler ürün verisi olmadan da sisteme başlayabilir — `productHistory` boş dizi olabilir.

### 4.2 Ürün/Stok Kaydı (`products.json`)

```json
{
  "productId": "P-2001",
  "productName": "Dr. C. Tuna Tea Tree Face Wash",
  "category": "SKINCARE",
  "subcategory": "Yüz Temizleme",
  "tags": ["temizleyici", "jel", "akne", "arındırıcı"],
  "season": "all",
  "currentStock": 900,
  "last30DaysSales": 75,
  "unitCost": 20.00,
  "unitPrice": 59.90
}
```

### 4.3 Bölge Yapılandırması (`regions.json`)

```json
{
  "regions": [
    {
      "name": "Marmara",
      "climateType": "Metropol",
      "medianBasket": 85.00,
      "trend": "Skincare",
      "cities": ["Istanbul", "Bursa", "Kocaeli"]
    },
    {
      "name": "Ege",
      "climateType": "Sıcak-Nemli",
      "medianBasket": 65.00,
      "trend": "Skincare",
      "cities": ["Izmir", "Mugla", "Aydin"]
    },
    {
      "name": "Akdeniz",
      "climateType": "Sıcak-Nemli",
      "medianBasket": 60.00,
      "trend": "Makeup",
      "cities": ["Antalya", "Mersin", "Adana"]
    },
    {
      "name": "İç Anadolu",
      "climateType": "Sıcak-Kuru",
      "medianBasket": 55.00,
      "trend": "Skincare",
      "cities": ["Ankara", "Konya", "Kayseri"]
    },
    {
      "name": "Karadeniz",
      "climateType": "Soğuk",
      "medianBasket": 50.00,
      "trend": "Skincare",
      "cities": ["Trabzon", "Samsun", "Rize"]
    },
    {
      "name": "Doğu Anadolu",
      "climateType": "Soğuk",
      "medianBasket": 45.00,
      "trend": "Skincare",
      "cities": ["Erzurum", "Van", "Kars"]
    },
    {
      "name": "Güneydoğu Anadolu",
      "climateType": "Sıcak-Kuru",
      "medianBasket": 50.00,
      "trend": "Perfume",
      "cities": ["Gaziantep", "Diyarbakir", "Sanliurfa"]
    }
  ],
  "stockDaysThreshold": 60
}
```

---

## 5. Örnek Girdi / Çıktı

### 5.1 İstek

```json
{
  "tenantId": "farmasi",
  "objective": "ClearOverstock",
  "city": "Istanbul",
  "customerId": "C-1001",
  "event": "MothersDay"
}
```

### 5.2 Müşteri Analiz Ajanı Çıktısı (`CustomerInsightJSON`)

```json
{
  "customerId": "C-1001",
  "city": "Istanbul",
  "region": "Marmara",
  "climateType": "Metropol",
  "age": 32,
  "ageSegment": "GençYetişkin",
  "gender": "F",
  "churnSegment": "Active",
  "valueSegment": "HighValue",
  "loyaltyTier": "Altın",
  "affinityCategory": "SKINCARE",
  "affinityType": "Odaklı",
  "diversityProfile": "Dengeli",
  "estimatedBudget": 102.60,
  "avgBasket": 85.50,
  "avgMonthlySpend": 171.00,
  "lastPurchaseDaysAgo": 12,
  "orderCount": 14,
  "totalSpent": 988.40,
  "membershipDays": 335,
  "missingRegulars": [
    {
      "productId": "P-2001",
      "productName": "Dr. C. Tuna Tea Tree Face Wash",
      "lastBought": "2026-01-20",
      "avgDaysBetween": 30,
      "daysOverdue": 5
    }
  ],
  "topProducts": [
    { "productId": "P-2001", "totalQuantity": 8, "totalSpent": 479.20, "lastBought": "2026-01-20" }
  ]
}
```

### 5.3 Stok Analiz Ajanı Çıktısı (`StockInsightJSON`)

```json
{
  "heroProducts": [
    {
      "productId": "P-2004",
      "productName": "Aloe Line Moisturizer",
      "category": "SKINCARE",
      "stockDays": 8,
      "dailySales": 3.17,
      "inventoryPressure": false,
      "seasonMatch": true
    }
  ],
  "slowMovers": [
    {
      "productId": "P-2003",
      "productName": "Dr. C. Tuna Sun Face Cream SPF50",
      "category": "SKINCARE",
      "stockDays": 95,
      "dailySales": 1.0,
      "inventoryPressure": true,
      "seasonMatch": false
    }
  ]
}
```

### 5.4 Kampanya Planlayıcı Çıktısı (`CampaignJSON`)

```json
{
  "campaignId": "CMP-20260212-IST-001",
  "tenantId": "farmasi",
  "objective": "ClearOverstock",
  "city": "Istanbul",
  "region": "Marmara",
  "event": "MothersDay",
  "targetSegment": {
    "churn": "Active",
    "value": "HighValue",
    "affinity": "Skincare",
    "ageSegment": "GençYetişkin",
    "climateType": "Metropol"
  },
  "strategy": {
    "type": "DiscountBundle",
    "description": "Yavaş hareket eden Makyaj ve Parfüm ürünlerini, trend olan Skincare yıldız ürünüyle indirimli paket yaparak stok eritme.",
    "discountPercent": 20,
    "marginCheck": {
      "floor": 25,
      "passed": true
    },
    "regionNote": "Metropol bölge — trend ve premium ürün çeşitliliği yüksek, geniş paket tercih edilir."
  },
  "products": {
    "hero": [{ "productId": "P-2010", "role": "anchor" }],
    "clearance": [
      { "productId": "P-2055", "role": "bundled", "discountPercent": 20 },
      { "productId": "P-2061", "role": "bundled", "discountPercent": 15 }
    ]
  },
  "messaging": {
    "headline": "Anneler Günü Cilt Bakım Paketi",
    "subtext": "Ona özel bir set hediye edin — favori cilt bakım ürünleri ve sürpriz ekstralar özel fiyatla.",
    "eventTheme": "MothersDay"
  },
  "recommendations": [
    {
      "productId": "P-2002",
      "productName": "Age Reversist Serum",
      "reason": "Cilt bakım yakınlığı + GençYetişkin yaş segmenti → anti-aging başlangıç ürünü",
      "matchScore": 0.87
    },
    {
      "productId": "P-6001",
      "productName": "Beauty Booster Collagen Chocolate",
      "reason": "Skincare odaklı müşteri → kolajen takviyesi ile içten dışa bakım",
      "matchScore": 0.72
    }
  ],
  "metadata": {
    "generatedAt": "2026-02-12T14:30:00Z",
    "agentVersion": "1.0.0"
  }
}
```

---

## 6. Karar Matrisi

### 6.1 Hedef × Segment → Strateji

| Hedef | Değer Segmenti | Kayıp Segmenti | Birincil Strateji | İndirim Tavanı |
|---|---|---|---|---|
| GelirArtır | YüksekDeğer | Aktif | Çapraz satış paketi (yıldız + tamamlayıcı) | %10 |
| GelirArtır | YüksekDeğer | Ilık | Yeniden etkileşim paketi + sadakat teşviki | %15 |
| GelirArtır | YüksekDeğer | Riskli | Geri kazanım teklifi + özel erişim | %20 |
| GelirArtır | Standart | Aktif | Daha yüksek sepete yükseltme | %10 |
| GelirArtır | Standart | Ilık | Kategori yakınlığı indirimi | %15 |
| GelirArtır | Standart | Riskli | Yeniden aktivasyon indirimi | %20 |
| StokErit | YüksekDeğer | Aktif | Yavaşları yıldızla paketle | %20 |
| StokErit | YüksekDeğer | Ilık | İndirimli paket + ücretsiz kargo | %25 |
| StokErit | YüksekDeğer | Riskli | Yavaş ürünlerde derin indirim | %30* |
| StokErit | Standart | Aktif | Yavaş ürünlerde flaş satış | %25 |
| StokErit | Standart | Ilık | Kategori tasfiyesi | %30* |
| StokErit | Standart | Riskli | Maksimum tasfiye indirimi | %35* |

*\*Minimum %25 marj tabanını korumak için maksimum %75 indirimle sınırlandırılır.*

### 6.2 Bölge-İklim × Ürün Filtresi

| İklim Tipi | Öncelikli Ürünler | Paketleme Notu |
|---|---|---|
| Metropol | Trend + premium, geniş kategori çeşitliliği | Büyük paketler, çoklu kategori |
| Sıcak-Nemli | SPF, hafif nemlendirici, mat makyaj | Yaz/güneş temalı paketler |
| Sıcak-Kuru | Yoğun nemlendirici, koruyucu bariyer kremleri | Koruma temalı paketler |
| Soğuk | Besleyici krem, dudak bakım, onarıcı serum | Kış bakım paketleri |

### 6.3 Müşteri ID Verilmediğinde

`customerId` belirtilmediğinde sistem bölge-toplu modunda çalışır:

| Hedef | Strateji |
|---|---|
| GelirArtır | Bölge trend kategorisini hedefle, bölge medyanı için çapraz satış paketleri |
| StokErit | En yüksek envanter baskısına sahip ürünlerde bölge çapında tasfiye |

### 6.4 Etkinlik Modifiye Etkisi

| Etkinlik | Mesajlaşma Etkisi | Paketleme Etkisi |
|---|---|---|
| AnnelerGunu | Hediye odaklı dil | Hediye seti paketleri tercih edilir |
| BlackFriday | Aciliyet + fırsat dili | Daha büyük paketler, daha yüksek indirim toleransı |
| SevgililerGunu | Romantik/çift dili | İkili paketler (ona + ona) |
| Yaz | Mevsimsel tazelik dili | Hafif/mevsimsel ürün tercihi |
| Yok | Nötr ürün dili | Standart paketleme |

Etkinlik yalnızca sunum katmanını değiştirir. Hedef mantığını veya segment hedeflemesini DEĞİŞTİRMEZ.

---

## 8. Hackathon Kısıtları İçin Risk Analizi

| Risk | Olasılık | Etki | Önlem |
|---|---|---|---|
| Ajan bağlantılarında zaman aşımı | Yüksek | Yüksek | Tüm JSON arayüzlerini önce tanımla (1. saat). Arayüzlere göre kodla. |
| Frontend cilalaması çok uzun sürer | Orta | Orta | Tek bir JSON görüntüleyici kart kullan. Süslü UI yok. Sadece Tailwind + hazır bileşenler. |
| Veri uç durumları (eksik müşteri, boş stok) | Yüksek | Orta | Bölge-toplu moduna düş. Uyarılarla kısmi sonuç döndür. |
| Döngüsel ajan çağrıları | Düşük | Yüksek | Mimari doğrusal akışı zorlar. Orkestratör dışında hiçbir ajan başka ajanı çağırmaz. |
| Kapsam kayması (ML ekleme, öneri motoru) | Orta | Yüksek | 1. saatten sonra kapsamı dondur. Sadece deterministik kurallar. |
| Demo başarısızlığı | Orta | Yüksek | Bilinen verilerle 2-3 altın yol demo senaryosu hazırla. Önce bunları test et. |

---

## 8. Sadeleştirme Kademeleri (Zaman Yetmezse)

### Kademe 1: Tam Uygulama (5 saat) ✅
4 ajan (Orkestratör + Müşteri Analiz + Stok Analiz + Kampanya Planlayıcı), dropdown'lu frontend, etkinlik modifiyesi, müşteri düzeyi + bölge düzeyi mod, iklim bazlı filtreleme.

### Kademe 2: Etkinlik Modifiyesini Çıkar (4 saat)
Etkinlik dropdown'ını ve modifiye mantığını kaldır. Kampanyalar sadece hedefe dayalı. ~30 dk tasarruf.

### Kademe 3: Bölge-Toplu Mod (3 saat)
`customerId` girdisini tamamen kaldır. Tüm kampanyalar bölge-toplu. Bireysel segmentasyon yok. ~1 saat tasarruf.

### Kademe 4: Tek Ajan + Frontend (2 saat)
Tüm mantığı tek fonksiyona topla. 4 ajan yapısını tek servis içinde "mantıksal modüller" olarak tut. Frontend çalışmaya devam eder.

### Kademe 5: Sadece Backend + Postman Demo (1.5 saat)
Frontend yok. Önceden hazırlanmış isteklerle Postman/curl üzerinden demo.

---

## 9. Önerilen Takım Dağılımı (3 Geliştirici × 5 Saat)

| Geliştirici | 1. Saat | 2-3. Saat | 4. Saat | 5. Saat |
|---|---|---|---|---|
| Gel. 1 (Backend Lider) | Tüm JSON arayüzlerini + veri dosyalarını tanımla | Orkestratör Ajan + API endpoint | Entegrasyon testi | Hata düzeltme + demo hazırlığı |
| Gel. 2 (Müşteri Analiz) | Müşteri Analiz Ajanı segmentasyon mantığı | Stok Analiz Ajanı stok performans mantığı | Kampanya Planlayıcı hedef mantığı + marj kuralları | Uç durum yönetimi |
| Gel. 3 (Frontend) | React SPA iskeleti + dropdown'lar | Kampanya kartı render'ı | API'ye bağlantı | Cilalama + demo senaryoları |

### 1. Saat Çıktısı (Kritik)
Herhangi bir mantık yazmadan önce üç geliştirici şu JSON sözleşmelerinde anlaşmalıdır:
- İstek şeması
- CustomerInsightJSON şeması
- StockInsightJSON şeması
- CampaignJSON şeması

Bu, hackathon'un en önemli saatidir.

---

## 9. Önerilen Takım Dağılımı (3 Geliştirici × 5 Saat)

| Geliştirici | 1. Saat | 2-3. Saat | 4. Saat | 5. Saat |
|---|---|---|---|---|
| Gel. 1 (Backend Lider) | Tüm JSON arayüzlerini + veri dosyalarını tanımla | Orkestratör Ajan + API endpoint | Entegrasyon testi | Hata düzeltme + demo hazırlığı |
| Gel. 2 (Mantık Lider) | Analiz Ajanı segmentasyon mantığı | Kampanya Planlayıcı hedef mantığı + marj kuralları | Etkinlik modifiyesi + bölge filtresi | Uç durum yönetimi |
| Gel. 3 (Frontend) | React SPA iskeleti + dropdown'lar | Kampanya kartı render'ı | API'ye bağlantı | Cilalama + demo senaryoları |

### 1. Saat Çıktısı (Kritik)
Herhangi bir mantık yazmadan önce üç geliştirici şu JSON sözleşmelerinde anlaşmalıdır:
- İstek şeması
- InsightJSON şeması
- CampaignJSON şeması

Bu, hackathon'un en önemli saatidir.

---

## 10. Teknoloji Yığını Önerisi

| Katman | Seçim | Gerekçe |
|---|---|---|
| Backend | Node.js + Express (veya Python + FastAPI) | Hızlı iskele, takım aşinalığı |
| Ajanlar | Düz fonksiyonlar/sınıflar (framework gerekmez) | Deterministik mantık, LLM çağrısı gerekmez |
| Scraper | Puppeteer + Cheerio (Node) veya Playwright + BeautifulSoup (Python) | JS-rendered siteleri destekler |
| Veri | Tenant bazlı JSON dosyaları (`/data/{tenantId}/`) | DB kurulum süresi yok, izolasyon basit |
| CSV Parser | csv-parse (Node) veya pandas (Python) | Şirketlerin CSV yüklemesi için |
| Frontend | React + Tailwind (veya sıkışırsanız düz HTML) | Tek sayfa, minimal bileşenler |
| API | `/api/campaign` + `/api/catalog/*` + `/api/data/*` + `/api/tenant/*` | Kampanya + katalog + veri yönetimi (products + customers) + tenant |
