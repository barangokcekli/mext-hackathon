"""
Example: How to call Customer Segment Agent from another agent/orchestrator
"""
import boto3
import json
from datetime import datetime

# Initialize AWS Bedrock AgentCore client
client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

# Agent configuration
AGENT_ID = 'customer_segment_agent-1GD3a24jRt'
AGENT_ARN = 'arn:aws:bedrock-agentcore:us-west-2:485169707250:runtime/customer_segment_agent-1GD3a24jRt'


def call_customer_segment_agent(customer_data):
    """
    Call the Customer Segment Agent with customer data.
    
    Args:
        customer_data: Dictionary containing customer information
        
    Returns:
        Dictionary with analysis results and AI explanation
    """
    try:
        # Prepare payload
        payload = {"customerData": customer_data}
        
        # Invoke agent
        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId='TSTALIASID',  # Replace with your alias ID
            sessionId=f'session-{datetime.now().timestamp()}',
            inputText=json.dumps(payload)
        )
        
        # Parse response
        result = json.loads(response['completion'])
        return result
        
    except Exception as e:
        print(f"Error calling agent: {e}")
        raise


def example_regular_customer():
    """Example: Analyze a regular customer with purchase history"""
    print("=" * 80)
    print("Example 1: Regular Customer Analysis")
    print("=" * 80)
    
    customer_data = {
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
    
    result = call_customer_segment_agent(customer_data)
    
    print(f"\nCustomer ID: {result['analysis']['customerId']}")
    print(f"Age Segment: {result['analysis']['ageSegment']}")
    print(f"Churn Risk: {result['analysis']['churnSegment']}")
    print(f"Value Segment: {result['analysis']['valueSegment']}")
    print(f"Loyalty Tier: {result['analysis']['loyaltyTier']}")
    print(f"Affinity Category: {result['analysis']['affinityCategory']}")
    print(f"\nAI Explanation: {result['explanation'][:200]}...")
    
    return result


def example_new_customer():
    """Example: Analyze a new customer without purchase history"""
    print("\n" + "=" * 80)
    print("Example 2: New Customer Analysis")
    print("=" * 80)
    
    customer_data = {
        "customerId": "C-NEW-001",
        "city": "Antalya",
        "customer": {
            "customerId": "C-NEW-001",
            "age": 22,
            "gender": "F",
            "registeredAt": "2026-02-01T00:00:00",
            "productHistory": []  # Empty for new customer
        },
        "region": {
            "name": "Akdeniz",
            "climateType": "Mediterranean",
            "medianBasket": 85.0,
            "trend": "SKINCARE"
        }
    }
    
    result = call_customer_segment_agent(customer_data)
    
    print(f"\nCustomer ID: {result['analysis']['customerId']}")
    print(f"Mode: {result['analysis']['mode']}")
    print(f"Age Segment: {result['analysis']['ageSegment']}")
    print(f"Estimated Budget: ${result['analysis']['estimatedBudget']:.2f}")
    print(f"Message: {result['analysis']['message']}")
    
    return result


def example_orchestrator_workflow():
    """Example: Orchestrator using customer segment for decision making"""
    print("\n" + "=" * 80)
    print("Example 3: Orchestrator Workflow")
    print("=" * 80)
    
    customer_data = {
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
    
    # Step 1: Get customer segmentation
    print("\n[Step 1] Calling Customer Segment Agent...")
    segment_result = call_customer_segment_agent(customer_data)
    analysis = segment_result['analysis']
    
    # Step 2: Make decisions based on segmentation
    print("\n[Step 2] Making decisions based on segmentation...")
    
    # Churn risk strategy
    if analysis['churnSegment'] == 'Riskli':
        strategy = "RETENTION"
        discount = 20
        print(f"  → Churn Risk: HIGH → Strategy: {strategy} (Discount: {discount}%)")
    elif analysis['churnSegment'] == 'Ilık':
        strategy = "ENGAGEMENT"
        discount = 10
        print(f"  → Churn Risk: MEDIUM → Strategy: {strategy} (Discount: {discount}%)")
    else:
        strategy = "UPSELL"
        discount = 0
        print(f"  → Churn Risk: LOW → Strategy: {strategy} (No discount needed)")
    
    # Value-based targeting
    if analysis['valueSegment'] == 'HighValue':
        tier = "PREMIUM"
        print(f"  → Value: HIGH → Tier: {tier} (Premium products)")
    else:
        tier = "STANDARD"
        print(f"  → Value: STANDARD → Tier: {tier} (Standard products)")
    
    # Category affinity
    print(f"  → Affinity: {analysis['affinityCategory']} → Recommend similar products")
    
    # Step 3: Simulate calling other agents
    print("\n[Step 3] Calling downstream agents...")
    print(f"  → Product Recommendation Agent (category={analysis['affinityCategory']})")
    print(f"  → Pricing Strategy Agent (tier={tier}, discount={discount}%)")
    print(f"  → Campaign Agent (strategy={strategy})")
    
    # Step 4: Return orchestrated result
    orchestrated_result = {
        "customer_segment": analysis,
        "strategy": strategy,
        "tier": tier,
        "discount": discount,
        "recommended_category": analysis['affinityCategory']
    }
    
    print("\n[Step 4] Orchestration Complete!")
    print(f"  Final Strategy: {json.dumps(orchestrated_result, indent=2)}")
    
    return orchestrated_result


def example_batch_processing():
    """Example: Process multiple customers in batch"""
    print("\n" + "=" * 80)
    print("Example 4: Batch Processing")
    print("=" * 80)
    
    customers = [
        {
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
        },
        {
            "customerId": "C-1002",
            "city": "Ankara",
            "customer": {
                "customerId": "C-1002",
                "age": 45,
                "gender": "F",
                "registeredAt": "2024-06-20T00:00:00",
                "productHistory": []
            },
            "region": {
                "name": "İç Anadolu",
                "climateType": "Continental",
                "medianBasket": 70.0,
                "trend": "MAKEUP"
            }
        }
    ]
    
    print(f"\nProcessing {len(customers)} customers...")
    
    results = []
    for i, customer_data in enumerate(customers, 1):
        print(f"\n  [{i}/{len(customers)}] Analyzing {customer_data['customerId']}...")
        result = call_customer_segment_agent(customer_data)
        results.append({
            "customerId": result['analysis']['customerId'],
            "ageSegment": result['analysis']['ageSegment'],
            "churnSegment": result['analysis']['churnSegment'],
            "loyaltyTier": result['analysis']['loyaltyTier']
        })
        print(f"      → {result['analysis']['ageSegment']} | {result['analysis']['churnSegment']} | {result['analysis']['loyaltyTier']}")
    
    print(f"\n✅ Batch processing complete! Analyzed {len(results)} customers.")
    return results


if __name__ == "__main__":
    print("\n🚀 Customer Segment Agent - Integration Examples\n")
    
    # Run examples
    try:
        # Example 1: Regular customer
        example_regular_customer()
        
        # Example 2: New customer
        example_new_customer()
        
        # Example 3: Orchestrator workflow
        example_orchestrator_workflow()
        
        # Example 4: Batch processing
        example_batch_processing()
        
        print("\n" + "=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. AWS credentials configured")
        print("  2. Correct agent ARN and alias ID")
        print("  3. Proper IAM permissions")
