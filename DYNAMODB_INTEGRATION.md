# DynamoDB Entegrasyonu

Bu dokümanda agent'ların DynamoDB ile nasıl entegre edileceği açıklanmaktadır.

## Genel Bakış

Sistemde 3 ana agent var:
1. **Customer Segment Agent** - Müşteri segmentasyonu
2. **Product Analysis Agent** - Ürün analizi
3. **Orchestrator Agent** - Agent koordinasyonu

Her agent hem mock data (JSON dosyaları) hem de DynamoDB ile çalışabilir.

## DynamoDB Tabloları

### 1. Customers
Müşteri bilgilerini saklar.

**Primary Key:** `customerId` (String)

**Global Secondary Indexes:**
- `RegionIndex` - region bazlı sorgular için
- `CityIndex` - city bazlı sorgular için

**Örnek Item:**
```json
{
  "customerId": "C-1001",
  "age": 32,
  "gender": "F",
  "city": "Istanbul",
  "region": "Marmara",
  "registeredAt": "2023-01-15T10:30:00Z"
}
```

### 2. Orders
Sipariş geçmişini saklar.

**Primary Key:** `orderId` (String)

**Global Secondary Indexes:**
- `CustomerIdIndex` - customerId + orderDate
- `ProductIdIndex` - productId + orderDate

**Örnek Item:**
```json
{
  "orderId": "ORD-12345",
  "customerId": "C-1001",
  "productId": "P-5001",
  "category": "SKINCARE",
  "amount": 125.50,
  "quantity": 2,
  "orderDate": "2024-02-10T14:20:00Z"
}
```

### 3. Products
Ürün bilgilerini saklar.

**Primary Key:** `productId` (String)

**Global Secondary Indexes:**
- `TenantIdIndex` - tenantId bazlı sorgular için
- `CategoryIndex` - category bazlı sorgular için

**Örnek Item:**
```json
{
  "productId": "P-5001",
  "tenantId": "farmasi",
  "name": "Hydrating Face Cream",
  "category": "SKINCARE",
  "basePrice": 89.90,
  "cost": 35.00,
  "stock": 150,
  "seasonalTags": ["WINTER", "SPRING"]
}
```

### 4. Regions
Bölge bilgilerini saklar.

**Primary Key:** `regionName` (String)

**Örnek Item:**
```json
{
  "regionName": "Marmara",
  "climateType": "Temperate",
  "medianBasket": 75.0,
  "trend": "SKINCARE"
}
```

### 5. ClimateData
Şehir bazlı iklim verilerini saklar.

**Primary Key:** `city` (String)

**Örnek Item:**
```json
{
  "city": "Istanbul",
  "avgTempC": 8,
  "humidity": 75,
  "season": "WINTER"
}
```

## Kurulum

### 1. DynamoDB Tablolarını Oluşturma

```bash
# Tabloları oluştur
python dynamodb_setup.py --create-tables

# Mock data'yı yükle
python dynamodb_setup.py --load-data

# Her ikisini de yap
python dynamodb_setup.py --all
```

### 2. AWS Credentials

AWS credentials'ınızın yapılandırıldığından emin olun:

```bash
aws configure
```

veya environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2
```

## Kullanım

### Customer Segment Agent

```python
from customer_segment_agent.dynamodb_client import get_dynamodb_client

# DynamoDB client oluştur
db_client = get_dynamodb_client(region_name="us-west-2")

# Müşteri verisi çek
customer_data = db_client.build_customer_payload("C-1001")

# Agent'a gönder
from customer_segment_agent import invoke
result = invoke({"customerData": customer_data})
```

### Product Analysis Agent

```python
from product_agent.dynamodb_client import get_product_dynamodb_client

# DynamoDB client oluştur
product_client = get_product_dynamodb_client(region_name="us-west-2")

# Ürün verisi çek
product_data = product_client.build_product_payload(tenant_id="farmasi")

# Agent'a gönder
from product_agent.product_analysis_agent import invoke
result = invoke(product_data)
```

### Orchestrator Agent (DynamoDB Mode)

Orchestrator agent'ı DynamoDB mode'da kullanmak için:

```python
payload = {
    "prompt": "Yaz kampanyası oluştur",
    "customerId": "C-1001",      # DynamoDB'den çekilecek
    "tenantId": "farmasi",       # DynamoDB'den çekilecek
    "useDynamoDB": True,         # DynamoDB mode aktif
    "useLLM": False              # Deterministik akış
}

from orchestrator_agent import invoke
result = invoke(payload)
```

### Mock Data Mode (Varsayılan)

DynamoDB kullanmadan mock data ile çalışmak için:

```python
payload = {
    "prompt": "Yaz kampanyası oluştur",
    "customerData": {...},  # JSON dosyasından yüklenen veri
    "productData": {...},   # JSON dosyasından yüklenen veri
    "useDynamoDB": False    # veya belirtme (default: False)
}

result = invoke(payload)
```

## Test

### DynamoDB ile Test

```bash
# Orchestrator'ı DynamoDB ile test et
python -c "
from orchestrator_agent import invoke
result = invoke({
    'prompt': 'Kış kampanyası oluştur',
    'customerId': 'C-2001',
    'tenantId': 'farmasi',
    'useDynamoDB': True,
    'useLLM': False
})
print(result)
"
```

### Mock Data ile Test

```bash
# Mevcut test script'i kullan (mock data)
python test_orchestrator.py --customer C-2001
```

## IAM Permissions

DynamoDB kullanımı için gerekli IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchGetItem",
        "dynamodb:PutItem",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-west-2:*:table/Customers",
        "arn:aws:dynamodb:us-west-2:*:table/Customers/index/*",
        "arn:aws:dynamodb:us-west-2:*:table/Orders",
        "arn:aws:dynamodb:us-west-2:*:table/Orders/index/*",
        "arn:aws:dynamodb:us-west-2:*:table/Products",
        "arn:aws:dynamodb:us-west-2:*:table/Products/index/*",
        "arn:aws:dynamodb:us-west-2:*:table/Regions",
        "arn:aws:dynamodb:us-west-2:*:table/ClimateData"
      ]
    }
  ]
}
```

## Maliyet Optimizasyonu

Tablolar **PAY_PER_REQUEST** (On-Demand) billing mode ile oluşturulmuştur. Bu:
- Düşük trafikte daha ekonomik
- Otomatik scaling
- Minimum yönetim gerektirir

Production'da yüksek ve öngörülebilir trafik varsa **PROVISIONED** mode'a geçilebilir.

## Troubleshooting

### DynamoDB clients yüklenemiyor

```bash
# Python path'i kontrol et
export PYTHONPATH="${PYTHONPATH}:./customer-segment-agent:./product-agent"
```

### Tablolar bulunamıyor

```bash
# Tabloları listele
aws dynamodb list-tables --region us-west-2

# Tablo detaylarını gör
aws dynamodb describe-table --table-name Customers --region us-west-2
```

### Data yüklenemiyor

```bash
# Dosya yollarını kontrol et
ls -la customer-segment-agent/mock-data/farmasi/
ls -la product-agent/data/

# Script'i verbose mode'da çalıştır
python dynamodb_setup.py --all
```

## Sonraki Adımlar

1. **Production Data Migration**: Mock data yerine gerçek production data'yı migrate et
2. **Caching**: Sık kullanılan verileri cache'le (ElastiCache/Redis)
3. **Monitoring**: CloudWatch alarms ve metrics ekle
4. **Backup**: DynamoDB Point-in-Time Recovery aktif et
5. **Security**: VPC endpoints ve encryption at rest aktif et
