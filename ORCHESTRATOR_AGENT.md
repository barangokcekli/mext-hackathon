# Orkestratör Ajan Dökümanı

## Sorumluluk

Orkestratör, sistemin giriş noktasıdır. Kullanıcı isteğini alır, doğrular, diğer ajanları sırayla çağırır ve son yanıtı döndürür. **Hiçbir iş mantığı içermez** — sadece koordinasyon yapar.

---

## Girdi

```json
{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue" | "ClearOverstock",
  "city": "Istanbul",
  "customerId": "C-1001",  // opsiyonel
  "event": "MothersDay" | "BlackFriday" | "ValentinesDay" | null  // opsiyonel
}
```

---

## Çıktı

```json
{
  "success": true,
  "campaign": { /* CampaignJSON */ },
  "metadata": {
    "tenantId": "farmasi",
    "processedAt": "2026-02-12T14:30:00Z",
    "executionTimeMs": 245
  }
}
```

Hata durumunda:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_TENANT" | "INVALID_CITY" | "CUSTOMER_NOT_FOUND" | "AGENT_ERROR",
    "message": "Açıklama"
  }
}
```

---

## İş Akışı

```
1. Girdi Doğrulama
   ├─ tenantId var mı? → tenants.json kontrol
   ├─ objective geçerli mi? → ["IncreaseRevenue", "ClearOverstock"]
   ├─ city geçerli mi? → regions.json'da var mı?
   └─ customerId varsa → customers.json'da var mı?

2. Tenant Verisi Yükleme
   ├─ /data/{tenantId}/customers.json
   ├─ /data/{tenantId}/products.json
   └─ /data/shared/regions.json

3. Bölge Çözümleme
   city → regions.json → { region, climateType, medianBasket, trend, seasonalNeeds }

4. Müşteri Analiz Ajanını Çağır
   Girdi: { city, customerId?, customer, region, currentSeason }
   Çıktı: CustomerInsightJSON

5. Stok Analiz Ajanını Çağır
   Girdi: { products, currentSeason, seasonalNeeds }
   Çıktı: StockInsightJSON

6. Kampanya Planlayıcıyı Çağır
   Girdi: { objective, event?, customerInsight, stockInsight, regionContext }
   Çıktı: CampaignJSON

7. Yanıt Sarmalama
   { success: true, campaign: CampaignJSON, metadata: {...} }
```

---

## Hata Yönetimi

| Hata Kodu | Ne Zaman | Yanıt |
|---|---|---|
| INVALID_TENANT | tenantId bulunamadı | 404, "Tenant not found" |
| INVALID_CITY | city regions.json'da yok | 400, "Invalid city" |
| CUSTOMER_NOT_FOUND | customerId bulunamadı | 404, "Customer not found" |
| MISSING_DATA | customers.json veya products.json yok | 500, "Tenant data incomplete" |
| AGENT_ERROR | Analiz veya Planlayıcı hata verdi | 500, agent hata mesajı |

---

## Döngü Önleme

Orkestratör **tek geçiş** yapar:

```
Müşteri Analiz Ajanı ──┐
                       ├──► Kampanya Planlayıcı → Bitti
Stok Analiz Ajanı ─────┘
```

- Geri bildirim döngüsü yok
- Tekrar deneme yok
- Ajanlar birbirini çağırmaz
- Müşteri ve Stok analizi paralel çalışabilir

---

## Pseudo-kod

```javascript
async function orchestrate(request) {
  // 1. Doğrulama
  const tenant = await validateTenant(request.tenantId);
  const city = validateCity(request.city);
  if (request.customerId) {
    await validateCustomer(request.tenantId, request.customerId);
  }

  // 2. Veri yükleme
  const customers = await loadJSON(`/data/${request.tenantId}/customers.json`);
  const products = await loadJSON(`/data/${request.tenantId}/products.json`);
  const regions = await loadJSON(`/data/shared/regions.json`);

  // 3. Bölge çözümleme
  const region = regions.regions.find(r => r.cities.includes(city));
  const currentSeason = getCurrentSeason();
  const seasonalNeeds = region.seasonalNeeds[currentSeason];

  // 4. Müşteri Analiz Ajanı
  const customer = request.customerId ? 
    customers.find(c => c.customerId === request.customerId) : null;
  
  const customerInsight = await customerAnalysisAgent.run({
    city: request.city,
    customerId: request.customerId,
    customer,
    region,
    currentSeason
  });

  // 5. Stok Analiz Ajanı (paralel çalışabilir)
  const stockInsight = await stockAnalysisAgent.run({
    products,
    currentSeason,
    seasonalNeeds
  });

  // 6. Kampanya Planlayıcı
  const campaign = await campaignPlanner.run({
    objective: request.objective,
    event: request.event,
    customerInsight,
    stockInsight,
    regionContext: {
      region: region.name,
      climateType: region.climateType,
      medianBasket: region.medianBasket,
      trend: region.trend,
      currentSeason,
      seasonalNeeds
    }
  });

  // 7. Yanıt
  return {
    success: true,
    campaign,
    metadata: {
      tenantId: request.tenantId,
      processedAt: new Date().toISOString(),
      executionTimeMs: Date.now() - startTime
    }
  };
}
```

---

## Test Senaryoları

### Senaryo 1: Tam Girdi
```json
{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue",
  "city": "Istanbul",
  "customerId": "C-1001",
  "event": "MothersDay"
}
```
Beklenen: Başarılı kampanya JSON

### Senaryo 2: Müşteri ID Yok (Bölge Modu)
```json
{
  "tenantId": "farmasi",
  "objective": "ClearOverstock",
  "city": "Ankara"
}
```
Beklenen: Bölge bazlı kampanya JSON

### Senaryo 3: Geçersiz Tenant
```json
{
  "tenantId": "nonexistent",
  "objective": "IncreaseRevenue",
  "city": "Istanbul"
}
```
Beklenen: `{ success: false, error: { code: "INVALID_TENANT" } }`

### Senaryo 4: Geçersiz Şehir
```json
{
  "tenantId": "farmasi",
  "objective": "IncreaseRevenue",
  "city": "Paris"
}
```
Beklenen: `{ success: false, error: { code: "INVALID_CITY" } }`

---

## API Endpoint

```
POST /api/campaign
Content-Type: application/json

Body: { tenantId, objective, city, customerId?, event? }
```

---

## Notlar

- Orkestratör **hiçbir segmentasyon veya kampanya kararı almaz**
- Sadece veri yükler, ajanları çağırır, yanıtı döndürür
- Tüm iş mantığı Müşteri Analiz, Stok Analiz ve Kampanya Planlayıcı ajanlarda
- Müşteri ve Stok analizi paralel çalışabilir (bağımsız)
- Hackathon'da ilk yazılacak bileşen — diğer ajanlar için arayüz sözleşmesi sağlar
