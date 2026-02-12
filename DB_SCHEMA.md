# Veri Modeli ve İlişkiler

Bu doküman sistemin tüm veri yapılarını, ilişkilerini ve türetilen metrikleri tanımlar.

Sistem multi-tenant mimaride çalışır. Her şirketin (tenant) verileri `/data/{tenantId}/` altında izole tutulur.

---

## 0. Tenant Kaydı (`tenants.json`)

```json
{
  "tenants": [
    {
      "tenantId": "farmasi",
      "companyName": "Farmasi Türkiye",
      "sector": "cosmetics",
      "contactEmail": "[email]",
      "apiKey": "frm_xxxxxxxxxxxx",
      "createdAt": "2026-02-12T08:00:00Z",
      "settings": {
        "marginFloor": 25,
        "stockDaysThreshold": 60,
        "maxRecommendations": 3,
        "currency": "TRY"
      }
    }
  ]
}
```

| Alan | Tip | Açıklama |
|---|---|---|
| tenantId | string | Benzersiz şirket kimliği (URL-safe) |
| companyName | string | Şirket adı |
| sector | string | Sektör (cosmetics, fashion, electronics, vb.) |
| contactEmail | string | İletişim e-postası |
| apiKey | string | API erişim anahtarı |
| settings.marginFloor | number | Şirkete özel marj tabanı (varsayılan %25) |
| settings.stockDaysThreshold | number | Stok gün eşiği (varsayılan 60) |
| settings.maxRecommendations | number | Maksimum öneri sayısı |
| settings.currency | string | Para birimi |

Tenant'a özel ayarlar sayesinde her şirket kendi marj tabanını, stok eşiğini ve para birimini belirleyebilir.

---

## 1. Varlık İlişki Diyagramı

```
┌───────────────────────────┐                ┌──────────────┐
│        customers          │                │   products   │
├───────────────────────────┤                ├──────────────┤
│ customerId                │                │ productId    │
│ city                      │                │ productName  │
│ region                    │                │ category     │
│ age                       │                │ subcategory  │
│ gender                    │                │ tags[]       │
│ registeredAt              │                │ season       │
│ productHistory[] ─────────┼── productId ──►│ currentStock │
│   ├─ productId            │                │ unitCost     │
│   ├─ category             │                │ unitPrice    │
│   ├─ totalQuantity        │                │ sourceUrl    │
│   ├─ totalSpent           │                └──────────────┘
│   ├─ orderCount           │
│   ├─ firstPurchase        │
│   ├─ lastPurchase         │
│   └─ avgDaysBetween       │
└───────────────────────────┘
                       ┌──────────────────┐
                       │    regions       │       ┌──────────────────┐
                       ├──────────────────┤       │ catalog_sources  │
                       │ name             │       ├──────────────────┤
                       │ climateType      │       │ url              │
                       │ medianBasket     │       │ lastScraped      │
                       │ trend            │       │ productCount     │
                       │ seasonalNeeds[]  │       │ selectors        │
                       │ cities[]         │
                       └──────────────────┘
```

> **Not:** Sipariş verileri ayrı bir dosya değildir. `productHistory[]` dizisi müşterinin ürün bazlı alışveriş özetini içerir — hangi üründen kaç tane aldığı, ne sıklıkla aldığı. Şirketler sisteme sadece `customers.json` ve `products.json` yükleyerek başlayabilir.

---

## 2. Tablolar

### 2.1 customers.json

Müşteri profil bilgileri ve ürün bazlı alışveriş özeti tek dosyada tutulur. Şirketler sisteme sadece `customers.json` ve `products.json` yükleyerek başlayabilir — `productHistory` opsiyoneldir, boş dizi olabilir.

```json
{
  "customerId": "C-1001",
  "city": "Istanbul",
  "region": "Marmara",
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
    },
    {
      "productId": "P-2004",
      "category": "SKINCARE",
      "totalQuantity": 7,
      "totalSpent": 454.30,
      "orderCount": 5,
      "firstPurchase": "2025-02-10",
      "lastPurchase": "2026-02-01",
      "avgDaysBetween": 45
    },
    {
      "productId": "P-1002",
      "category": "MAKEUP",
      "totalQuantity": 1,
      "totalSpent": 54.90,
      "orderCount": 1,
      "firstPurchase": "2025-10-15",
      "lastPurchase": "2025-10-15",
      "avgDaysBetween": null
    }
  ]
}
```

| Alan | Tip | Açıklama |
|---|---|---|
| customerId | string | Benzersiz müşteri kimliği |
| city | string | Müşterinin şehri |
| region | string | Şehrin bağlı olduğu bölge (regions.json'dan türetilir) |
| age | number | Yaş |
| gender | string | "F", "M" veya null |
| registeredAt | date | Kayıt tarihi (sadakat hesabı için) |
| productHistory | array | Ürün bazlı alışveriş özeti (opsiyonel, boş dizi olabilir) |

#### productHistory[] Elemanları

| Alan | Tip | Açıklama |
|---|---|---|
| productId | string | Ürün kimliği |
| category | string | Ürün kategorisi (MAKEUP / SKINCARE / FRAGRANCE / PERSONALCARE / HAIRCARE / WELLNESS) |
| totalQuantity | number | Toplam alınan adet |
| totalSpent | number | Bu ürüne toplam harcanan tutar |
| orderCount | number | Bu ürün için kaç kez sipariş verildi |
| firstPurchase | date | İlk alım tarihi |
| lastPurchase | date | Son alım tarihi |
| avgDaysBetween | number | Alımlar arası ortalama gün (null ise tek alım) |

> **Avantajlar:** Ürün bazlı özet veri daha kompakt, analiz için daha hızlı. Hangi ürünü ne sıklıkla aldığı direkt görülür.

### 2.2 products.json

Ürün kataloğu ve stok bilgisi.

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

| Alan | Tip | Açıklama |
|---|---|---|
| productId | string | Benzersiz ürün kimliği |
| productName | string | Ürün adı |
| category | string | Ana kategori (MAKEUP / SKINCARE / FRAGRANCE / PERSONALCARE / HAIRCARE / WELLNESS) |
| subcategory | string | Alt kategori (Fondöten, Serum, Şampuan, vb.) |
| tags | string[] | Ürün etiketleri (iklim/yaş/cinsiyet/mevsim uyumu için) |
| season | string | "all", "winter", "summer", "spring", "autumn" |
| currentStock | number | Mevcut stok adedi |
| last30DaysSales | number | Son 30 gün satış adedi |
| unitCost | number | Birim maliyet |
| unitPrice | number | Birim satış fiyatı |

### 2.3 regions.json

Bölge yapılandırması — iklim, mevsimsel ihtiyaçlar, medyan sepet.

```json
{
  "regions": [
    {
      "name": "Marmara",
      "climateType": "Metropol",
      "medianBasket": 85.00,
      "trend": "Skincare",
      "seasonalNeeds": {
        "winter": ["nemlendirici", "dudak-bakım", "el-kremi"],
        "summer": ["SPF", "hafif-nemlendirici", "mat-makyaj"],
        "spring": ["anti-aging", "serum", "temizleyici"],
        "autumn": ["onarıcı", "besleyici-krem", "maske"]
      },
      "cities": ["Istanbul", "Bursa", "Kocaeli"]
    },
    {
      "name": "Ege",
      "climateType": "Sıcak-Nemli",
      "medianBasket": 65.00,
      "trend": "Skincare",
      "seasonalNeeds": {
        "winter": ["nemlendirici", "koruyucu-krem"],
        "summer": ["SPF", "hafif-nemlendirici", "mat-makyaj", "bronzlaştırıcı"],
        "spring": ["temizleyici", "tonik", "hafif-serum"],
        "autumn": ["nemlendirici", "onarıcı-serum"]
      },
      "cities": ["Izmir", "Mugla", "Aydin"]
    },
    {
      "name": "Akdeniz",
      "climateType": "Sıcak-Nemli",
      "medianBasket": 60.00,
      "trend": "Makeup",
      "seasonalNeeds": {
        "winter": ["nemlendirici", "dudak-bakım"],
        "summer": ["SPF", "bronzlaştırıcı", "su-bazlı-fondöten"],
        "spring": ["hafif-nemlendirici", "temizleyici"],
        "autumn": ["onarıcı", "nemlendirici"]
      },
      "cities": ["Antalya", "Mersin", "Adana"]
    },
    {
      "name": "İç Anadolu",
      "climateType": "Sıcak-Kuru",
      "medianBasket": 55.00,
      "trend": "Skincare",
      "seasonalNeeds": {
        "winter": ["yoğun-nemlendirici", "dudak-bakım", "el-kremi", "koruyucu-bariyer"],
        "summer": ["SPF", "hafif-nemlendirici"],
        "spring": ["nemlendirici", "temizleyici"],
        "autumn": ["yoğun-nemlendirici", "onarıcı-serum"]
      },
      "cities": ["Ankara", "Konya", "Kayseri"]
    },
    {
      "name": "Karadeniz",
      "climateType": "Soğuk",
      "medianBasket": 50.00,
      "trend": "Skincare",
      "seasonalNeeds": {
        "winter": ["besleyici-krem", "dudak-bakım", "koruyucu-serum", "el-kremi"],
        "summer": ["hafif-nemlendirici", "SPF"],
        "spring": ["nemlendirici", "temizleyici"],
        "autumn": ["besleyici-krem", "onarıcı-serum", "maske"]
      },
      "cities": ["Trabzon", "Samsun", "Rize"]
    },
    {
      "name": "Doğu Anadolu",
      "climateType": "Soğuk",
      "medianBasket": 45.00,
      "trend": "Skincare",
      "seasonalNeeds": {
        "winter": ["yoğun-besleyici-krem", "dudak-bakım", "el-kremi", "koruyucu-bariyer"],
        "summer": ["nemlendirici", "SPF"],
        "spring": ["nemlendirici", "onarıcı"],
        "autumn": ["besleyici-krem", "koruyucu-serum"]
      },
      "cities": ["Erzurum", "Van", "Kars"]
    },
    {
      "name": "Güneydoğu Anadolu",
      "climateType": "Sıcak-Kuru",
      "medianBasket": 50.00,
      "trend": "Perfume",
      "seasonalNeeds": {
        "winter": ["yoğun-nemlendirici", "dudak-bakım"],
        "summer": ["SPF", "mat-makyaj", "hafif-parfüm"],
        "spring": ["nemlendirici", "temizleyici"],
        "autumn": ["nemlendirici", "koruyucu-krem"]
      },
      "cities": ["Gaziantep", "Diyarbakir", "Sanliurfa"]
    }
  ],
  "stockDaysThreshold": 60
}
```

---

## 3. Türetilen Veriler (Analiz Ajanı Hesaplar)

Aşağıdaki metrikler ham veriden türetilir ve `InsightJSON` içinde döndürülür.

### 3.1 Müşteri Türetilen Metrikleri

Tüm hesaplamalar müşteri kaydındaki `productHistory[]` dizisi üzerinden yapılır.

```
products = customer.productHistory
```

| Metrik | Formül | Açıklama |
|---|---|---|
| lastPurchaseDaysAgo | `bugün - max(products.map(p => p.lastPurchase))` | Son alışverişten bu yana geçen gün |
| totalSpent | `sum(products.map(p => p.totalSpent))` | Toplam harcama |
| totalOrders | `sum(products.map(p => p.orderCount))` | Toplam sipariş sayısı |
| avgBasket | `totalSpent / totalOrders` | Ortalama sepet tutarı |
| avgMonthlySpend | `totalSpent / aktifAySayısı` | Aylık ortalama harcama |
| membershipDays | `bugün - registeredAt` | Üyelik süresi (gün) |
| uniqueProducts | `products.length` | Kaç farklı ürün aldı |

#### Bütçe Tahmini

Müşterinin geçmiş harcamalarından tahmini kampanya bütçesi türetilir:

```
estimatedBudget = avgBasket * 1.2  // ortalama sepetin %20 üstü tolerans

Kampanya planlayıcı bu bütçeyi aşan paketler önermez.
Bütçe aşılırsa:
  - Paketten ürün çıkar (en düşük öncelikli)
  - Veya daha küçük ambalaj/adet önerilir
```

#### Sadakat Skoru

```
sadakatPuanı hesaplama:

membershipMonths = membershipDays / 30
orderFrequency = totalOrders / membershipMonths  // aylık sipariş sıklığı

if (membershipMonths >= 12 && orderFrequency >= 2) → "Platin"
else if (membershipMonths >= 6 && orderFrequency >= 1) → "Altın"
else if (totalOrders >= 3) → "Gümüş"
else → "Bronz"
```

| Sadakat | Koşul | Kampanya Etkisi |
|---|---|---|
| Platin | ≥12 ay üye, aylık ≥2 sipariş | Özel erişim, erken kampanya, ekstra hediye, düşük indirim yeterli |
| Altın | ≥6 ay üye, aylık ≥1 sipariş | Sadakat bonusu, ücretsiz kargo, orta indirim |
| Gümüş | ≥3 sipariş | Standart kampanya + küçük teşvik |
| Bronz | Yeni/az alışveriş | Tanışma indirimi, ilk alışveriş bonusu |

#### Kategori Eğilimi

```
categoryBreakdown = grupla(products, category)
  → { "SKINCARE": { totalSpent: 1200, orderCount: 12 }, "FRAGRANCE": { totalSpent: 300, orderCount: 2 } }

affinityCategory = en yüksek totalSpent'e sahip kategori
affinityRatio = affinityCategory.orderCount / totalOrders  // ne kadar odaklı

if (affinityRatio > 0.6) → "Odaklı" (tek kategoriye sadık)
else → "Keşifçi" (birden fazla kategori deniyor)
```

#### Alışveriş Çeşitlilik Analizi

Müşteri hep aynı ürünleri mi alıyor, farklı ürünler mi deniyor?

```
uniqueProducts = products.length
totalPurchases = sum(products.map(p => p.orderCount))

diversityRatio = uniqueProducts / totalPurchases

if (diversityRatio > 0.7) → "Kaşif" (sürekli yeni ürün deniyor)
else if (diversityRatio > 0.4) → "Dengeli" (bazı favoriler + yeni denemeler)
else → "Sadık" (aynı ürünleri tekrar alıyor)
```

| Çeşitlilik | Kampanya Etkisi |
|---|---|
| Kaşif | Yeni ürünler, deneme boyları, keşif paketleri öner |
| Dengeli | Favori ürün + 1 yeni ürün karışımı |
| Sadık | Favori ürünlerde miktar indirimi, stok garantisi, abonelik teklifi |

#### Dönemsel Alışveriş Tespiti

Müşterinin düzenli aldığı ürünleri tespit et ve bu dönem alıp almadığını kontrol et.

```
// Ortalama alım sıklığı 60 günden az olan ürünler = düzenli ürünler
düzenliÜrünler = products.filter(p => p.avgDaysBetween !== null && p.avgDaysBetween <= 60)

// Bu ay alınmış mı?
buAyAlınanlar = products.filter(p => ayFarkı(p.lastPurchase) === 0).map(p => p.productId)

// Düzenli ürünlerden bu ay alınmayanlar
eksikDüzenliÜrünler = düzenliÜrünler.filter(p => {
  const daysSinceLastPurchase = bugün - p.lastPurchase;
  const isOverdue = daysSinceLastPurchase > p.avgDaysBetween * 1.2;  // %20 tolerans
  return isOverdue && !buAyAlınanlar.includes(p.productId);
})
```

| Durum | Kampanya Etkisi |
|---|---|
| Düzenli ürün zamanı gelmiş | Hatırlatma + küçük teşvik ile kampanyaya dahil et |
| Düzenli ürün bu ay alınmış | Bu ürünü kampanyadan çıkar, farklı ürün öner |
| Düzenli ürün yok | Normal segmentasyon kuralları geçerli |

### 3.2 Ürün Türetilen Metrikleri

```
günlükSatış = last30DaysSales / 30
stokGunu = currentStock / günlükSatış
envanterBaskısı = stokGunu > stockDaysThreshold
brütMarj = ((unitPrice - unitCost) / unitPrice) * 100
maksİndirim = brütMarj - 25
```

### 3.3 Mevsimsel Uyum

Mevcut mevsim + bölge ihtiyaçları + ürün etiketleri kesişimi:

```
mevsim = getCurrentSeason()  // orderDate veya sistem tarihinden
bölgeİhtiyaçları = regions.find(r => r.cities.includes(city)).seasonalNeeds[mevsim]
ürünEtiketleri = product.tags

mevsimselUyum = bölgeİhtiyaçları.filter(tag => ürünEtiketleri.includes(tag)).length > 0

Ayrıca ürünün season alanı kontrol edilir:
  product.season === "all" → her zaman uygun
  product.season === mevsim → uygun
  aksi halde → düşük öncelik
```

---

## 4. Güncellenmiş InsightJSON Şeması

Analiz Ajanının döndürdüğü tam yapı:

```json
{
  "customer": {
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
    "affinityCategory": "Skincare",
    "affinityType": "Odaklı",
    "diversityProfile": "Dengeli",
    "estimatedBudget": 102.60,
    "avgBasket": 85.50,
    "avgMonthlySpend": 171.00,
    "lastPurchaseDaysAgo": 12,
    "missingRegulars": [
      { "productId": "P-2001", "productName": "Dr. C. Tuna Tea Tree Face Wash", "lastBought": "2026-01-20", "avgDaysBetween": 30, "daysOverdue": 5 }
    ],
    "topProducts": [
      { "productId": "P-2001", "totalQuantity": 8, "totalSpent": 479.20, "lastBought": "2026-01-20" },
      { "productId": "P-2004", "totalQuantity": 7, "totalSpent": 454.30, "lastBought": "2026-02-01" }
    ]
  },
  "stock": {
    "heroProducts": [
      { "productId": "P-2010", "category": "Skincare", "stockDays": 8, "inventoryPressure": false, "seasonMatch": true }
    ],
    "slowMovers": [
      { "productId": "P-2055", "category": "Makeup", "stockDays": 95, "inventoryPressure": true, "seasonMatch": false },
      { "productId": "P-2061", "category": "Perfume", "stockDays": 120, "inventoryPressure": true, "seasonMatch": true }
    ]
  },
  "regionContext": {
    "region": "Marmara",
    "climateType": "Metropol",
    "medianBasket": 85.00,
    "trend": "Skincare",
    "currentSeason": "winter",
    "seasonalNeeds": ["nemlendirici", "dudak-bakım", "el-kremi"]
  }
}
```

---

## 5. Kampanya Planlayıcı Karar Akışı (Güncellenmiş)

```
Girdi: objective + event? + InsightJSON
         │
         ▼
    ┌─ 1. Bütçe Kontrolü ─────────────────────────────┐
    │ estimatedBudget = müşteri avgBasket * 1.2         │
    │ Paket toplam fiyatı bütçeyi aşmamalı             │
    └──────────────────────────┬────────────────────────┘
                               │
                               ▼
    ┌─ 2. Sadakat Katmanı ─────────────────────────────┐
    │ Platin → özel erişim, ekstra hediye              │
    │ Altın  → sadakat bonusu, ücretsiz kargo          │
    │ Gümüş  → standart + küçük teşvik                 │
    │ Bronz  → tanışma indirimi                        │
    └──────────────────────────┬────────────────────────┘
                               │
                               ▼
    ┌─ 3. Düzenli Ürün Kontrolü ───────────────────────┐
    │ missingRegulars varsa → kampanyaya dahil et       │
    │ Bu ay alınmış ürünler → kampanyadan çıkar         │
    └──────────────────────────┬────────────────────────┘
                               │
                               ▼
    ┌─ 4. Çeşitlilik Profili ──────────────────────────┐
    │ Kaşif  → yeni ürünler öner                       │
    │ Dengeli → favori + 1 yeni                        │
    │ Sadık  → favori ürünlerde miktar indirimi         │
    └──────────────────────────┬────────────────────────┘
                               │
                               ▼
    ┌─ 5. Mevsim + Bölge Filtresi ─────────────────────┐
    │ seasonalNeeds etiketleriyle ürün eşleştir         │
    │ Mevsime uygun ürünleri önceliklendir              │
    └──────────────────────────┬────────────────────────┘
                               │
                               ▼
    ┌─ 6. Yaş + Cinsiyet Filtresi ─────────────────────┐
    │ GenZ → trend, düşük fiyat                        │
    │ Olgun → premium, anti-aging                      │
    │ M → erkek bakım, parfüm                          │
    └──────────────────────────┬────────────────────────┘
                               │
                               ▼
    ┌─ 7. Hedef Mantığı (objective) ───────────────────┐
    │ GelirArtır → çapraz satış, upsell               │
    │ StokErit  → indirimli paket, tasfiye             │
    └──────────────────────────┬────────────────────────┘
                               │
                               ▼
    ┌─ 8. Marj + Bütçe Son Kontrol ────────────────────┐
    │ Her ürün marj tabanı ≥%25                        │
    │ Paket toplamı ≤ estimatedBudget                  │
    └──────────────────────────┬────────────────────────┘
                               │
                               ▼
                         CampaignJSON
```


---

## 5. Katalog Kaynakları (`catalog_sources.json`)

Daha önce scrape edilen sitelerin kaydı.

```json
{
  "sources": [
    {
      "url": "https://farmasi.com.tr/farmasi",
      "lastScraped": "2026-02-12T15:00:00Z",
      "productCount": 48,
      "selectors": {
        "productCard": ".product-card",
        "name": ".product-name",
        "price": ".product-price",
        "category": ".breadcrumb"
      }
    }
  ]
}
```

| Alan | Tip | Açıklama |
|---|---|---|
| url | string | Kaynak site URL'si |
| lastScraped | date | Son çekim zamanı |
| productCount | number | Çekilen ürün sayısı |
| selectors | object | Site için CSS seçiciler (opsiyonel, sonraki çekimlerde tekrar kullanılır) |

`products.json` içindeki her ürüne `sourceUrl` alanı eklenir:

```json
{
  "productId": "P-1001",
  "productName": "VFX Pro Camera Ready Foundation",
  "sourceUrl": "https://farmasi.com.tr/farmasi",
  ...
}
```

---

## 6. Ürün Öneri Mantığı

Kampanya Planlayıcı, kampanya ürünlerinin yanında "bunu da deneyebilirsin" önerileri üretir.

### 6.1 Öneri Kuralları

```
Girdi: InsightJSON (müşteri profili + stok durumu)

1. Kategori Genişletme
   Müşteri affinityCategory dışındaki kategorilerden,
   yaş segmentine uygun ürünler öner.
   
   Örnek: Skincare odaklı GenZ → trend Makyaj ürünü öner

2. Bölge-Mevsim Uyumu
   Müşterinin bölge iklim tipi + mevcut mevsime uygun,
   daha önce almadığı ürünleri öner.
   
   Örnek: Kış + Soğuk bölge → besleyici el kremi (daha önce almamış)

3. Tamamlayıcı Ürün
   Müşterinin düzenli aldığı ürünlerin tamamlayıcılarını öner.
   
   Örnek: Şampuan alıyor → aynı serinin saç maskesini öner

4. Yaş-Uygun Yükseltme
   Yaş segmenti geçişine uygun ürünler öner.
   
   Örnek: 34 yaş (GençYetişkin üst sınır) → anti-aging başlangıç serumu

5. Çeşitlilik Profiline Göre
   Kaşif → tamamen yeni kategori/ürün
   Sadık → favori ürünün premium versiyonu
   Dengeli → favori kategoriden yeni ürün
```

### 6.2 Öneri Skoru Hesaplama

```
matchScore = (
  kategoriUyumu * 0.3 +
  mevsimUyumu * 0.2 +
  yaşUyumu * 0.2 +
  tamamlayıcıBonus * 0.15 +
  çeşitlilikUyumu * 0.15
)

kategoriUyumu:
  Aynı kategori → 0.5
  Tamamlayıcı kategori → 0.8
  Yeni kategori (Kaşif profil) → 1.0

mevsimUyumu:
  Ürün mevsim etiketleri ∩ bölge seasonalNeeds → 0-1

yaşUyumu:
  Ürün etiketleri ∩ yaş segmenti öncelikli etiketler → 0-1

tamamlayıcıBonus:
  Aynı seri/marka ürünü → 1.0
  Farklı seri ama aynı ihtiyaç → 0.5

çeşitlilikUyumu:
  Kaşif + yeni ürün → 1.0
  Sadık + favori ürün varyantı → 1.0
  Uyumsuz → 0.2
```

### 6.3 CampaignJSON'daki Öneri Çıktısı

```json
"recommendations": [
  {
    "productId": "P-2002",
    "productName": "Age Reversist Serum",
    "reason": "Cilt bakım yakınlığı + GençYetişkin yaş segmenti → anti-aging başlangıç ürünü",
    "matchScore": 0.87,
    "matchFactors": {
      "kategoriUyumu": 0.5,
      "mevsimUyumu": 0.8,
      "yaşUyumu": 1.0,
      "tamamlayıcıBonus": 1.0,
      "çeşitlilikUyumu": 0.8
    }
  }
]
```

Öneriler kampanya paketinin parçası değildir — ayrı bir "keşfet" bölümü olarak sunulur. Maksimum 3 öneri döndürülür, `matchScore > 0.5` olanlar filtrelenir.
