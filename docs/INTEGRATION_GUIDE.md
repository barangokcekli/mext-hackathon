# Customer Segment Agent - Integration Guide

This guide explains how to integrate and call the Customer Segment Agent from other agents or orchestrators.

## 🔗 Agent Information

- **Agent Name:** `customer_segment_agent`
- **Agent ARN:** `arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt`
- **Region:** `us-west-2`
- **Endpoint Type:** AWS Bedrock AgentCore Runtime

## 📡 Integration Methods

### Method 1: Direct AWS SDK Call (Recommended)

Use AWS Bedrock AgentCore Runtime SDK to invoke the agent directly.

#### Python Example

```python
import boto3
import json

# Initialize Bedrock AgentCore client
client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

# Prepare customer data
customer_data = {
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

# Invoke the agent
response = client.invoke_agent(
    agentId='customer_segment_agent-1GD3a24jRt',
    agentAliasId='TSTALIASID',  # Use your alias ID
    sessionId='unique-session-id',
    inputText=json.dumps(customer_data)
)

# Parse response
result = json.loads(response['completion'])
print(f"Customer Segment: {result['analysis']['ageSegment']}")
print(f"Churn Risk: {result['analysis']['churnSegment']}")
print(f"Loyalty Tier: {result['analysis']['loyaltyTier']}")
```

#### Node.js Example

```javascript
const { BedrockAgentRuntimeClient, InvokeAgentCommand } = require("@aws-sdk/client-bedrock-agent-runtime");

const client = new BedrockAgentRuntimeClient({ region: "us-west-2" });

async function analyzeCustomer(customerData) {
    const command = new InvokeAgentCommand({
        agentId: "customer_segment_agent-1GD3a24jRt",
        agentAliasId: "TSTALIASID",
        sessionId: "unique-session-id",
        inputText: JSON.stringify({ customerData })
    });

    try {
        const response = await client.send(command);
        const result = JSON.parse(response.completion);
        
        console.log("Age Segment:", result.analysis.ageSegment);
        console.log("Churn Risk:", result.analysis.churnSegment);
        console.log("Loyalty Tier:", result.analysis.loyaltyTier);
        
        return result;
    } catch (error) {
        console.error("Error calling agent:", error);
        throw error;
    }
}

// Usage
const customerData = {
    customerId: "C-1001",
    city: "Istanbul",
    customer: {
        customerId: "C-1001",
        age: 32,
        gender: "F",
        registeredAt: "2024-03-15T00:00:00",
        productHistory: [
            {
                productId: "P-2001",
                category: "SKINCARE",
                totalQuantity: 8,
                totalSpent: 479.20,
                orderCount: 8,
                lastPurchase: "2026-01-20T00:00:00",
                avgDaysBetween: 30
            }
        ]
    },
    region: {
        name: "Marmara",
        climateType: "Temperate",
        medianBasket: 75.0,
        trend: "SKINCARE"
    }
};

analyzeCustomer(customerData);
```

### Method 2: Strands Agent-to-Agent (A2A)

If your orchestrator is also a Strands Agent, use the Agent-to-Agent pattern.

```python
from strands import Agent

# Initialize your orchestrator agent
orchestrator = Agent(
    system_prompt="You are an orchestrator that coordinates customer analysis."
)

# Define the customer segment agent as a tool
customer_segment_tool = {
    "name": "analyze_customer_segment",
    "description": "Analyzes customer data and provides segmentation insights including age, churn risk, value, and loyalty tiers.",
    "parameters": {
        "type": "object",
        "properties": {
            "customerData": {
                "type": "object",
                "description": "Customer data including demographics and purchase history",
                "required": ["customerId", "city", "customer", "region"]
            }
        },
        "required": ["customerData"]
    },
    "endpoint": "arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt"
}

# Register the tool
orchestrator.add_tool(customer_segment_tool)

# Use in orchestrator
result = orchestrator("Analyze customer C-1001 from Istanbul")
```

### Method 3: HTTP/REST API (If Exposed)

If you've exposed the agent via API Gateway or similar:

```python
import requests

url = "https://your-api-gateway-url/analyze"
headers = {"Content-Type": "application/json"}

payload = {
    "customerData": {
        "customerId": "C-1001",
        # ... rest of customer data
    }
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

print(f"Analysis: {result['analysis']}")
print(f"Explanation: {result['explanation']}")
```

## 📋 Request Format

### Required Fields

```json
{
  "customerData": {
    "customerId": "string (optional for region mode)",
    "city": "string (required)",
    "customer": {
      "customerId": "string",
      "age": "number (0-120)",
      "gender": "string (F/M/U)",
      "registeredAt": "ISO 8601 datetime",
      "productHistory": [
        {
          "productId": "string",
          "category": "string",
          "totalQuantity": "number (>=0)",
          "totalSpent": "number (>=0)",
          "orderCount": "number (>=0)",
          "lastPurchase": "ISO 8601 datetime",
          "avgDaysBetween": "number or null"
        }
      ]
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

### Field Validation Rules

- `age`: Must be between 0 and 120
- `totalSpent`: Must be >= 0
- `orderCount`: Must be >= 0
- `totalQuantity`: Must be >= 0
- `productHistory`: Can be empty array for new customers
- `customerId`: Optional (omit for region-based analysis)

## 📤 Response Format

```json
{
  "analysis": {
    "mode": "regular|new_customer|region",
    "customerId": "string",
    "city": "string",
    "region": "string",
    "climateType": "string",
    "age": "number",
    "ageSegment": "GenZ|GençYetişkin|Yetişkin|Olgun",
    "gender": "F|M|U",
    "churnSegment": "Aktif|Ilık|Riskli",
    "valueSegment": "HighValue|Standard",
    "loyaltyTier": "Platin|Altın|Gümüş|Bronz",
    "affinityCategory": "string",
    "affinityType": "Odaklı|Keşifçi",
    "diversityProfile": "Kaşif|Dengeli|Sadık",
    "estimatedBudget": "number",
    "avgBasket": "number",
    "avgMonthlySpend": "number",
    "lastPurchaseDaysAgo": "number",
    "orderCount": "number",
    "totalSpent": "number",
    "membershipDays": "number",
    "missingRegulars": [
      {
        "productId": "string",
        "productName": "string",
        "lastBought": "ISO 8601 datetime",
        "avgDaysBetween": "number",
        "daysOverdue": "number"
      }
    ],
    "topProducts": [
      {
        "productId": "string",
        "totalQuantity": "number",
        "totalSpent": "number",
        "lastBought": "ISO 8601 datetime"
      }
    ],
    "message": "string"
  },
  "explanation": "string (AI-generated natural language explanation)",
  "timestamp": "ISO 8601 datetime"
}
```

## 🔄 Usage Patterns

### Pattern 1: Campaign Orchestrator

```python
# Campaign orchestrator calls customer segment agent
def create_personalized_campaign(customer_id):
    # Step 1: Get customer segmentation
    segment_result = call_customer_segment_agent(customer_id)
    
    # Step 2: Use segmentation for campaign logic
    if segment_result['analysis']['churnSegment'] == 'Riskli':
        campaign_type = 'retention'
    elif segment_result['analysis']['valueSegment'] == 'HighValue':
        campaign_type = 'premium'
    else:
        campaign_type = 'standard'
    
    # Step 3: Call campaign agent with segment data
    campaign = call_campaign_agent(
        customer_id=customer_id,
        segment=segment_result['analysis'],
        campaign_type=campaign_type
    )
    
    return campaign
```

### Pattern 2: Multi-Agent Workflow

```python
# Orchestrator coordinates multiple agents
def analyze_and_recommend(customer_id):
    # Agent 1: Customer Segmentation
    segment = customer_segment_agent.analyze(customer_id)
    
    # Agent 2: Product Recommendation (uses segment data)
    recommendations = product_agent.recommend(
        customer_id=customer_id,
        affinity_category=segment['affinityCategory'],
        value_segment=segment['valueSegment']
    )
    
    # Agent 3: Pricing Strategy (uses segment data)
    pricing = pricing_agent.calculate(
        customer_id=customer_id,
        loyalty_tier=segment['loyaltyTier'],
        churn_risk=segment['churnSegment']
    )
    
    return {
        'segment': segment,
        'recommendations': recommendations,
        'pricing': pricing
    }
```

### Pattern 3: Batch Processing

```python
# Process multiple customers in parallel
import concurrent.futures

def analyze_customer_batch(customer_ids):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(call_customer_segment_agent, cid): cid 
            for cid in customer_ids
        }
        
        results = {}
        for future in concurrent.futures.as_completed(futures):
            customer_id = futures[future]
            try:
                results[customer_id] = future.result()
            except Exception as e:
                print(f"Error analyzing {customer_id}: {e}")
        
        return results

# Usage
customer_ids = ["C-1001", "C-1002", "C-1003"]
batch_results = analyze_customer_batch(customer_ids)
```

## ⚡ Performance Considerations

- **Latency:** ~3 seconds (includes AWS cold start)
- **Throughput:** 29,238 customers/second (pure analysis)
- **Concurrent Requests:** Supports parallel invocations
- **Rate Limits:** Follow AWS Bedrock AgentCore limits

### Optimization Tips

1. **Batch Processing:** Group multiple customer analyses
2. **Caching:** Cache results for frequently accessed customers
3. **Async Calls:** Use async/await for non-blocking operations
4. **Connection Pooling:** Reuse AWS SDK clients

## 🔐 Authentication & Authorization

### IAM Policy Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeAgent",
        "bedrock-agent-runtime:InvokeAgent"
      ],
      "Resource": "arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt"
    }
  ]
}
```

### Environment Variables

```bash
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export CUSTOMER_SEGMENT_AGENT_ARN=arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt
```

## 🐛 Error Handling

### Common Errors

```python
def call_customer_segment_agent_safe(customer_data):
    try:
        response = client.invoke_agent(
            agentId='customer_segment_agent-1GD3a24jRt',
            sessionId='unique-session-id',
            inputText=json.dumps({"customerData": customer_data})
        )
        return json.loads(response['completion'])
    
    except client.exceptions.ValidationException as e:
        # Invalid input data (age out of range, negative values, etc.)
        print(f"Validation error: {e}")
        return {"error": "Invalid customer data", "details": str(e)}
    
    except client.exceptions.ThrottlingException as e:
        # Rate limit exceeded
        print(f"Throttling error: {e}")
        time.sleep(1)  # Retry with backoff
        return call_customer_segment_agent_safe(customer_data)
    
    except client.exceptions.ServiceException as e:
        # AWS service error
        print(f"Service error: {e}")
        return {"error": "Service unavailable", "details": str(e)}
    
    except Exception as e:
        # Unexpected error
        print(f"Unexpected error: {e}")
        return {"error": "Unknown error", "details": str(e)}
```

## 📊 Monitoring & Logging

### CloudWatch Logs

```bash
# Tail agent logs
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT \
  --follow \
  --format short

# Filter by customer ID
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT \
  --filter-pattern "C-1001"
```

### X-Ray Tracing

The agent has X-Ray tracing enabled. View traces in the AWS X-Ray console:
https://console.aws.amazon.com/xray/home?region=us-west-2

### GenAI Observability Dashboard

Monitor agent performance and usage:
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core

## 🧪 Testing Integration

### Unit Test Example

```python
import unittest
from unittest.mock import Mock, patch

class TestCustomerSegmentIntegration(unittest.TestCase):
    
    @patch('boto3.client')
    def test_analyze_customer(self, mock_client):
        # Mock response
        mock_response = {
            'completion': json.dumps({
                'analysis': {
                    'customerId': 'C-1001',
                    'ageSegment': 'GençYetişkin',
                    'churnSegment': 'Aktif',
                    'loyaltyTier': 'Gümüş'
                },
                'timestamp': '2026-02-12T00:00:00'
            })
        }
        mock_client.return_value.invoke_agent.return_value = mock_response
        
        # Test
        result = call_customer_segment_agent('C-1001')
        
        # Assert
        self.assertEqual(result['analysis']['ageSegment'], 'GençYetişkin')
        self.assertEqual(result['analysis']['churnSegment'], 'Aktif')
```

## 📞 Support & Contact

- **GitHub:** https://github.com/7Auri/mext-hackathon
- **Documentation:** See README.md for detailed agent documentation
- **Examples:** Check `examples/` folder for request/response samples

## 🔄 Version History

- **v1.0.0** (2026-02-12): Initial production release with logging and validation
