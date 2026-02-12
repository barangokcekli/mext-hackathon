# Müşteri Analiz Ajanı Dökümanı

## Sorumluluk

Müşteri Analiz Ajanı, müşteri verilerini analiz eder ve segmentasyon yapar. **Stok analizi yapmaz, kampanya kararı almaz** — sadece müşteri profili çıkarır.

---

## Girdi

```json
{
  "city": "Istanbul",
  "customerId": "C-1001",  // opsiyonel
  "customer": { /* customer kaydı */ },
  "region": { /* region bilgisi */ },
  "currentSeason": "winter"
}
```

---

## Çıktı (CustomerInsightJSON)

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
    { "productId": "P-2001", "totalQuantity": 8, "totalSpent": 479.20, "lastBought": "2026-01-20" },
    { "productId": "P-2004", "totalQuantity": 7, "totalSpent": 454.30, "lastBought": "2026-02-01" }
  ]
}
```

`customerId` yoksa bölge bazlı genel profil döndürülür.

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

### 1. Veri Hazırlama

```javascript
if (!customerId) {
  // Bölge modu
  return getRegionProfile(city, region);
}

const products = customer.productHistory;

// Boş productHistory kontrolü
if (products.length === 0) {
  return getNewCustomerProfile(customer, region);
}
```

### 2. Temel Metrikler

```javascript
const lastPurchaseDaysAgo = daysSince(max(products.map(p => p.lastPurchase)));
const totalSpent = sum(products.map(p => p.totalSpent));
const totalOrders = sum(products.map(p => p.orderCount));
const avgBasket = totalSpent / totalOrders;
const membershipDays = daysSince(customer.registeredAt);
const avgMonthlySpend = totalSpent / (membershipDays / 30);
```

### 3. Yaş Segmenti

```javascript
const ageSegment = 
  customer.age <= 25 ? "GenZ" :
  customer.age <= 35 ? "GençYetişkin" :
  customer.age <= 50 ? "Yetişkin" : "Olgun";
```

### 4. Kayıp Segmenti

```javascript
const churnSegment = 
  lastPurchaseDaysAgo > 60 ? "Riskli" :
  lastPurchaseDaysAgo >= 30 ? "Ilık" : "Aktif";
```

### 5. Değer Segmenti

```javascript
const valueSegment = avgBasket > region.medianBasket ? "HighValue" : "Standard";
```

### 6. Sadakat Katmanı

```javascript
const membershipMonths = membershipDays / 30;
const orderFrequency = totalOrders / membershipMonths;

const loyaltyTier = 
  (membershipMonths >= 12 && orderFrequency >= 2) ? "Platin" :
  (membershipMonths >= 6 && orderFrequency >= 1) ? "Altın" :
  (totalOrders >= 3) ? "Gümüş" : "Bronz";
```

### 7. Kategori Yakınlığı

```javascript
const categoryBreakdown = groupBy(products, 'category', (items) => ({
  totalSpent: sum(items.map(p => p.totalSpent)),
  orderCount: sum(items.map(p => p.orderCount))
}));

const affinityCategory = maxKey(categoryBreakdown, 'totalSpent');
const affinityRatio = categoryBreakdown[affinityCategory].orderCount / totalOrders;
const affinityType = affinityRatio > 0.6 ? "Odaklı" : "Keşifçi";
```

### 8. Çeşitlilik Profili

```javascript
const uniqueProducts = products.length;
const diversityRatio = uniqueProducts / totalOrders;

const diversityProfile = 
  diversityRatio > 0.7 ? "Kaşif" :
  diversityRatio > 0.4 ? "Dengeli" : "Sadık";
```

### 9. Bütçe Tahmini

```javascript
const estimatedBudget = avgBasket * 1.2;  // %20 tolerans
```

### 10. Düzenli Ürünler

```javascript
const regulars = products.filter(p => 
  p.avgDaysBetween !== null && 
  p.avgDaysBetween <= 60
);

const missingRegulars = regulars.filter(p => {
  const daysSinceLastPurchase = daysSince(p.lastPurchase);
  return daysSinceLastPurchase > p.avgDaysBetween * 1.2;
}).map(p => ({
  productId: p.productId,
  productName: getProductName(p.productId),
  lastBought: p.lastPurchase,
  avgDaysBetween: p.avgDaysBetween,
  daysOverdue: daysSince(p.lastPurchase) - p.avgDaysBetween
}));
```

### 11. En Çok Alınan Ürünler

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

---

## Bölge Modu (customerId yoksa)

```javascript
function getRegionProfile(city, region) {
  return {
    city,
    region: region.name,
    climateType: region.climateType,
    ageSegment: "Yetişkin",
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

## Yeni Müşteri Profili (productHistory boş)

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
    churnSegment: "Riskli",
    valueSegment: "Standard",
    loyaltyTier: "Bronz",
    affinityCategory: region.trend,
    affinityType: "Keşifçi",
    diversityProfile: "Kaşif",
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

## Pseudo-kod

```javascript
async function analyzeCustomer({ city, customerId, customer, region, currentSeason }) {
  // 1. Müşteri kontrolü
  if (!customerId) {
    return getRegionProfile(city, region);
  }
  
  if (customer.productHistory.length === 0) {
    return getNewCustomerProfile(customer, region);
  }
  
  // 2. Temel metrikler
  const metrics = calculateMetrics(customer.productHistory, customer.registeredAt);
  
  // 3. Segmentasyon
  const segments = {
    ageSegment: getAgeSegment(customer.age),
    churnSegment: getChurnSegment(metrics.lastPurchaseDaysAgo),
    valueSegment: getValueSegment(metrics.avgBasket, region.medianBasket),
    loyaltyTier: getLoyaltyTier(metrics.membershipMonths, metrics.orderFrequency),
    affinityCategory: getAffinityCategory(customer.productHistory),
    affinityType: getAffinityType(affinityRatio),
    diversityProfile: getDiversityProfile(metrics.diversityRatio)
  };
  
  // 4. Düzenli ürünler ve top products
  const missingRegulars = getMissingRegulars(customer.productHistory);
  const topProducts = getTopProducts(customer.productHistory);
  
  // 5. CustomerInsightJSON oluştur
  return {
    ...customer,
    ...segments,
    ...metrics,
    missingRegulars,
    topProducts
  };
}
```

---

## Test Senaryoları

### Senaryo 1: Aktif YüksekDeğer Müşteri
```
customerId: "C-1001"
Beklenen:
  - churnSegment: "Aktif"
  - valueSegment: "HighValue"
  - loyaltyTier: "Altın"
  - missingRegulars: [P-2001]
```

### Senaryo 2: Riskli Standart Müşteri
```
customerId: "C-1005"
Beklenen:
  - churnSegment: "Riskli"
  - valueSegment: "Standard"
  - loyaltyTier: "Gümüş"
```

### Senaryo 3: Yeni Müşteri
```
customerId: "C-1009" (productHistory: [])
Beklenen:
  - churnSegment: "Riskli"
  - loyaltyTier: "Bronz"
  - diversityProfile: "Kaşif"
```

---

## Notlar

- Müşteri Analiz Ajanı **sadece müşteri segmentasyonu** yapar
- Stok analizi yapmaz
- Kampanya kararı almaz
- Tüm hesaplamalar deterministik (ML yok)
- Segment tabloları referans olarak kullanılır
