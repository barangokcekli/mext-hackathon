# Design Document: User Segment Agent

## Overview

The User Segment Agent is a customer segmentation system implemented as a Strands Agent and deployed on Amazon Bedrock AgentCore Runtime. The system analyzes customer data to generate comprehensive profiling insights, operating in three distinct modes: regular mode (full customer analysis), region mode (no customer ID provided), and new customer mode (empty purchase history). All calculations are deterministic and rule-based, using predefined segmentation tables and thresholds.

The agent is built using the Strands Agents framework, which provides a model-driven approach leveraging AI models' planning, reasoning, and tool calling capabilities. It accepts input containing customer data, regional market data, and contextual information, then outputs a structured CustomerInsightJSON object with demographic segments, behavioral classifications, financial metrics, activity metrics, and product insights.

The deployment uses the BedrockAgentCoreApp wrapper from the bedrock-agentcore SDK, enabling seamless deployment to AWS AgentCore Runtime in the us-west-2 region with automatic HTTP server setup and built-in deployment tools.

## Architecture

The system follows a Strands Agent architecture deployed on AgentCore Runtime:

```
HTTP Request → AgentCore Runtime → BedrockAgentCoreApp → Strands Agent → Analysis Pipeline
                                                              ↓
                                    Input Validation → Mode Detection → Metric Calculation → Segmentation → Output Assembly
```

### Deployment Architecture

1. **AgentCore Runtime**: Serverless runtime environment on AWS
2. **BedrockAgentCoreApp**: HTTP wrapper that exposes the agent via /invocations endpoint
3. **Strands Agent**: AI-powered agent with system prompt for customer analysis
4. **Analysis Functions**: Deterministic calculation functions for segmentation

### Processing Pipeline

For Regular Mode, the pipeline executes:

1. Receive HTTP POST request at /invocations endpoint
2. Extract customer data from payload
3. Perform deterministic analysis using helper functions
4. Use Strands Agent to generate natural language explanation
5. Return structured JSON response with analysis and explanation

## Components and Interfaces

### Deployment Components

#### 1. BedrockAgentCoreApp

HTTP wrapper that provides AgentCore Runtime integration:

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Agent logic here
    return response
```

#### 2. Strands Agent

AI agent with system prompt for customer analysis:

```python
from strands import Agent

agent = Agent(
    system_prompt="""You are a Customer Segment Analysis Agent..."""
)
```

### Input Interface

```typescript
interface AnalyzeCustomerInput {
  city: string;
  customerId?: string;
  customer: Customer;
  region: Region;
  currentSeason: string;
}

interface Customer {
  customerId: string;
  city: string;
  age: number;
  gender: string;
  registeredAt: string; // ISO date
  productHistory: ProductHistoryItem[];
}

interface ProductHistoryItem {
  productId: string;
  category: string;
  totalQuantity: number;
  totalSpent: number;
  orderCount: number;
  lastPurchase: string; // ISO date
  avgDaysBetween: number | null;
}

interface Region {
  name: string;
  climateType: string;
  medianBasket: number;
  trend: string; // trending category
}
```

### Output Interface

```typescript
interface CustomerInsightJSON {
  customerId?: string;
  city: string;
  region: string;
  climateType: string;
  age?: number;
  ageSegment: string;
  gender?: string;
  churnSegment: string;
  valueSegment: string;
  loyaltyTier: string;
  affinityCategory: string;
  affinityType: string;
  diversityProfile: string;
  estimatedBudget: number;
  avgBasket: number;
  avgMonthlySpend: number;
  lastPurchaseDaysAgo: number;
  orderCount: number;
  totalSpent: number;
  membershipDays: number;
  missingRegulars: MissingRegular[];
  topProducts: TopProduct[];
}

interface MissingRegular {
  productId: string;
  productName: string;
  lastBought: string;
  avgDaysBetween: number;
  daysOverdue: number;
}

interface TopProduct {
  productId: string;
  totalQuantity: number;
  totalSpent: number;
  lastBought: string;
}
```

### Core Components

#### 1. ModeDetector

Determines which operational mode to use based on input.

```typescript
function detectMode(customerId: string | undefined, productHistory: ProductHistoryItem[]): 
  'region' | 'new-customer' | 'regular'
```

#### 2. MetricsCalculator

Calculates all financial and activity metrics from purchase history.

```typescript
interface Metrics {
  lastPurchaseDaysAgo: number;
  totalSpent: number;
  orderCount: number;
  avgBasket: number;
  membershipDays: number;
  membershipMonths: number;
  avgMonthlySpend: number;
  orderFrequency: number;
}

function calculateMetrics(
  productHistory: ProductHistoryItem[], 
  registeredAt: string,
  currentDate: string
): Metrics
```

#### 3. SegmentClassifier

Applies segmentation rules to classify customer across all dimensions.

```typescript
interface Segments {
  ageSegment: string;
  churnSegment: string;
  valueSegment: string;
  loyaltyTier: string;
  affinityCategory: string;
  affinityType: string;
  diversityProfile: string;
}

function classifySegments(
  customer: Customer,
  metrics: Metrics,
  productHistory: ProductHistoryItem[],
  regionMedianBasket: number
): Segments
```

#### 4. ProductAnalyzer

Identifies missing regular products and top products.

```typescript
function findMissingRegulars(
  productHistory: ProductHistoryItem[],
  currentDate: string
): MissingRegular[]

function findTopProducts(
  productHistory: ProductHistoryItem[]
): TopProduct[]
```

#### 5. ProfileAssembler

Assembles the final CustomerInsightJSON output.

```typescript
function assembleProfile(
  customer: Customer,
  region: Region,
  metrics: Metrics,
  segments: Segments,
  missingRegulars: MissingRegular[],
  topProducts: TopProduct[]
): CustomerInsightJSON
```

## Data Models

### Segmentation Rules

#### Age Segment Mapping

```typescript
function getAgeSegment(age: number): string {
  if (age <= 25) return "GenZ";
  if (age <= 35) return "GençYetişkin";
  if (age <= 50) return "Yetişkin";
  return "Olgun";
}
```

#### Churn Segment Mapping

```typescript
function getChurnSegment(lastPurchaseDaysAgo: number): string {
  if (lastPurchaseDaysAgo > 60) return "Riskli";
  if (lastPurchaseDaysAgo >= 30) return "Ilık";
  return "Aktif";
}
```

#### Value Segment Mapping

```typescript
function getValueSegment(avgBasket: number, regionMedianBasket: number): string {
  return avgBasket > regionMedianBasket ? "HighValue" : "Standard";
}
```

#### Loyalty Tier Mapping

```typescript
function getLoyaltyTier(membershipMonths: number, orderFrequency: number): string {
  if (membershipMonths >= 12 && orderFrequency >= 2) return "Platin";
  if (membershipMonths >= 6 && orderFrequency >= 1) return "Altın";
  if (orderFrequency * membershipMonths >= 3) return "Gümüş";
  return "Bronz";
}
```

Note: The loyalty tier calculation for "Gümüş" uses total orders (orderFrequency * membershipMonths) >= 3.

#### Category Affinity

```typescript
interface CategoryBreakdown {
  [category: string]: {
    totalSpent: number;
    orderCount: number;
  };
}

function getCategoryAffinity(productHistory: ProductHistoryItem[]): {
  affinityCategory: string;
  affinityRatio: number;
  affinityType: string;
} {
  const breakdown = groupByCategory(productHistory);
  const affinityCategory = findMaxSpendingCategory(breakdown);
  const totalOrders = sumOrderCounts(productHistory);
  const affinityRatio = breakdown[affinityCategory].orderCount / totalOrders;
  const affinityType = affinityRatio > 0.6 ? "Odaklı" : "Keşifçi";
  
  return { affinityCategory, affinityRatio, affinityType };
}
```

#### Diversity Profile

```typescript
function getDiversityProfile(productHistory: ProductHistoryItem[], totalOrders: number): string {
  const uniqueProducts = productHistory.length;
  const diversityRatio = uniqueProducts / totalOrders;
  
  if (diversityRatio > 0.7) return "Kaşif";
  if (diversityRatio > 0.4) return "Dengeli";
  return "Sadık";
}
```

### Special Mode Profiles

#### Region Profile

When no customerId is provided, return a generic profile based on regional data:

```typescript
function getRegionProfile(city: string, region: Region): CustomerInsightJSON {
  return {
    city,
    region: region.name,
    climateType: region.climateType,
    ageSegment: "Yetişkin",
    gender: null,
    churnSegment: "Aktif",
    valueSegment: "Standard",
    loyaltyTier: "Gümüş",
    affinityCategory: region.trend,
    affinityType: "Keşifçi",
    diversityProfile: "Dengeli",
    estimatedBudget: region.medianBasket * 1.2,
    avgBasket: region.medianBasket,
    avgMonthlySpend: region.medianBasket * 2,
    lastPurchaseDaysAgo: 30,
    orderCount: 0,
    totalSpent: 0,
    membershipDays: 0,
    missingRegulars: [],
    topProducts: []
  };
}
```

#### New Customer Profile

When customer has empty productHistory:

```typescript
function getNewCustomerProfile(customer: Customer, region: Region, currentDate: string): CustomerInsightJSON {
  const membershipDays = daysBetween(customer.registeredAt, currentDate);
  
  return {
    customerId: customer.customerId,
    city: customer.city,
    region: region.name,
    climateType: region.climateType,
    age: customer.age,
    ageSegment: getAgeSegment(customer.age),
    gender: customer.gender,
    churnSegment: "Riskli",
    valueSegment: "Standard",
    loyaltyTier: "Bronz",
    affinityCategory: region.trend,
    affinityType: "Keşifçi",
    diversityProfile: "Kaşif",
    estimatedBudget: region.medianBasket * 1.2,
    avgBasket: region.medianBasket,
    avgMonthlySpend: 0,
    lastPurchaseDaysAgo: 999,
    orderCount: 0,
    totalSpent: 0,
    membershipDays,
    missingRegulars: [],
    topProducts: []
  };
}
```

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Complete output structure
*For any* valid input, the output CustomerInsightJSON should contain all required fields (customerId/city/region/climateType, age/ageSegment/gender, churnSegment/valueSegment/loyaltyTier, affinityCategory/affinityType/diversityProfile, estimatedBudget/avgBasket/avgMonthlySpend/totalSpent, lastPurchaseDaysAgo/orderCount/membershipDays, missingRegulars/topProducts)
**Validates: Requirements 2.1**

### Property 2: Age segmentation correctness
*For any* customer age, the ageSegment should be "GenZ" for ages 18-25, "GençYetişkin" for ages 26-35, "Yetişkin" for ages 36-50, and "Olgun" for ages 51+
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 3: Churn segmentation correctness
*For any* last purchase date, the churnSegment should be "Aktif" when less than 30 days ago, "Ilık" when 30-60 days ago, and "Riskli" when more than 60 days ago
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 4: Value segmentation correctness
*For any* average basket size and region median basket, the valueSegment should be "HighValue" when avgBasket exceeds the median, and "Standard" otherwise
**Validates: Requirements 5.1, 5.2**

### Property 5: Loyalty tier correctness
*For any* membership duration and order frequency, the loyaltyTier should be "Platin" for 12+ months with 2+ orders/month, "Altın" for 6+ months with 1+ orders/month, "Gümüş" for 3+ total orders, and "Bronz" otherwise
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 6: Affinity category identification
*For any* purchase history, the affinityCategory should be the category with the highest total spending
**Validates: Requirements 7.1**

### Property 7: Affinity ratio calculation
*For any* purchase history, the affinity ratio should equal the number of orders in the affinity category divided by total orders
**Validates: Requirements 7.2**

### Property 8: Affinity type classification
*For any* affinity ratio, the affinityType should be "Odaklı" when ratio exceeds 0.6, and "Keşifçi" otherwise
**Validates: Requirements 7.3, 7.4**

### Property 9: Diversity ratio calculation
*For any* purchase history, the diversity ratio should equal the number of unique products divided by total orders
**Validates: Requirements 8.1**

### Property 10: Diversity profile classification
*For any* diversity ratio, the diversityProfile should be "Kaşif" when ratio exceeds 0.7, "Dengeli" when ratio is between 0.4 and 0.7 inclusive, and "Sadık" when ratio is 0.4 or below
**Validates: Requirements 8.2, 8.3, 8.4**

### Property 11: Total spent calculation
*For any* purchase history, the totalSpent should equal the sum of all product totalSpent values
**Validates: Requirements 9.1**

### Property 12: Order count calculation
*For any* purchase history, the orderCount should equal the sum of all product orderCount values
**Validates: Requirements 9.2**

### Property 13: Average basket arithmetic relationship
*For any* purchase history, the avgBasket should equal totalSpent divided by orderCount
**Validates: Requirements 9.3**

### Property 14: Estimated budget arithmetic relationship
*For any* average basket, the estimatedBudget should equal avgBasket multiplied by 1.2
**Validates: Requirements 9.4**

### Property 15: Membership days calculation
*For any* registration date and current date, the membershipDays should equal the number of days between them
**Validates: Requirements 9.5**

### Property 16: Average monthly spend arithmetic relationship
*For any* total spent and membership duration, the avgMonthlySpend should equal totalSpent divided by membership months
**Validates: Requirements 9.6**

### Property 17: Last purchase days calculation
*For any* purchase history, the lastPurchaseDaysAgo should equal the days since the most recent purchase date
**Validates: Requirements 10.1**

### Property 18: Regular products identification
*For any* purchase history, regular products should be those with avgDaysBetween not null and 60 days or less
**Validates: Requirements 11.1**

### Property 19: Missing regulars classification
*For any* regular product, it should be classified as missing when days since last purchase exceeds avgDaysBetween multiplied by 1.2
**Validates: Requirements 11.2**

### Property 20: Missing regulars structure
*For any* missing regular product, the output should include productId, productName, lastBought, avgDaysBetween, and daysOverdue fields
**Validates: Requirements 11.3**

### Property 21: Days overdue arithmetic relationship
*For any* missing regular product, daysOverdue should equal days since last purchase minus avgDaysBetween
**Validates: Requirements 11.4**

### Property 22: Top products sorting
*For any* purchase history, top products should be sorted by totalSpent in descending order
**Validates: Requirements 12.1**

### Property 23: Top products count
*For any* purchase history, the number of top products returned should be the minimum of 5 and the total number of products
**Validates: Requirements 12.2**

### Property 24: Top products structure
*For any* top product, the output should include productId, totalQuantity, totalSpent, and lastBought fields
**Validates: Requirements 12.3**

### Property 25: Region mode defaults
*For any* region-based profile (no customerId), the avgBasket should equal region.medianBasket, affinityCategory should equal region.trend, and all segment values should match expected defaults (ageSegment: "Yetişkin", churnSegment: "Aktif", valueSegment: "Standard", loyaltyTier: "Gümüş", affinityType: "Keşifçi", diversityProfile: "Dengeli")
**Validates: Requirements 13.2, 13.3, 13.4, 13.5, 13.6**

### Property 26: New customer mode defaults
*For any* new customer profile (empty productHistory), the segments should be churnSegment: "Riskli", valueSegment: "Standard", loyaltyTier: "Bronz", diversityProfile: "Kaşif", affinityCategory: region.trend, affinityType: "Keşifçi", lastPurchaseDaysAgo: 999, and missingRegulars and topProducts should be empty arrays
**Validates: Requirements 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9**

### Property 27: Deterministic execution
*For any* input data, running the analysis twice should produce identical output results
**Validates: Requirements 15.3**

### Property 28: AgentCore deployment
*For any* deployment, the agent should be accessible via AgentCore Runtime ARN and respond to invocation requests
**Validates: Requirements 16.4**

### Property 29: API documentation completeness
*For any* deployment, the API documentation should include AgentCore ARN, IAM Role ARN, ECR Repository URI, and example payloads
**Validates: Requirements 18.2, 18.3, 18.4, 18.5**

## Error Handling

### Input Validation

The system should validate input data and handle edge cases:

1. **Missing Required Fields**: If required fields (city, customer, region) are missing, throw a validation error
2. **Invalid Date Formats**: If date strings cannot be parsed, throw a validation error
3. **Negative Values**: If numeric values (age, totalSpent, orderCount) are negative, throw a validation error
4. **Empty Product History**: Handle gracefully by switching to new customer mode
5. **Division by Zero**: When orderCount is 0, handle avgBasket calculation by using region median

### Edge Cases

1. **Single Product Purchase**: When customer has only one product in history, diversity ratio will be 1.0 (Kaşif profile)
2. **Same-Day Registration and Purchase**: membershipDays could be 0, handle division in avgMonthlySpend
3. **No Regular Products**: missingRegulars array will be empty
4. **Fewer Than 5 Products**: topProducts will contain all available products
5. **All Products in Same Category**: affinityRatio will be 1.0 (Odaklı type)

### Error Response Format

When validation errors occur, return an error object:

```typescript
interface ErrorResponse {
  error: string;
  message: string;
  field?: string;
}
```

## Testing Strategy

### Unit Testing

Unit tests should cover:

1. **Mode Detection**: Test region mode, new customer mode, and regular mode detection
2. **Segmentation Functions**: Test each segmentation function with boundary values
   - Age segments at boundaries (25, 26, 35, 36, 50, 51)
   - Churn segments at boundaries (29, 30, 60, 61 days)
   - Value segment at median boundary
   - Loyalty tiers at threshold boundaries
   - Affinity type at 0.6 ratio boundary
   - Diversity profile at 0.4 and 0.7 boundaries
3. **Metric Calculations**: Test arithmetic calculations with known values
4. **Date Calculations**: Test day counting with various date ranges
5. **Product Analysis**: Test missing regulars and top products with edge cases
6. **Error Handling**: Test validation errors and edge cases

### Property-Based Testing

Property-based tests should verify universal properties across randomized inputs. Each test should run a minimum of 100 iterations.

**Test Configuration**: Use a property-based testing library appropriate for the implementation language (e.g., fast-check for TypeScript/JavaScript, Hypothesis for Python, QuickCheck for Haskell).

**Property Test Examples**:

1. **Property 1-27**: Implement each correctness property as a property-based test
2. **Tag Format**: Each test should include a comment: `// Feature: user-segment-agent, Property N: [property description]`
3. **Generators**: Create generators for:
   - Random customer data with valid constraints
   - Random purchase histories with varying sizes
   - Random dates within reasonable ranges
   - Random product data with categories
   - Random region data

**Key Property Tests**:

- **Arithmetic Relationships**: Verify avgBasket = totalSpent / orderCount, estimatedBudget = avgBasket * 1.2, etc.
- **Segmentation Boundaries**: Generate random values around boundaries and verify correct classification
- **Sorting Invariants**: Verify top products are always in descending order by totalSpent
- **Mode Consistency**: Verify region mode and new customer mode always return expected defaults
- **Determinism**: Run analysis twice with same input and verify outputs are identical

### Integration Testing

Integration tests should verify:

1. **End-to-End Flow**: Test complete analysis pipeline from input to output
2. **Mode Switching**: Test transitions between different operational modes
3. **Real Data Scenarios**: Test with realistic customer and product data
4. **Performance**: Verify analysis completes within acceptable time limits

### Test Data

Create test fixtures for:

1. **Active High-Value Customer**: Recent purchases, high spending, long membership
2. **At-Risk Standard Customer**: No recent purchases, average spending
3. **New Customer**: Empty purchase history
4. **Region Profile**: No customer ID provided
5. **Edge Cases**: Single product, all same category, boundary values
