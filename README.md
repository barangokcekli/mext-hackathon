# Customer Segment Agent

AI-powered customer segmentation agent built with AWS Bedrock AgentCore and Strands Agents framework.

## 🎯 Overview

This agent analyzes customer data and provides comprehensive segmentation insights including:
- Age segments (GenZ, GençYetişkin, Yetişkin, Olgun)
- Churn risk analysis (Aktif, Ilık, Riskli)
- Value classification (HighValue, Standard)
- Loyalty tiers (Platin, Altın, Gümüş, Bronz)
- Product affinity and diversity profiles

## 🚀 Features

- **Three Analysis Modes:**
  - Regular: Full customer history analysis
  - New Customer: Profile for customers without purchase history
  - Region: Location-based demographic profiling

- **Performance:**
  - 0.03ms average per customer analysis
  - 29,000+ customers/second throughput
  - Production-ready with logging and validation

- **Production Ready:**
  - Input validation with detailed error messages
  - Comprehensive logging (CloudWatch integration)
  - Error handling with fallback mechanisms
  - AWS Bedrock AgentCore deployment

## 📋 Requirements

```txt
strands-agents
bedrock-agentcore
aws-opentelemetry-distro>=0.10.1
boto3
```

## 🛠️ Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

Configure AWS credentials in `.aws/credentials`:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-west-2
```

## 📦 Deployment

```bash
# Deploy to AWS Bedrock AgentCore
agentcore deploy

# Check status
agentcore status

# View logs
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT --follow
```

## 💻 Usage

### Request Format

**Regular Customer (with purchase history):**
```json
{
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
    }
  }
}
```

**New Customer (no purchase history):**
```json
{
  "customerData": {
    "customerId": "C-NEW-001",
    "city": "Antalya",
    "customer": {
      "customerId": "C-NEW-001",
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

**Region-based (no customer ID):**
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

### Invoke Agent

```bash
# Local test
agentcore invoke '{"customerData": {...}}'

# Or use the test script
python performance_test_pure.py
```

### Response Format

```json
{
  "analysis": {
    "mode": "regular",
    "customerId": "C-1001",
    "city": "Istanbul",
    "region": "Marmara",
    "age": 32,
    "ageSegment": "GençYetişkin",
    "gender": "F",
    "churnSegment": "Aktif",
    "valueSegment": "Standard",
    "loyaltyTier": "Gümüş",
    "affinityCategory": "SKINCARE",
    "affinityType": "Odaklı",
    "diversityProfile": "Sadık",
    "avgBasket": 59.90,
    "totalSpent": 479.20,
    "orderCount": 8,
    "lastPurchaseDaysAgo": 23,
    "topProducts": [...],
    "missingRegulars": []
  },
  "explanation": "AI-generated natural language explanation...",
  "timestamp": "2026-02-12T11:40:06.062708"
}
```

## 🧪 Testing

```bash
# Run performance test (20 customers)
python performance_test_pure.py

# Test deployed agent
python test_deployed_agent_20.py

# Quick shell test
./test_aws_deployed_quick.sh
```

## 📊 Performance Metrics

- **Throughput:** 29,238 customers/second
- **Latency:** 0.03ms average per customer
- **Rating:** A+ (Blazing Fast)
- **Scalability:** 
  - 1,000 customers: 0.03s
  - 10,000 customers: 0.34s
  - 2.5M+ customers per day capacity

## 🗂️ Project Structure

```
.
├── customer_segment_agent.py      # Main agent code
├── .bedrock_agentcore.yaml        # Deployment config
├── requirements.txt               # Dependencies
├── database_schema.sql            # Database schema
├── mock-data/                     # Test data
│   ├── regions.json
│   ├── tenants.json
│   └── farmasi/
│       ├── customers.json
│       ├── customers-100.json
│       └── products.json
├── example-request*.json          # Request examples
├── example-response*.json         # Response examples
└── performance_test_*.py          # Test scripts
```

## 🔍 Segmentation Logic

### Age Segments
- **GenZ:** ≤25 years
- **GençYetişkin:** 26-35 years
- **Yetişkin:** 36-50 years
- **Olgun:** >50 years

### Churn Segments
- **Aktif:** Last purchase <30 days ago
- **Ilık:** Last purchase 30-60 days ago
- **Riskli:** Last purchase >60 days ago

### Value Segments
- **HighValue:** Avg basket > region median
- **Standard:** Avg basket ≤ region median

### Loyalty Tiers
- **Platin:** 12+ months membership, 2+ orders/month
- **Altın:** 6+ months membership, 1+ orders/month
- **Gümüş:** 3+ total orders
- **Bronz:** <3 total orders

## 📈 Monitoring

**CloudWatch Logs:**
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT --follow
```

**GenAI Observability Dashboard:**
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core

## 🏗️ Architecture

- **Framework:** Strands Agents
- **Runtime:** AWS Bedrock AgentCore
- **Deployment:** Direct Code Deploy (no Docker)
- **Region:** us-west-2
- **Observability:** CloudWatch + X-Ray
- **Memory:** STM_ONLY mode

## 🔐 Security

- Input validation for all customer data
- Age validation (0-120 range)
- Negative value checks for financial data
- Error handling with detailed logging
- AWS IAM role-based access control

## 📝 License

Proprietary - Hackathon Project

## 👥 Credits

See `credits.txt` for AWS credentials and configuration details.

## 🚧 Future Improvements

- [ ] ML-based dynamic segmentation
- [ ] Tenant-specific rule customization
- [ ] Real-time streaming analytics
- [ ] A/B testing framework
- [ ] Advanced caching layer
- [ ] Multi-language support
