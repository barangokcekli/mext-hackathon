# Stok Analiz Ajanı Dökümanı

## Sorumluluk

Stok Analiz Ajanı, ürün stok durumunu analiz eder. Yıldız ve yavaş ürünleri belirler, mevsimsel uyumu kontrol eder. **Müşteri analizi yapmaz, kampanya kararı almaz** — sadece stok performansı çıkarır.

---

## Girdi

```json
{
  "products": [ /* products.json */ ],
  "currentSeason": "winter",
  "seasonalNeeds": ["nemlendirici", "dudak-bakım", "el-kremi"]
}
```

---

## Çıktı (StockInsightJSON)

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
    },
    {
      "productId": "P-1002",
      "productName": "Full Blast Mascara",
      "category": "MAKEUP",
      "stockDays": 6,
      "dailySales": 6.67,
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
    },
    {
      "productId": "P-6001",
      "productName": "Beauty Booster Collagen Chocolate",
      "category": "WELLNESS",
      "stockDays": 80,
      "dailySales": 0.83,
      "inventoryPressure": true,
      "seasonMatch": true
    }
  ]
}
```

---

## Stok Metrikleri

### Temel Hesaplamalar

| Metrik | Formül | Açıklama |
|---|---|---|
| Günlük Satış | `last30DaysSales / 30` | Ortalama günlük satış adedi |
| Stok Günü | `currentStock / günlükSatış` | Mevcut stokun kaç gün yeteceği |
| Envanter Baskısı | `stokGunu > 60` | Stok fazlası var mı (eşik: 60 gün) |
| Brüt Marj | `(unitPrice - unitCost) / unitPrice * 100` | Yüzde olarak brüt kar marjı |
| Maks İndirim | `brütMarj - 25` | Marj tabanını koruyacak maksimum indirim |

### Ürün Segmentleri

| Segment | Koşul | Açıklama | Kampanya Rolü |
|---|---|---|---|
| Yıldız (Hero) | `stokGunu ≤ 20` ve `günlükSatış` üst çeyrek | Hızlı satan, talep yüksek | Çapa ürün, düşük indirim (%0-5) |
| Normal | `20 < stokGunu ≤ 60` | Dengeli stok-satış oranı | Tamamlayıcı, orta indirim (%5-15) |
| Yavaş (Slow Mover) | `stokGunu > 60` | Stok baskısı altında | Eritme hedefi, yüksek indirim (%15-35) |
| Ölü Stok (Dead Stock) | `günlükSatış = 0` ve `currentStock > 0` | Hiç satılmıyor | Agresif tasfiye veya hediye (%35-75) |

### Mevsimsel Uyum

```javascript
const seasonMatch = 
  product.season === "all" ||                              // Her mevsim uygun
  product.season === currentSeason ||                      // Mevsim eşleşiyor
  product.tags.some(tag => seasonalNeeds.includes(tag));   // Etiket eşleşiyor
```

| Durum | Açıklama | Kampanya Etkisi |
|---|---|---|
| seasonMatch: true | Mevsime uygun | Öncelikli, yüksek görünürlük |
| seasonMatch: false | Mevsim dışı | Düşük öncelik, daha yüksek indirim gerekebilir |

---

## İş Akışı

### 1. Stok Metrikleri Hesaplama

```javascript
const productsWithMetrics = products.map(p => {
  const dailySales = p.last30DaysSales / 30;
  const stockDays = dailySales > 0 ? p.currentStock / dailySales : 999;
  const inventoryPressure = stockDays > 60;
  
  // Mevsimsel uyum
  const seasonMatch = 
    p.season === "all" || 
    p.season === currentSeason ||
    p.tags.some(tag => seasonalNeeds.includes(tag));
  
  // Marj hesaplama
  const grossMargin = ((p.unitPrice - p.unitCost) / p.unitPrice) * 100;
  const maxDiscount = Math.max(0, grossMargin - 25);  // %25 marj tabanı
  
  return { 
    ...p, 
    dailySales,
    stockDays, 
    inventoryPressure, 
    seasonMatch,
    grossMargin,
    maxDiscount
  };
});
```

### 2. Yıldız Ürünler (Hero Products)

Hızlı satan, talep yüksek ürünler. Kampanyada çapa ürün olarak kullanılır.

```javascript
const heroProducts = productsWithMetrics
  .filter(p => p.stockDays <= 20 && p.dailySales > 0)
  .sort((a, b) => a.stockDays - b.stockDays)  // En hızlı satanlar önce
  .slice(0, 3)
  .map(p => ({
    productId: p.productId,
    productName: p.productName,
    category: p.category,
    stockDays: Math.round(p.stockDays * 10) / 10,
    dailySales: Math.round(p.dailySales * 100) / 100,
    inventoryPressure: false,
    seasonMatch: p.seasonMatch
  }));
```

**Kullanım:**
- Kampanyaya çekicilik katar
- Düşük indirim yeterli (%0-5)
- Müşteri yakınlık kategorisinden seçilir

### 3. Yavaş Ürünler (Slow Movers)

Stok baskısı altında, eritilmesi gereken ürünler.

```javascript
const slowMovers = productsWithMetrics
  .filter(p => p.inventoryPressure)
  .sort((a, b) => b.stockDays - a.stockDays)  // En yavaş satanlar önce
  .slice(0, 5)
  .map(p => ({
    productId: p.productId,
    productName: p.productName,
    category: p.category,
    stockDays: Math.round(p.stockDays * 10) / 10,
    dailySales: Math.round(p.dailySales * 100) / 100,
    inventoryPressure: true,
    seasonMatch: p.seasonMatch
  }));
```

**Kullanım:**
- StokErit hedefinde öncelikli
- Yüksek indirim (%15-35)
- Mevsime uygun olanlar önce seçilir

### 4. Kategori Bazlı Stok Özeti (Opsiyonel)

```javascript
const categoryStockSummary = Object.entries(
  groupBy(productsWithMetrics, 'category')
).map(([category, items]) => ({
  category,
  totalStock: sum(items.map(p => p.currentStock)),
  avgStockDays: avg(items.map(p => p.stockDays)),
  heroCount: items.filter(p => p.stockDays <= 20).length,
  slowCount: items.filter(p => p.inventoryPressure).length
}));
```

---

## Stok Profili Çıktısı

```javascript
return {
  heroProducts,
  slowMovers,
  // Opsiyonel: kategori özeti
  categoryStockSummary
};
```

---

## Pseudo-kod

```javascript
async function analyzeStock({ products, currentSeason, seasonalNeeds }) {
  // 1. Stok metrikleri hesapla
  const productsWithMetrics = products.map(p => ({
    ...p,
    dailySales: p.last30DaysSales / 30,
    stockDays: calculateStockDays(p),
    inventoryPressure: isInventoryPressure(p),
    seasonMatch: checkSeasonMatch(p, currentSeason, seasonalNeeds),
    grossMargin: calculateGrossMargin(p),
    maxDiscount: calculateMaxDiscount(p)
  }));
  
  // 2. Yıldız ürünler
  const heroProducts = productsWithMetrics
    .filter(p => p.stockDays <= 20 && p.dailySales > 0)
    .sort((a, b) => a.stockDays - b.stockDays)
    .slice(0, 3);
  
  // 3. Yavaş ürünler
  const slowMovers = productsWithMetrics
    .filter(p => p.inventoryPressure)
    .sort((a, b) => b.stockDays - a.stockDays)
    .slice(0, 5);
  
  // 4. StockInsightJSON oluştur
  return {
    heroProducts: formatProducts(heroProducts),
    slowMovers: formatProducts(slowMovers)
  };
}
```

---

## Test Senaryoları

### Senaryo 1: Yıldız Ürün Tespiti
```
products: [P-1002 (stockDays: 6), P-2004 (stockDays: 8), P-4001 (stockDays: 7)]
Beklenen:
  - heroProducts: [P-1002, P-4001, P-2004] (stok gününe göre sıralı)
  - inventoryPressure: false
```

### Senaryo 2: Yavaş Ürün Tespiti
```
products: [P-2003 (stockDays: 95), P-6001 (stockDays: 80)]
Beklenen:
  - slowMovers: [P-2003, P-6001]
  - inventoryPressure: true
```

### Senaryo 3: Mevsimsel Uyum (Kış)
```
currentSeason: "winter"
seasonalNeeds: ["nemlendirici", "dudak-bakım"]
products: [
  P-2003 (season: "summer", tags: ["SPF"]),
  P-2006 (season: "winter", tags: ["nemlendirici"])
]
Beklenen:
  - P-2003.seasonMatch: false
  - P-2006.seasonMatch: true
```

### Senaryo 4: Marj Kontrolü
```
product: { unitPrice: 100, unitCost: 60 }
Beklenen:
  - grossMargin: 40%
  - maxDiscount: 15% (40 - 25)
```

### Senaryo 5: Ölü Stok
```
product: { currentStock: 500, last30DaysSales: 0 }
Beklenen:
  - dailySales: 0
  - stockDays: 999
  - segment: "ÖlüStok"
```

---

## Bölge-İklim Etkisi

Stok analizi müşteri bağımsızdır, ancak mevsimsel ihtiyaçlar bölgeye göre değişir:

| İklim Tipi | Kış İhtiyaçları | Yaz İhtiyaçları |
|---|---|---|
| Metropol | nemlendirici, dudak-bakım, el-kremi | SPF, hafif-nemlendirici, mat-makyaj |
| Sıcak-Nemli | nemlendirici, koruyucu-krem | SPF, bronzlaştırıcı, su-bazlı-fondöten |
| Sıcak-Kuru | yoğun-nemlendirici, koruyucu-bariyer | SPF, hafif-nemlendirici |
| Soğuk | besleyici-krem, dudak-bakım, koruyucu-serum | hafif-nemlendirici, SPF |

Kampanya Planlayıcı bu bilgiyi kullanarak bölgeye uygun ürünleri seçer.

---

## Notlar

- Stok Analiz Ajanı **sadece stok performansı** analiz eder
- Müşteri analizi yapmaz
- Kampanya kararı almaz
- Tüm ürünler için çalışır (müşteri bağımsız)
- Mevsimsel uyum bölge bazlı `seasonalNeeds` ile belirlenir
- Marj tabanı %25 her zaman korunur
