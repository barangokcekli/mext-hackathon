# Customer Segment Agent - API Documentation

## Overview

The Customer Segment Agent is a customer data analysis system deployed on Amazon Bedrock AgentCore Runtime. It performs customer segmentation and profiling by analyzing purchase history, demographics, and behavioral patterns to generate comprehensive customer insights.

**Version:** 1.0  
**Last Updated:** 2026-02-12  
**Status:** Production Ready ✅

---

## Deployment Information

### Agent Details

**Agent ARN:**
```
arn:aws:bedrock-agentcore:us-west-2:YOUR_ACCOUNT_ID:runtime/customer_segment_agent-XXXXX
```

**Region:** `us-west-2`

**Account ID:** `YOUR_ACCOUNT_ID`

**Agent Name:** `customer_segment_agent`

### IAM Configuration

**Execution Role ARN:**
```
arn:aws:iam::YOUR_ACCOUNT_ID:role/AmazonBedrockAgentCoreSDKRuntime-us-west-2-XXXXX
```

**Execution Policy:** `BedrockAgentCoreRuntimeExecutionPolicy-customer_segment_agent`

### Storage Configuration

**ECR Repository URI:**
```
YOUR_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/bedrock-agentcore-customer_segment_agent
```

**S3 Bucket:**
```
s3://bedrock-agentcore-codebuild-sources-YOUR_ACCOUNT_ID-us-west-2
```

---

## API Endpoints

The agent is invoked through the AgentCore Runtime using the agent ARN. There are no direct HTTP endpoints - all invocations go through AWS SDK or AgentCore CLI.

---

## Authentication

All API calls require valid AWS credentials with permissions to invoke the AgentCore Runtime. The execution role must have the following permissions:

- `bedrock-agentcore:InvokeAgent`
- Access to CloudWatch Logs for observability
- Access to X-Ray for tracing (optional)

---

## Request Format

### Payload Structure

The agent accepts JSON payloads with two possible formats:

#### 1. Customer Data Payload (Structured Analysis)

Used for analyzing specific customer data and generating segmentation insights.

```json
{
  "customerData": {
    "customerId": "string (optional)",
    "city": "string (required)",
    "customer": {
      "customerId": "string (required)",
      "city": "string (required)",
      "age": "number (required)",
      "gender": "string (required)",
      "registeredAt": "ISO 8601 date string (required)",
      "productHistory": [
        {
          "productId": "string (required)",
          "category": "string (required)",
          "totalQuantity": "number (required)",
          "totalSpent": "number (required)",
          "orderCount": "number (required)",
          "lastPurchase": "ISO 8601 date string (required)",
          "avgDaysBetween": "number or null (required)"
        }
      ]
    },
    "region": {
      "name": "string (required)",
      "climateType": "string (required)",
      "medianBasket": "number (required)",
      "trend": "string (required)"
    },
    "currentSeason": "string (required)"
  }
}
```

#### 2. Prompt Payload (Conversational)

Used for asking general questions about customer segmentation.

```json
{
  "prompt": "string (required)"
}
```

---

## Response Format

### Customer Data Response

When a customer data payload is provided, the response includes both structured analysis and natural language explanation:

```json
{
  "analysis": {
    "customerId": "string (optional)",
    "city": "string",
    "region": "string",
    "climateType": "string",
    "age": "number (optional)",
    "ageSegment": "string",
    "gender": "string (optional)",
    "churnSegment": "string",
    "valueSegment": "string",
    "loyaltyTier": "string",
    "affinityCategory": "string",
    "affinityType": "string",
    "diversityProfile": "string",
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
        "lastBought": "ISO 8601 date string",
        "avgDaysBetween": "number",
        "daysOverdue": "number"
      }
    ],
    "topProducts": [
      {
        "productId": "string",
        "totalQuantity": "number",
        "totalSpent": "number",
        "lastBought": "ISO 8601 date string"
      }
    ]
  },
  "explanation": "string (natural language summary)"
}
```

### Prompt Response

When a prompt payload is provided, the response contains a natural language answer:

```json
{
  "response": "string (natural language answer)"
}
```

---

## Field Descriptions

### Segmentation Fields

| Field | Type | Description | Possible Values |
|-------|------|-------------|-----------------|
| `ageSegment` | string | Age-based customer segment | GenZ (18-25), GençYetişkin (26-35), Yetişkin (36-50), Olgun (51+) |
| `churnSegment` | string | Churn risk classification | Aktif (<30 days), Ilık (30-60 days), Riskli (>60 days) |
| `valueSegment` | string | Spending level classification | HighValue, Standard |
| `loyaltyTier` | string | Loyalty program tier | Platin, Altın, Gümüş, Bronz |
| `affinityType` | string | Category focus classification | Odaklı (>60% in one category), Keşifçi (≤60%) |
| `diversityProfile` | string | Product variety preference | Kaşif (>0.7), Dengeli (0.4-0.7), Sadık (≤0.4) |

### Financial Metrics

| Field | Type | Description |
|-------|------|-------------|
| `totalSpent` | number | Total amount spent across all purchases |
| `orderCount` | number | Total number of orders placed |
| `avgBasket` | number | Average order value (totalSpent / orderCount) |
| `estimatedBudget` | number | Estimated budget (avgBasket × 1.2) |
| `avgMonthlySpend` | number | Average spending per month |

### Activity Metrics

| Field | Type | Description |
|-------|------|-------------|
| `lastPurchaseDaysAgo` | number | Days since last purchase |
| `membershipDays` | number | Days since registration |
| `orderCount` | number | Total number of orders |

### Product Insights

| Field | Type | Description |
|-------|------|-------------|
| `affinityCategory` | string | Category with highest spending |
| `missingRegulars` | array | Regular products overdue for repurchase |
| `topProducts` | array | Top 5 products by spending |

---

## Usage Examples

### Example 1: New Customer Analysis

**Request:**
```json
{
  "customerData": {
    "customerId": "C-NEW-001",
    "city": "Istanbul",
    "customer": {
      "customerId": "C-NEW-001",
      "city": "Istanbul",
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
```

**Response:**
```json
{
  "analysis": {
    "customerId": "C-NEW-001",
    "city": "Istanbul",
    "region": "Marmara",
    "climateType": "Temperate",
    "age": 28,
    "ageSegment": "GençYetişkin",
    "gender": "F",
    "churnSegment": "Riskli",
    "valueSegment": "Standard",
    "loyaltyTier": "Bronz",
    "affinityCategory": "Skincare",
    "affinityType": "Keşifçi",
    "diversityProfile": "Kaşif",
    "estimatedBudget": 300.0,
    "avgBasket": 250.0,
    "avgMonthlySpend": 0,
    "lastPurchaseDaysAgo": 999,
    "orderCount": 0,
    "totalSpent": 0,
    "membershipDays": 28,
    "missingRegulars": [],
    "topProducts": []
  },
  "explanation": "This is a new customer in the GençYetişkin age segment with no purchase history yet..."
}
```

### Example 2: Active Customer with Purchase History

**Request:**
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
        },
        {
          "productId": "P-2004",
          "category": "SKINCARE",
          "totalQuantity": 7,
          "totalSpent": 454.30,
          "orderCount": 5,
          "lastPurchase": "2026-02-01T00:00:00",
          "avgDaysBetween": 45
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
}
```

**Response:**
```json
{
  "analysis": {
    "customerId": "C-1001",
    "city": "Istanbul",
    "region": "Marmara",
    "climateType": "Temperate",
    "age": 32,
    "ageSegment": "GençYetişkin",
    "gender": "F",
    "churnSegment": "Ilık",
    "valueSegment": "HighValue",
    "loyaltyTier": "Altın",
    "affinityCategory": "SKINCARE",
    "affinityType": "Odaklı",
    "diversityProfile": "Sadık",
    "estimatedBudget": 86.28,
    "avgBasket": 71.90,
    "avgMonthlySpend": 42.47,
    "lastPurchaseDaysAgo": 11,
    "orderCount": 13,
    "totalSpent": 933.50,
    "membershipDays": 699,
    "missingRegulars": [
      {
        "productId": "P-2001",
        "productName": "P-2001",
        "lastBought": "2026-01-20T00:00:00",
        "avgDaysBetween": 30,
        "daysOverdue": -13
      }
    ],
    "topProducts": [
      {
        "productId": "P-2001",
        "totalQuantity": 8,
        "totalSpent": 479.20,
        "lastBought": "2026-01-20T00:00:00"
      },
      {
        "productId": "P-2004",
        "totalQuantity": 7,
        "totalSpent": 454.30,
        "lastBought": "2026-02-01T00:00:00"
      }
    ]
  },
  "explanation": "This customer is a high-value, loyal customer in the Altın tier..."
}
```

### Example 3: Region Mode (No Customer ID)

**Request:**
```json
{
  "customerData": {
    "city": "Ankara",
    "region": {
      "name": "Central Anatolia",
      "climateType": "Continental",
      "medianBasket": 200.0,
      "trend": "Makeup"
    },
    "currentSeason": "Winter"
  }
}
```

**Response:**
```json
{
  "analysis": {
    "city": "Ankara",
    "region": "Central Anatolia",
    "climateType": "Continental",
    "ageSegment": "Yetişkin",
    "churnSegment": "Aktif",
    "valueSegment": "Standard",
    "loyaltyTier": "Gümüş",
    "affinityCategory": "Makeup",
    "affinityType": "Keşifçi",
    "diversityProfile": "Dengeli",
    "estimatedBudget": 240.0,
    "avgBasket": 200.0,
    "avgMonthlySpend": 400.0,
    "lastPurchaseDaysAgo": 30,
    "orderCount": 0,
    "totalSpent": 0,
    "membershipDays": 0,
    "missingRegulars": [],
    "topProducts": []
  },
  "explanation": "This is a region-based profile for Central Anatolia..."
}
```

### Example 4: Prompt-Only Request

**Request:**
```json
{
  "prompt": "What is customer segmentation and how does it help businesses?"
}
```

**Response:**
```json
{
  "response": "Customer segmentation is the process of dividing customers into groups based on shared characteristics such as demographics, behavior, and purchasing patterns. It helps businesses by enabling targeted marketing, personalized recommendations, improved customer retention, and better resource allocation..."
}
```

---

## Invocation Methods

### Method 1: AgentCore CLI

```bash
# Basic invocation
agentcore invoke '{"customerData": {...}}'

# With output to file
agentcore invoke '{"customerData": {...}}' > response.json

# Using a payload file
agentcore invoke "$(cat payload.json)"
```

### Method 2: AWS SDK (Python)

```python
import boto3
import json

# Initialize client
client = boto3.client('bedrock-agentcore', region_name='us-west-2')

# Prepare payload
payload = {
    "customerData": {
        "customerId": "C-1001",
        "city": "Istanbul",
        "customer": {
            "customerId": "C-1001",
            "city": "Istanbul",
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
}

# Invoke agent
response = client.invoke_agent(
    agentArn='arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt',
    payload=payload
)

# Parse response
result = json.loads(response['body'].read())
print(json.dumps(result, indent=2))
```

### Method 3: AWS SDK (JavaScript/TypeScript)

```javascript
import { BedrockAgentCoreClient, InvokeAgentCommand } from "@aws-sdk/client-bedrock-agentcore";

// Initialize client
const client = new BedrockAgentCoreClient({ region: "us-west-2" });

// Prepare payload
const payload = {
  customerData: {
    customerId: "C-1001",
    city: "Istanbul",
    customer: {
      customerId: "C-1001",
      city: "Istanbul",
      age: 32,
      gender: "F",
      registeredAt: "2024-03-15T00:00:00",
      productHistory: []
    },
    region: {
      name: "Marmara",
      climateType: "Temperate",
      medianBasket: 250.0,
      trend: "Skincare"
    },
    currentSeason: "Winter"
  }
};

// Invoke agent
const command = new InvokeAgentCommand({
  agentArn: "arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt",
  payload: payload
});

const response = await client.send(command);
console.log(JSON.stringify(response, null, 2));
```

---

## Operational Modes

The agent operates in three distinct modes based on the input:

### 1. Regular Mode
- **Trigger:** Customer ID provided AND purchase history is not empty
- **Behavior:** Full customer analysis with all metrics and segmentation
- **Use Case:** Analyzing existing customers with transaction history

### 2. New Customer Mode
- **Trigger:** Customer ID provided BUT purchase history is empty
- **Behavior:** Profile with default segments and region-based estimates
- **Use Case:** Onboarding new customers or customers with no purchases yet

### 3. Region Mode
- **Trigger:** No customer ID provided
- **Behavior:** Generic profile based on regional market data
- **Use Case:** Getting market insights or default profiles for a region

---

## Error Handling

### Common Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `ValidationError` | Missing required fields in payload | Check payload structure against schema |
| `InvalidDateFormat` | Date string not in ISO 8601 format | Use format: `YYYY-MM-DDTHH:mm:ss` |
| `NegativeValue` | Numeric field has negative value | Ensure all numeric values are non-negative |
| `AccessDenied` | Insufficient IAM permissions | Verify IAM role has `bedrock-agentcore:InvokeAgent` permission |
| `ThrottlingException` | Too many requests | Implement exponential backoff retry logic |

### Error Response Format

```json
{
  "error": "ValidationError",
  "message": "Missing required field: customer.age",
  "field": "customer.age"
}
```

---

## Monitoring and Observability

### CloudWatch Logs

**Runtime Logs:**
```
/aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT
```

**Memory Logs:**
```
/aws/vendedlogs/bedrock-agentcore/memory/APPLICATION_LOGS/customer_segment_agent_mem-zs7BzAHo8c
```

### Viewing Logs

```bash
# Tail runtime logs
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT \
  --follow

# View recent logs (last hour)
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT \
  --since 1h

# Filter logs by pattern
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT \
  --filter-pattern "ERROR"
```

### GenAI Observability Dashboard

Access the CloudWatch GenAI Observability Dashboard:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core
```

### X-Ray Tracing

X-Ray tracing is enabled for the agent. View traces in the AWS X-Ray console to analyze request flow and performance.

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Average Response Time | < 2 seconds |
| Cold Start Time | < 5 seconds |
| Maximum Payload Size | 256 KB |
| Timeout | 60 seconds |
| Concurrent Invocations | Auto-scaling (no fixed limit) |

---

## Best Practices

### 1. Input Validation
- Always validate input data before sending to the agent
- Ensure dates are in ISO 8601 format
- Verify numeric values are non-negative

### 2. Error Handling
- Implement retry logic with exponential backoff
- Log all errors for debugging
- Handle timeout scenarios gracefully

### 3. Performance Optimization
- Cache region data to avoid redundant lookups
- Batch multiple customer analyses when possible
- Use appropriate timeout values based on payload size

### 4. Security
- Never include sensitive data in logs
- Use IAM roles with least privilege principle
- Rotate AWS credentials regularly
- Enable CloudTrail for audit logging

### 5. Monitoring
- Set up CloudWatch alarms for error rates
- Monitor response times and set alerts for degradation
- Track invocation counts for capacity planning

---

## Rate Limits and Quotas

| Resource | Limit | Notes |
|----------|-------|-------|
| Invocations per second | 100 | Soft limit, can be increased |
| Payload size | 256 KB | Hard limit |
| Response size | 256 KB | Hard limit |
| Concurrent executions | 1000 | Soft limit, can be increased |

To request limit increases, contact AWS Support.

---

## Versioning

**Current Version:** 1.0  
**API Stability:** Stable  
**Breaking Changes:** None planned

Future versions will maintain backward compatibility. Any breaking changes will be announced with a new major version.

---

## Support and Contact

For issues or questions:

1. **Technical Issues:** Check CloudWatch Logs for error details
2. **AWS Support:** Open a support ticket in AWS Console
3. **Documentation:** Refer to this API documentation
4. **Deployment Issues:** Review DEPLOYMENT_INFO.md

---

## Changelog

### Version 1.0 (2026-02-12)
- Initial production release
- Deployed to us-west-2 region
- Support for three operational modes (Regular, New Customer, Region)
- Comprehensive segmentation analysis
- CloudWatch and X-Ray observability enabled

---

## Appendix

### A. Segmentation Logic Reference

#### Age Segments
- **GenZ:** 18-25 years
- **GençYetişkin:** 26-35 years
- **Yetişkin:** 36-50 years
- **Olgun:** 51+ years

#### Churn Segments
- **Aktif:** Last purchase < 30 days ago
- **Ilık:** Last purchase 30-60 days ago
- **Riskli:** Last purchase > 60 days ago

#### Value Segments
- **HighValue:** avgBasket > region median
- **Standard:** avgBasket ≤ region median

#### Loyalty Tiers
- **Platin:** 12+ months membership AND 2+ orders/month
- **Altın:** 6+ months membership AND 1+ orders/month
- **Gümüş:** 3+ total orders
- **Bronz:** < 3 total orders

#### Affinity Types
- **Odaklı:** > 60% of orders in one category
- **Keşifçi:** ≤ 60% of orders in one category

#### Diversity Profiles
- **Kaşif:** Diversity ratio > 0.7
- **Dengeli:** Diversity ratio 0.4-0.7
- **Sadık:** Diversity ratio ≤ 0.4

### B. Calculation Formulas

```
avgBasket = totalSpent / orderCount
estimatedBudget = avgBasket × 1.2
avgMonthlySpend = totalSpent / membershipMonths
diversityRatio = uniqueProducts / totalOrders
affinityRatio = ordersInAffinityCategory / totalOrders
orderFrequency = totalOrders / membershipMonths
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-12  
**Maintained By:** Customer Segment Agent Team
