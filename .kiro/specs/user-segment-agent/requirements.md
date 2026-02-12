# Requirements Document

## Introduction

The User Segment Agent is a customer data analysis system that performs customer segmentation and profiling, deployed as a Strands Agent on Amazon Bedrock AgentCore Runtime. The agent analyzes customer purchase history, demographics, and behavioral patterns to generate comprehensive customer insights. It does NOT perform stock analysis or campaign decision-making - its sole responsibility is customer profiling and segmentation.

The agent will be implemented using the Strands Agents framework and deployed to AWS AgentCore Runtime in the us-east-1 region, providing a scalable, serverless solution for customer analysis.

## Glossary

- **System**: The User Segment Agent
- **Customer**: An individual with a customer record in the system
- **Region**: A geographic area with associated climate and market characteristics
- **Product_History**: A collection of product purchase records for a customer
- **Segment**: A classification category for customer characteristics or behavior
- **Churn_Segment**: Classification based on recency of last purchase (Aktif, Ilık, Riskli)
- **Value_Segment**: Classification based on spending level (HighValue, Standard)
- **Loyalty_Tier**: Classification based on membership duration and order frequency (Platin, Altın, Gümüş, Bronz)
- **Affinity_Category**: The product category a customer purchases most frequently
- **Affinity_Type**: Classification of category focus (Odaklı, Keşifçi)
- **Diversity_Profile**: Classification of product variety preference (Kaşif, Dengeli, Sadık)
- **Regular_Product**: A product purchased repeatedly with predictable intervals
- **Missing_Regular**: A regular product that is overdue for repurchase

## Requirements

### Requirement 1: Input Processing

**User Story:** As a system integrator, I want the agent to accept structured input data, so that I can provide customer and regional context for analysis.

#### Acceptance Criteria

1. WHEN input is provided, THE System SHALL accept a city parameter as a string
2. WHEN input is provided, THE System SHALL accept an optional customerId parameter
3. WHEN input is provided, THE System SHALL accept a customer object containing customer data
4. WHEN input is provided, THE System SHALL accept a region object containing regional market data
5. WHEN input is provided, THE System SHALL accept a currentSeason parameter

### Requirement 2: Output Generation

**User Story:** As a system integrator, I want the agent to output comprehensive customer insights in JSON format, so that I can use the segmentation data in downstream systems.

#### Acceptance Criteria

1. THE System SHALL output a CustomerInsightJSON object containing all required fields
2. WHEN generating output, THE System SHALL include basic information fields (customerId, city, region, climateType)
3. WHEN generating output, THE System SHALL include demographic fields (age, ageSegment, gender)
4. WHEN generating output, THE System SHALL include behavioral segment fields (churnSegment, valueSegment, loyaltyTier)
5. WHEN generating output, THE System SHALL include purchase pattern fields (affinityCategory, affinityType, diversityProfile)
6. WHEN generating output, THE System SHALL include financial metric fields (estimatedBudget, avgBasket, avgMonthlySpend, totalSpent)
7. WHEN generating output, THE System SHALL include activity metric fields (lastPurchaseDaysAgo, orderCount, membershipDays)
8. WHEN generating output, THE System SHALL include product insight fields (missingRegulars, topProducts)

### Requirement 3: Age Segmentation

**User Story:** As a marketing analyst, I want customers classified by age segment, so that I can understand generational preferences.

#### Acceptance Criteria

1. WHEN a customer age is 18-25, THE System SHALL assign ageSegment as "GenZ"
2. WHEN a customer age is 26-35, THE System SHALL assign ageSegment as "GençYetişkin"
3. WHEN a customer age is 36-50, THE System SHALL assign ageSegment as "Yetişkin"
4. WHEN a customer age is 51 or above, THE System SHALL assign ageSegment as "Olgun"

### Requirement 4: Churn Segmentation

**User Story:** As a retention manager, I want customers classified by churn risk, so that I can identify customers who need re-engagement.

#### Acceptance Criteria

1. WHEN last purchase was less than 30 days ago, THE System SHALL assign churnSegment as "Aktif"
2. WHEN last purchase was 30-60 days ago, THE System SHALL assign churnSegment as "Ilık"
3. WHEN last purchase was more than 60 days ago, THE System SHALL assign churnSegment as "Riskli"

### Requirement 5: Value Segmentation

**User Story:** As a business analyst, I want customers classified by spending level, so that I can identify high-value customers.

#### Acceptance Criteria

1. WHEN average basket size exceeds the region median basket, THE System SHALL assign valueSegment as "HighValue"
2. WHEN average basket size is at or below the region median basket, THE System SHALL assign valueSegment as "Standard"

### Requirement 6: Loyalty Tier Classification

**User Story:** As a loyalty program manager, I want customers classified into loyalty tiers, so that I can provide appropriate rewards and recognition.

#### Acceptance Criteria

1. WHEN a customer has been a member for 12 or more months AND orders at least 2 times per month, THE System SHALL assign loyaltyTier as "Platin"
2. WHEN a customer has been a member for 6 or more months AND orders at least 1 time per month, THE System SHALL assign loyaltyTier as "Altın"
3. WHEN a customer has placed 3 or more orders, THE System SHALL assign loyaltyTier as "Gümüş"
4. WHEN a customer does not meet the criteria for Platin, Altın, or Gümüş, THE System SHALL assign loyaltyTier as "Bronz"

### Requirement 7: Category Affinity Analysis

**User Story:** As a product manager, I want to understand customer category preferences, so that I can recommend relevant products.

#### Acceptance Criteria

1. WHEN analyzing purchase history, THE System SHALL identify the category with the highest total spending as the affinityCategory
2. WHEN analyzing purchase history, THE System SHALL calculate the affinity ratio as the proportion of orders in the affinity category
3. WHEN affinity ratio exceeds 0.6, THE System SHALL assign affinityType as "Odaklı"
4. WHEN affinity ratio is 0.6 or below, THE System SHALL assign affinityType as "Keşifçi"

### Requirement 8: Diversity Profile Classification

**User Story:** As a merchandising manager, I want to understand customer product variety preferences, so that I can tailor product recommendations.

#### Acceptance Criteria

1. WHEN analyzing purchase history, THE System SHALL calculate diversity ratio as unique products divided by total orders
2. WHEN diversity ratio exceeds 0.7, THE System SHALL assign diversityProfile as "Kaşif"
3. WHEN diversity ratio is between 0.4 and 0.7 inclusive, THE System SHALL assign diversityProfile as "Dengeli"
4. WHEN diversity ratio is 0.4 or below, THE System SHALL assign diversityProfile as "Sadık"

### Requirement 9: Financial Metrics Calculation

**User Story:** As a financial analyst, I want accurate financial metrics calculated from purchase history, so that I can understand customer spending patterns.

#### Acceptance Criteria

1. WHEN calculating metrics, THE System SHALL compute total spent as the sum of all product totalSpent values
2. WHEN calculating metrics, THE System SHALL compute order count as the sum of all product orderCount values
3. WHEN calculating metrics, THE System SHALL compute average basket as total spent divided by order count
4. WHEN calculating metrics, THE System SHALL compute estimated budget as average basket multiplied by 1.2
5. WHEN calculating metrics, THE System SHALL compute membership days as days since registration date
6. WHEN calculating metrics, THE System SHALL compute average monthly spend as total spent divided by membership months

### Requirement 10: Activity Metrics Calculation

**User Story:** As a customer success manager, I want to track customer activity metrics, so that I can monitor engagement levels.

#### Acceptance Criteria

1. WHEN calculating activity metrics, THE System SHALL compute last purchase days ago as days since the most recent purchase date
2. WHEN calculating activity metrics, THE System SHALL compute order count from purchase history
3. WHEN calculating activity metrics, THE System SHALL compute membership days from registration date

### Requirement 11: Missing Regular Products Identification

**User Story:** As a replenishment manager, I want to identify products that customers are overdue to repurchase, so that I can send timely reminders.

#### Acceptance Criteria

1. WHEN analyzing purchase history, THE System SHALL identify regular products as those with avgDaysBetween not null and 60 days or less
2. WHEN a regular product's days since last purchase exceeds avgDaysBetween multiplied by 1.2, THE System SHALL classify it as a missing regular
3. WHEN identifying missing regulars, THE System SHALL include productId, productName, lastBought date, avgDaysBetween, and daysOverdue
4. WHEN calculating daysOverdue, THE System SHALL compute it as days since last purchase minus avgDaysBetween

### Requirement 12: Top Products Identification

**User Story:** As a sales analyst, I want to identify each customer's top purchased products, so that I can understand their preferences.

#### Acceptance Criteria

1. WHEN identifying top products, THE System SHALL sort products by total spent in descending order
2. WHEN identifying top products, THE System SHALL return the top 5 products
3. WHEN returning top products, THE System SHALL include productId, totalQuantity, totalSpent, and lastBought date

### Requirement 13: Region Mode Operation

**User Story:** As a system integrator, I want the agent to provide region-based profiles when no customer ID is provided, so that I can get general market insights.

#### Acceptance Criteria

1. WHEN customerId is not provided, THE System SHALL return a region-based profile
2. WHEN in region mode, THE System SHALL use region median basket for avgBasket
3. WHEN in region mode, THE System SHALL use region trend for affinityCategory
4. WHEN in region mode, THE System SHALL set default segment values (ageSegment: "Yetişkin", churnSegment: "Aktif", valueSegment: "Standard", loyaltyTier: "Gümüş", affinityType: "Keşifçi", diversityProfile: "Dengeli")
5. WHEN in region mode, THE System SHALL set activity metrics to zero or default values (orderCount: 0, totalSpent: 0, membershipDays: 0, lastPurchaseDaysAgo: 30)
6. WHEN in region mode, THE System SHALL return empty arrays for missingRegulars and topProducts

### Requirement 14: New Customer Mode Operation

**User Story:** As a customer onboarding specialist, I want appropriate profiles for customers with no purchase history, so that I can provide relevant initial recommendations.

#### Acceptance Criteria

1. WHEN a customer has an empty productHistory array, THE System SHALL return a new customer profile
2. WHEN in new customer mode, THE System SHALL assign churnSegment as "Riskli"
3. WHEN in new customer mode, THE System SHALL assign valueSegment as "Standard"
4. WHEN in new customer mode, THE System SHALL assign loyaltyTier as "Bronz"
5. WHEN in new customer mode, THE System SHALL assign diversityProfile as "Kaşif"
6. WHEN in new customer mode, THE System SHALL use region trend for affinityCategory and "Keşifçi" for affinityType
7. WHEN in new customer mode, THE System SHALL set lastPurchaseDaysAgo to 999
8. WHEN in new customer mode, THE System SHALL set financial metrics to zero or region-based defaults
9. WHEN in new customer mode, THE System SHALL return empty arrays for missingRegulars and topProducts

### Requirement 15: Deterministic Calculation

**User Story:** As a system architect, I want all calculations to be deterministic and rule-based, so that results are reproducible and explainable.

#### Acceptance Criteria

1. THE System SHALL use only deterministic algorithms for all calculations
2. THE System SHALL NOT use machine learning or probabilistic methods
3. WHEN given identical input data, THE System SHALL produce identical output results

### Requirement 16: Strands Agent Deployment

**User Story:** As a DevOps engineer, I want the agent deployed as a Strands Agent on AgentCore Runtime, so that it can scale automatically and integrate with AWS services.

#### Acceptance Criteria

1. THE System SHALL be implemented using the Strands Agents framework
2. THE System SHALL use the BedrockAgentCoreApp wrapper for HTTP service deployment
3. THE System SHALL expose an entrypoint function decorated with @app.entrypoint
4. THE System SHALL be deployable to Amazon Bedrock AgentCore Runtime in us-east-1
5. THE System SHALL use AWS credentials from credits.txt file (default profile) for deployment
6. THE System SHALL be deployed using the bedrock-agentcore-starter-toolkit
7. THE System SHALL be named "customer_segment_agent_kiro" when deployed to AgentCore

### Requirement 17: AgentCore Runtime Configuration

**User Story:** As a system administrator, I want proper AgentCore configuration, so that the agent can be invoked and monitored in production.

#### Acceptance Criteria

1. WHEN configuring AgentCore, THE System SHALL create required IAM roles automatically
2. WHEN configuring AgentCore, THE System SHALL create required ECR repository automatically
3. WHEN deployed, THE System SHALL provide an AgentCore ARN for invocation
4. WHEN deployed, THE System SHALL provide IAM Role ARN for documentation
5. WHEN deployed, THE System SHALL provide ECR Repository URI for documentation
6. THE System SHALL support invocation via agentcore invoke command
7. THE System SHALL run in a uv Python virtual environment (.venv)

### Requirement 18: API Documentation

**User Story:** As a frontend developer, I want comprehensive API documentation, so that I can integrate with the deployed agent.

#### Acceptance Criteria

1. THE System SHALL provide an API documentation file (customer-segment-agent-api.md)
2. WHEN documented, THE API doc SHALL include the AgentCore ARN
3. WHEN documented, THE API doc SHALL include the IAM Role ARN
4. WHEN documented, THE API doc SHALL include the ECR Repository URI
5. WHEN documented, THE API doc SHALL include example invocation payloads
6. WHEN documented, THE API doc SHALL include expected response formats
7. WHEN documented, THE API doc SHALL include deployment region information
