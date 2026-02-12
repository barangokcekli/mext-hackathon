# Kampanya Planlayıcı Ajanı Dökümanı

## Sorumluluk

Kampanya Planlayıcı, hedef ve analiz sonucuna göre kampanya stratejisi oluşturur. Ürün seçer, indirim hesaplar, mesajlaşma yapar, ürün önerileri üretir. **Veri analizi yapmaz** — sadece InsightJSON'ı kullanır.

---

## Girdi

```json
{
  "objective": "IncreaseRevenue" | "ClearOverstock",
  "event": "MothersDay" | "BlackFriday" | "ValentinesDay" | null,
  "customerInsight": { /* CustomerInsightJSON */ },
  "stockInsight": { /* StockInsightJSON */ },
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

---

## Çıktı (CampaignJSON)

```json
{
  "campaignId": "CMP-20260212-IST-001",
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue",
  "city": "Istanbul",
  "region": "Marmara",
  "event": "MothersDay",
  "targetSegment": {
    "churn": "Active",
    "value": "HighValue",
    "affinity": "SKINCARE",
    "ageSegment": "GençYetişkin",
    "loyaltyTier": "Altın",
    "climateType": "Metropol"
  },
  "strategy": {
    "type": "CrossSell",
    "description": "Yüksek değerli aktif müşteri için cilt bakım çapraz satış paketi. Favori kategoriden yıldız ürün + tamamlayıcı ürünler.",
    "discountPercent": 10,
    "marginCheck": {
      "floor": 25,
      "passed": true
    },
    "regionNote": "Metropol bölge — trend ve premium ürün çeşitliliği yüksek."
  },
  "products": {
    "hero": [
      {
        "productId": "P-2004",
        "productName": "Aloe Line Moisturizer",
        "category": "SKINCARE",
        "role": "anchor",
        "originalPrice": 64.90,
        "campaignPrice": 58.41,
        "discountPercent": 10
      }
    ],
    "complementary": [
      {
        "productId": "P-2001",
        "productName": "Dr. C. Tuna Tea Tree Face Wash",
        "category": "SKINCARE",
        "role": "crossSell",
        "originalPrice": 59.90,
        "campaignPrice": 53.91,
        "discountPercent": 10
      }
    ]
  },
  "packageTotal": {
    "originalPrice": 124.80,
    "campaignPrice": 112.32,
    "totalSavings": 12.48,
    "withinBudget": true,
    "estimatedBudget": 102.60
  },
  "messaging": {
    "headline": "Anneler Günü Cilt Bakım Paketi",
    "subtext": "Ona özel bir set hediye edin — favori cilt bakım ürünleri özel fiyatla.",
    "eventTheme": "MothersDay",
    "urgency": "Sınırlı süre!"
  },
  "recommendations": [
    {
      "productId": "P-2002",
      "productName": "Age Reversist Serum",
      "category": "SKINCARE",
      "reason": "Cilt bakım yakınlığı + GençYetişkin yaş segmenti → anti-aging başlangıç ürünü",
      "matchScore": 0.87,
      "originalPrice": 119.90
    },
    {
      "productId": "P-6001",
      "productName": "Beauty Booster Collagen Chocolate",
      "category": "WELLNESS",
      "reason": "SKINCARE odaklı müşteri → kolajen takviyesi ile içten dışa bakım",
      "matchScore": 0.72,
      "originalPrice": 179.90
    }
  ],
  "metadata": {
    "generatedAt": "2026-02-12T14:30:00Z",
    "agentVersion": "1.0.0"
  }
}
```

---

## İş Akışı

### 1. Hedef Stratejisi Belirleme

```javascript
function determineStrategy(objective, customerInsight) {
  const { churnSegment, valueSegment, loyaltyTier } = customerInsight;
  
  if (objective === "IncreaseRevenue") {
    if (valueSegment === "HighValue" && churnSegment === "Active") {
      return { type: "CrossSell", discountMax: 10 };
    } else if (churnSegment === "Riskli") {
      return { type: "WinBack", discountMax: 20 };
    } else {
      return { type: "Upsell", discountMax: 15 };
    }
  } else if (objective === "ClearOverstock") {
    if (valueSegment === "HighValue") {
      return { type: "BundleWithHero", discountMax: 20 };
    } else {
      return { type: "FlashSale", discountMax: 30 };
    }
  }
}
```

### 2. Ürün Seçimi

```javascript
function selectProducts(strategy, customerInsight, stockInsight, regionContext) {
  const { affinityCategory, estimatedBudget, missingRegulars, diversityProfile } = customerInsight;
  const { heroProducts, slowMovers } = stockInsight;
  const { seasonalNeeds, climateType } = regionContext;
  
  let selectedProducts = [];
  
  if (strategy.objective === "IncreaseRevenue") {
    // Yıldız ürün seç (müşteri yakınlık kategorisinden)
    const hero = heroProducts.find(p => p.category === affinityCategory);
    if (hero) selectedProducts.push({ ...hero, role: "anchor" });
    
    // Zamanı gelmiş düzenli ürünler varsa ekle
    if (missingRegulars.length > 0) {
      selectedProducts.push(...missingRegulars.map(p => ({ ...p, role: "reminder" })));
    }
    
    // Çeşitlilik profiline göre tamamlayıcı seç
    if (diversityProfile === "Kaşif") {
      // Yeni kategori ürünü
      const newCategory = heroProducts.find(p => p.category !== affinityCategory);
      if (newCategory) selectedProducts.push({ ...newCategory, role: "crossSell" });
    } else if (diversityProfile === "Sadık") {
      // Favori kategoriden başka ürün
      const sameCategory = heroProducts.filter(p => p.category === affinityCategory)[1];
      if (sameCategory) selectedProducts.push({ ...sameCategory, role: "favorite" });
    }
  } else if (strategy.objective === "ClearOverstock") {
    // Yavaş ürünleri seç (mevsime uygun olanları öncelikle)
    const seasonalSlowMovers = slowMovers.filter(p => p.seasonMatch);
    selectedProducts.push(...seasonalSlowMovers.slice(0, 2).map(p => ({ ...p, role: "clearance" })));
    
    // Çekicilik için bir yıldız ürün ekle
    const hero = heroProducts[0];
    if (hero) selectedProducts.push({ ...hero, role: "anchor" });
  }
  
  // Bütçe kontrolü
  let totalPrice = selectedProducts.reduce((sum, p) => sum + p.unitPrice, 0);
  while (totalPrice > estimatedBudget && selectedProducts.length > 1) {
    selectedProducts.pop();  // En düşük öncelikli ürünü çıkar
    totalPrice = selectedProducts.reduce((sum, p) => sum + p.unitPrice, 0);
  }
  
  return selectedProducts;
}
```

### 3. İndirim Hesaplama

```javascript
function calculateDiscount(product, strategy) {
  // Marj kontrolü
  const grossMargin = ((product.unitPrice - product.unitCost) / product.unitPrice) * 100;
  const maxDiscount = Math.min(grossMargin - 25, strategy.discountMax);
  
  if (maxDiscount <= 0) {
    return { discountPercent: 0, campaignPrice: product.unitPrice };
  }
  
  // Rol bazlı indirim
  let discountPercent = 0;
  if (product.role === "anchor") {
    discountPercent = Math.min(5, maxDiscount);  // Yıldız ürün düşük indirim
  } else if (product.role === "clearance") {
    discountPercent = maxDiscount;  // Tasfiye maksimum indirim
  } else {
    discountPercent = Math.min(strategy.discountMax, maxDiscount);
  }
  
  const campaignPrice = product.unitPrice * (1 - discountPercent / 100);
  return { discountPercent, campaignPrice };
}
```

### 4. Mesajlaşma Oluşturma

```javascript
function generateMessaging(objective, event, insight) {
  let headline, subtext, urgency;
  
  if (event === "MothersDay") {
    headline = "Anneler Günü Özel Paketi";
    subtext = "Ona özel bir set hediye edin";
    urgency = "Sınırlı süre!";
  } else if (event === "BlackFriday") {
    headline = "Black Friday Fırsatı";
    subtext = "Yılın en büyük indirimi";
    urgency = "Bugün son gün!";
  } else if (objective === "IncreaseRevenue") {
    headline = `${insight.customer.affinityCategory} Özel Paketi`;
    subtext = "Favori ürünleriniz bir arada";
    urgency = null;
  } else {
    headline = "Flaş İndirim";
    subtext = "Stoklar tükenene kadar";
    urgency = "Acele edin!";
  }
  
  return { headline, subtext, urgency, eventTheme: event };
}
```

### 5. Ürün Önerileri

```javascript
function generateRecommendations(insight, selectedProducts) {
  const { affinityCategory, ageSegment, diversityProfile } = insight.customer;
  const { seasonalNeeds } = insight.regionContext;
  
  const recommendations = [];
  
  // Kural 1: Kategori genişletme
  if (diversityProfile === "Kaşif") {
    const newCategoryProduct = products.find(p => 
      p.category !== affinityCategory && 
      !selectedProducts.includes(p.productId)
    );
    if (newCategoryProduct) {
      recommendations.push({
        ...newCategoryProduct,
        reason: `${affinityCategory} odaklısınız → ${newCategoryProduct.category} kategorisini keşfedin`,
        matchScore: 0.85
      });
    }
  }
  
  // Kural 2: Yaş uyumlu ürün
  if (ageSegment === "GençYetişkin" && affinityCategory === "SKINCARE") {
    const antiAgingProduct = products.find(p => 
      p.tags.includes("anti-aging") && 
      !selectedProducts.includes(p.productId)
    );
    if (antiAgingProduct) {
      recommendations.push({
        ...antiAgingProduct,
        reason: "Cilt bakım yakınlığı + GençYetişkin yaş segmenti → anti-aging başlangıç ürünü",
        matchScore: 0.87
      });
    }
  }
  
  // Kural 3: Mevsimsel uyum
  const seasonalProduct = products.find(p => 
    p.tags.some(tag => seasonalNeeds.includes(tag)) &&
    !selectedProducts.includes(p.productId)
  );
  if (seasonalProduct) {
    recommendations.push({
      ...seasonalProduct,
      reason: `Mevsime uygun → ${seasonalNeeds.join(", ")}`,
      matchScore: 0.78
    });
  }
  
  return recommendations.slice(0, 3);  // Maksimum 3 öneri
}
```

---

## Karar Matrisi

### Hedef × Segment → Strateji

| Hedef | Değer | Kayıp | Strateji | İndirim Max |
|---|---|---|---|---|
| GelirArtır | Yüksek | Aktif | CrossSell | 10% |
| GelirArtır | Yüksek | Ilık | ReEngagement | 15% |
| GelirArtır | Yüksek | Riskli | WinBack | 20% |
| GelirArtır | Standart | Aktif | Upsell | 10% |
| GelirArtır | Standart | Ilık | CategoryDiscount | 15% |
| GelirArtır | Standart | Riskli | ReActivation | 20% |
| StokErit | Yüksek | Aktif | BundleWithHero | 20% |
| StokErit | Yüksek | Ilık | DiscountBundle | 25% |
| StokErit | Yüksek | Riskli | DeepDiscount | 30% |
| StokErit | Standart | Aktif | FlashSale | 25% |
| StokErit | Standart | Ilık | CategoryClearance | 30% |
| StokErit | Standart | Riskli | MaxClearance | 35% |

### Sadakat Katmanı Etkisi

| Katman | Kampanya Etkisi |
|---|---|
| Platin | Özel erişim, ekstra hediye, düşük indirim yeterli |
| Altın | Sadakat bonusu, ücretsiz kargo |
| Gümüş | Standart kampanya + küçük teşvik |
| Bronz | Tanışma indirimi |

---

## Pseudo-kod

```javascript
async function planCampaign({ objective, event, customerInsight, stockInsight, regionContext }) {
  // 1. Strateji belirle
  const strategy = determineStrategy(objective, customerInsight);
  
  // 2. Ürün seç
  const selectedProducts = selectProducts(strategy, customerInsight, stockInsight, regionContext);
  
  // 3. İndirim hesapla
  const productsWithPricing = selectedProducts.map(p => ({
    ...p,
    ...calculateDiscount(p, strategy)
  }));
  
  // 4. Bütçe kontrolü
  const packageTotal = calculatePackageTotal(productsWithPricing, customerInsight.estimatedBudget);
  
  // 5. Mesajlaşma oluştur
  const messaging = generateMessaging(objective, event, customerInsight);
  
  // 6. Ürün önerileri
  const recommendations = generateRecommendations(customerInsight, stockInsight, selectedProducts);
  
  // 7. CampaignJSON oluştur
  return {
    campaignId: generateCampaignId(),
    objective,
    event,
    targetSegment: extractSegment(customerInsight),
    strategy,
    products: groupProductsByRole(productsWithPricing),
    packageTotal,
    messaging,
    recommendations,
    metadata: {
      generatedAt: new Date().toISOString(),
      agentVersion: "1.0.0"
    }
  };
}
```

---

## Test Senaryoları

### Senaryo 1: GelirArtır + YüksekDeğer + Aktif
```
Beklenen:
  - strategy.type: "CrossSell"
  - discountPercent: ≤10%
  - products.hero: müşteri affinityCategory'den
  - packageTotal.withinBudget: true
```

### Senaryo 2: StokErit + Standart + Riskli
```
Beklenen:
  - strategy.type: "MaxClearance"
  - discountPercent: ≤35%
  - products: slowMovers ağırlıklı
  - messaging.urgency: "Acele edin!"
```

### Senaryo 3: Anneler Günü Etkinliği
```
event: "MothersDay"
Beklenen:
  - messaging.headline: "Anneler Günü..."
  - messaging.eventTheme: "MothersDay"
  - products: hediye seti formatı
```

### Senaryo 4: Bütçe Aşımı
```
estimatedBudget: 80.00
selectedProducts toplam: 150.00
Beklenen:
  - En düşük öncelikli ürünler çıkarılır
  - packageTotal.campaignPrice ≤ 80.00
  - packageTotal.withinBudget: true
```

---

## Notlar

- Kampanya Planlayıcı **hiçbir veri analizi yapmaz**
- Müşteri ve Stok analiz sonuçlarını kullanır
- Marj tabanı %25 her zaman korunur
- Bütçe aşılırsa ürün çıkarılır
- Etkinlik sadece mesajlaşmayı değiştirir, hedef mantığını değil
- Öneriler kampanya paketinin dışındadır
