"""
Performance Test: Pure analysis function (no agent/AWS)
"""
import time
import sys

# Import only the analysis function, not the agent
sys.path.insert(0, '.')

# Import individual functions
from customer_segment_agent import (
    calculate_age_segment,
    calculate_churn_segment,
    calculate_value_segment,
    calculate_loyalty_tier,
    analyze_customer_data
)

# 20 farklı müşteri profili
customers = [
    {"customerId": "C-TEST-001", "city": "Istanbul", "customer": {"customerId": "C-TEST-001", "age": 32, "gender": "F", "registeredAt": "2023-01-15T00:00:00", "productHistory": [{"productId": "P-2001", "category": "SKINCARE", "totalQuantity": 15, "totalSpent": 899.25, "orderCount": 15, "lastPurchase": "2026-02-10T00:00:00", "avgDaysBetween": 25}]}, "region": {"name": "Marmara", "climateType": "Temperate", "medianBasket": 75.0, "trend": "SKINCARE"}},
    {"customerId": "C-TEST-002", "city": "Ankara", "customer": {"customerId": "C-TEST-002", "age": 45, "gender": "F", "registeredAt": "2024-06-20T00:00:00", "productHistory": [{"productId": "P-1001", "category": "MAKEUP", "totalQuantity": 2, "totalSpent": 179.80, "orderCount": 2, "lastPurchase": "2025-12-20T00:00:00", "avgDaysBetween": 60}]}, "region": {"name": "İç Anadolu", "climateType": "Continental", "medianBasket": 70.0, "trend": "MAKEUP"}},
    {"customerId": "C-TEST-003", "city": "Izmir", "customer": {"customerId": "C-TEST-003", "age": 38, "gender": "F", "registeredAt": "2024-03-10T00:00:00", "productHistory": [{"productId": "P-3001", "category": "FRAGRANCE", "totalQuantity": 3, "totalSpent": 449.70, "orderCount": 3, "lastPurchase": "2025-10-15T00:00:00", "avgDaysBetween": 45}]}, "region": {"name": "Ege", "climateType": "Mediterranean", "medianBasket": 80.0, "trend": "FRAGRANCE"}},
    {"customerId": "C-TEST-004", "city": "Antalya", "customer": {"customerId": "C-TEST-004", "age": 22, "gender": "F", "registeredAt": "2026-02-01T00:00:00", "productHistory": []}, "region": {"name": "Akdeniz", "climateType": "Mediterranean", "medianBasket": 85.0, "trend": "SKINCARE"}},
    {"customerId": "C-TEST-005", "city": "Bursa", "customer": {"customerId": "C-TEST-005", "age": 24, "gender": "F", "registeredAt": "2025-08-15T00:00:00", "productHistory": [{"productId": "P-1001", "category": "MAKEUP", "totalQuantity": 1, "totalSpent": 89.90, "orderCount": 1, "lastPurchase": "2026-01-20T00:00:00", "avgDaysBetween": None}, {"productId": "P-2004", "category": "SKINCARE", "totalQuantity": 1, "totalSpent": 64.90, "orderCount": 1, "lastPurchase": "2026-01-15T00:00:00", "avgDaysBetween": None}]}, "region": {"name": "Marmara", "climateType": "Temperate", "medianBasket": 75.0, "trend": "MAKEUP"}},
    {"customerId": "C-TEST-006", "city": "Trabzon", "customer": {"customerId": "C-TEST-006", "age": 58, "gender": "F", "registeredAt": "2023-05-10T00:00:00", "productHistory": [{"productId": "P-2002", "category": "SKINCARE", "totalQuantity": 20, "totalSpent": 2398.00, "orderCount": 20, "lastPurchase": "2026-02-09T00:00:00", "avgDaysBetween": 28}]}, "region": {"name": "Karadeniz", "climateType": "Oceanic", "medianBasket": 65.0, "trend": "WELLNESS"}},
    {"customerId": "C-TEST-007", "city": "Istanbul", "customer": {"customerId": "C-TEST-007", "age": 29, "gender": "M", "registeredAt": "2025-03-20T00:00:00", "productHistory": [{"productId": "P-3002", "category": "FRAGRANCE", "totalQuantity": 4, "totalSpent": 559.60, "orderCount": 4, "lastPurchase": "2026-02-01T00:00:00", "avgDaysBetween": 60}]}, "region": {"name": "Marmara", "climateType": "Temperate", "medianBasket": 75.0, "trend": "FRAGRANCE"}},
    {"customerId": "C-TEST-008", "city": "Gaziantep", "customer": {"customerId": "C-TEST-008", "age": 35, "gender": "F", "registeredAt": "2024-11-15T00:00:00", "productHistory": [{"productId": "P-1002", "category": "MAKEUP", "totalQuantity": 5, "totalSpent": 274.50, "orderCount": 5, "lastPurchase": "2026-02-08T00:00:00", "avgDaysBetween": 40}]}, "region": {"name": "Güneydoğu Anadolu", "climateType": "Continental", "medianBasket": 60.0, "trend": "PERSONALCARE"}},
    {"customerId": "C-TEST-009", "city": "Adana", "customer": {"customerId": "C-TEST-009", "age": 41, "gender": "F", "registeredAt": "2025-06-01T00:00:00", "productHistory": [{"productId": "P-2004", "category": "SKINCARE", "totalQuantity": 8, "totalSpent": 519.20, "orderCount": 8, "lastPurchase": "2026-02-10T00:00:00", "avgDaysBetween": 30}]}, "region": {"name": "Akdeniz", "climateType": "Mediterranean", "medianBasket": 85.0, "trend": "SKINCARE"}},
    {"customerId": "C-TEST-010", "city": "Kayseri", "customer": {"customerId": "C-TEST-010", "age": 27, "gender": "F", "registeredAt": "2026-01-10T00:00:00", "productHistory": [{"productId": "P-1001", "category": "MAKEUP", "totalQuantity": 1, "totalSpent": 89.90, "orderCount": 1, "lastPurchase": "2026-01-25T00:00:00", "avgDaysBetween": None}]}, "region": {"name": "İç Anadolu", "climateType": "Continental", "medianBasket": 70.0, "trend": "MAKEUP"}},
    {"customerId": "C-TEST-011", "city": "Eskişehir", "customer": {"customerId": "C-TEST-011", "age": 26, "gender": "F", "registeredAt": "2024-09-01T00:00:00", "productHistory": [{"productId": "P-1001", "category": "MAKEUP", "totalQuantity": 10, "totalSpent": 899.00, "orderCount": 10, "lastPurchase": "2026-02-11T00:00:00", "avgDaysBetween": 28}]}, "region": {"name": "İç Anadolu", "climateType": "Continental", "medianBasket": 70.0, "trend": "MAKEUP"}},
    {"customerId": "C-TEST-012", "city": "Samsun", "customer": {"customerId": "C-TEST-012", "age": 55, "gender": "F", "registeredAt": "2023-08-20T00:00:00", "productHistory": [{"productId": "P-6001", "category": "WELLNESS", "totalQuantity": 15, "totalSpent": 2698.50, "orderCount": 15, "lastPurchase": "2026-02-10T00:00:00", "avgDaysBetween": 30}]}, "region": {"name": "Karadeniz", "climateType": "Oceanic", "medianBasket": 65.0, "trend": "WELLNESS"}},
    {"customerId": "C-TEST-013", "city": "Konya", "customer": {"customerId": "C-TEST-013", "age": 33, "gender": "F", "registeredAt": "2024-07-15T00:00:00", "productHistory": [{"productId": "P-2001", "category": "SKINCARE", "totalQuantity": 6, "totalSpent": 359.40, "orderCount": 6, "lastPurchase": "2025-10-20T00:00:00", "avgDaysBetween": 30}]}, "region": {"name": "İç Anadolu", "climateType": "Continental", "medianBasket": 70.0, "trend": "SKINCARE"}},
    {"customerId": "C-TEST-014", "city": "Mersin", "customer": {"customerId": "C-TEST-014", "age": 30, "gender": "F", "registeredAt": "2025-02-10T00:00:00", "productHistory": [{"productId": "P-1001", "category": "MAKEUP", "totalQuantity": 2, "totalSpent": 179.80, "orderCount": 2, "lastPurchase": "2026-02-05T00:00:00", "avgDaysBetween": None}]}, "region": {"name": "Akdeniz", "climateType": "Mediterranean", "medianBasket": 85.0, "trend": "SKINCARE"}},
    {"customerId": "C-TEST-015", "city": "Diyarbakır", "customer": {"customerId": "C-TEST-015", "age": 42, "gender": "F", "registeredAt": "2025-11-01T00:00:00", "productHistory": [{"productId": "P-2002", "category": "SKINCARE", "totalQuantity": 3, "totalSpent": 359.70, "orderCount": 3, "lastPurchase": "2026-02-08T00:00:00", "avgDaysBetween": 30}]}, "region": {"name": "Güneydoğu Anadolu", "climateType": "Continental", "medianBasket": 60.0, "trend": "SKINCARE"}},
    {"customerId": "C-TEST-016", "city": "Denizli", "customer": {"customerId": "C-TEST-016", "age": 28, "gender": "F", "registeredAt": "2024-12-01T00:00:00", "productHistory": [{"productId": "P-5001", "category": "HAIRCARE", "totalQuantity": 8, "totalSpent": 399.20, "orderCount": 8, "lastPurchase": "2026-02-10T00:00:00", "avgDaysBetween": 25}]}, "region": {"name": "Ege", "climateType": "Mediterranean", "medianBasket": 80.0, "trend": "HAIRCARE"}},
    {"customerId": "C-TEST-017", "city": "Malatya", "customer": {"customerId": "C-TEST-017", "age": 36, "gender": "F", "registeredAt": "2025-10-15T00:00:00", "productHistory": [{"productId": "P-1001", "category": "MAKEUP", "totalQuantity": 2, "totalSpent": 179.80, "orderCount": 2, "lastPurchase": "2026-02-11T00:00:00", "avgDaysBetween": None}]}, "region": {"name": "Doğu Anadolu", "climateType": "Continental", "medianBasket": 55.0, "trend": "MAKEUP"}},
    {"customerId": "C-TEST-018", "city": "Balıkesir", "customer": {"customerId": "C-TEST-018", "age": 47, "gender": "F", "registeredAt": "2024-04-10T00:00:00", "productHistory": [{"productId": "P-3001", "category": "FRAGRANCE", "totalQuantity": 3, "totalSpent": 449.70, "orderCount": 3, "lastPurchase": "2025-12-25T00:00:00", "avgDaysBetween": 90}]}, "region": {"name": "Marmara", "climateType": "Temperate", "medianBasket": 75.0, "trend": "FRAGRANCE"}},
    {"customerId": "C-TEST-019", "city": "Kocaeli", "customer": {"customerId": "C-TEST-019", "age": 34, "gender": "F", "registeredAt": "2023-06-01T00:00:00", "productHistory": [{"productId": "P-2001", "category": "SKINCARE", "totalQuantity": 25, "totalSpent": 1498.75, "orderCount": 25, "lastPurchase": "2026-02-11T00:00:00", "avgDaysBetween": 20}]}, "region": {"name": "Marmara", "climateType": "Temperate", "medianBasket": 75.0, "trend": "SKINCARE"}},
    {"customerId": "C-TEST-020", "city": "Van", "customer": {"customerId": "C-TEST-020", "age": 39, "gender": "F", "registeredAt": "2025-05-20T00:00:00", "productHistory": [{"productId": "P-2004", "category": "SKINCARE", "totalQuantity": 5, "totalSpent": 324.50, "orderCount": 5, "lastPurchase": "2026-02-09T00:00:00", "avgDaysBetween": 35}]}, "region": {"name": "Doğu Anadolu", "climateType": "Continental", "medianBasket": 55.0, "trend": "SKINCARE"}},
]

print("=" * 100)
print("⚡ PERFORMANCE TEST: 20 CUSTOMER ANALYSIS (Pure Python - No AWS)")
print("=" * 100)

# Toplam süre
total_start = time.time()

# Her müşteri için süre kaydet
individual_times = []
results = []

for i, customer_data in enumerate(customers, 1):
    customer_id = customer_data['customerId']
    
    # Tek müşteri analizi
    start = time.time()
    result = analyze_customer_data(customer_data)
    end = time.time()
    
    elapsed = (end - start) * 1000  # milliseconds
    individual_times.append(elapsed)
    results.append(result)
    
    mode_icon = "🆕" if result['mode'] == 'new_customer' else "👤"
    print(f"{mode_icon} {i:2d}. {customer_id}: {elapsed:6.2f}ms | {result['ageSegment']:15s} | {result['churnSegment']:6s} | {result['loyaltyTier']:6s} | ${result['totalSpent']:8.2f}")

total_end = time.time()
total_elapsed = (total_end - total_start) * 1000

print("\n" + "=" * 100)
print("📊 PERFORMANCE SUMMARY")
print("=" * 100)

print(f"\n⏱️  TIMING STATISTICS:")
print(f"  Total Time: {total_elapsed:.2f}ms ({total_elapsed/1000:.3f}s)")
print(f"  Average per Customer: {sum(individual_times)/len(individual_times):.2f}ms")
print(f"  Fastest: {min(individual_times):.2f}ms (Customer #{individual_times.index(min(individual_times))+1})")
print(f"  Slowest: {max(individual_times):.2f}ms (Customer #{individual_times.index(max(individual_times))+1})")
print(f"  Throughput: {len(customers)/(total_elapsed/1000):.2f} customers/second")
print(f"  Estimated 1000 customers: {(total_elapsed/len(customers))*1000/1000:.2f}s")
print(f"  Estimated 10000 customers: {(total_elapsed/len(customers))*10000/1000:.2f}s")

print(f"\n✅ ANALYSIS RESULTS:")
print(f"  Total Customers: {len(results)}")
print(f"  Regular Mode: {len([r for r in results if r['mode'] == 'regular'])}")
print(f"  New Customer Mode: {len([r for r in results if r['mode'] == 'new_customer'])}")
print(f"  Region Mode: {len([r for r in results if r['mode'] == 'region'])}")

# Segment dağılımı
age_segments = {}
churn_segments = {}
loyalty_tiers = {}
value_segments = {}

for r in results:
    age_segments[r['ageSegment']] = age_segments.get(r['ageSegment'], 0) + 1
    churn_segments[r['churnSegment']] = churn_segments.get(r['churnSegment'], 0) + 1
    loyalty_tiers[r['loyaltyTier']] = loyalty_tiers.get(r['loyaltyTier'], 0) + 1
    value_segments[r['valueSegment']] = value_segments.get(r['valueSegment'], 0) + 1

print(f"\n🎯 SEGMENTATION BREAKDOWN:")
print(f"  Age Segments: {dict(sorted(age_segments.items()))}")
print(f"  Churn Risk: {dict(sorted(churn_segments.items()))}")
print(f"  Value Tiers: {dict(sorted(value_segments.items()))}")
print(f"  Loyalty Tiers: {dict(sorted(loyalty_tiers.items()))}")

# Finansal özet
total_revenue = sum(r['totalSpent'] for r in results)
avg_customer_value = total_revenue / len(results)
total_orders = sum(r['orderCount'] for r in results)

print(f"\n💰 FINANCIAL SUMMARY:")
print(f"  Total Revenue: ${total_revenue:,.2f}")
print(f"  Avg Customer Value: ${avg_customer_value:,.2f}")
print(f"  Total Orders: {total_orders}")
print(f"  Avg Orders per Customer: {total_orders/len(results):.1f}")

# Performans değerlendirmesi
avg_time = sum(individual_times)/len(individual_times)
if avg_time < 10:
    performance = "🚀 BLAZING FAST"
    rating = "A+"
elif avg_time < 50:
    performance = "⚡ EXCELLENT"
    rating = "A"
elif avg_time < 100:
    performance = "✅ GOOD"
    rating = "B"
elif avg_time < 200:
    performance = "⚠️  ACCEPTABLE"
    rating = "C"
else:
    performance = "❌ NEEDS OPTIMIZATION"
    rating = "D"

print(f"\n🏆 PERFORMANCE RATING: {performance} (Grade: {rating})")
print(f"  Target: <50ms per customer")
print(f"  Actual: {avg_time:.2f}ms per customer")
print(f"  Status: {'PASSED ✅' if avg_time < 50 else 'REVIEW NEEDED ⚠️' if avg_time < 100 else 'FAILED ❌'}")

# Throughput projections
print(f"\n📈 THROUGHPUT PROJECTIONS:")
throughput_per_sec = len(customers)/(total_elapsed/1000)
print(f"  Per Second: {throughput_per_sec:.2f} customers")
print(f"  Per Minute: {throughput_per_sec * 60:.0f} customers")
print(f"  Per Hour: {throughput_per_sec * 3600:.0f} customers")
print(f"  Per Day: {throughput_per_sec * 86400:,.0f} customers")

print("\n" + "=" * 100)
print("✅ PERFORMANCE TEST COMPLETE!")
print("=" * 100)
