# 🎯 Customer Segment Agent - AWS Bedrock AgentCore

Müşteri segmentasyonu ve profilleme için AWS Bedrock AgentCore Runtime üzerinde deploy edilmiş yapay zeka destekli agent.

[![AWS](https://img.shields.io/badge/AWS-Bedrock%20AgentCore-orange)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![Strands](https://img.shields.io/badge/Framework-Strands%20Agents-green)](https://github.com/strands-ai/strands-agents)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 İçindekiler

- [Genel Bakış](#-genel-bakış)
- [Özellikler](#-özellikler)
- [Mimari](#-mimari)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [Entegrasyon](#-entegrasyon)
- [Deployment](#-deployment)
- [Katkıda Bulunma](#-katkıda-bulunma)

## 🎯 Genel Bakış

Customer Segment Agent, müşteri verilerini analiz ederek kapsamlı segmentasyon ve profilleme insights'ları sağlar. Deterministik kurallar ve hesaplamalar kullanarak:

- **Demografik Segmentasyon**: Yaş, cinsiyet, lokasyon
- **Davranışsal Segmentasyon**: Churn risk, değer, sadakat
- **Ürün Tercihleri**: Kategori afinitesi, çeşitlilik profili
- **Finansal Metrikler**: Harcama analizi, sepet ortalaması
- **Aktivite Metrikleri**: Son alışveriş, üyelik süresi
- **Ürün İçgörüleri**: Eksik düzenli ürünler, en çok satın alınan ürünler

## ✨ Özellikler

### 🎭 Üç Operasyon Modu

1. **Regular Mode**: Satın alma geçmişi olan müşteriler için tam analiz
2. **New Customer Mode**: Henüz alışveriş yapmamış yeni müşteriler için profil
3. **Region Mode**: Müşteri ID'si olmadan bölgesel pazar insights'ı

### 📊 Segmentasyon Kategorileri

| Kategori | Segmentler | Açıklama |
|----------|-----------|----------|
| **Yaş** | GenZ, GençYetişkin, Yetişkin, Olgun | 18-25, 26-35, 36-50, 51+ |
| **Churn** | Aktif, Ilık, Riskli | <30, 30-60, >60 gün |
| **Değer** | HighValue, Standard | Bölge medyanı karşılaştırması |
| **Sadakat** | Platin, Altın, Gümüş, Bronz | Üyelik ve sipariş frekansı |
| **Afinite** | Odaklı, Keşifçi | Kategori odaklanması |
| **Çeşitlilik** | Kaşif, Dengeli, Sadık | Ürün çeşitliliği tercihi |

### 🚀 Teknik Özellikler

- ✅ **Deterministik**: Aynı girdi her zaman aynı çıktıyı verir
- ✅ **Ölçeklenebilir**: AWS AgentCore Runtime otomatik scaling
- ✅ **Hızlı**: Ortalama yanıt süresi <2 saniye
- ✅ **Güvenli**: IAM tabanlı erişim kontrolü
- ✅ **İzlenebilir**: CloudWatch Logs ve X-Ray tracing
- ✅ **Entegre**: Diğer agentlarla kolay entegrasyon

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Bedrock AgentCore                     │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Customer Segment Agent                    │  │
│  │                                                         │  │
│  │  ┌─────────────┐    ┌──────────────┐                 │  │
│  │  │   Strands   │───▶│  Analysis    │                 │  │
│  │  │   Agent     │    │  Pipeline    │                 │  │
│  │  └─────────────┘    └──────────────┘                 │  │
│  │                            │                           │  │
│  │         ┌──────────────────┼──────────────────┐       │  │
│  │         ▼                  ▼                  ▼       │  │
│  │  ┌──────────┐      ┌──────────┐      ┌──────────┐   │  │
│  │  │  Region  │      │   New    │      │ Regular  │   │  │
│  │  │   Mode   │      │ Customer │      │   Mode   │   │  │
│  │  └──────────┘      └──────────┘      └──────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Observability & Monitoring                │  │
│  │  • CloudWatch Logs  • X-Ray Tracing  • Metrics       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Kurulum

### Gereksinimler

- Python 3.11+
- AWS Account
- AWS Credentials (Access Key + Secret Key)

### Lokal Kurulum

```bash
# Repository'yi klonla
git clone https://github.com/your-username/customer-segment-agent.git
cd customer-segment-agent

# Virtual environment oluştur
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Bağımlılıkları kur
pip install -r requirements.txt

# AWS credentials ayarla
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
```

### AgentCore CLI Kurulumu

```bash
pip install bedrock-agentcore-starter-toolkit
```

## 💻 Kullanım

### Hızlı Test

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

### Python SDK ile Kullanım

```python
import boto3
import json

# Client oluştur
client = boto3.client('bedrock-agentcore', region_name='us-west-2')

# Agent'ı çağır
response = client.invoke_agent(
    agentArn='arn:aws:bedrock-agentcore:us-west-2:ACCOUNT_ID:runtime/customer_segment_agent-XXXXX',
    payload={
        "customerData": {
            "customerId": "C-1001",
            "city": "Istanbul",
            "customer": {...},
            "region": {...}
        }
    }
)

# Sonucu parse et
result = json.loads(response['body'].read())
print(json.dumps(result, indent=2))
```

## 📚 API Dokümantasyonu

Detaylı API dokümantasyonu için:
- [API Reference](customer-segment-agent-api.md)
- [Integration Guide](INTEGRATION_GUIDE.md)
- [Remote Access Guide](REMOTE_ACCESS_GUIDE.md)

### Request Format

```json
{
  "customerData": {
    "customerId": "string (optional)",
    "city": "string",
    "customer": {
      "customerId": "string",
      "age": "number",
      "gender": "string",
      "registeredAt": "ISO 8601 date",
      "productHistory": [...]
    },
    "region": {
      "name": "string",
      "climateType": "string",
      "medianBasket": "number",
      "trend": "string"
    }
  }
}
```

### Response Format

```json
{
  "analysis": {
    "customerId": "C-1001",
    "ageSegment": "GençYetişkin",
    "churnSegment": "Aktif",
    "valueSegment": "HighValue",
    "loyaltyTier": "Altın",
    "affinityCategory": "SKINCARE",
    "affinityType": "Odaklı",
    "diversityProfile": "Dengeli",
    "avgBasket": 75.24,
    "totalSpent": 1053.4,
    "orderCount": 14,
    "missingRegulars": [...],
    "topProducts": [...]
  },
  "explanation": "Natural language summary..."
}
```

## 🔌 Entegrasyon

### Orchestrator Agent'tan Çağırma

```python
class OrchestratorAgent:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-agentcore', region_name='us-west-2')
        self.segment_agent_arn = 'arn:aws:bedrock-agentcore:...'
    
    def analyze_customer(self, customer_data):
        response = self.bedrock_client.invoke_agent(
            agentArn=self.segment_agent_arn,
            payload={"customerData": customer_data}
        )
        return json.loads(response['body'].read())['analysis']
```

Daha fazla entegrasyon örneği için [Integration Guide](INTEGRATION_GUIDE.md) dosyasına bakın.

## 🚢 Deployment

### AWS'ye Deploy Etme

```bash
# 1. AgentCore'u yapılandır
agentcore configure --entrypoint customer_segment_agent.py

# 2. Deploy et
agentcore deploy

# 3. Test et
agentcore invoke '{"customerData": {...}}'
```

### Deployment Bilgileri

Deploy edildikten sonra şu bilgileri alacaksınız:
- **Agent ARN**: Agent'ı çağırmak için
- **IAM Role ARN**: İzinler için
- **CloudWatch Log Group**: Monitoring için

Detaylı deployment bilgileri için [DEPLOYMENT_INFO.md](DEPLOYMENT_INFO.md) dosyasına bakın.

## 📊 Monitoring

### CloudWatch Logs

```bash
# Logları takip et
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-XXXXX-DEFAULT --follow

# Son 1 saatin logları
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-XXXXX-DEFAULT --since 1h
```

### GenAI Observability Dashboard

AWS Console'da GenAI Observability Dashboard'a erişin:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core
```

## 🧪 Testing

### Unit Tests

```bash
# Testleri çalıştır
pytest test_customer_segment_agent.py -v

# Coverage ile
pytest --cov=customer_segment_agent test_customer_segment_agent.py
```

### Property-Based Tests

```bash
# Hypothesis ile property-based testler
pytest test_customer_segment_agent.py::TestAgeSegmentationProperties -v
```

## 📁 Proje Yapısı

```
customer-segment-agent/
├── customer_segment_agent.py      # Ana agent implementasyonu
├── requirements.txt                # Python bağımlılıkları
├── .gitignore                      # Git ignore kuralları
├── README.md                       # Bu dosya
├── customer-segment-agent-api.md  # API dokümantasyonu
├── INTEGRATION_GUIDE.md           # Entegrasyon rehberi
├── REMOTE_ACCESS_GUIDE.md         # Uzaktan erişim rehberi
├── DEPLOYMENT_INFO.md             # Deployment bilgileri
├── .kiro/
│   └── specs/
│       └── user-segment-agent/
│           ├── requirements.md     # Gereksinimler
│           ├── design.md           # Tasarım dokümantasyonu
│           └── tasks.md            # Implementasyon planı
└── mock-data/                      # Test verileri
    ├── regions.json
    └── farmasi/
        ├── customers.json
        └── products.json
```

## 🔒 Güvenlik

### Credentials Yönetimi

**❌ ASLA YAPMAYIN:**
- AWS credentials'ı kod içinde hardcode etmeyin
- `credits.txt` dosyasını commit etmeyin
- Public repository'de credentials paylaşmayın

**✅ YAPIN:**
- Environment variables kullanın
- AWS IAM roles kullanın
- `.gitignore` dosyasını güncel tutun
- Least privilege principle uygulayın

### IAM Permissions

Minimum gerekli izinler:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["bedrock-agentcore:InvokeAgent"],
      "Resource": "arn:aws:bedrock-agentcore:us-west-2:ACCOUNT_ID:runtime/customer_segment_agent-*"
    }
  ]
}
```

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 License

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 👥 Ekip

- **Proje Sahibi**: [Your Name]
- **Katkıda Bulunanlar**: [Contributors]

## 📞 İletişim

- **Issues**: [GitHub Issues](https://github.com/your-username/customer-segment-agent/issues)
- **Email**: your-email@example.com

## 🙏 Teşekkürler

- [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/)
- [Strands Agents Framework](https://github.com/strands-ai/strands-agents)
- Tüm katkıda bulunanlara

---

**Not**: Bu agent AWS Bedrock AgentCore Runtime üzerinde deploy edilmiştir ve production-ready durumdadır. Herhangi bir sorun veya soru için lütfen issue açın.
