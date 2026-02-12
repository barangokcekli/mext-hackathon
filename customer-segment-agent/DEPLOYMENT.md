# Customer Segment Agent - Deployment Guide

## Prerequisites

- AWS Account with Bedrock AgentCore access
- Python 3.11+
- AWS CLI configured
- `bedrock-agentcore` toolkit installed

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/7Auri/mext-hackathon.git
cd mext-hackathon/customer-segment-agent
```

### 2. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-west-2
```

### 4. Deploy to AWS

```bash
agentcore deploy
```

## Deployment Configuration

### `.bedrock_agentcore.yaml`

```yaml
default_agent: customer_segment_agent
agents:
  customer_segment_agent:
    name: customer_segment_agent
    language: python
    entrypoint: customer_segment_agent.py
    deployment_type: direct_code_deploy
    runtime_type: PYTHON_3_11
    platform: linux/arm64
    source_path: .
    aws:
      region: us-west-2
      account: '472634336236'
      execution_role_auto_create: true
      s3_auto_create: true
      network_configuration:
        network_mode: PUBLIC
      protocol_configuration:
        server_protocol: HTTP
      observability:
        enabled: true
    memory:
      mode: STM_ONLY
      event_expiry_days: 30
```

## Deployment Steps

### Step 1: Memory Creation

The deployment process automatically creates:
- STM-only memory resource
- Memory ARN: `arn:aws:bedrock-agentcore:us-west-2:472634336236:memory/customer_segment_agent_mem-NVGPGw6zel`
- Wait time: ~2-3 minutes

### Step 2: IAM Role Creation

Automatically creates execution role:
- Role: `AmazonBedrockAgentCoreSDKRuntime-us-west-2-56eb986018`
- Policies: Bedrock AgentCore execution permissions
- Trust relationship: Bedrock AgentCore service

### Step 3: S3 Bucket Creation

Creates deployment bucket:
- Bucket: `bedrock-agentcore-codebuild-sources-472634336236-us-west-2`
- Purpose: Store deployment packages
- Size: ~33MB per deployment

### Step 4: Code Packaging

- Builds dependencies for Linux ARM64
- Packages source code
- Creates deployment.zip
- Uploads to S3

### Step 5: Agent Deployment

- Deploys to Bedrock AgentCore Runtime
- Agent ARN: `arn:aws:bedrock-agentcore:us-west-2:472634336236:runtime/customer_segment_agent-AF1ggg7Wx7`
- Enables observability (CloudWatch + X-Ray)
- Waits for endpoint readiness

## Post-Deployment

### Verify Deployment

```bash
agentcore status
```

### Test Agent

```bash
agentcore invoke '{"customerData": {"customerId": "C-TEST-001", ...}}'
```

### View Logs

```bash
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-AF1ggg7Wx7-DEFAULT --follow
```

## Environment Variables

```bash
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export CUSTOMER_SEGMENT_AGENT_ARN=arn:aws:bedrock-agentcore:us-west-2:472634336236:runtime/customer_segment_agent-AF1ggg7Wx7
```

## Deployment Modes

### 1. Cloud Deployment (Recommended)

```bash
agentcore deploy
```

- Direct code deploy to AWS
- No Docker required
- Production-ready
- Auto-scaling

### 2. Local Development

```bash
agentcore deploy --local
```

- Runs locally for testing
- Docker-based
- Fast iteration
- No AWS costs

## Updating Deployment

### Update Code

```bash
# Make changes to customer_segment_agent.py
agentcore deploy
```

### Update Configuration

```bash
# Edit .bedrock_agentcore.yaml
agentcore deploy
```

## Monitoring

### CloudWatch Logs

```bash
# Tail logs
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-AF1ggg7Wx7-DEFAULT --follow

# Filter by customer ID
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/customer_segment_agent-AF1ggg7Wx7-DEFAULT \
  --filter-pattern "C-1001"
```

### X-Ray Tracing

View traces in AWS X-Ray console:
https://console.aws.amazon.com/xray/home?region=us-west-2

### GenAI Observability Dashboard

https://console.aws.amazon.com/cloudwatch/home?region=us-west-2#gen-ai-observability/agent-core

## Troubleshooting

### Deployment Fails

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check IAM permissions
aws iam get-role --role-name AmazonBedrockAgentCoreSDKRuntime-us-west-2-56eb986018

# Check S3 bucket
aws s3 ls s3://bedrock-agentcore-codebuild-sources-472634336236-us-west-2/
```

### Agent Not Responding

```bash
# Check agent status
agentcore status

# View recent logs
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-AF1ggg7Wx7-DEFAULT --since 1h
```

### Memory Issues

```bash
# Check memory status
aws bedrock-agent get-memory \
  --memory-id customer_segment_agent_mem-NVGPGw6zel \
  --region us-west-2
```

## Cost Optimization

### Estimated Costs

- **Agent Runtime**: $0.00025 per request
- **CloudWatch Logs**: $0.50 per GB ingested
- **X-Ray Tracing**: $5.00 per million traces
- **S3 Storage**: $0.023 per GB/month

### Cost Reduction Tips

1. **Reduce Logging**: Adjust log level to WARNING
2. **Batch Requests**: Process multiple customers per request
3. **Cache Results**: Implement caching layer
4. **Optimize Memory**: Use appropriate memory size

## Security Best Practices

### IAM Policies

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
      "Resource": "arn:aws:bedrock-agentcore:us-west-2:472634336236:runtime/customer_segment_agent-AF1ggg7Wx7"
    }
  ]
}
```

### Network Security

- Use VPC endpoints for private access
- Enable AWS WAF for API Gateway
- Implement rate limiting
- Use API keys or OAuth

### Data Security

- Encrypt data in transit (TLS)
- No PII storage
- Audit logging enabled
- Compliance-ready

## Rollback

### Revert to Previous Version

```bash
# List previous deployments
aws s3 ls s3://bedrock-agentcore-codebuild-sources-472634336236-us-west-2/customer_segment_agent/

# Deploy specific version
# (Manual process - copy old deployment.zip and redeploy)
```

## Multi-Region Deployment

### Deploy to Multiple Regions

```bash
# Deploy to us-east-1
export AWS_REGION=us-east-1
agentcore deploy

# Deploy to eu-west-1
export AWS_REGION=eu-west-1
agentcore deploy
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Deploy Customer Segment Agent

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Deploy to AWS
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: agentcore deploy
```

## Support

For deployment issues:
- Check AWS Bedrock AgentCore documentation
- Review CloudWatch logs
- Contact AWS Support
- GitHub Issues: https://github.com/7Auri/mext-hackathon/issues
