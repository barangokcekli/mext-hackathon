# Mock Data Açıklaması

Bu klasör sistemin test edilmesi için hazır mock data içerir.

## Yapı

```
mock-data/
├── tenants.json              # Tenant kayıtları
├── regions.json              # Bölge yapılandırması (paylaşımlı)
└── farmasi/                  # Farmasi tenant verisi
    ├── products.json         # 19 ürün (6 kategori)
    ├── customers.json        # 8 müşteri (farklı profiller)
    └── catalog_sources.json  # Scrape kaynakları
```

## Müşteri Profilleri

| ID | Şehir | Yaş | Profil | Ürün Sayısı | Beklenen Segment |
|---|---|---|---|---|---|
| C-1001 | Istanbul | 32 | Sadık SKINCARE müşterisi | 6 ürün, 16 sipariş | Aktif + YüksekDeğer + Altın |
| C-1002 | Ankara | 28 | MAKEUP odaklı GenZ | 4 ürün, 5 sipariş | Ilık + Standart + Gümüş |
| C-1003 | Izmir | 45 | Premium SKINCARE + WELLNESS | 4 ürün, 10 sipariş | Aktif + YüksekDeğer + Platin |
| C-1004 | Antalya | 22 | Yeni müşteri, MAKEUP | 2 ürün, 2 sipariş | Ilık + Standart + Bronz |
| C-1005 | Trabzon | 38 | Soğuk bölge, kış ürünleri | 3 ürün, 3 sipariş | Riskli + Standart + Gümüş |
| C-1006 | Istanbul | 29 | Erkek müşteri | 3 ürün, 3 sipariş | Aktif + YüksekDeğer + Gümüş |
| C-1007 | Bursa | 52 | Olgun, anti-aging odaklı | 4 ürün, 9 sipariş | Aktif + YüksekDeğer + Altın |
| C-1008 | Gaziantep | 35 | FRAGRANCE odaklı | 3 ürün, 3 sipariş | Riskli + Standart + Gümüş |

## Ürün Profilleri

### Yıldız Ürünler (Hızlı Satanlar)
- P-1002: Full Blast Mascara (200 adet/30 gün → 6.7 gün stok)
- P-4001: Eurofresh Toothpaste (300 adet/30 gün → 6.7 gün stok)
- P-2004: Aloe Line Moisturizer (95 adet/30 gün → 7.4 gün stok)

### Yavaş Ürünler (Stok Baskısı)
- P-2003: Sun Face Cream SPF50 (30 adet/30 gün → 50 gün stok) — mevsim dışı
- P-5002: Hair Mask (35 adet/30 gün → 10 gün stok)
- P-6001: Collagen Chocolate (25 adet/30 gün → 8 gün stok)

## Test Senaryoları

### Senaryo 1: Aktif YüksekDeğer Müşteri
```json
{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue",
  "city": "Istanbul",
  "customerId": "C-1001"
}
```
Beklenen:
- Strateji: CrossSell
- Ürünler: P-2001 (düzenli ürün, zamanı gelmiş) + P-2004 (yıldız)
- İndirim: ≤10%

### Senaryo 2: Riskli Standart Müşteri
```json
{
  "tenantId": "farmasi",
  "objective": "ClearOverstock",
  "city": "Trabzon",
  "customerId": "C-1005"
}
```
Beklenen:
- Strateji: MaxClearance
- Ürünler: Kış ürünleri (P-2006, P-2007, P-4002)
- İndirim: ≤35%

### Senaryo 3: Bölge Modu
```json
{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue",
  "city": "Ankara"
}
```
Beklenen:
- Müşteri: Bölge profili (İç Anadolu)
- Trend: SKINCARE
- Mevsimsel: Kış ürünleri öncelikli

### Senaryo 4: Anneler Günü Etkinliği
```json
{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue",
  "city": "Izmir",
  "customerId": "C-1003",
  "event": "MothersDay"
}
```
Beklenen:
- Mesajlaşma: "Anneler Günü..."
- Paket: Hediye seti formatı
- Ürünler: Premium SKINCARE + WELLNESS

## Veri Kullanımı

### Backend'de Yükleme
```javascript
const tenants = require('./mock-data/tenants.json');
const regions = require('./mock-data/regions.json');
const products = require('./mock-data/farmasi/products.json');
const customers = require('./mock-data/farmasi/customers.json');
```

### Tenant Doğrulama
```javascript
const tenant = tenants.tenants.find(t => t.tenantId === 'farmasi');
if (!tenant) throw new Error('Tenant not found');
```

### Bölge Çözümleme
```javascript
const region = regions.regions.find(r => r.cities.includes('Istanbul'));
// { name: "Marmara", climateType: "Metropol", medianBasket: 85.00, ... }
```

### Müşteri Analizi
```javascript
const customer = customers.find(c => c.customerId === 'C-1001');
const products = customer.productHistory;
const lastPurchase = Math.max(...products.map(p => new Date(p.lastPurchase)));
const totalSpent = products.reduce((sum, p) => sum + p.totalSpent, 0);
const totalOrders = products.reduce((sum, p) => sum + p.orderCount, 0);
const avgBasket = totalSpent / totalOrders;

// Düzenli ürünler
const regulars = products.filter(p => p.avgDaysBetween !== null && p.avgDaysBetween <= 60);
const overdue = regulars.filter(p => {
  const daysSince = (Date.now() - new Date(p.lastPurchase)) / (1000 * 60 * 60 * 24);
  return daysSince > p.avgDaysBetween * 1.2;
});
```

## Notlar

- Tüm tarihler ISO 8601 formatında
- Fiyatlar TRY cinsinden
- `productHistory` boş olabilir (yeni müşteriler için)
- `avgDaysBetween` null ise tek alım yapılmış
- Stok günü hesabı: `currentStock / (last30DaysSales / 30)`
- Marj tabanı: %25 (tenant settings'de)
