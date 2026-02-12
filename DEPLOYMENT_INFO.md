# Customer Segment Agent - Deployment Information

## Deployment Status: ✅ SUCCESSFUL

Deployed on: 2026-02-12 10:40:21 UTC

## Agent Details

**Agent Name:** customer_segment_agent

**Agent ARN:**
```
arn:aws:bedrock-agentcore:us-west-2:YOUR_ACCOUNT_ID:runtime/customer_segment_agent-XXXXX
```

**Region:** us-west-2

**Account ID:** YOUR_ACCOUNT_ID

**Endpoint Status:** READY (DEFAULT)

**Network:** Public

**Deployment Type:** Direct Code Deploy

## IAM Configuration

**Execution Role ARN:**
```
arn:aws:iam::YOUR_ACCOUNT_ID:role/AmazonBedrockAgentCoreSDKRuntime-us-west-2-XXXXX
```

**Execution Policy:** BedrockAgentCoreRuntimeExecutionPolicy-customer_segment_agent

## Storage Configuration

**S3 Bucket:**
```
s3://bedrock-agentcore-codebuild-sources-YOUR_ACCOUNT_ID-us-west-2
```

**Deployment Package:**
```
s3://bedrock-agentcore-codebuild-sources-YOUR_ACCOUNT_ID-us-west-2/customer_segment_agent/deployment.zip
```

**Package Size:** 33.25 MB

## Memory Configuration

**Memory Resource ID:** customer_segment_agent_mem-XXXXX

**Memory Type:** STM only (Short-Term Memory)

**Memory Status:** ACTIVE

## Observability

**CloudWatch Logs:**
- Runtime Logs: `/aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT`
- OpenTelemetry Logs: `otel-rt-logs` stream
- Memory Logs: `/aws/vendedlogs/bedrock-agentcore/memory/APPLICATION_LOGS/customer_segment_agent_mem-zs7BzAHo8c`

**GenAI Observability Dashboard:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core
```

**Features Enabled:**
- ✅ CloudWatch Logs
- ✅ X-Ray Tracing
- ✅ OpenTelemetry Instrumentation

**Note:** Observability data may take up to 10 minutes to appear after first launch.

## Invocation

### Using AgentCore CLI

```bash
agentcore invoke '{"prompt": "Hello"}'
```

### Using AWS SDK (Python)

```python
import boto3

client = boto3.client('bedrock-agentcore', region_name='us-west-2')

response = client.invoke_agent(
    agentArn='arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt',
    payload={
        "customerData": {
            "customerId": "CUST123",
            "city": "Istanbul",
            "customer": {
                "customerId": "CUST123",
                "city": "Istanbul",
                "age": 35,
                "gender": "F",
                "registeredAt": "2024-01-15T00:00:00",
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
)
```

## Monitoring Commands

### Check Agent Status
```bash
agentcore status
```

### Tail Runtime Logs
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT \
  --log-stream-name-prefix "2026/02/12/[runtime-logs" \
  --follow
```

### View Recent Logs (Last Hour)
```bash
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT \
  --log-stream-name-prefix "2026/02/12/[runtime-logs" \
  --since 1h
```

## Requirements Validated

✅ **Requirement 16.4:** Agent deployed to Amazon Bedrock AgentCore Runtime
✅ **Requirement 16.7:** Agent named "customer_segment_agent" in AgentCore
✅ **Requirement 17.3:** AgentCore ARN available for invocation

## Next Steps

1. Test the deployed agent with sample customer data (Task 9)
2. Create comprehensive API documentation (Task 10)
3. Monitor observability dashboard for performance metrics
