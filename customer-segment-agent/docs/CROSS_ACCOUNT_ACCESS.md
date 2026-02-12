# Cross-Account Access Setup

This guide explains how to allow other AWS accounts to use your Customer Segment Agent.

## Option 1: IAM Cross-Account Access (Recommended)

### Step 1: Create IAM Policy in Your Account

Create a policy that allows access to your agent:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAgentInvocation",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::EXTERNAL_ACCOUNT_ID:root",
          "arn:aws:iam::EXTERNAL_ACCOUNT_ID:role/RoleName"
        ]
      },
      "Action": [
        "bedrock:InvokeAgent",
        "bedrock-agent-runtime:InvokeAgent"
      ],
      "Resource": "arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt"
    }
  ]
}
```

### Step 2: Apply Policy to Agent

```bash
# Create policy file
cat > agent-access-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCrossAccountAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::EXTERNAL_ACCOUNT_ID:root"
      },
      "Action": [
        "bedrock:InvokeAgent",
        "bedrock-agent-runtime:InvokeAgent"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Apply policy (requires AWS CLI)
aws bedrock-agent put-resource-policy \
  --resource-arn arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt \
  --policy file://agent-access-policy.json \
  --region us-west-2
```

### Step 3: External Account Setup

The external account needs to create a role with permissions:

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

### Step 4: External Account Usage

```python
import boto3

# Assume role in external account
sts = boto3.client('sts')
assumed_role = sts.assume_role(
    RoleArn='arn:aws:iam::EXTERNAL_ACCOUNT_ID:role/AgentAccessRole',
    RoleSessionName='CustomerSegmentSession'
)

# Use temporary credentials
client = boto3.client(
    'bedrock-agent-runtime',
    region_name='us-west-2',
    aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
    aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
    aws_session_token=assumed_role['Credentials']['SessionToken']
)

# Call agent
response = client.invoke_agent(
    agentId='customer_segment_agent-1GD3a24jRt',
    sessionId='unique-session-id',
    inputText='...'
)
```

## Option 2: API Gateway + Lambda (Public Access)

For public or HTTP-based access, expose the agent via API Gateway.

### Step 1: Create Lambda Function

```python
import boto3
import json

client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

def lambda_handler(event, context):
    """Lambda function to invoke Customer Segment Agent"""
    try:
        # Parse request
        body = json.loads(event['body'])
        customer_data = body.get('customerData')
        
        # Invoke agent
        response = client.invoke_agent(
            agentId='customer_segment_agent-1GD3a24jRt',
            agentAliasId='TSTALIASID',
            sessionId=f"session-{context.request_id}",
            inputText=json.dumps({"customerData": customer_data})
        )
        
        # Return response
        result = json.loads(response['completion'])
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Step 2: Create API Gateway

```bash
# Create REST API
aws apigateway create-rest-api \
  --name "CustomerSegmentAPI" \
  --description "API for Customer Segment Agent" \
  --region us-west-2

# Create resource and method
# ... (API Gateway setup steps)
```

### Step 3: Usage

```bash
# Call via HTTP
curl -X POST https://your-api-id.execute-api.us-west-2.amazonaws.com/prod/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "customerData": {
      "customerId": "C-1001",
      ...
    }
  }'
```

## Option 3: Share Code (Deploy Their Own)

The simplest option: Share the code and let them deploy their own instance.

### Step 1: Clone Repository

```bash
git clone https://github.com/7Auri/mext-hackathon.git
cd mext-hackathon
```

### Step 2: Configure AWS

```bash
# Configure their AWS credentials
aws configure

# Update .bedrock_agentcore.yaml with their account
```

### Step 3: Deploy

```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Deploy to their account
agentcore deploy
```

Now they have their own instance in their AWS account!

## Security Considerations

### For Cross-Account Access:
- ✅ Use IAM roles, not access keys
- ✅ Apply least privilege principle
- ✅ Enable CloudTrail logging
- ✅ Set up billing alerts
- ✅ Use resource-based policies
- ✅ Implement rate limiting

### For API Gateway:
- ✅ Use API keys or OAuth
- ✅ Enable throttling
- ✅ Set up WAF rules
- ✅ Monitor usage with CloudWatch
- ✅ Implement CORS properly
- ✅ Use custom domain with SSL

### For Code Sharing:
- ✅ Remove sensitive data (credentials, keys)
- ✅ Document deployment steps
- ✅ Provide example configurations
- ✅ Include security best practices

## Cost Considerations

When sharing access:
- **Cross-Account:** You pay for all invocations
- **API Gateway:** You pay for API Gateway + Lambda + Agent
- **Code Sharing:** Each account pays for their own usage

## Monitoring Shared Access

```bash
# View CloudWatch logs
aws logs tail /aws/bedrock-agentcore/runtimes/customer_segment_agent-1GD3a24jRt-DEFAULT \
  --follow \
  --filter-pattern "EXTERNAL_ACCOUNT_ID"

# View X-Ray traces
aws xray get-trace-summaries \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --region us-west-2
```

## Revoking Access

### Remove Cross-Account Access:
```bash
aws bedrock-agent delete-resource-policy \
  --resource-arn arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt \
  --region us-west-2
```

### Disable API Gateway:
```bash
aws apigateway delete-rest-api \
  --rest-api-id YOUR_API_ID \
  --region us-west-2
```

## Support

For questions about cross-account access:
- Check AWS Bedrock AgentCore documentation
- Review IAM best practices
- Contact AWS Support for complex scenarios
