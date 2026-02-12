"""
Test deployed agent on AWS with 20 customers
"""
import subprocess
import json
import time

# 20 test customer
test_customers = [
    # 1. Aktif High-Value
    {
        "customerId": "C-TEST-001",
        "city": "Istanbul",
        "customer": {
            "customerId": "C-TEST-001",
            "age": 32,
            "gender": "F",
            "registeredAt": "2023-01-15T00:00:00",
            "productHistory": [
                {"productId": "P-2001", "category": "SKINCARE", "totalQuantity": 15, "totalSpent": 899.25, "orderCount": 15, "lastPurchase": "2026-02-10T00:00:00", "avgDaysBetween": 25}
            ]
        },
        "region": {"name": "Marmara", "climateType": "Temperate", "medianBasket": 75.0, "trend": "SKINCARE"}
    },
    # 2. Riskli
    {
        "customerId": "C-TEST-002",
        "city": "Ankara",
        "customer": {
            "customerId": "C-TEST-002",
            "age": 45,
            "gender": "F",
            "registeredAt": "2024-06-20T00:00:00",
            "productHistory": [
                {"productId": "P-1001", "category": "MAKEUP", "totalQuantity": 2, "totalSpent": 179.80, "orderCount": 2, "lastPurchase": "2025-12-20T00:00:00", "avgDaysBetween": 60}
            ]
        },
        "region": {"name": "İç Anadolu", "climateType": "Continental", "medianBasket": 70.0, "trend": "MAKEUP"}
    },
    # 3. Yeni Müşteri
    {
        "customerId": "C-TEST-003",
        "city": "Antalya",
        "customer": {
            "customerId": "C-TEST-003",
            "age": 22,
            "gender": "F",
            "registeredAt": "2026-02-01T00:00:00",
            "productHistory": []
        },
        "region": {"name": "Akdeniz", "climateType": "Mediterranean", "medianBasket": 85.0, "trend": "SKINCARE"}
    },
]

print("=" * 100)
print("🚀 TESTING DEPLOYED AGENT ON AWS - 3 CUSTOMERS")
print("=" * 100)

total_start = time.time()
results = []
times = []

for i, customer_data in enumerate(test_customers, 1):
    customer_id = customer_data['customerId']
    
    # Prepare payload
    payload = {
        "customerData": customer_data
    }
    
    payload_json = json.dumps(payload)
    
    print(f"\n{'='*100}")
    print(f"TEST {i}/3: {customer_id}")
    print(f"{'='*100}")
    
    # Invoke agent
    start = time.time()
    try:
        result = subprocess.run(
            ['agentcore', 'invoke', payload_json],
            capture_output=True,
            text=True,
            timeout=30
        )
        end = time.time()
        elapsed = (end - start) * 1000
        times.append(elapsed)
        
        if result.returncode == 0:
            # Parse response
            try:
                response = json.loads(result.stdout)
                results.append(response)
                
                # Extract analysis if available
                if 'analysis' in response:
                    analysis = response['analysis']
                    print(f"✅ SUCCESS ({elapsed:.0f}ms)")
                    print(f"  Mode: {analysis.get('mode', 'N/A')}")
                    print(f"  Age: {analysis.get('age', 'N/A')} ({analysis.get('ageSegment', 'N/A')})")
                    print(f"  Churn: {analysis.get('churnSegment', 'N/A')}")
                    print(f"  Value: {analysis.get('valueSegment', 'N/A')}")
                    print(f"  Loyalty: {analysis.get('loyaltyTier', 'N/A')}")
                    print(f"  Total Spent: ${analysis.get('totalSpent', 0):.2f}")
                    print(f"  Orders: {analysis.get('orderCount', 0)}")
                else:
                    print(f"✅ SUCCESS ({elapsed:.0f}ms)")
                    print(f"  Response: {result.stdout[:200]}...")
                    
            except json.JSONDecodeError:
                print(f"⚠️  Response not JSON ({elapsed:.0f}ms)")
                print(f"  Output: {result.stdout[:200]}")
        else:
            print(f"❌ FAILED ({elapsed:.0f}ms)")
            print(f"  Error: {result.stderr[:200]}")
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT (>30s)")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

total_end = time.time()
total_elapsed = (total_end - total_start) * 1000

print(f"\n{'='*100}")
print("📊 DEPLOYMENT TEST SUMMARY")
print(f"{'='*100}")

if times:
    print(f"\n⏱️  TIMING:")
    print(f"  Total Time: {total_elapsed:.0f}ms ({total_elapsed/1000:.2f}s)")
    print(f"  Average per Customer: {sum(times)/len(times):.0f}ms")
    print(f"  Fastest: {min(times):.0f}ms")
    print(f"  Slowest: {max(times):.0f}ms")
    
    avg_time = sum(times)/len(times)
    if avg_time < 1000:
        rating = "🚀 EXCELLENT"
    elif avg_time < 3000:
        rating = "✅ GOOD"
    elif avg_time < 5000:
        rating = "⚠️  ACCEPTABLE"
    else:
        rating = "❌ SLOW"
    
    print(f"\n🏆 PERFORMANCE: {rating}")
    print(f"  Average: {avg_time:.0f}ms per customer")
    print(f"  Note: Includes network latency + cold start")

print(f"\n✅ RESULTS:")
print(f"  Total Tests: {len(test_customers)}")
print(f"  Successful: {len(results)}")
print(f"  Failed: {len(test_customers) - len(results)}")

print(f"\n{'='*100}")
print("✅ DEPLOYMENT TEST COMPLETE!")
print(f"{'='*100}")
