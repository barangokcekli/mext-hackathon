# Customer Segment Agent - Implementation Details

## Code Structure

```
customer-segment-agent/
├── customer_segment_agent.py    # Main agent implementation
├── requirements.txt              # Python dependencies
├── .bedrock_agentcore.yaml      # Deployment configuration
├── README.md                     # User documentation
├── ARCHITECTURE.md               # System architecture
├── DEPLOYMENT.md                 # Deployment guide
├── IMPLEMENTATION.md             # This file
├── PRESENTATION.md               # Presentation guide
├── docs/
│   ├── INTEGRATION_GUIDE.md     # Integration documentation
│   └── CROSS_ACCOUNT_ACCESS.md  # Cross-account setup
├── examples/
│   ├── integration_example.py   # Python integration examples
│   ├── integration_example.js   # Node.js integration examples
│   ├── example-request.json
│   ├── example-request-new-customer.json
│   ├── example-request-region.json
│   ├── example-response.json
│   ├── example-response-new-customer.json
│   ├── example-response-region.json
│   ├── example-user.json
│   └── example-user-segment.json
├── tests/
│   ├── performance_test_pure.py
│   ├── performance_test_20_customers.py
│   ├── test_deployed_agent_20.py
│   └── test_aws_deployed_quick.sh
├── schemas/
│   ├── database_schema.sql      # MySQL schema
│   └── mongodb_schema.js         # MongoDB schema
└── mock-data/
    ├── regions.json
    ├── tenants.json
    └── farmasi/
        ├── customers.json
        ├── customers-100.json
        └── products.json
```

## Core Implementation

### Main Agent (`customer_segment_agent.py`)

#### 1. Imports and Setup

```python
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()
```

#### 2. Strands Agent Initialization

```python
agent = Agent(
    system_prompt="""You are a Customer Segment Analysis Agent. 
    Your role is to analyze customer data and provide comprehensive 
    segmentation insights..."""
)
```

#### 3. Segmentation Functions

**Age Segmentation:**
```python
def calculate_age_segment(age: int) -> str:
    if age <= 25:
        return "GenZ"
    elif age <= 35:
        return "GençYetişkin"
    elif age <= 50:
        return "Yetişkin"
    else:
        return "Olgun"
```

**Churn Risk Analysis:**
```python
def calculate_churn_segment(last_purchase_days_ago: int) -> str:
    if last_purchase_days_ago > 60:
        return "Riskli"
    elif last_purchase_days_ago >= 30:
        return "Ilık"
    else:
        return "Aktif"
```

**Value Classification:**
```python
def calculate_value_segment(avg_basket: float, region_median: float) -> str:
    return "HighValue" if avg_basket > region_median else "Standard"
```

**Loyalty Tier:**
```python
def calculate_loyalty_tier(membership_months: float, 
                          order_frequency: float, 
                          total_orders: int) -> str:
    if membership_months >= 12 and order_frequency >= 2:
        return "Platin"
    elif membership_months >= 6 and order_frequency >= 1:
        return "Altın"
    elif total_orders >= 3:
        return "Gümüş"
    else:
        return "Bronz"
```

#### 4. Input Validation

```python
def validate_customer_data(customer_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    if not isinstance(customer_data, dict):
        return False, "customerData must be a dictionary"
    
    customer = customer_data.get("customer", {})
    if customer:
        age = customer.get("age")
        if age is not None and (age < 0 or age > 120):
            return False, f"Invalid age: {age}"
        
        product_history = customer.get("productHistory", [])
        for product in product_history:
            if product.get("totalSpent", 0) < 0:
                return False, f"Invalid totalSpent"
            if product.get("orderCount", 0) < 0:
                return False, f"Invalid orderCount"
    
    return True, None
```

#### 5. Main Analysis Function

```python
def analyze_customer_data(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Starting analysis for customer: {customer_data.get('customerId', 'N/A')}")
    
    # Validate input
    is_valid, error_msg = validate_customer_data(customer_data)
    if not is_valid:
        logger.error(f"Validation failed: {error_msg}")
        raise ValueError(error_msg)
    
    # Extract basic info
    customer_id = customer_data.get("customerId")
    city = customer_data.get("city", "")
    
    # Handle different modes
    if not customer_id:
        return handle_region_mode(customer_data)
    
    customer = customer_data.get("customer", {})
    product_history = customer.get("productHistory", [])
    
    if not product_history:
        return handle_new_customer_mode(customer_data)
    
    return handle_regular_mode(customer_data)
```

#### 6. Agent Entrypoint

```python
@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("=== Agent invocation started ===")
    try:
        user_message = payload.get("prompt", "")
        customer_data = payload.get("customerData", {})
        
        if customer_data:
            logger.info("Customer data provided, starting analysis")
            analysis_result = analyze_customer_data(customer_data)
            
            # Generate AI explanation
            try:
                logger.info("Generating AI explanation")
                agent_response = agent(f"Provide a brief explanation of this customer analysis:\n{summary}")
                explanation = agent_response.message
                logger.info("AI explanation generated successfully")
            except Exception as agent_error:
                logger.warning(f"Agent explanation failed: {str(agent_error)}, using fallback")
                explanation = f"Customer segmentation analysis completed. {analysis_result.get('message', '')}"
            
            result = {
                "analysis": analysis_result,
                "explanation": explanation,
                "timestamp": datetime.now().isoformat()
            }
            logger.info("=== Analysis completed successfully ===")
            return result
        
        # Handle general queries
        # ...
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return {
            "error": str(ve),
            "message": "Invalid input data",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "message": "Failed to process customer analysis",
            "timestamp": datetime.now().isoformat()
        }
```

## Key Implementation Decisions

### 1. Rule-Based vs ML-Based

**Decision**: Rule-based segmentation
**Rationale**:
- Deterministic and explainable
- Fast execution (0.03ms per customer)
- No training data required
- Easy to maintain and update
- Predictable behavior

### 2. Hybrid AI Approach

**Decision**: Rule-based analysis + AI explanation
**Rationale**:
- Combines speed of rules with flexibility of AI
- AI generates natural language insights
- Fallback mechanism if AI fails
- Best of both worlds

### 3. Three Analysis Modes

**Decision**: Regular, New Customer, Region modes
**Rationale**:
- Handles different data availability scenarios
- Graceful degradation
- Always provides useful insights
- Flexible for various use cases

### 4. Input Validation

**Decision**: Comprehensive validation before processing
**Rationale**:
- Prevents invalid data from causing errors
- Clear error messages for debugging
- Security against malicious input
- Better user experience

### 5. Logging Strategy

**Decision**: Structured logging at multiple levels
**Rationale**:
- Easy debugging in production
- Performance monitoring
- Audit trail
- CloudWatch integration

## Performance Optimizations

### 1. Pure Python Calculations

- No external API calls for segmentation
- In-memory processing
- Minimal dependencies
- Fast execution

### 2. Efficient Data Structures

- Dictionary lookups (O(1))
- List comprehensions
- Generator expressions where applicable
- Minimal memory footprint

### 3. Lazy Evaluation

- AI explanation only when needed
- Conditional processing based on mode
- Early returns for invalid data

### 4. Caching Strategy

- Dependencies cached during deployment
- No runtime caching (stateless design)
- Future: Redis/ElastiCache integration

## Error Handling

### 1. Validation Errors

```python
except ValueError as ve:
    logger.error(f"Validation error: {str(ve)}")
    return {
        "error": str(ve),
        "message": "Invalid input data",
        "timestamp": datetime.now().isoformat()
    }
```

### 2. AI Failures

```python
except Exception as agent_error:
    logger.warning(f"Agent explanation failed: {str(agent_error)}, using fallback")
    explanation = f"Customer segmentation analysis completed."
```

### 3. Unexpected Errors

```python
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    return {
        "error": str(e),
        "message": "Failed to process customer analysis",
        "timestamp": datetime.now().isoformat()
    }
```

## Testing Strategy

### 1. Unit Tests

- Test individual segmentation functions
- Validate edge cases
- Check error handling

### 2. Integration Tests

- Test full analysis flow
- Verify AI explanation generation
- Check logging output

### 3. Performance Tests

- Measure latency per customer
- Calculate throughput
- Identify bottlenecks

### 4. Load Tests

- Test concurrent requests
- Verify scalability
- Check resource usage

## Dependencies

```txt
strands-agents          # Strands Agent framework
bedrock-agentcore       # AWS Bedrock AgentCore runtime
aws-opentelemetry-distro>=0.10.1  # Observability
boto3                   # AWS SDK
```

## Future Improvements

### 1. ML-Based Segmentation

- Train models on historical data
- Dynamic threshold learning
- Predictive analytics

### 2. Real-time Streaming

- Support for streaming data
- Incremental updates
- Event-driven architecture

### 3. Advanced Caching

- Redis integration
- TTL-based invalidation
- Distributed caching

### 4. A/B Testing

- Built-in experimentation
- Variant management
- Statistical analysis

### 5. Multi-tenancy

- Tenant-specific rules
- Isolated data processing
- Custom configurations

## Code Quality

### Linting

```bash
pylint customer_segment_agent.py
flake8 customer_segment_agent.py
```

### Type Checking

```bash
mypy customer_segment_agent.py
```

### Code Formatting

```bash
black customer_segment_agent.py
isort customer_segment_agent.py
```

## Contribution Guidelines

1. Follow PEP 8 style guide
2. Add type hints
3. Write docstrings
4. Include unit tests
5. Update documentation
6. Run linters before commit

## License

Proprietary - Hackathon Project
