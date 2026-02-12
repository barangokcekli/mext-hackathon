# Customer Segment Agent - Entegrasyon Rehberi

## 🔗 Agent'a Erişim Yöntemleri

AgentCore Runtime üzerinde deploy edilen agentlar için **direkt HTTP URL yoktur**. Agent'a erişim için AWS SDK veya AgentCore CLI kullanılması gerekir.

### Agent Bilgileri

**Agent ARN:**
```
arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt
```

**Region:** us-west-2  
**Account:** 485169707250

---

## 🧪 Hızlı Test (AgentCore CLI)

### Test 1: Yeni Müşteri Analizi

```bash
agentcore invoke '{
  "customerData": {
    "customerId": "C-TEST-001",
    "city": "Istanbul",
    "customer": {
      "customerId": "C-TEST-001",
      "age": 28,
      "gender": "F",
      "registeredAt": "2026-01-15T00:00:00",
      "productHistory": []
    },
    "region": {
      "name": "Marmara",
      "climateType": "Temperate",
      "medianBasket": 250.0,
      "trend": "Skincare"
    },
    "currentSeason": "Winter"
  }
}'
```

### Test 2: Aktif Müşteri Analizi

```bash
agentcore invoke '{
  "customerData": {
    "customerId": "C-1001",
    "city": "Istanbul",
    "customer": {
      "customerId": "C-1001",
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
    },
    "currentSeason": "Winter"
  }
}'
```

---

## 🔌 Diğer Agentlarla Entegrasyon

### Yöntem 1: Orchestrator Agent İçinden Çağırma (Önerilen)

Orchestrator agent içinden Customer Segment Agent'ı çağırmak için AWS SDK kullanın:

```python
import boto3
import json

class OrchestratorAgent:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-agentcore', region_name='us-west-2')
        self.segment_agent_arn = 'arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt'
    
    def analyze_customer(self, customer_data):
        """Customer Segment Agent'ı çağır"""
        payload = {
            "customerData": customer_data
        }
        
        response = self.bedrock_client.invoke_agent(
            agentArn=self.segment_agent_arn,
            payload=payload
        )
        
        result = json.loads(response['body'].read())
        return result['analysis']
    
    def plan_campaign(self, customer_id, customer_data, region_data):
        """Kampanya planla - önce müşteri analizi yap"""
        
        # 1. Customer Segment Agent'ı çağır
        segment_analysis = self.analyze_customer({
            "customerId": customer_id,
            "city": customer_data['city'],
            "customer": customer_data,
            "region": region_data,
            "currentSeason": "Winter"
        })
        
        # 2. Analiz sonuçlarını kullanarak kampanya planla
        campaign_strategy = self._create_campaign_strategy(segment_analysis)
        
        return {
            "customerAnalysis": segment_analysis,
            "campaignStrategy": campaign_strategy
        }
    
    def _create_campaign_strategy(self, segment_analysis):
        """Segment analizine göre kampanya stratejisi oluştur"""
        strategy = {
            "targetSegment": segment_analysis['ageSegment'],
            "churnRisk": segment_analysis['churnSegment'],
            "valueSegment": segment_analysis['valueSegment'],
            "recommendations": []
        }
        
        # Churn risk'e göre öneriler
        if segment_analysis['churnSegment'] == 'Riskli':
            strategy['recommendations'].append({
                "type": "retention",
                "message": "Win-back kampanyası öner",
                "discount": "20%"
            })
        
        # Value segment'e göre öneriler
        if segment_analysis['valueSegment'] == 'HighValue':
            strategy['recommendations'].append({
                "type": "loyalty",
                "message": "Premium ürün öner",
                "benefit": "VIP avantajlar"
            })
        
        # Missing regulars için öneriler
        if segment_analysis.get('missingRegulars'):
            strategy['recommendations'].append({
                "type": "replenishment",
                "message": "Düzenli ürün hatırlatması",
                "products": [p['productId'] for p in segment_analysis['missingRegulars']]
            })
        
        return strategy

# Kullanım örneği
orchestrator = OrchestratorAgent()

customer_data = {
    "customerId": "C-1001",
    "city": "Istanbul",
    "age": 32,
    "gender": "F",
    "registeredAt": "2024-03-15T00:00:00",
    "productHistory": [...]
}

region_data = {
    "name": "Marmara",
    "climateType": "Temperate",
    "medianBasket": 75.0,
    "trend": "SKINCARE"
}

result = orchestrator.plan_campaign("C-1001", customer_data, region_data)
print(json.dumps(result, indent=2))
```

---

### Yöntem 2: Analysis Agent İçinden Çağırma

Analysis agent müşteri verilerini analiz ederken segment bilgilerini kullanabilir:

```python
import boto3
import json

class AnalysisAgent:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-agentcore', region_name='us-west-2')
        self.segment_agent_arn = 'arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt'
    
    def get_customer_segments(self, customer_data):
        """Customer Segment Agent'tan segment bilgilerini al"""
        payload = {"customerData": customer_data}
        
        response = self.bedrock_client.invoke_agent(
            agentArn=self.segment_agent_arn,
            payload=payload
        )
        
        result = json.loads(response['body'].read())
        return result['analysis']
    
    def analyze_customer_behavior(self, customer_id, customer_data, region_data):
        """Müşteri davranışını analiz et"""
        
        # Segment bilgilerini al
        segments = self.get_customer_segments({
            "customerId": customer_id,
            "city": customer_data['city'],
            "customer": customer_data,
            "region": region_data,
            "currentSeason": "Winter"
        })
        
        # Davranış analizi yap
        behavior_analysis = {
            "segments": segments,
            "insights": self._generate_insights(segments),
            "nextBestActions": self._recommend_actions(segments)
        }
        
        return behavior_analysis
    
    def _generate_insights(self, segments):
        """Segment bilgilerinden içgörüler çıkar"""
        insights = []
        
        if segments['churnSegment'] == 'Riskli':
            insights.append("Müşteri churn riski altında - acil aksiyon gerekli")
        
        if segments['valueSegment'] == 'HighValue':
            insights.append("Yüksek değerli müşteri - özel ilgi gösterilmeli")
        
        if segments['diversityProfile'] == 'Kaşif':
            insights.append("Yeni ürünlere açık - çapraz satış fırsatı")
        
        return insights
    
    def _recommend_actions(self, segments):
        """Segment bilgilerine göre aksiyon öner"""
        actions = []
        
        # Churn risk'e göre
        if segments['churnSegment'] in ['Ilık', 'Riskli']:
            actions.append({
                "priority": "high",
                "action": "send_retention_offer",
                "channel": "email"
            })
        
        # Missing regulars için
        if segments.get('missingRegulars'):
            actions.append({
                "priority": "medium",
                "action": "send_replenishment_reminder",
                "products": [p['productId'] for p in segments['missingRegulars']]
            })
        
        return actions
```

---

### Yöntem 3: Campaign Planner Agent İçinden Çağırma

Campaign planner agent kampanya hedef kitlesi belirlerken segment bilgilerini kullanabilir:

```python
import boto3
import json

class CampaignPlannerAgent:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-agentcore', region_name='us-west-2')
        self.segment_agent_arn = 'arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt'
    
    def segment_customers_for_campaign(self, customer_list, region_data):
        """Kampanya için müşterileri segmentlere ayır"""
        segmented_customers = []
        
        for customer in customer_list:
            # Her müşteri için segment analizi yap
            segment_data = self._get_customer_segment(customer, region_data)
            
            segmented_customers.append({
                "customerId": customer['customerId'],
                "segments": segment_data,
                "campaignEligibility": self._check_campaign_eligibility(segment_data)
            })
        
        return segmented_customers
    
    def _get_customer_segment(self, customer, region_data):
        """Tek bir müşteri için segment bilgisi al"""
        payload = {
            "customerData": {
                "customerId": customer['customerId'],
                "city": customer['city'],
                "customer": customer,
                "region": region_data,
                "currentSeason": "Winter"
            }
        }
        
        response = self.bedrock_client.invoke_agent(
            agentArn=self.segment_agent_arn,
            payload=payload
        )
        
        result = json.loads(response['body'].read())
        return result['analysis']
    
    def _check_campaign_eligibility(self, segment_data):
        """Kampanya uygunluğunu kontrol et"""
        eligibility = {
            "winback": segment_data['churnSegment'] == 'Riskli',
            "loyalty": segment_data['loyaltyTier'] in ['Platin', 'Altın'],
            "crosssell": segment_data['diversityProfile'] == 'Kaşif',
            "replenishment": len(segment_data.get('missingRegulars', [])) > 0
        }
        
        return eligibility
    
    def create_targeted_campaign(self, campaign_type, customer_list, region_data):
        """Hedefli kampanya oluştur"""
        
        # Müşterileri segmentlere ayır
        segmented = self.segment_customers_for_campaign(customer_list, region_data)
        
        # Kampanya tipine göre hedef müşterileri filtrele
        target_customers = []
        
        if campaign_type == "winback":
            target_customers = [c for c in segmented 
                              if c['campaignEligibility']['winback']]
        
        elif campaign_type == "loyalty":
            target_customers = [c for c in segmented 
                              if c['campaignEligibility']['loyalty']]
        
        elif campaign_type == "crosssell":
            target_customers = [c for c in segmented 
                              if c['campaignEligibility']['crosssell']]
        
        return {
            "campaignType": campaign_type,
            "targetCount": len(target_customers),
            "targetCustomers": target_customers
        }
```

---

## 🔄 Toplu İşlem (Batch Processing)

Birden fazla müşteri için segment analizi yapmak:

```python
import boto3
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class BatchSegmentProcessor:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-agentcore', region_name='us-west-2')
        self.segment_agent_arn = 'arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt'
    
    def process_customer(self, customer, region_data):
        """Tek bir müşteri için segment analizi"""
        payload = {
            "customerData": {
                "customerId": customer['customerId'],
                "city": customer['city'],
                "customer": customer,
                "region": region_data,
                "currentSeason": "Winter"
            }
        }
        
        try:
            response = self.bedrock_client.invoke_agent(
                agentArn=self.segment_agent_arn,
                payload=payload
            )
            result = json.loads(response['body'].read())
            return {
                "customerId": customer['customerId'],
                "success": True,
                "analysis": result['analysis']
            }
        except Exception as e:
            return {
                "customerId": customer['customerId'],
                "success": False,
                "error": str(e)
            }
    
    def process_batch(self, customer_list, region_data, max_workers=10):
        """Birden fazla müşteri için paralel işlem"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Tüm müşteriler için işlem başlat
            futures = {
                executor.submit(self.process_customer, customer, region_data): customer
                for customer in customer_list
            }
            
            # Sonuçları topla
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        return results

# Kullanım
processor = BatchSegmentProcessor()

customers = [
    {"customerId": "C-1001", "city": "Istanbul", ...},
    {"customerId": "C-1002", "city": "Ankara", ...},
    # ... daha fazla müşteri
]

region_data = {
    "name": "Marmara",
    "climateType": "Temperate",
    "medianBasket": 75.0,
    "trend": "SKINCARE"
}

results = processor.process_batch(customers, region_data)

# Başarılı ve başarısız işlemleri ayır
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"Başarılı: {len(successful)}, Başarısız: {len(failed)}")
```

---

## 📊 Segment Dağılımı Analizi

Tüm müşteri tabanı için segment dağılımını analiz etmek:

```python
from collections import Counter

class SegmentDistributionAnalyzer:
    def __init__(self, batch_processor):
        self.batch_processor = batch_processor
    
    def analyze_distribution(self, customer_list, region_data):
        """Segment dağılımını analiz et"""
        
        # Tüm müşteriler için segment analizi yap
        results = self.batch_processor.process_batch(customer_list, region_data)
        
        # Başarılı sonuçları al
        successful = [r['analysis'] for r in results if r['success']]
        
        # Dağılımları hesapla
        distribution = {
            "ageSegments": Counter(s['ageSegment'] for s in successful),
            "churnSegments": Counter(s['churnSegment'] for s in successful),
            "valueSegments": Counter(s['valueSegment'] for s in successful),
            "loyaltyTiers": Counter(s['loyaltyTier'] for s in successful),
            "affinityTypes": Counter(s['affinityType'] for s in successful),
            "diversityProfiles": Counter(s['diversityProfile'] for s in successful)
        }
        
        # Yüzdelik hesapla
        total = len(successful)
        distribution_pct = {}
        
        for key, counter in distribution.items():
            distribution_pct[key] = {
                segment: {
                    "count": count,
                    "percentage": round(count / total * 100, 2)
                }
                for segment, count in counter.items()
            }
        
        return {
            "totalCustomers": total,
            "distribution": distribution_pct,
            "insights": self._generate_distribution_insights(distribution_pct)
        }
    
    def _generate_distribution_insights(self, distribution):
        """Dağılım içgörüleri oluştur"""
        insights = []
        
        # Churn risk analizi
        churn = distribution['churnSegments']
        risky_pct = churn.get('Riskli', {}).get('percentage', 0)
        if risky_pct > 30:
            insights.append(f"⚠️ Müşterilerin %{risky_pct}'si churn riski altında")
        
        # Value segment analizi
        value = distribution['valueSegments']
        high_value_pct = value.get('HighValue', {}).get('percentage', 0)
        insights.append(f"💎 Müşterilerin %{high_value_pct}'si yüksek değerli")
        
        # Loyalty tier analizi
        loyalty = distribution['loyaltyTiers']
        premium_pct = (loyalty.get('Platin', {}).get('percentage', 0) + 
                      loyalty.get('Altın', {}).get('percentage', 0))
        insights.append(f"⭐ Müşterilerin %{premium_pct}'si premium tier'da")
        
        return insights
```

---

## 🔐 IAM Permissions

Diğer agentların Customer Segment Agent'ı çağırabilmesi için gerekli IAM izinleri:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:InvokeAgent"
      ],
      "Resource": "arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt"
    }
  ]
}
```

---

## 📝 Örnek Entegrasyon Senaryoları

### Senaryo 1: Orchestrator → Customer Segment → Campaign Planner

```python
# 1. Orchestrator müşteri verisini alır
customer_data = get_customer_from_database(customer_id)

# 2. Customer Segment Agent'ı çağırır
segment_analysis = customer_segment_agent.analyze(customer_data)

# 3. Segment analizini Campaign Planner'a gönderir
campaign_plan = campaign_planner_agent.create_campaign(segment_analysis)

# 4. Sonucu döner
return {
    "customerSegments": segment_analysis,
    "campaignPlan": campaign_plan
}
```

### Senaryo 2: Analysis Agent → Customer Segment → Stock Analysis

```python
# 1. Analysis Agent müşteri segmentlerini alır
segments = customer_segment_agent.analyze_batch(customer_list)

# 2. Segment dağılımına göre stok ihtiyacını hesaplar
segment_distribution = calculate_distribution(segments)

# 3. Stock Analysis Agent'a segment bazlı talep tahmini gönderir
stock_forecast = stock_analysis_agent.forecast_demand(segment_distribution)

return stock_forecast
```

---

## 🚀 Performans İpuçları

1. **Batch Processing:** Birden fazla müşteri için paralel işlem yapın
2. **Caching:** Sık kullanılan segment analizlerini cache'leyin
3. **Retry Logic:** Geçici hatalar için exponential backoff kullanın
4. **Timeout:** Uzun süren işlemler için uygun timeout değerleri ayarlayın
5. **Error Handling:** Her agent çağrısını try-catch ile sarın

---

## 📞 Destek

Entegrasyon sorunları için:
- CloudWatch Logs: `/aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT`
- API Dokümantasyonu: `customer-segment-agent-api.md`
- Deployment Bilgileri: `DEPLOYMENT_INFO.md`
