"""
Customer Segment Agent - Strands Agent Implementation
Analyzes customer data and performs segmentation based on purchase history,
demographics, and behavioral patterns.
"""

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

# Initialize Strands agent with system prompt
agent = Agent(
    system_prompt="""You are a Customer Segment Analysis Agent. Your role is to analyze customer data and provide comprehensive segmentation insights.

You analyze:
- Customer demographics (age, gender, location)
- Purchase history and patterns
- Behavioral segments (churn risk, value, loyalty)
- Product preferences and diversity

You provide structured insights including:
- Age segments (GenZ, GençYetişkin, Yetişkin, Olgun)
- Churn segments (Aktif, Ilık, Riskli)
- Value segments (HighValue, Standard)
- Loyalty tiers (Platin, Altın, Gümüş, Bronz)
- Category affinity and diversity profiles

You do NOT perform stock analysis or campaign decisions - only customer profiling and segmentation.

When given customer data, analyze it systematically and provide clear, actionable insights."""
)


def calculate_age_segment(age: int) -> str:
    """Calculate age segment based on customer age."""
    if age <= 25:
        return "GenZ"
    elif age <= 35:
        return "GençYetişkin"
    elif age <= 50:
        return "Yetişkin"
    else:
        return "Olgun"


def calculate_churn_segment(last_purchase_days_ago: int) -> str:
    """Calculate churn segment based on last purchase recency."""
    if last_purchase_days_ago > 60:
        return "Riskli"
    elif last_purchase_days_ago >= 30:
        return "Ilık"
    else:
        return "Aktif"


def calculate_value_segment(avg_basket: float, region_median: float) -> str:
    """Calculate value segment based on spending."""
    return "HighValue" if avg_basket > region_median else "Standard"


def calculate_loyalty_tier(membership_months: float, order_frequency: float, total_orders: int) -> str:
    """Calculate loyalty tier based on membership and order frequency."""
    if membership_months >= 12 and order_frequency >= 2:
        return "Platin"
    elif membership_months >= 6 and order_frequency >= 1:
        return "Altın"
    elif total_orders >= 3:
        return "Gümüş"
    else:
        return "Bronz"


def validate_customer_data(customer_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate input customer data."""
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
                return False, f"Invalid totalSpent for product {product.get('productId')}"
            if product.get("orderCount", 0) < 0:
                return False, f"Invalid orderCount for product {product.get('productId')}"
    
    return True, None


def analyze_customer_data(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze customer data and return segmentation insights.
    
    This function performs deterministic rule-based analysis without ML.
    """
    logger.info(f"Starting analysis for customer: {customer_data.get('customerId', 'N/A')}")
    
    # Validate input
    is_valid, error_msg = validate_customer_data(customer_data)
    if not is_valid:
        logger.error(f"Validation failed: {error_msg}")
        raise ValueError(error_msg)
    
    # Extract basic info
    customer_id = customer_data.get("customerId")
    city = customer_data.get("city", "")
    
    # Handle region mode (no customer ID)
    if not customer_id:
        logger.info(f"Region mode analysis for city: {city}")
        region = customer_data.get("region", {})
        median_basket = region.get("medianBasket", 0)
        return {
            "mode": "region",
            "city": city,
            "region": region.get("name", ""),
            "climateType": region.get("climateType", ""),
            "ageSegment": "Yetişkin",
            "gender": None,
            "churnSegment": "Aktif",
            "valueSegment": "Standard",
            "loyaltyTier": "Gümüş",
            "affinityCategory": region.get("trend", ""),
            "affinityType": "Keşifçi",
            "diversityProfile": "Dengeli",
            "avgBasket": median_basket,
            "estimatedBudget": median_basket * 1.2,
            "avgMonthlySpend": median_basket * 2,
            "lastPurchaseDaysAgo": 30,
            "orderCount": 0,
            "totalSpent": 0,
            "membershipDays": 0,
            "missingRegulars": [],
            "topProducts": [],
            "message": "Region-based profile (no specific customer data)"
        }
    
    customer = customer_data.get("customer", {})
    region = customer_data.get("region", {})
    product_history = customer.get("productHistory", [])
    
    # Handle new customer mode (empty purchase history)
    if not product_history:
        logger.info(f"New customer mode for: {customer_id}")
        age = customer.get("age", 30)
        membership_days = (datetime.now() - datetime.fromisoformat(customer.get("registeredAt", datetime.now().isoformat()))).days
        median_basket = region.get("medianBasket", 0)
        
        return {
            "mode": "new_customer",
            "customerId": customer_id,
            "city": city,
            "region": region.get("name", ""),
            "climateType": region.get("climateType", ""),
            "age": age,
            "ageSegment": calculate_age_segment(age),
            "gender": customer.get("gender", ""),
            "churnSegment": "Riskli",
            "valueSegment": "Standard",
            "loyaltyTier": "Bronz",
            "affinityCategory": region.get("trend", ""),
            "affinityType": "Keşifçi",
            "diversityProfile": "Kaşif",
            "avgBasket": median_basket,
            "estimatedBudget": median_basket * 1.2,
            "avgMonthlySpend": 0,
            "lastPurchaseDaysAgo": 999,
            "orderCount": 0,
            "totalSpent": 0,
            "membershipDays": membership_days,
            "missingRegulars": [],
            "topProducts": [],
            "message": "New customer profile (no purchase history yet)"
        }
    
    # Regular mode - full analysis
    logger.info(f"Regular mode analysis for: {customer_id} with {len(product_history)} products")
    age = customer.get("age", 30)
    
    # Calculate metrics
    total_spent = sum(p.get("totalSpent", 0) for p in product_history)
    total_orders = sum(p.get("orderCount", 0) for p in product_history)
    avg_basket = total_spent / total_orders if total_orders > 0 else 0
    
    logger.debug(f"Metrics - Total spent: {total_spent}, Orders: {total_orders}, Avg basket: {avg_basket}")
    
    # Calculate dates
    registered_at = datetime.fromisoformat(customer.get("registeredAt", datetime.now().isoformat()))
    membership_days = (datetime.now() - registered_at).days
    membership_months = membership_days / 30 if membership_days > 0 else 0
    
    # Find most recent purchase
    last_purchase_dates = [datetime.fromisoformat(p.get("lastPurchase", datetime.now().isoformat())) for p in product_history]
    last_purchase_days_ago = (datetime.now() - max(last_purchase_dates)).days if last_purchase_dates else 999
    
    order_frequency = total_orders / membership_months if membership_months > 0 else 0
    avg_monthly_spend = total_spent / membership_months if membership_months > 0 else 0
    
    # Category affinity analysis
    category_breakdown = {}
    for product in product_history:
        category = product.get("category", "Unknown")
        if category not in category_breakdown:
            category_breakdown[category] = {"totalSpent": 0, "orderCount": 0}
        category_breakdown[category]["totalSpent"] += product.get("totalSpent", 0)
        category_breakdown[category]["orderCount"] += product.get("orderCount", 0)
    
    affinity_category = max(category_breakdown.items(), key=lambda x: x[1]["totalSpent"])[0] if category_breakdown else "Unknown"
    affinity_ratio = category_breakdown[affinity_category]["orderCount"] / total_orders if total_orders > 0 else 0
    affinity_type = "Odaklı" if affinity_ratio > 0.6 else "Keşifçi"
    
    # Diversity profile
    unique_products = len(product_history)
    diversity_ratio = unique_products / total_orders if total_orders > 0 else 0
    if diversity_ratio > 0.7:
        diversity_profile = "Kaşif"
    elif diversity_ratio > 0.4:
        diversity_profile = "Dengeli"
    else:
        diversity_profile = "Sadık"
    
    # Missing regulars
    missing_regulars = []
    for product in product_history:
        avg_days_between = product.get("avgDaysBetween")
        if avg_days_between and avg_days_between <= 60:
            last_purchase = datetime.fromisoformat(product.get("lastPurchase", datetime.now().isoformat()))
            days_since_last = (datetime.now() - last_purchase).days
            if days_since_last > avg_days_between * 1.2:
                missing_regulars.append({
                    "productId": product.get("productId", ""),
                    "productName": product.get("productId", ""),  # In real scenario, lookup product name
                    "lastBought": product.get("lastPurchase", ""),
                    "avgDaysBetween": avg_days_between,
                    "daysOverdue": days_since_last - avg_days_between
                })
    
    # Top products
    top_products = sorted(product_history, key=lambda x: x.get("totalSpent", 0), reverse=True)[:5]
    top_products_list = [
        {
            "productId": p.get("productId", ""),
            "totalQuantity": p.get("totalQuantity", 0),
            "totalSpent": p.get("totalSpent", 0),
            "lastBought": p.get("lastPurchase", "")
        }
        for p in top_products
    ]
    
    # Calculate segments
    age_segment = calculate_age_segment(age)
    churn_segment = calculate_churn_segment(last_purchase_days_ago)
    value_segment = calculate_value_segment(avg_basket, region.get("medianBasket", 0))
    loyalty_tier = calculate_loyalty_tier(membership_months, order_frequency, total_orders)
    
    logger.info(f"Segments - Age: {age_segment}, Churn: {churn_segment}, Value: {value_segment}, Loyalty: {loyalty_tier}")
    
    return {
        "mode": "regular",
        "customerId": customer_id,
        "city": city,
        "region": region.get("name", ""),
        "climateType": region.get("climateType", ""),
        "age": age,
        "ageSegment": age_segment,
        "gender": customer.get("gender", ""),
        "churnSegment": churn_segment,
        "valueSegment": value_segment,
        "loyaltyTier": loyalty_tier,
        "affinityCategory": affinity_category,
        "affinityType": affinity_type,
        "diversityProfile": diversity_profile,
        "estimatedBudget": avg_basket * 1.2,
        "avgBasket": avg_basket,
        "avgMonthlySpend": avg_monthly_spend,
        "lastPurchaseDaysAgo": last_purchase_days_ago,
        "orderCount": total_orders,
        "totalSpent": total_spent,
        "membershipDays": membership_days,
        "missingRegulars": missing_regulars,
        "topProducts": top_products_list,
        "message": "Full customer analysis completed"
    }


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entrypoint for the customer segment agent.
    
    Accepts customer data and returns comprehensive segmentation insights.
    """
    logger.info("=== Agent invocation started ===")
    try:
        # Extract prompt or customer data
        user_message = payload.get("prompt", "")
        customer_data = payload.get("customerData", {})
        
        logger.debug(f"Payload keys: {list(payload.keys())}")
        
        # If customer data is provided, perform analysis
        if customer_data:
            logger.info("Customer data provided, starting analysis")
            analysis_result = analyze_customer_data(customer_data)
            
            # Create a summary message for the agent
            summary = f"""Customer Analysis Complete:
- Customer ID: {analysis_result.get('customerId', 'N/A')}
- Mode: {analysis_result.get('mode', 'unknown')}
- Age Segment: {analysis_result.get('ageSegment', 'N/A')}
- Churn Segment: {analysis_result.get('churnSegment', 'N/A')}
- Value Segment: {analysis_result.get('valueSegment', 'N/A')}
- Loyalty Tier: {analysis_result.get('loyaltyTier', 'N/A')}
- Affinity Category: {analysis_result.get('affinityCategory', 'N/A')}
- Diversity Profile: {analysis_result.get('diversityProfile', 'N/A')}

{analysis_result.get('message', '')}"""
            
            # Use agent to provide natural language explanation
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
        
        # Otherwise, use agent for general queries
        if not user_message:
            user_message = "Hello! I'm the Customer Segment Agent. Provide customer data for analysis."
        
        logger.info(f"Processing general query: {user_message[:50]}...")
        try:
            result = agent(user_message)
            logger.info("General query processed successfully")
            return {
                "result": result.message,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as agent_error:
            logger.warning(f"Agent query failed: {str(agent_error)}, using fallback")
            return {
                "result": "I'm the Customer Segment Agent. I analyze customer data to provide segmentation insights including age segments, churn risk, value classification, loyalty tiers, and product preferences. Please provide customer data for analysis.",
                "timestamp": datetime.now().isoformat()
            }
        
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


if __name__ == "__main__":
    app.run()
