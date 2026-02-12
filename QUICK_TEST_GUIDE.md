# Quick Test Guide - Playground

## 🚀 Hızlı Başlangıç

### 1. Basit Test (Aktif Müşteri)

```json
{
  "customerData": {
    "customerId": "C-1001",
    "city": "Istanbul",
    "customer": {
      "customerId": "C-1001",
      "city": "Istanbul",
      "age": 32,
      "gender": "F",
      "registeredAt": "2024-03-15T00:00:00",
      "productHistory": [
        {
          "productId": "P-2001",
          "category": "SKINCARE",
          "totalQuantity": 8,
          "totalSpent": 479.20,
          "orderCount": 8,
          "lastPurchase": "2026-01-20T00:00:00",
          "avgDaysBetween": 30
        }
      ]
    },
    "region": {
      "name": "Marmara",
      "climateType": "Temperate",
      "medianBasket": 75.0,
      "trend": "SKINCARE"
    }
  }
}
```

**Beklenen:** Aktif, HighValue, Gümüş, SKINCARE Odaklı

---

### 2. Yeni Müşteri Testi

```json
{
  "customerData": {
    "customerId": "C-NEW-001",
    "city": "Antalya",
    "customer": {
      "customerId": "C-NEW-001",
      "city": "Antalya",
      "age": 22,
      "gender": "F",
      "registeredAt": "2026-02-01T00:00:00",
      "productHistory": []
    },
    "region": {
      "name": "Akdeniz",
      "climateType": "Mediterranean",
      "medianBasket": 85.0,
      "trend": "SKINCARE"
    }
  }
}
```

**Beklenen:** Riskli, Standard, Bronz, Kaşif, lastPurchaseDaysAgo: 999

---

### 3. Region Mode Testi

```json
{
  "customerData": {
    "city": "Antalya",
    "region": {
      "name": "Akdeniz",
      "climateType": "Mediterranean",
      "medianBasket": 85.0,
      "trend": "SKINCARE"
    }
  }
}
```

**Beklenen:** mode: "region", default segmentler, orderCount: 0

---

## ✅ Kontrol Listesi

Her test sonrasında kontrol et:

- [ ] `mode` doğru mu? (regular/new_customer/region)
- [ ] `ageSegment` yaşa göre doğru mu?
- [ ] `churnSegment` son alışverişe göre doğru mu?
- [ ] `valueSegment` avg basket vs median'a göre doğru mu?
- [ ] `loyaltyTier` üyelik ve frekansa göre doğru mu?
- [ ] `affinityCategory` en çok harcanan kategori mi?
- [ ] `diversityProfile` ürün çeşitliliğine göre doğru mu?
- [ ] `totalSpent` doğru hesaplanmış mı?
- [ ] `avgBasket` = totalSpent / orderCount mu?
- [ ] `estimatedBudget` = avgBasket * 1.2 mi?
- [ ] `topProducts` spending'e göre sıralı mı?
- [ ] `missingRegulars` varsa doğru tespit edilmiş mi?

---

## 📋 Segment Kuralları

### Age Segments
- GenZ: 18-25
- GençYetişkin: 26-35
- Yetişkin: 36-50
- Olgun: 51+

### Churn Segments
- Aktif: <30 gün
- Ilık: 30-60 gün
- Riskli: >60 gün

### Value Segments
- HighValue: avgBasket > regionMedian
- Standard: avgBasket ≤ regionMedian

### Loyalty Tiers
- Platin: 12+ ay VE 2+ sipariş/ay
- Altın: 6+ ay VE 1+ sipariş/ay
- Gümüş: 3+ toplam sipariş
- Bronz: <3 sipariş

### Affinity Types
- Odaklı: >60% tek kategoride
- Keşifçi: ≤60% dağılım

### Diversity Profiles
- Kaşif: >70% çeşitlilik
- Dengeli: 40-70% çeşitlilik
- Sadık: ≤40% çeşitlilik

---

## 🎯 Hızlı Senaryo Testleri

**Test Seti 1: Churn Risk**
1. Aktif müşteri (Test 1)
2. Riskli müşteri (lastPurchase: 2025-10-01)
3. Ilık müşteri (lastPurchase: 2025-12-20)

**Test Seti 2: Loyalty**
1. Bronz (2 sipariş, yeni üye)
2. Gümüş (5 sipariş, 6 ay üye)
3. Altın (10 sipariş, 8 ay üye)

**Test Seti 3: Özel Durumlar**
1. Yeni müşteri (boş history)
2. Region mode (no customerId)
3. Missing regulars (avgDaysBetween var, gecikmiş)

---

## 💡 İpuçları

1. **Tarihler:** Bugünün tarihi 2026-02-12, buna göre lastPurchase ayarla
2. **Missing Regulars:** avgDaysBetween * 1.2'den fazla gecikme olmalı
3. **Region Median:** Her bölgenin farklı median basket değeri var
4. **Diversity Ratio:** uniqueProducts / totalOrders
5. **Affinity Ratio:** categoryOrders / totalOrders

---

Detaylı testler için: `PLAYGROUND_TEST_PROMPTS.md`
