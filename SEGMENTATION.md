# Segmentasyon Modeli

Bu doküman müşteri ve ürün segmentasyonunu ayrı ayrı tanımlar. Analiz Ajanı bu kuralları kullanarak `InsightJSON` üretir.

Sistem tek ülke (Türkiye) üzerinde çalışır. Bölge ve şehir bazlı karar alır.

---

## 1. Müşteri Segmentasyonu

### 1.1 Veri Kaynağı

`customers.json` dosyasından okunur. Alışveriş geçmişi `productHistory[]` dizisi olarak müşteri kaydının içinde gömülüdür — hangi üründen kaç tane aldığı, ne sıklıkla aldığı.

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

Türetilen metrikler `productHistory[]` üzerinden hesaplanır:

```
products = customer.productHistory
lastPurchaseDaysAgo = bugün - max(products.map(p => p.lastPurchase))
totalSpent = sum(products.map(p => p.totalSpent))
totalOrders = sum(products.map(p => p.orderCount))
avgBasket = totalSpent / totalOrders
categoryBreakdown = grupla(products, category)
```

### 1.2 Yaş Segmenti

| Segment | Aralık | Ürün Eğilimi |
|---|---|---|
| GenZ | 18–25 | Makyaj, trend ürünler, düşük fiyat hassasiyeti, düşük sepet |
| Genç Yetişkin | 26–35 | Cilt bakım, anti-aging başlangıç, orta sepet |
| Yetişkin | 36–50 | Premium cilt bakım, parfüm, yüksek sepet |
| Olgun | 51+ | Anti-aging, özel bakım, sadakat yüksek |

```
if (age <= 25) → "GenZ"
else if (age <= 35) → "GençYetişkin"
else if (age <= 50) → "Yetişkin"
else → "Olgun"
```

### 1.3 Bölge Segmenti

Şehirden bölge ve iklim tipi çözümlenir. İklim tipi, ürün filtreleme ve paketleme kararlarını etkiler.

| İklim Tipi | Bölgeler | Ürün Etkisi |
|---|---|---|
| Sıcak-Nemli | Ege, Akdeniz | Hafif nemlendiriciler, SPF ürünler, mat makyaj |
| Sıcak-Kuru | İç Anadolu, Güneydoğu Anadolu | Yoğun nemlendiriciler, koruyucu kremler |
| Soğuk | Karadeniz, Doğu Anadolu | Besleyici kremler, dudak bakım, koruyucu serumlar |
| Metropol | Marmara (Istanbul, Bursa, Kocaeli) | Trend ürünler, premium segmentler, çeşitlilik yüksek |

Bölge-şehir eşlemesi `regions.json` dosyasından gelir:

```json
{
  "regions": [
    { "name": "Marmara", "climateType": "Metropol", "medianBasket": 85.00, "trend": "Skincare", "cities": ["Istanbul", "Bursa", "Kocaeli"] },
    { "name": "Ege", "climateType": "Sıcak-Nemli", "medianBasket": 65.00, "trend": "Skincare", "cities": ["Izmir", "Mugla", "Aydin"] },
    { "name": "Akdeniz", "climateType": "Sıcak-Nemli", "medianBasket": 60.00, "trend": "Makeup", "cities": ["Antalya", "Mersin", "Adana"] },
    { "name": "İç Anadolu", "climateType": "Sıcak-Kuru", "medianBasket": 55.00, "trend": "Skincare", "cities": ["Ankara", "Konya", "Kayseri"] },
    { "name": "Karadeniz", "climateType": "Soğuk", "medianBasket": 50.00, "trend": "Skincare", "cities": ["Trabzon", "Samsun", "Rize"] },
    { "name": "Doğu Anadolu", "climateType": "Soğuk", "medianBasket": 45.00, "trend": "Skincare", "cities": ["Erzurum", "Van", "Kars"] },
    { "name": "Güneydoğu Anadolu", "climateType": "Sıcak-Kuru", "medianBasket": 50.00, "trend": "Perfume", "cities": ["Gaziantep", "Diyarbakir", "Sanliurfa"] }
  ],
  "stockDaysThreshold": 60
}
```

Kampanya planlayıcıda kullanımı:

```
region = regions.find(r => r.cities.includes(city))
climateType = region.climateType

Ürün filtreleme:
  "Sıcak-Nemli" → SPF, hafif krem, mat fondöten öncelikli
  "Sıcak-Kuru"  → yoğun nemlendirici, koruyucu bariyer kremleri öncelikli
  "Soğuk"       → besleyici krem, dudak bakım, onarıcı serum öncelikli
  "Metropol"    → trend + premium ürünler, geniş kategori çeşitliliği
```

### 1.4 Cinsiyet Segmenti

| Segment | Ürün Etkisi |
|---|---|
| F | Tam kategori erişimi |
| M | Erkek bakım, parfüm ağırlıklı |
| Belirtilmemiş | Cinsiyet-nötr ürünler öncelikli |

### 1.5 Bütçe Tahmini

Müşterinin geçmiş alışverişlerinden tahmini kampanya bütçesi türetilir. Kampanya planlayıcı bu bütçeyi aşan paketler önermez.

```
estimatedBudget = avgBasket * 1.2  // ortalama sepetin %20 üstü tolerans

Bütçe aşılırsa:
  - Paketten en düşük öncelikli ürün çıkar
  - Veya daha küçük ambalaj/adet önerilir
```

### 1.6 Sadakat Segmenti

Üyelik süresi ve sipariş sıklığına göre belirlenir. Yüksek sadakat = daha yüksek ödüllü kampanyalar.

| Katman | Koşul | Kampanya Etkisi |
|---|---|---|
| Platin | ≥12 ay üye, aylık ≥2 sipariş | Özel erişim, erken kampanya, ekstra hediye, düşük indirim yeterli |
| Altın | ≥6 ay üye, aylık ≥1 sipariş | Sadakat bonusu, ücretsiz kargo, orta indirim |
| Gümüş | ≥3 sipariş | Standart kampanya + küçük teşvik |
| Bronz | Yeni/az alışveriş | Tanışma indirimi, ilk alışveriş bonusu |

```
membershipMonths = (bugün - registeredAt) / 30
orderFrequency = sum(customer.productHistory.map(p => p.orderCount)) / membershipMonths

if (membershipMonths >= 12 && orderFrequency >= 2) → "Platin"
else if (membershipMonths >= 6 && orderFrequency >= 1) → "Altın"
else if (sum(customer.productHistory.map(p => p.orderCount)) >= 3) → "Gümüş"
else → "Bronz"
```

### 1.7 Alışveriş Çeşitlilik Profili

Müşteri hep aynı ürünleri mi alıyor, farklı ürünler mi deniyor?

| Profil | Koşul | Kampanya Etkisi |
|---|---|---|
| Kaşif | diversityRatio > 0.7 | Yeni ürünler, deneme boyları, keşif paketleri |
| Dengeli | 0.4 < diversityRatio ≤ 0.7 | Favori ürün + 1 yeni ürün karışımı |
| Sadık | diversityRatio ≤ 0.4 | Favori ürünlerde miktar indirimi, abonelik teklifi |

```
uniqueProducts = customer.productHistory.length
totalPurchases = sum(customer.productHistory.map(p => p.orderCount))
diversityRatio = uniqueProducts / totalPurchases
```

### 1.8 Dönemsel Alışveriş Tespiti

Düzenli alınan ürünlerin bu dönem alınıp alınmadığını kontrol eder.

```
// Ortalama alım sıklığı 60 günden az olan ürünler = düzenli ürünler
düzenliÜrünler = customer.productHistory.filter(p => p.avgDaysBetween !== null && p.avgDaysBetween <= 60)

// Düzenli ürünlerden zamanı gelmiş olanlar
eksikDüzenliÜrünler = düzenliÜrünler.filter(p => {
  const daysSinceLastPurchase = bugün - p.lastPurchase;
  const isOverdue = daysSinceLastPurchase > p.avgDaysBetween * 1.2;  // %20 tolerans
  return isOverdue;
})
```

| Durum | Kampanya Etkisi |
|---|---|
| Düzenli ürün zamanı gelmiş | Hatırlatma + küçük teşvik ile kampanyaya dahil et |
| Düzenli ürün henüz erken | Bu ürünü kampanyadan çıkar, farklı ürün öner |
| Düzenli ürün yok | Normal segmentasyon kuralları geçerli |

### 1.9 Kayıp Segmenti (Churn)

Son satın alma gün sayısına göre belirlenir.

| Segment | Koşul | Açıklama |
|---|---|---|
| Aktif | `lastPurchaseDaysAgo < 30` | Yakın zamanda alışveriş yapmış |
| Ilık | `30 ≤ lastPurchaseDaysAgo ≤ 60` | Etkileşim azalmış |
| Riskli | `lastPurchaseDaysAgo > 60` | Kaybedilme riski yüksek |

```
lastPurchaseDaysAgo = bugün - max(customer.productHistory.map(p => p.lastPurchase))

if (lastPurchaseDaysAgo > 60) → "Riskli"
else if (lastPurchaseDaysAgo >= 30) → "Ilık"
else → "Aktif"
```

> `productHistory` boşsa müşteri otomatik olarak "Riskli" segmentine atanır.

### 1.10 Değer Segmenti (Value)

Müşterinin ortalama sepet tutarı, bulunduğu bölgenin medyan sepet tutarıyla karşılaştırılır.

| Segment | Koşul |
|---|---|
| YüksekDeğer | `avgBasket > regionMedianBasket` |
| Standart | `avgBasket ≤ regionMedianBasket` |

```
totalSpent = sum(customer.productHistory.map(p => p.totalSpent))
totalOrders = sum(customer.productHistory.map(p => p.orderCount))
avgBasket = totalSpent / totalOrders
regionMedian = regions.find(r => r.cities.includes(city)).medianBasket

if (avgBasket > regionMedian) → "YüksekDeğer"
else → "Standart"
```

Bölge medyanları:

| Bölge | Medyan Sepet (TRY) |
|---|---|
| Marmara | 85.00 |
| Ege | 65.00 |
| Akdeniz | 60.00 |
| İç Anadolu | 55.00 |
| Karadeniz | 50.00 |
| Doğu Anadolu | 45.00 |
| Güneydoğu Anadolu | 50.00 |

### 1.11 Kategori Yakınlığı (Affinity)

Müşterinin en çok sipariş verdiği kategori + odaklanma derecesi.

```
categoryBreakdown = grupla(customer.productHistory, category)
  → { "SKINCARE": { totalSpent: 933.50, orderCount: 13 }, "MAKEUP": { totalSpent: 54.90, orderCount: 1 } }

affinity = maxKey(categoryBreakdown, 'totalSpent') → "SKINCARE"
affinityRatio = categoryBreakdown[affinity].orderCount / sum(all orderCounts) = 13 / 14 = 0.93

if (affinityRatio > 0.6) → "Odaklı" (tek kategoriye sadık)
else → "Keşifçi" (birden fazla kategori deniyor)
```

Eşitlik durumunda bölge trendine yakın olan kategori seçilir.

### 1.12 Müşteri Segment Matrisi

Kayıp ve Değer segmentlerinin kesişimi 6 müşteri profili oluşturur:

| | Aktif | Ilık | Riskli |
|---|---|---|---|
| YüksekDeğer | Sadık VIP | Soğuyan VIP | Kaybedilen VIP |
| Standart | Düzenli Alıcı | Uzaklaşan Alıcı | Kayıp Alıcı |

Her profilin kampanya stratejisindeki karşılığı:

| Profil | Kampanya Yaklaşımı |
|---|---|
| Sadık VIP | Çapraz satış, yeni ürün tanıtımı, düşük indirim |
| Soğuyan VIP | Yeniden etkileşim, sadakat ödülü, orta indirim |
| Kaybedilen VIP | Geri kazanım, özel teklif, yüksek indirim |
| Düzenli Alıcı | Sepet yükseltme, kategori genişletme |
| Uzaklaşan Alıcı | Hatırlatma, kategori indirimi |
| Kayıp Alıcı | Reaksiyon indirimi, son şans teklifi |

### 1.13 Müşteri ID Yoksa

`customerId` verilmediğinde bireysel segmentasyon yapılmaz. Sistem bölge-toplu moduna geçer:

- Değer segmenti: bölge medyanına göre genel hedefleme
- Kayıp segmenti: atlanır
- Yakınlık: bölge trend kategorisi kullanılır
- İklim filtresi: şehirden çözümlenen iklim tipine göre ürün filtreleme yapılır

---

## 2. Ürün Segmentasyonu

### 2.1 Veri Kaynağı

`products.json` dosyasından okunur. Stok verileri tüm Türkiye için ortaktır (tek depo mantığı).

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

### 2.2 Türetilen Metrikler

| Metrik | Formül | Açıklama |
|---|---|---|
| Günlük Satış | `last30DaysSales / 30` | Ortalama günlük satış adedi |
| Stok Günü | `currentStock / günlükSatış` | Mevcut stokun kaç gün yeteceği |
| Envanter Baskısı | `stokGunu > eşikDeğer` | Stok fazlası var mı (eşik: varsayılan 60 gün) |
| Brüt Marj | `(unitPrice - unitCost) / unitPrice * 100` | Yüzde olarak brüt kar marjı |
| Maks İndirim | `brütMarj - 25` | Marj tabanını koruyacak maksimum indirim |

```
günlükSatış = last30DaysSales / 30
stokGunu = currentStock / günlükSatış
envanterBaskısı = stokGunu > stockDaysThreshold  // varsayılan 60

brütMarj = ((unitPrice - unitCost) / unitPrice) * 100
maksİndirim = brütMarj - 25  // %25 marj tabanı korunur
```

### 2.3 Ürün Segmentleri

| Segment | Koşul | Açıklama |
|---|---|---|
| Yıldız (Hero) | `stokGunu ≤ 20` ve `günlükSatış` üst çeyrek | Hızlı satan, talep yüksek |
| Normal | `20 < stokGunu ≤ eşikDeğer` | Dengeli stok-satış oranı |
| Yavaş (Slow Mover) | `stokGunu > eşikDeğer` | Stok baskısı altında, eritilmesi gerekiyor |
| Ölü Stok (Dead Stock) | `günlükSatış = 0` ve `currentStock > 0` | Hiç satılmıyor |

```
if (günlükSatış === 0 && currentStock > 0) → "ÖlüStok"
else if (stokGunu > eşikDeğer) → "Yavaş"
else if (stokGunu <= 20 && günlükSatış üst çeyrek) → "Yıldız"
else → "Normal"
```

### 2.4 Ürün Segment Matrisi

| Segment | Kampanya Rolü | İndirim Aralığı |
|---|---|---|
| Yıldız | Çapa ürün (anchor) — pakete çekicilik katar | %0–5 (zaten satıyor) |
| Normal | Tamamlayıcı — çapraz satış adayı | %5–15 |
| Yavaş | Eritme hedefi — indirim veya paket | %15–35 (marj tabanına kadar) |
| Ölü Stok | Agresif tasfiye veya hediye olarak paketleme | %35–75 (marj tabanına kadar) |

### 2.5 Kategori Bazlı Gruplama

Ürünler kategori bazında gruplanır:

```
stokOzeti = grupla(stock, [category])

Her grup için:
  - toplamStok
  - toplamSatış
  - ortalamaStokGunu
  - baskıAltındakiÜrünSayısı
  - yıldızÜrünler[]
  - yavaşÜrünler[]
```

### 2.6 Mevsimsel Uyum

Ürünün mevcut mevsim + bölge ihtiyaçlarıyla uyumu kontrol edilir.

```
mevsim = getCurrentSeason()
bölgeİhtiyaçları = regions.find(r => r.cities.includes(city)).seasonalNeeds[mevsim]
ürünEtiketleri = product.tags

mevsimselUyum = bölgeİhtiyaçları.some(tag => ürünEtiketleri.includes(tag))

Ayrıca:
  product.season === "all" → her zaman uygun
  product.season === mevsim → uygun
  aksi halde → düşük öncelik
```

Örnek: Kış ayında Trabzon'da kampanya → `["besleyici-krem", "dudak-bakım", "koruyucu-serum", "el-kremi"]` etiketli ürünler öncelikli.

### 2.7 Bölge-Ürün Uyumu

Ürün segmentasyonu bölgeden bağımsızdır (tek stok havuzu), ancak kampanya planlayıcı ürün seçerken bölge iklim tipini filtre olarak kullanır:

```
Örnek: city = "Trabzon" → region = "Karadeniz" → climateType = "Soğuk"

Ürün seçimi sıralaması:
  1. Hedef segmentteki ürünler (ör: Yavaş ürünler — StokErit hedefi)
  2. İklim tipine uygun kategori filtresi (Soğuk → besleyici krem, dudak bakım)
  3. Müşteri yakınlık kategorisi ile kesişim
  4. Marj tabanı kontrolü
```

### 2.8 Marj Tabanı Kuralı

Hiçbir ürüne marj tabanının altında indirim uygulanamaz.

```
brütMarj = ((unitPrice - unitCost) / unitPrice) * 100

if (brütMarj <= 25) → indirim uygulanamaz, sadece paketleme
if (brütMarj > 25) → maksİndirim = brütMarj - 25

Örnek:
  unitPrice: 45, unitCost: 15
  brütMarj = 66.7%
  maksİndirim = 66.7 - 25 = %41.7
  → %41'e kadar indirim yapılabilir
```

---

## 3. Segmentlerin Kampanya Mantığıyla Kesişimi

### 3.1 GelirArtır Hedefi

```
Müşteri hedefleme:
  Öncelik: YüksekDeğer > Standart
  Kayıp bonus: Riskli → ek teşvik
  Sadakat: Platin/Altın → özel erişim, düşük indirim yeterli
  Yaş filtresi: Yetişkin/Olgun → premium, GenZ → trend

Ürün seçimi:
  Çapa: Yıldız ürünler (müşteri yakınlık kategorisinden)
  Tamamlayıcı: Normal ürünler (farklı kategoriden → çapraz satış)
  Bölge + mevsim filtresi: seasonalNeeds etiketleriyle eşleşen ürünler öncelikli
  Düzenli ürün kontrolü: Bu ay alınmamış düzenli ürünler dahil edilir
  Çeşitlilik: Kaşif → yeni ürün, Sadık → favori ürün indirimi

Bütçe: estimatedBudget aşılmaz
İndirim: Düşük (%5–15)
```

### 3.2 StokErit Hedefi

```
Müşteri hedefleme:
  Öncelik: Fiyat duyarlı segmentler (Standart, Riskli)
  YüksekDeğer müşteriler: paketleme ile eritme
  Sadakat: Bronz → tanışma indirimi ile stok eritme fırsatı

Ürün seçimi:
  Birincil: Yavaş ve Ölü Stok ürünler
  Çapa: Yıldız ürün pakete eklenerek çekicilik sağlanır
  Bölge + mevsim filtresi: mevsime uygun yavaş ürünler öncelikli
  Düzenli ürün kontrolü: Zaten alınmış ürünler kampanyadan çıkar
  Çeşitlilik: Kaşif → daha önce almadığı yavaş ürünler

Bütçe: estimatedBudget aşılmaz
İndirim: Yüksek (%15–35, marj tabanına kadar)
```

### 3.3 Özet Akış

```
Girdi: objective + city + customerId?
         │
         ▼
    şehir → bölge → iklim tipi + mevsimsel ihtiyaçlar (regions.json)
         │
         ▼
┌─ Müşteri Segmentasyonu ──────┐    ┌─ Ürün Segmentasyonu ─────┐
│ Yaş: GenZ/.../Olgun           │    │ Yıldız/Normal/Yavaş      │
│ Bölge: İklim tipi             │    │ /ÖlüStok                 │
│ Cinsiyet: F/M/?               │    │ + Marj hesabı             │
│ Kayıp: Aktif/Ilık/Riskli     │    │ + Mevsimsel uyum          │
│ Değer: Yüksek/Standart       │    │ + Etiket eşleşmesi        │
│ Sadakat: Platin/.../Bronz     │    │                           │
│ Yakınlık: Kategori + Odak    │    │                           │
│ Çeşitlilik: Kaşif/.../Sadık  │    │                           │
│ Bütçe: estimatedBudget       │    │                           │
│ Eksik düzenli ürünler         │    │                           │
└──────────┬────────────────────┘    └──────────┬───────────────┘
           │                                    │
           └───────────┬────────────────────────┘
                       │
                       ▼
              ┌─ InsightJSON ──────┐
              │ customer: {}       │
              │ stock: {}          │
              │ regionContext: {}   │
              └───────┬────────────┘
                      │
                      ▼
            Kampanya Planlayıcı
            (hedef + segment + bölge + mevsim
             + bütçe + sadakat + çeşitlilik → strateji)
```
