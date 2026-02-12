# Analiz Ajanı Dökümanı

## Sorumluluk

Analiz Ajanı, müşteri ve ürün verilerini analiz eder. Segmentasyon yapar, stok durumunu değerlendirir, bölge bağlamını ekler. **Kampanya kararı almaz** — sadece veri analizi yapar.

---

## Girdi

```json
{
  "city": "Istanbul",
  "customerId": "C-1001",  // opsiyonel
  "customers": [ /* customers.json */ ],
  "products": [ /* products.json */ ],
  "regions": { /* regions.json */ }
}
```

---

## Çıktı (InsightJSON)

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
      { "productId": "P-2001", "totalQuantity": 8, "totalSpent": 479.20, "lastBought": "2026-01-20" },
      { "productId": "P-2004", "totalQuantity": 7, "totalSpent": 454.30, "lastBought": "2026-02-01" }
    ]
  },
  "stock": {
    "heroProducts": [
      {
        "productId": "P-2004",
        "productName": "Aloe Line Moisturizer",
        "category": "SKINCARE",
        "stockDays": 8,
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
        "inventoryPressure": true,
        "seasonMatch": false
      }
    ]
  },
  "regionContext": {
    "region": "Marmara",
    "climateType": "Metropol",
    "medianBasket": 85.00,
    "trend": "SKINCARE",
    "currentSeason": "winter",
    "seasonalNeeds": ["nemlendirici", "dudak-bakım", "el-kremi"]
  }
}
```

`customerId` yoksa `customer` objesi bölge bazlı genel profil içerir.

---

## Segmentasyon Tabloları

### Yaş Segmenti

| Segment | Yaş Aralığı | Ürün Eğilimi | Kampanya Yaklaşımı |
|---|---|---|---|
| GenZ | 18-25 | Makyaj, trend ürünler, düşük fiyat | Sosyal medya odaklı, influencer, deneme boyları |
| GençYetişkin | 26-35 | Cilt bakım, anti-aging başlangıç | Kalite-fiyat dengesi, rutin oluşturma |
| Yetişkin | 36-50 | Premium cilt bakım, parfüm | Lüks paketler, sadakat programları |
| Olgun | 51+ | Anti-aging, özel bakım | Premium ürünler, uzman tavsiyesi |

### Kayıp (Churn) Segmenti

| Segment | Son Alışveriş | Durum | Kampanya Stratejisi |
|---|---|---|---|
| Aktif | < 30 gün | Düzenli alışveriş yapıyor | Çapraz satış, yeni ürün tanıtımı, düşük indirim |
| Ilık | 30-60 gün | Etkileşim azalmış | Hatırlatma, orta indirim, sadakat bonusu |
| Riskli | > 60 gün | Kaybedilme riski yüksek | Geri kazanım, yüksek indirim, özel teklif |

### Değer Segmenti

| Segment | Koşul | Profil | Kampanya Yaklaşımı |
|---|---|---|---|
| YüksekDeğer | avgBasket > bölge medyanı | Yüksek harcama yapıyor | Premium paketler, özel erişim, düşük indirim yeterli |
| Standart | avgBasket ≤ bölge medyanı | Ortalama harcama | Değer odaklı paketler, fiyat avantajı |

### Sadakat Katmanı

| Katman | Koşul | Kampanya Avantajları |
|---|---|---|
| Platin | ≥12 ay üye, aylık ≥2 sipariş | Özel erişim, erken kampanya, ekstra hediye, VIP muamele |
| Altın | ≥6 ay üye, aylık ≥1 sipariş | Sadakat bonusu, ücretsiz kargo, öncelikli destek |
| Gümüş | ≥3 sipariş | Standart kampanya + küçük teşvik, puan kazanımı |
| Bronz | Yeni/az alışveriş | Tanışma indirimi, ilk alışveriş bonusu, hoş geldin paketi |

### Kategori Yakınlığı

| Tip | Koşul | Profil | Kampanya Yaklaşımı |
|---|---|---|---|
| Odaklı | affinityRatio > 0.6 | Tek kategoriye sadık | Favori kategoriden derinlemesine ürünler, kategori uzmanı |
| Keşifçi | affinityRatio ≤ 0.6 | Birden fazla kategori deniyor | Çapraz kategori paketler, keşif setleri |

### Çeşitlilik Profili

| Profil | Koşul | Alışveriş Davranışı | Kampanya Stratejisi |
|---|---|---|---|
| Kaşif | diversityRatio > 0.7 | Sürekli yeni ürün deniyor | Yeni ürünler, deneme boyları, keşif paketleri, sürpriz ürünler |
| Dengeli | 0.4 < diversityRatio ≤ 0.7 | Bazı favoriler + yeni denemeler | Favori ürün + 1 yeni ürün karışımı, dengeli paketler |
| Sadık | diversityRatio ≤ 0.4 | Aynı ürünleri tekrar alıyor | Favori ürünlerde miktar indirimi, stok garantisi, abonelik |

### Bölge-İklim Segmenti

| İklim Tipi | Bölgeler | Öncelikli Ürünler | Paketleme Yaklaşımı |
|---|---|---|---|
| Metropol | Marmara | Trend + premium, geniş çeşitlilik | Büyük paketler, çoklu kategori, şehirli yaşam |
| Sıcak-Nemli | Ege, Akdeniz | SPF, hafif nemlendirici, mat makyaj | Yaz/güneş temalı, plaj hazırlığı |
| Sıcak-Kuru | İç Anadolu, G.Doğu | Yoğun nemlendirici, koruyucu bariyer | Koruma temalı, nem kilidi |
| Soğuk | Karadeniz, D.Anadolu | Besleyici krem, dudak bakım, onarıcı | Kış bakım, soğuktan koruma |

### Müşteri Segment Matrisi (Kayıp × Değer)

| | Aktif | Ilık | Riskli |
|---|---|---|---|
| **YüksekDeğer** | Sadık VIP<br/>→ Çapraz satış, yeni ürün, %5-10 | Soğuyan VIP<br/>→ Yeniden etkileşim, sadakat, %10-15 | Kaybedilen VIP<br/>→ Geri kazanım, özel teklif, %15-20 |
| **Standart** | Düzenli Alıcı<br/>→ Sepet yükseltme, kategori genişletme, %10 | Uzaklaşan Alıcı<br/>→ Hatırlatma, kategori indirimi, %15 | Kayıp Alıcı<br/>→ Reaksiyon indirimi, son şans, %20-25 |

### Düzenli Ürün Durumu

| Durum | Tespit | Kampanya Etkisi |
|---|---|---|
| Zamanı Gelmiş | `daysSinceLastPurchase > avgDaysBetween * 1.2` | Hatırlatma + küçük teşvik, "Zamanı geldi" mesajı |
| Henüz Erken | `daysSinceLastPurchase < avgDaysBetween * 0.8` | Kampanyadan çıkar, farklı ürün öner |
| Düzenli Değil | `avgDaysBetween === null` veya `> 60` | Normal segmentasyon kuralları |

---

## İş Akışı

Analiz Ajanı 3 ana bölümde çalışır:

1. **Bölge Analizi** — Şehirden bölge, iklim, mevsim bilgisi
2. **Müşteri Analizi** — Segmentasyon ve profil çıkarma (customerId varsa)
3. **Stok Analizi** — Ürün performansı ve envanter durumu

---

## 1. Bölge Analizi

```javascript
const region = regions.regions.find(r => r.cities.includes(city));
const currentSeason = getCurrentSeason();  // winter, spring, summer, autumn
const seasonalNeeds = region.seasonalNeeds[currentSeason];

// Çıktı
const regionContext = {
  region: region.name,
  climateType: region.climateType,
  medianBasket: region.medianBasket,
  trend: region.trend,
  currentSeason,
  seasonalNeeds
};
```

**Mevsim Belirleme:**
```javascript
function getCurrentSeason() {
  const month = new Date().getMonth() + 1;
  if (month >= 3 && month <= 5) return "spring";
  if (month >= 6 && month <= 8) return "summer";
  if (month >= 9 && month <= 11) return "autumn";
  return "winter";
}
```

---

## 2. Müşteri Analizi

### 2.1 Veri Hazırlama

### 2.1 Veri Hazırlama

```javascript
if (!customerId) {
  // Bölge modu — 2.7'ye atla
  return getRegionProfile(city, region);
}

const customer = customers.find(c => c.customerId === customerId);
const products = customer.productHistory;

// Boş productHistory kontrolü
if (products.length === 0) {
  // Yeni müşteri — varsayılan değerler
  return getNewCustomerProfile(customer, region);
}
```

### 2.2 Temel Metrikler

```javascript
// Türetilen metrikler
const lastPurchaseDaysAgo = daysSince(max(products.map(p => p.lastPurchase)));
const totalSpent = sum(products.map(p => p.totalSpent));
const totalOrders = sum(products.map(p => p.orderCount));
const avgBasket = totalSpent / totalOrders;
const membershipDays = daysSince(customer.registeredAt);
const avgMonthlySpend = totalSpent / (membershipDays / 30);
```

### 2.3 Yaş Segmenti

```javascript
const ageSegment = 
  customer.age <= 25 ? "GenZ" :
  customer.age <= 35 ? "GençYetişkin" :
  customer.age <= 50 ? "Yetişkin" : "Olgun";
```

**Referans:** Yaş Segmenti tablosuna bakın.

### 2.4 Kayıp Segmenti

```javascript
const churnSegment = 
  lastPurchaseDaysAgo > 60 ? "Riskli" :
  lastPurchaseDaysAgo >= 30 ? "Ilık" : "Aktif";
```

**Referans:** Kayıp (Churn) Segmenti tablosuna bakın.

### 2.5 Değer Segmenti

```javascript
const valueSegment = avgBasket > region.medianBasket ? "HighValue" : "Standard";
```

**Referans:** Değer Segmenti tablosuna bakın.

### 2.6 Sadakat Katmanı

```javascript
const membershipMonths = membershipDays / 30;
const orderFrequency = totalOrders / membershipMonths;

const loyaltyTier = 
  (membershipMonths >= 12 && orderFrequency >= 2) ? "Platin" :
  (membershipMonths >= 6 && orderFrequency >= 1) ? "Altın" :
  (totalOrders >= 3) ? "Gümüş" : "Bronz";
```

**Referans:** Sadakat Katmanı tablosuna bakın.

### 2.7 Kategori Yakınlığı

```javascript
// Kategori bazında toplam harcama ve sipariş sayısı
const categoryBreakdown = groupBy(products, 'category', (items) => ({
  totalSpent: sum(items.map(p => p.totalSpent)),
  orderCount: sum(items.map(p => p.orderCount))
}));

// En çok harcama yapılan kategori
const affinityCategory = maxKey(categoryBreakdown, 'totalSpent');
const affinityRatio = categoryBreakdown[affinityCategory].orderCount / totalOrders;
const affinityType = affinityRatio > 0.6 ? "Odaklı" : "Keşifçi";
```

**Referans:** Kategori Yakınlığı tablosuna bakın.

### 2.8 Çeşitlilik Profili

```javascript
const uniqueProducts = products.length;
const diversityRatio = uniqueProducts / totalOrders;

const diversityProfile = 
  diversityRatio > 0.7 ? "Kaşif" :
  diversityRatio > 0.4 ? "Dengeli" : "Sadık";
```

**Referans:** Çeşitlilik Profili tablosuna bakın.

### 2.9 Bütçe Tahmini

```javascript
const estimatedBudget = avgBasket * 1.2;  // %20 tolerans
```

Kampanya Planlayıcı bu bütçeyi aşan paketler önermez.

### 2.10 Düzenli Ürünler

```javascript
// Ortalama alım sıklığı 60 günden az olan ürünler
const regulars = products.filter(p => 
  p.avgDaysBetween !== null && 
  p.avgDaysBetween <= 60
);

// Zamanı gelmiş düzenli ürünler (%20 tolerans)
const missingRegulars = regulars.filter(p => {
  const daysSinceLastPurchase = daysSince(p.lastPurchase);
  const daysOverdue = daysSinceLastPurchase - p.avgDaysBetween;
  return daysSinceLastPurchase > p.avgDaysBetween * 1.2;
}).map(p => ({
  productId: p.productId,
  productName: getProductName(p.productId),  // products.json'dan
  lastBought: p.lastPurchase,
  avgDaysBetween: p.avgDaysBetween,
  daysOverdue: daysSince(p.lastPurchase) - p.avgDaysBetween
}));
```

**Referans:** Düzenli Ürün Durumu tablosuna bakın.

### 2.11 En Çok Alınan Ürünler

```javascript
const topProducts = products
  .sort((a, b) => b.totalSpent - a.totalSpent)
  .slice(0, 5)
  .map(p => ({
    productId: p.productId,
    totalQuantity: p.totalQuantity,
    totalSpent: p.totalSpent,
    lastBought: p.lastPurchase
  }));
```

### 2.12 Müşteri Profili Çıktısı

```javascript
const customerInsight = {
  customerId: customer.customerId,
  city: customer.city,
  region: region.name,
  climateType: region.climateType,
  age: customer.age,
  ageSegment,
  gender: customer.gender,
  churnSegment,
  valueSegment,
  loyaltyTier,
  affinityCategory,
  affinityType,
  diversityProfile,
  estimatedBudget,
  avgBasket,
  avgMonthlySpend,
  lastPurchaseDaysAgo,
  orderCount: totalOrders,
  totalSpent,
  membershipDays,
  missingRegulars,
  topProducts
};
```

---

## 3. Stok Analizi

Tüm ürünler için stok performansı hesaplanır (müşteri bağımsız).

### 3.1 Stok Metrikleri

```javascript
// Her ürün için stok günü hesapla
const productsWithStockDays = products.map(p => {
  const dailySales = p.last30DaysSales / 30;
  const stockDays = dailySales > 0 ? p.currentStock / dailySales : 999;
  const inventoryPressure = stockDays > 60;  // eşik değer
  
  // Mevsimsel uyum
  const seasonMatch = 
    p.season === "all" || 
    p.season === currentSeason ||
    p.tags.some(tag => seasonalNeeds.includes(tag));
  
  return { 
    ...p, 
    stockDays, 
    inventoryPressure, 
    seasonMatch,
    dailySales 
  };
});
```

### 3.2 Yıldız Ürünler (Hero Products)

Hızlı satan, talep yüksek ürünler.

```javascript
const heroProducts = productsWithStockDays
  .filter(p => p.stockDays <= 20 && p.dailySales > 0)
  .sort((a, b) => a.stockDays - b.stockDays)
  .slice(0, 3)
  .map(p => ({
    productId: p.productId,
    productName: p.productName,
    category: p.category,
    stockDays: p.stockDays,
    inventoryPressure: false,
    seasonMatch: p.seasonMatch
  }));
```

### 3.3 Yavaş Ürünler (Slow Movers)

Stok baskısı altında, eritilmesi gereken ürünler.

```javascript
const slowMovers = productsWithStockDays
  .filter(p => p.inventoryPressure)
  .sort((a, b) => b.stockDays - a.stockDays)
  .slice(0, 5)
  .map(p => ({
    productId: p.productId,
    productName: p.productName,
    category: p.category,
    stockDays: p.stockDays,
    inventoryPressure: true,
    seasonMatch: p.seasonMatch
  }));
```

### 3.4 Stok Profili Çıktısı

```javascript
const stockInsight = {
  heroProducts,
  slowMovers
};
```

---

## 4. Bölge Modu (customerId yoksa)

Müşteri ID verilmediğinde genel bölge profili döndürülür.

```javascript
function getRegionProfile(city, region) {
  return {
    city,
    region: region.name,
    climateType: region.climateType,
    ageSegment: "Yetişkin",  // varsayılan
    gender: null,
    churnSegment: "Aktif",
    valueSegment: "Standard",
    loyaltyTier: "Gümüş",
    affinityCategory: region.trend,
    affinityType: "Keşifçi",
    diversityProfile: "Dengeli",
    estimatedBudget: region.medianBasket * 1.2,
    avgBasket: region.medianBasket,
    avgMonthlySpend: region.medianBasket * 2,
    lastPurchaseDaysAgo: 30,
    orderCount: 0,
    totalSpent: 0,
    membershipDays: 0,
    missingRegulars: [],
    topProducts: []
  };
}
```

---

## 5. Yeni Müşteri Profili (productHistory boş)

```javascript
function getNewCustomerProfile(customer, region) {
  return {
    customerId: customer.customerId,
    city: customer.city,
    region: region.name,
    climateType: region.climateType,
    age: customer.age,
    ageSegment: getAgeSegment(customer.age),
    gender: customer.gender,
    churnSegment: "Riskli",  // henüz alışveriş yapmamış
    valueSegment: "Standard",
    loyaltyTier: "Bronz",
    affinityCategory: region.trend,  // bölge trendini kullan
    affinityType: "Keşifçi",
    diversityProfile: "Kaşif",  // yeni müşteri, keşfetmeye açık
    estimatedBudget: region.medianBasket * 1.2,
    avgBasket: region.medianBasket,
    avgMonthlySpend: 0,
    lastPurchaseDaysAgo: 999,
    orderCount: 0,
    totalSpent: 0,
    membershipDays: daysSince(customer.registeredAt),
    missingRegulars: [],
    topProducts: []
  };
}
```

---

## 6. Final InsightJSON Oluşturma

```javascript
return {
  customer: customerInsight,
  stock: stockInsight,
  regionContext: {
    region: region.name,
    climateType: region.climateType,
    medianBasket: region.medianBasket,
    trend: region.trend,
    currentSeason,
    seasonalNeeds
  }
};
```

### 4. Bölge Modu (customerId yoksa)

```javascript
// Genel bölge profili
const customer = {
  city,
  region: region.name,
  climateType: region.climateType,
  ageSegment: "Yetişkin",  // varsayılan
  gender: null,
  churnSegment: "Aktif",
  valueSegment: "Standard",
  loyaltyTier: "Gümüş",
  affinityCategory: region.trend,
  affinityType: "Keşifçi",
  diversityProfile: "Dengeli",
  estimatedBudget: region.medianBasket * 1.2,
  avgBasket: region.medianBasket,
  avgMonthlySpend: region.medianBasket * 2,
  lastPurchaseDaysAgo: 30,
  orderCount: 0,
  totalSpent: 0,
  membershipDays: 0,
  missingRegulars: [],
  topProducts: []
};
```

---

## Pseudo-kod

```javascript
async function analyze({ city, customerId, customers, products, regions }) {
  // 1. Bölge analizi
  const region = regions.regions.find(r => r.cities.includes(city));
  const currentSeason = getCurrentSeason();
  const seasonalNeeds = region.seasonalNeeds[currentSeason];

  // 2. Müşteri analizi
  let customerInsight;
  if (customerId) {
    const customer = customers.find(c => c.customerId === customerId);
    customerInsight = analyzeCustomer(customer, region);
  } else {
    customerInsight = getRegionProfile(city, region);
  }

  // 3. Stok analizi
  const stockInsight = analyzeStock(products, currentSeason, seasonalNeeds);

  // 4. InsightJSON oluştur
  return {
    customer: customerInsight,
    stock: stockInsight,
    regionContext: {
      region: region.name,
      climateType: region.climateType,
      medianBasket: region.medianBasket,
      trend: region.trend,
      currentSeason,
      seasonalNeeds
    }
  };
}
```

---

## Test Senaryoları

### Senaryo 1: Aktif YüksekDeğer Müşteri
```
customerId: "C-1001"
city: "Istanbul"
Beklenen:
  - churnSegment: "Aktif"
  - valueSegment: "HighValue"
  - loyaltyTier: "Altın" veya "Platin"
```

### Senaryo 2: Riskli Standart Müşteri
```
customerId: "C-1005"
city: "Ankara"
Beklenen:
  - churnSegment: "Riskli"
  - valueSegment: "Standard"
  - missingRegulars: dolu olabilir
```

### Senaryo 3: Bölge Modu
```
customerId: null
city: "Izmir"
Beklenen:
  - customer.affinityCategory: "SKINCARE" (Ege bölge trendi)
  - customer.avgBasket: 65.00 (Ege medyan)
```

### Senaryo 4: Kış Mevsimi Stok
```
currentSeason: "winter"
city: "Trabzon"
Beklenen:
  - seasonalNeeds: ["besleyici-krem", "dudak-bakım", ...]
  - slowMovers: yaz ürünleri (SPF, bronzlaştırıcı)
```

---

## Notlar

- Analiz Ajanı **hiçbir kampanya kararı almaz**
- Sadece veri analizi ve segmentasyon yapar
- Tüm hesaplamalar deterministik (ML yok)
- `productHistory` boşsa müşteri "Riskli" + "Bronz" olur
- Bölge modu için genel profil döndürür

  const inventoryPressure = stockDays > 60;
  
  // Mevsimsel uyum
  const seasonMatch = 
    p.season === "all" || 
    p.season === currentSeason ||
    p.tags.some(tag => seasonalNeeds.includes(tag));
  
  return { ...p, stockDays, inventoryPressure, seasonMatch };
});

// Yıldız ürünler (hızlı satanlar)
const heroProducts = productsWithStockDays
  .filter(p => p.stockDays <= 20)
  .sort((a, b) => a.stockDays - b.stockDays)
  .slice(0, 3);

// Yavaş ürünler (stok baskısı altında)
const slowMovers = productsWithStockDays
  .filter(p => p.inventoryPressure)
  .sort((a, b) => b.stockDays - a.stockDays)
  .slice(0, 5);
```

---

## Pseudo-kod

```javascript
async function analyze({ city, customerId, customers, products, regions }) {
  // 1. Bölge analizi
  const region = regions.regions.find(r => r.cities.includes(city));
  const currentSeason = getCurrentSeason();
  const seasonalNeeds = region.seasonalNeeds[currentSeason];

  // 2. Müşteri analizi
  let customerInsight;
  if (customerId) {
    const customer = customers.find(c => c.customerId === customerId);
    if (customer.productHistory.length === 0) {
      customerInsight = getNewCustomerProfile(customer, region);
    } else {
      customerInsight = analyzeCustomer(customer, region);
    }
  } else {
    customerInsight = getRegionProfile(city, region);
  }

  // 3. Stok analizi
  const stockInsight = analyzeStock(products, currentSeason, seasonalNeeds);

  // 4. InsightJSON oluştur
  return {
    customer: customerInsight,
    stock: stockInsight,
    regionContext: {
      region: region.name,
      climateType: region.climateType,
      medianBasket: region.medianBasket,
      trend: region.trend,
      currentSeason,
      seasonalNeeds
    }
  };
}
```

---

## Test Senaryoları

### Senaryo 1: Aktif YüksekDeğer Müşteri
```
customerId: "C-1001"
city: "Istanbul"
Beklenen:
  - churnSegment: "Aktif"
  - valueSegment: "HighValue"
  - loyaltyTier: "Altın" veya "Platin"
  - missingRegulars: P-2001 (30 gün sıklık, 37 gün geçmiş)
```

### Senaryo 2: Riskli Standart Müşteri
```
customerId: "C-1005"
city: "Trabzon"
Beklenen:
  - churnSegment: "Riskli" (>180 gün)
  - valueSegment: "Standard"
  - loyaltyTier: "Gümüş"
  - affinityCategory: "SKINCARE"
```

### Senaryo 3: Bölge Modu
```
customerId: null
city: "Izmir"
Beklenen:
  - customer.affinityCategory: "SKINCARE" (Ege bölge trendi)
  - customer.avgBasket: 65.00 (Ege medyan)
  - customer.climateType: "Sıcak-Nemli"
```

### Senaryo 4: Yeni Müşteri (Boş productHistory)
```
customerId: "C-1009" (yeni kayıt, alışveriş yok)
city: "Ankara"
Beklenen:
  - churnSegment: "Riskli"
  - loyaltyTier: "Bronz"
  - diversityProfile: "Kaşif"
  - estimatedBudget: bölge medyanı * 1.2
```

### Senaryo 5: Kış Mevsimi Stok
```
currentSeason: "winter"
city: "Trabzon"
Beklenen:
  - seasonalNeeds: ["besleyici-krem", "dudak-bakım", ...]
  - slowMovers: yaz ürünleri (P-2003: SPF, seasonMatch: false)
  - heroProducts: kış ürünleri öncelikli
```

---

## Notlar

- Analiz Ajanı **hiçbir kampanya kararı almaz**
- Sadece veri analizi ve segmentasyon yapar
- Tüm hesaplamalar deterministik (ML yok)
- `productHistory` boşsa müşteri "Riskli" + "Bronz" + "Kaşif" olur
- Bölge modu için genel profil döndürür
- Segment tabloları referans olarak kullanılır
