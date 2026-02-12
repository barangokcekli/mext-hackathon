# Customer Segment Agent - Uzaktan Erişim Rehberi

## ✅ Evet, Başka Bir PC'den Çağırabilirsiniz!

Agent AWS Bedrock AgentCore Runtime'da deploy edildiği için **internet bağlantısı olan herhangi bir cihazdan** erişilebilir.

---

## 🔑 Gereksinimler

### 1. AWS Credentials

Başka bir PC'den agent'ı çağırmak için sadece AWS credentials gerekli:

```bash
# AWS Access Key ID
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE

# AWS Secret Access Key
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Region
AWS_DEFAULT_REGION=us-west-2
```

**Mevcut credentials'ınız:** `credits.txt` dosyasında

### 2. Gerekli Yazılımlar

**Seçenek A: AgentCore CLI (En Kolay)**
```bash
pip install bedrock-agentcore-starter-toolkit
```

**Seçenek B: AWS SDK (Python)**
```bash
pip install boto3
```

**Seçenek C: AWS SDK (Node.js)**
```bash
npm install @aws-sdk/client-bedrock-agentcore
```

---

## 🚀 Hızlı Başlangıç (Yeni PC'de)

### Adım 1: AWS Credentials Ayarla

**Yöntem 1: Environment Variables (Önerilen)**
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"
```

**Yöntem 2: AWS CLI Config**
```bash
aws configure
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region name: us-west-2
# Default output format: json
```

**Yöntem 3: Credentials File**
```bash
# ~/.aws/credentials dosyası oluştur
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
region = us-west-2
```

### Adım 2: AgentCore CLI Kur

```bash
pip install bedrock-agentcore-starter-toolkit
```

### Adım 3: Agent'ı Test Et

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

---

## 💻 Platform Bazlı Kurulum

### Windows

```powershell
# 1. Python kur (python.org)
# 2. AgentCore CLI kur
pip install bedrock-agentcore-starter-toolkit

# 3. Credentials ayarla
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:AWS_DEFAULT_REGION="us-west-2"

# 4. Test et
agentcore invoke '{"customerData": {...}}'
```

### macOS / Linux

```bash
# 1. Python zaten kurulu (genelde)
# 2. AgentCore CLI kur
pip3 install bedrock-agentcore-starter-toolkit

# 3. Credentials ayarla
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# 4. Test et
agentcore invoke '{"customerData": {...}}'
```

### Docker Container

```dockerfile
FROM python:3.11-slim

# AgentCore CLI kur
RUN pip install bedrock-agentcore-starter-toolkit boto3

# Credentials ayarla (environment variables ile)
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_DEFAULT_REGION="us-west-2"

# Test script
COPY test_agent.py /app/test_agent.py
WORKDIR /app

CMD ["python", "test_agent.py"]
```

---

## 🌐 Web Uygulamasından Çağırma

### Backend API (Python Flask)

```python
from flask import Flask, request, jsonify
import boto3
import json

app = Flask(__name__)

# AWS client
bedrock_client = boto3.client('bedrock-agentcore', region_name='us-west-2')
AGENT_ARN = 'arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt'

@app.route('/api/analyze-customer', methods=['POST'])
def analyze_customer():
    """Customer segment analizi endpoint'i"""
    try:
        customer_data = request.json
        
        # Agent'ı çağır
        response = bedrock_client.invoke_agent(
            agentArn=AGENT_ARN,
            payload={"customerData": customer_data}
        )
        
        result = json.loads(response['body'].read())
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint'i"""
    return jsonify({"status": "healthy", "agent": "customer-segment"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Frontend (JavaScript)

```javascript
// Customer segment analizi yap
async function analyzeCustomer(customerData) {
  try {
    const response = await fetch('http://your-backend-url/api/analyze-customer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(customerData)
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error analyzing customer:', error);
    throw error;
  }
}

// Kullanım
const customerData = {
  customerId: "C-1001",
  city: "Istanbul",
  customer: {
    customerId: "C-1001",
    age: 32,
    gender: "F",
    registeredAt: "2024-03-15T00:00:00",
    productHistory: [...]
  },
  region: {
    name: "Marmara",
    climateType: "Temperate",
    medianBasket: 75.0,
    trend: "SKINCARE"
  },
  currentSeason: "Winter"
};

analyzeCustomer(customerData)
  .then(result => {
    console.log('Customer Analysis:', result.analysis);
    console.log('Explanation:', result.explanation);
  })
  .catch(error => {
    console.error('Failed to analyze customer:', error);
  });
```

---

## 📱 Mobil Uygulamadan Çağırma

### React Native

```javascript
import AWS from 'aws-sdk';

// AWS config
AWS.config.update({
  accessKeyId: 'your-access-key',
  secretAccessKey: 'your-secret-key',
  region: 'us-west-2'
});

const bedrockClient = new AWS.BedrockAgentCore();

async function analyzeCustomer(customerData) {
  const params = {
    agentArn: 'arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt',
    payload: {
      customerData: customerData
    }
  };
  
  try {
    const response = await bedrockClient.invokeAgent(params).promise();
    return JSON.parse(response.body);
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

---

## 🔒 Güvenlik Best Practices

### 1. Credentials'ı Güvenli Sakla

**❌ YAPMAYIN:**
```python
# Kod içinde hardcode etmeyin!
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
```

**✅ YAPIN:**
```python
# Environment variables kullanın
import os
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
```

### 2. IAM Permissions - Least Privilege

Agent'ı çağıracak kullanıcılar için minimal izinler:

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

### 3. Rate Limiting

Çok fazla istek göndermemek için rate limiting ekleyin:

```python
from time import sleep
from functools import wraps

def rate_limit(max_per_second):
    min_interval = 1.0 / max_per_second
    def decorator(func):
        last_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(10)  # Max 10 requests per second
def analyze_customer(customer_data):
    # Agent çağrısı
    pass
```

---

## 🧪 Test Script (Başka PC'de Çalıştırılabilir)

```python
#!/usr/bin/env python3
"""
Customer Segment Agent Test Script
Herhangi bir PC'den çalıştırılabilir
"""

import boto3
import json
import os
import sys

def test_agent():
    """Agent'ı test et"""
    
    # AWS credentials kontrolü
    if not os.environ.get('AWS_ACCESS_KEY_ID'):
        print("❌ AWS_ACCESS_KEY_ID environment variable bulunamadı!")
        print("Lütfen credentials'ı ayarlayın:")
        print("  export AWS_ACCESS_KEY_ID='your-key'")
        print("  export AWS_SECRET_ACCESS_KEY='your-secret'")
        sys.exit(1)
    
    print("✅ AWS credentials bulundu")
    
    # Client oluştur
    try:
        client = boto3.client('bedrock-agentcore', region_name='us-west-2')
        print("✅ AWS client oluşturuldu")
    except Exception as e:
        print(f"❌ Client oluşturulamadı: {e}")
        sys.exit(1)
    
    # Test payload
    payload = {
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
    }
    
    print("\n📤 Agent'a istek gönderiliyor...")
    
    # Agent'ı çağır
    try:
        response = client.invoke_agent(
            agentArn='arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt',
            payload=payload
        )
        
        result = json.loads(response['body'].read())
        
        print("✅ Agent başarıyla çağrıldı!\n")
        print("📊 Sonuç:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Agent çağrısı başarısız: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Customer Segment Agent - Remote Test")
    print("=" * 60)
    print()
    
    success = test_agent()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Test başarılı!")
    else:
        print("❌ Test başarısız!")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
```

**Kullanım:**
```bash
# 1. Script'i kaydet
curl -o test_agent.py https://your-repo/test_agent.py

# 2. Credentials ayarla
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# 3. Çalıştır
python3 test_agent.py
```

---

## 🌍 Farklı Lokasyonlardan Erişim

### Aynı AWS Account - Farklı Bölgeler

Agent us-west-2'de deploy edildi, ama **herhangi bir bölgeden** çağırabilirsiniz:

```python
# Tokyo'dan çağır
client = boto3.client('bedrock-agentcore', region_name='us-west-2')  # Agent'ın bölgesi
response = client.invoke_agent(agentArn='...', payload={...})
```

### Farklı AWS Accounts

Cross-account erişim için IAM role assumption gerekli:

```python
import boto3

# Assume role
sts_client = boto3.client('sts')
assumed_role = sts_client.assume_role(
    RoleArn='arn:aws:iam::485169707250:role/CrossAccountAgentAccess',
    RoleSessionName='CustomerSegmentSession'
)

# Temporary credentials ile client oluştur
credentials = assumed_role['Credentials']
client = boto3.client(
    'bedrock-agentcore',
    region_name='us-west-2',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken']
)

# Agent'ı çağır
response = client.invoke_agent(agentArn='...', payload={...})
```

---

## 📊 Monitoring (Uzaktan)

Başka bir PC'den agent'ın durumunu kontrol etmek:

```python
import boto3

def check_agent_status():
    """Agent durumunu kontrol et"""
    logs_client = boto3.client('logs', region_name='us-west-2')
    
    # Son 1 saatin loglarını al
    response = logs_client.filter_log_events(
        logGroupName='/aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT',
        startTime=int((time.time() - 3600) * 1000),  # Son 1 saat
        limit=10
    )
    
    print("Son 10 log:")
    for event in response['events']:
        print(f"  {event['message']}")
    
    return len(response['events']) > 0

# Kullanım
if check_agent_status():
    print("✅ Agent aktif ve çalışıyor")
else:
    print("⚠️ Son 1 saatte log bulunamadı")
```

---

## 🎯 Özet

### ✅ Evet, Başka PC'den Çağırabilirsiniz!

**Gerekli Tek Şey:**
1. AWS Credentials (Access Key + Secret Key)
2. Internet bağlantısı
3. Python veya Node.js (AWS SDK için)

**Agent Bilgileri:**
- **ARN:** `arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt`
- **Region:** us-west-2
- **Erişim:** Dünya çapında, 7/24

**Hızlı Test:**
```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
pip install bedrock-agentcore-starter-toolkit
agentcore invoke '{"customerData": {...}}'
```

---

## 📞 Sorun Giderme

### "Credentials not found" Hatası
```bash
# Credentials'ı kontrol et
aws sts get-caller-identity

# Çıktı:
# {
#   "UserId": "...",
#   "Account": "485169707250",
#   "Arn": "arn:aws:iam::485169707250:user/..."
# }
```

### "Access Denied" Hatası
IAM kullanıcınızın `bedrock-agentcore:InvokeAgent` iznine sahip olduğundan emin olun.

### "Region not found" Hatası
Region'ı us-west-2 olarak ayarlayın:
```bash
export AWS_DEFAULT_REGION=us-west-2
```

---

**Sonuç:** Agent AWS'de olduğu için, credentials'a sahip olan **herkes, her yerden** çağırabilir! 🌍
