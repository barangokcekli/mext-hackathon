#!/bin/bash

export AWS_PROFILE=default

echo "=========================================="
echo "🚀 AWS DEPLOYED AGENT - QUICK TEST"
echo "=========================================="

# Test 1: Aktif Müşteri
echo ""
echo "TEST 1: Aktif High-Value Müşteri"
echo "------------------------------------------"
time agentcore invoke '{"customerData": {"customerId": "C-TEST-001", "city": "Istanbul", "customer": {"customerId": "C-TEST-001", "age": 32, "gender": "F", "registeredAt": "2023-01-15T00:00:00", "productHistory": [{"productId": "P-2001", "category": "SKINCARE", "totalQuantity": 15, "totalSpent": 899.25, "orderCount": 15, "lastPurchase": "2026-02-10T00:00:00", "avgDaysBetween": 25}]}, "region": {"name": "Marmara", "climateType": "Temperate", "medianBasket": 75.0, "trend": "SKINCARE"}}}' | grep -A 5 '"analysis"'

# Test 2: Yeni Müşteri
echo ""
echo "TEST 2: Yeni Müşteri (Boş History)"
echo "------------------------------------------"
time agentcore invoke '{"customerData": {"customerId": "C-NEW-001", "city": "Antalya", "customer": {"customerId": "C-NEW-001", "age": 22, "gender": "F", "registeredAt": "2026-02-01T00:00:00", "productHistory": []}, "region": {"name": "Akdeniz", "climateType": "Mediterranean", "medianBasket": 85.0, "trend": "SKINCARE"}}}' | grep -A 5 '"analysis"'

# Test 3: Region Mode
echo ""
echo "TEST 3: Region Mode (No Customer ID)"
echo "------------------------------------------"
time agentcore invoke '{"customerData": {"city": "Antalya", "region": {"name": "Akdeniz", "climateType": "Mediterranean", "medianBasket": 85.0, "trend": "SKINCARE"}}}' | grep -A 5 '"analysis"'

echo ""
echo "=========================================="
echo "✅ TESTS COMPLETE!"
echo "=========================================="
