# Implementation Plan: User Segment Agent - Strands Agent Deployment

## Overview

This implementation plan focuses on developing and deploying a customer segmentation agent as a Strands Agent on Amazon Bedrock AgentCore Runtime. The agent will be implemented in Python using the Strands Agents framework with deterministic calculations for customer profiling. The deployment will use the bedrock-agentcore-starter-toolkit for seamless AWS integration.

## Tasks

- [x] 1. Set up AWS credentials and project environment
  - Configure AWS credentials from credits.txt file as default profile
  - Create uv Python virtual environment (.venv) with Python 3.11+
  - Install core dependencies: strands-agents, bedrock-agentcore, bedrock-agentcore-starter-toolkit
  - Install observability dependencies: aws-opentelemetry-distro, boto3
  - Verify AWS credentials work with us-west-2 region
  - _Requirements: 16.1, 16.5, 17.7_

- [ ] 2. Implement core segmentation logic functions
  - [x] 2.1 Implement age segmentation function
    - Create calculate_age_segment(age) function
    - Return GenZ (18-25), GençYetişkin (26-35), Yetişkin (36-50), Olgun (51+)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 2.2 Implement churn segmentation function
    - Create calculate_churn_segment(last_purchase_days_ago) function
    - Return Aktif (<30 days), Ilık (30-60 days), Riskli (>60 days)
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 2.3 Implement value segmentation function
    - Create calculate_value_segment(avg_basket, region_median) function
    - Return HighValue or Standard based on comparison
    - _Requirements: 5.1, 5.2_
  
  - [x] 2.4 Implement loyalty tier function
    - Create calculate_loyalty_tier(membership_months, order_frequency, total_orders) function
    - Return Platin, Altın, Gümüş, or Bronz based on criteria
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 3. Implement customer data analysis function
  - [x] 3.1 Create analyze_customer_data function
    - Accept customer data dictionary as input
    - Detect mode: region, new_customer, or regular
    - _Requirements: 13.1, 14.1_
  
  - [x] 3.2 Implement region mode logic
    - Return region-based profile when no customerId
    - Use region median basket and trend
    - Set default segments
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_
  
  - [x] 3.3 Implement new customer mode logic
    - Return new customer profile when productHistory is empty
    - Set appropriate default segments
    - Calculate membership days
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9_
  
  - [x] 3.4 Implement regular mode analysis
    - Calculate all financial metrics (totalSpent, orderCount, avgBasket, etc.)
    - Calculate all activity metrics (lastPurchaseDaysAgo, membershipDays, etc.)
    - Perform category affinity analysis
    - Calculate diversity profile
    - Identify missing regular products
    - Extract top 5 products by spending
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 9.1-9.6, 10.1-10.3, 11.1-11.4, 12.1-12.3_

- [ ] 4. Implement Strands Agent with BedrockAgentCoreApp
  - [x] 4.1 Create customer_segment_agent.py file
    - Import BedrockAgentCoreApp and Agent from strands
    - Initialize BedrockAgentCoreApp instance
    - Create Strands Agent with system prompt for customer analysis
    - _Requirements: 16.1, 16.2_
  
  - [x] 4.2 Implement entrypoint function
    - Decorate function with @app.entrypoint
    - Accept payload dictionary as input
    - Extract customerData or prompt from payload
    - Call analyze_customer_data if customerData provided
    - Use Strands Agent to generate natural language explanation
    - Return structured response with analysis and explanation
    - Handle errors gracefully
    - _Requirements: 16.3, 2.1-2.8_
  
  - [x] 4.3 Add main execution block
    - Call app.run() when script is executed directly
    - _Requirements: 16.2_

- [x] 5. Create requirements.txt file
  - List strands-agents dependency
  - List bedrock-agentcore dependency
  - List aws-opentelemetry-distro>=0.10.1 dependency
  - List boto3 dependency
  - _Requirements: 16.1, 16.2_

- [x] 6. Test agent locally
  - Start agent locally with: python customer_segment_agent.py
  - Test /invocations endpoint with curl
  - Test with sample customer data payload
  - Test with prompt-only payload
  - Verify responses are correct
  - Stop local agent
  - **COMPLETED:** 90 unit tests passed, 20 diverse customer profiles tested successfully
  - _Requirements: 15.3_

- [x] 7. Configure AgentCore Runtime
  - Run: agentcore configure --entrypoint customer_segment_agent.py
  - Verify IAM role creation
  - Verify ECR repository creation
  - Note the created IAM role ARN
  - Note the created ECR repository URI
  - _Requirements: 17.1, 17.2_

- [x] 8. Deploy to AgentCore Runtime
  - Run: agentcore launch
  - Wait for deployment to complete
  - Note the AgentCore Runtime ARN
  - Verify deployment status
  - _Requirements: 16.4, 16.7, 17.3_

- [x] 9. Test deployed agent
  - Run: agentcore invoke with test payload
  - Test with customer data payload
  - Test with prompt-only payload
  - Verify responses match local testing
  - _Requirements: 17.6_

- [x] 10. Create API documentation
  - Create customer-segment-agent-api.md file
  - Document AgentCore Runtime ARN
  - Document IAM Role ARN
  - Document ECR Repository URI
  - Document deployment region (us-west-2)
  - Include example invocation payloads
  - Include expected response formats
  - Add usage instructions
  - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7_

- [x] 11. Cleanup temporary files
  - Remove any test files created during development
  - Keep only essential files: customer_segment_agent.py, requirements.txt, customer-segment-agent-api.md
  - _Requirements: N/A_

## Notes

- All tasks must be completed in sequence
- Use uv virtual environment (.venv) for all Python operations
- Use AWS credentials from credits.txt (default profile)
- Deploy to us-west-2 region
- Keep code simple - focus on core functionality
- All calculations must be deterministic (no ML)
- Agent name in AgentCore: customer_segment_agent_kiro
- Use bedrock-agentcore-starter-toolkit for deployment
